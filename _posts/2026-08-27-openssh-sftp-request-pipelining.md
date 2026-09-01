---
layout: post
title: "SFTP Request Pipelining in OpenSSH — Window Ramping, Negotiated Limits and scp"
date:   2026-08-27
lang: en
locale: en-GB
categories: network security linux
tags: ssh linux network protocole
series: openssh
description: How the OpenSSH SFTP client keeps requests in flight, ramps its window from one to sixty-four, negotiates buffer sizes with the server and backs scp.
image: /assets/article/network/openssh-sftp-pipelining.png
isMath: false
---

SFTP is a request and response protocol carried inside a single SSH channel. Implemented in the obvious way, a file transfer costs one network round trip per block, which caps throughput at the block size divided by the round-trip time no matter how much bandwidth is available. On a 100 ms link with 32 KiB blocks that ceiling is about 320 KiB per second, and no amount of extra capacity moves it.

The OpenSSH client does not work that way. A large part of `sftp-client.c` exists to keep many requests outstanding at once, to size those requests against limits the server advertises, and to recover when a server returns less data than was asked for. This article reads that machinery, and then follows it into `scp`, which has been a front end to the same code since OpenSSH 9.0. The revision analysed declares `OpenSSH_10.5p1` in `version.h`.

The protocol itself was never finished as an RFC. The working document is [draft-ietf-secsh-filexfer-02](https://datatracker.ietf.org/doc/html/draft-ietf-secsh-filexfer-02), and OpenSSH's extensions to it are recorded in the `PROTOCOL` file distributed with the source.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Two numbers that set the shape of a transfer

The defaults are declared at the top of `sftp-client.c`:

```c
#define DEFAULT_COPY_BUFLEN	32768
#define DEFAULT_NUM_REQUESTS	64
```

The first is how much data a single read or write asks for. The second is how many such requests may be outstanding at any moment. Together they describe a sliding window of about 2 MiB, and both are reachable from the command line. `sftp -B` sets the buffer size and `sftp -R` sets the request ceiling, which `sftp.1` documents as "how many requests may be outstanding at any one time", noting that "the default is 64 outstanding requests".

The product of the two is what matters for throughput. A window of 64 requests at 32 KiB stays busy on a link whose bandwidth-delay product is under 2 MiB, and becomes the limiting factor above that.

![Component diagram of the SFTP client showing the request window, the outstanding request queue, and the relationship between sftp, scp and sftp-client.c]({{site.url_complet}}/assets/article/network/openssh-sftp-pipelining-concept.png)

## The buffer size is negotiated, not assumed

Sending 32 KiB requests to a server that refuses them wastes a round trip per file. OpenSSH added an extension so the client can ask first, described in `PROTOCOL`:

```
	uint32		id
	string		"limits@openssh.com"
```

to which the server replies with four values:

```
	uint32		id
	uint64		max-packet-length
	uint64		max-read-length
	uint64		max-write-length
	uint64		max-open-handles
```

The document is direct about why this matters, saying clients "should not attempt to exceed these limits as the server might sever the connection immediately".

The client queries at connection setup and clamps itself accordingly, keeping separate sizes for the two directions:

```c
/* Query the server for its limits */
if (ret->exts & SFTP_EXT_LIMITS) {
	struct sftp_limits limits;
	if (sftp_get_limits(ret, &limits) != 0)
		fatal_f("limits failed");

	/* If the caller did not specify, find a good value */
	if (transfer_buflen == 0) {
		ret->download_buflen = MINIMUM(limits.read_length,
		    SFTP_MAX_MSG_LENGTH - 1024);
		ret->upload_buflen = MINIMUM(limits.write_length,
		    SFTP_MAX_MSG_LENGTH - 1024);
		ret->download_buflen = MAXIMUM(ret->download_buflen, 64);
		ret->upload_buflen = MAXIMUM(ret->upload_buflen, 64);
```

Two details are worth noting. The negotiated value applies only when the user did not ask for a specific size, so an explicit `-B` overrides the server's advice rather than being clamped by it. And the result is floored at 64 bytes, so a server advertising an unusable limit cannot drive the client into requests so small that no progress is made.

## The window opens gradually

Knowing the ceiling does not mean starting at it. The download path begins with a single request in flight:

```c
write_error = read_error = write_errno = num_req = 0;
max_req = 1;
```

and grows the window by one on each reply that is not the end of the file:

```c
if (max_req > 0) {	/* max_req = 0 iff EOF received */
	if (size > 0 && offset > size) {
		/* Only one request at a time
		 * after the expected EOF */
		max_req = 1;
	} else if (max_req < conn->num_requests) {
		++max_req;
	}
}
```

![Sequence diagram of an SFTP download showing the outstanding-request window growing from one to sixty-four, short-read re-requests, and the drain at end of file]({{site.url_complet}}/assets/article/network/openssh-sftp-pipelining-sequence.png)

The ramp exists because the client learns things from the first few replies that change how it should behave, and discovering them after one request is cheaper than discovering them after sixty-four. It also collapses the window deliberately once the transfer passes the size reported when the file was opened, so the client stops speculating past the end of a file whose length may have changed.

The upload path enforces the same ceiling from the opposite direction, reading an acknowledgement whenever the number of unacknowledged writes reaches the limit:

```c
if (id == startid || len == 0 ||
    id - ackid >= conn->num_requests) {
```

## Handling a server that returns less than it was asked

A server may legitimately answer a 32 KiB read with fewer bytes. A pipelined client cannot treat that as end of file, because a later request in flight may already cover data beyond it. The client re-requests the missing tail and adjusts its idea of a reasonable request size:

```c
/* Resend the request for the missing data */
req->id = conn->msg_id++;
req->len -= len;
req->offset += len;
send_read_request(conn, req->id,
    req->offset, req->len, handle, handle_len);
/* Reduce the request size */
if (len < buflen)
	buflen = MAXIMUM(MIN_READ_SIZE, len);
```

`MIN_READ_SIZE` is 512, so the adaptation has a floor. A server that consistently returns short reads pulls the client down toward its actual behaviour instead of forcing a re-request on every block indefinitely.

When the transfer finishes, the client does not assume the pipeline drained correctly. It asserts it:

```c
/* Sanity check */
if (TAILQ_FIRST(&requests) != NULL)
	fatal("Transfer complete, but requests still in queue");
```

This is the check that separates a pipelined implementation from a correct one. Outstanding requests tracked in a queue can be lost through a logic error in exactly the paths that are hardest to test, and the failure mode without this line is a truncated file that reports success.

## What the server side looks like

`sftp-server.c` is comparatively plain: a dispatch table mapping request types to handlers.

```c
static const struct sftp_handler handlers[] = {
	/* NB. SSH2_FXP_OPEN does the readonly check in the handler itself */
	{ "open", NULL, SSH2_FXP_OPEN, process_open, 0 },
	{ "close", NULL, SSH2_FXP_CLOSE, process_close, 0 },
	{ "read", NULL, SSH2_FXP_READ, process_read, 0 },
	{ "write", NULL, SSH2_FXP_WRITE, process_write, 1 },
	...
```

The trailing integer marks a handler as mutating, which is how `sftp-server -R` implements read-only service without each handler needing its own check. OpenSSH's protocol extensions are registered in a second table of the same shape, including `posix-rename@openssh.com`, `hardlink@openssh.com`, `fsync@openssh.com`, `statvfs@openssh.com` and the `limits@openssh.com` request described above.

## scp is a front end to this code

Since OpenSSH 9.0, `scp` speaks SFTP by default. The mode variable in `scp.c` is initialised to the SFTP path, and the historical protocol is opt-in:

```c
enum scp_mode_e mode = MODE_SFTP;
```

`scp.1` documents the flag that reverses this, saying `-O` will "use the legacy SCP protocol for file transfers instead of the SFTP protocol", and that it "may be necessary for servers that do not implement SFTP, for backwards-compatibility for particular filename wildcard patterns and for expanding paths with a `~` prefix for older SFTP servers".

The practical consequence is that `scp` inherited the pipelining described above. It also inherited a different model of filename handling, which is the source of most reported behaviour changes: the legacy protocol expanded globs and tildes by passing them through a remote shell, and the SFTP path does not.

`sftp-client.h` also exposes a transfer that never touches local disk:

```c
int sftp_crossload(struct sftp_conn *from, struct sftp_conn *to, ...
```

This moves data between two SFTP connections directly, which is what a copy between two remote hosts uses.

## Conclusion

The client's throughput comes from three mechanisms working together rather than from a single buffer size. Requests are pipelined so the link stays busy across round trips, the request size is negotiated against limits the server publishes rather than assumed, and the window opens gradually so that a server behaving unusually is discovered cheaply.

The correctness of the result rests on the parts that handle imperfect replies: re-requesting a short read instead of treating it as end of file, flooring the adaptive buffer size, and asserting that the request queue is empty before declaring a transfer complete.

![Mindmap of SFTP request pipelining in OpenSSH covering the request window, negotiated limits, short-read handling and the scp front end]({{site.url_complet}}/assets/article/network/openssh-sftp-pipelining.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Outstanding request** | A read or write sent to the server whose reply has not yet arrived, tracked in a queue by the client. |
| **Request window** | The number of outstanding requests the client permits, ramping from one up to `num_requests`. |
| **`num_requests`** | The ceiling on the request window, 64 by default and settable with `sftp -R`. |
| **Transfer buffer length** | The number of bytes a single read or write asks for, 32768 by default and settable with `sftp -B`. |
| **`limits@openssh.com`** | The protocol extension by which a client asks a server for its maximum packet, read, write and open-handle limits. |
| **Short read** | A data reply containing fewer bytes than requested, which the client re-requests rather than treating as end of file. |
| **`MIN_READ_SIZE`** | The 512-byte floor below which the adaptive request size will not shrink. |
| **Acknowledgement window** | The upload-side equivalent of the request window, bounded by the comparison of the current message id against the last acknowledged one. |
| **Crossload** | A transfer between two SFTP connections that does not stage data on the local filesystem. |
| **Legacy SCP protocol** | The original rcp-derived transfer protocol, still selectable with `scp -O` but no longer the default. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| At most `num_requests` operations are in flight at any moment. | The `max_req` ceiling on downloads and the `id - ackid` comparison on uploads. | Memory use tracks file size rather than configured window size. |
| A completed transfer leaves no request in the queue. | An explicit `fatal()` check after the transfer loop. | A dropped reply yields a truncated file that reports success. |
| Request sizes never exceed the limits the server advertised. | The clamp against `limits.read_length` and `limits.write_length` at connection setup. | The server severs the connection, as `PROTOCOL` warns it may. |
| The adaptive request size never falls below 512 bytes. | The `MAXIMUM(MIN_READ_SIZE, len)` floor. | A misbehaving server drives the client into requests too small to make progress. |
| A short reply is treated as incomplete data rather than as end of file. | The re-request path in the download loop. | Files are silently truncated at the first short read. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| An explicit `-B` overrides the server's advertised limits instead of being clamped by them. | Leave the buffer size unset unless there is a measured reason, so negotiation can pick a safe value. |
| Raising `-R` increases memory use in proportion to the window. | Tune it for a specific high-latency link rather than globally. |
| `scp` uses SFTP by default, and does not expand globs or `~` through a remote shell. | Test wildcard and tilde paths against the default mode, and reserve `-O` for servers without an SFTP subsystem. |
| A server implementing SFTP without `limits@openssh.com` gets the compiled-in defaults. | Ensure such a server accepts 32 KiB reads and writes, or have clients set `-B` explicitly. |
| `sftp-server -R` rejects mutating operations using a per-handler flag. | Rely on the server-side read-only mode rather than filtering client behaviour, since the client is not the enforcement point. |

## Frequently Asked Questions

**Q: Why is pipelining necessary at all, given that SSH already has its own flow control?**

Because the two operate at different layers and solve different problems. The channel window governs how many bytes may be in flight on the SSH channel, but SFTP sits above it as a request and response protocol. A client that issues one read and waits for its reply before issuing the next is idle for a full round trip regardless of how much channel credit is available. Keeping several SFTP requests outstanding is what converts that available credit into throughput.

**Q: What does the client learn from the first few replies that justifies starting at one request?**

Three things that change its subsequent behaviour:

- Whether the server returns full-size blocks, since a short reply pulls the adaptive request size down toward what the server actually serves.
- Whether the file's real length matches what was reported when it was opened, which determines when the window should collapse back to one.
- Whether the transfer is short enough to finish before the window ever reaches its ceiling, in which case the ramp costs nothing.

Discovering any of these after a single request is cheaper than discovering it with sixty-four already in flight.

**Q: Why can a short data reply not be treated as the end of the file?**

Because requests are pipelined, so the client may already have issued reads covering offsets beyond the short one. Data for those offsets can still arrive. Treating the short reply as terminal would abandon a file that the server was willing to serve in full, and would do so silently. The client instead re-requests the missing tail at an adjusted offset and length, and only end of file, signalled explicitly, stops the loop.

**Q: What is the purpose of the `limits@openssh.com` extension?**

It lets the client discover the server's maximum packet, read, write and open-handle sizes before sending anything large. `PROTOCOL` warns that a server "might sever the connection immediately" if a client exceeds these, so the alternative to asking is guessing and risking a dropped connection. The client queries at setup and clamps its download and upload buffer sizes independently, subject to a 64-byte floor.

**Q: `scp` and `sftp` now share a transfer implementation. What follows from that for behaviour and for tuning?**

For behaviour, `scp` gained the SFTP path's filename semantics along with its performance. The legacy protocol expanded wildcards and `~` by handing the path to a remote shell, while the SFTP path does not, which accounts for most of the differences people notice after upgrading. `scp -O` restores the old protocol for servers that need it.

For tuning, the two commands respond to the same underlying knobs, so a link that needs a larger window benefits from the same window size in both. The negotiation with `limits@openssh.com` also applies to both, which means a server that advertises conservative limits constrains `scp` exactly as it constrains `sftp`.

## References

### Specifications

- [draft-ietf-secsh-filexfer-02 — SSH File Transfer Protocol](https://datatracker.ietf.org/doc/html/draft-ietf-secsh-filexfer-02)
- [RFC 4254 — The Secure Shell (SSH) Connection Protocol](https://datatracker.ietf.org/doc/html/rfc4254)

### OpenSSH documents

- [PROTOCOL](https://github.com/openssh/openssh-portable/blob/0ef0f5a839831c213f24e3f2ae434765c607fb50/PROTOCOL) — the SFTP extensions, including `limits@openssh.com`

### Manual pages

- [sftp(1)](https://man.openbsd.org/sftp.1)
- [scp(1)](https://man.openbsd.org/scp.1)
- [sftp-server(8)](https://man.openbsd.org/sftp-server.8)

### Analyzed source

- [openssh/openssh-portable](https://github.com/openssh/openssh-portable) — analyzed at commit [`0ef0f5a839831c213f24e3f2ae434765c607fb50`](https://github.com/openssh/openssh-portable/tree/0ef0f5a839831c213f24e3f2ae434765c607fb50), 2026-08-27. The commit carries no release tag and sits after `V_9_7_P1`; `version.h` at this revision declares `OpenSSH_10.5p1`.
