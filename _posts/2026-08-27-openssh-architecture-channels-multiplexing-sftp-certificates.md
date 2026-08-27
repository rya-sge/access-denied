---
layout: post
title: "OpenSSH Architecture — Channels, Multiplexing, SFTP Pipelining, Certificates and Detached Signatures"
date:   2026-08-27
lang: en
locale: en-GB
categories: network security linux
tags: ssh linux network protocole digital-signature
description: How OpenSSH implements its channel layer, ControlMaster multiplexing, SFTP request pipelining, certificate options and sshsig detached signatures.
image: /assets/article/network/openssh-architecture-channels-multiplexing-sftp-certificates.png
isMath: false
---

Portable OpenSSH is roughly 158 C files. The features a user names individually (port forwarding, X11 forwarding, agent forwarding, SOCKS proxying, file transfer) are not separate subsystems in that source. They are configurations of a small number of abstractions that the code implements once.

This article reads five of those abstractions in the portable tree at its current development revision, which declares `OpenSSH_10.5p1` in `version.h`. Each section takes one subsystem, names the files that implement it, and quotes the constants and control flow that define its behaviour. The five were chosen because each one answers a question that the manual pages state as a fact without explaining the mechanism, such as why a second `ssh` to the same host returns instantly, why an SFTP transfer over a long link is not limited to one block per round trip, and why an unknown option inside a certificate is sometimes fatal and sometimes ignored.

The reading is deliberately narrow. It covers the connection protocol and the tools built on it, not the transport layer, the key exchange, or the privilege-separation model of the server.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The channel layer

Once authentication completes, an SSH connection carries the [SSH Connection Protocol](https://datatracker.ietf.org/doc/html/rfc4254), and everything after that point is a channel. `channels.c` is the largest hand-written C file in the tree at roughly 150 KB, and it implements one abstraction that every user-visible feature is expressed in.

The evidence is the type list in `channels.h`, which enumerates 23 values in a single namespace:

```c
#define SSH_CHANNEL_X11_LISTENER	1	/* Listening for inet X11 conn. */
#define SSH_CHANNEL_PORT_LISTENER	2	/* Listening on a port. */
#define SSH_CHANNEL_OPENING		3	/* waiting for confirmation */
#define SSH_CHANNEL_OPEN		4	/* normal open two-way channel */
#define SSH_CHANNEL_CLOSED		5	/* waiting for close confirmation */
#define SSH_CHANNEL_AUTH_SOCKET		6	/* authentication socket */
#define SSH_CHANNEL_X11_OPEN		7	/* reading first X11 packet */
#define SSH_CHANNEL_LARVAL		10	/* larval session */
#define SSH_CHANNEL_RPORT_LISTENER	11	/* Listening to a R-style port  */
#define SSH_CHANNEL_CONNECTING		12
#define SSH_CHANNEL_DYNAMIC		13
#define SSH_CHANNEL_ZOMBIE		14	/* Almost dead. */
#define SSH_CHANNEL_MUX_LISTENER	15	/* Listener for mux conn. */
#define SSH_CHANNEL_MUX_CLIENT		16	/* Conn. to mux client */
#define SSH_CHANNEL_ABANDONED		17	/* Abandoned session, eg mux */
#define SSH_CHANNEL_UNIX_LISTENER	18	/* Listening on a domain socket. */
#define SSH_CHANNEL_RUNIX_LISTENER	19	/* Listening to a R-style domain socket */
#define SSH_CHANNEL_MUX_PROXY		20	/* proxy channel for mux-client */
#define SSH_CHANNEL_RDYNAMIC_OPEN	21	/* reverse SOCKS, parsing request */
#define SSH_CHANNEL_RDYNAMIC_FINISH	22	/* reverse SOCKS, finishing connect */
```

Two observations follow from that list. First, the field is called `type` but several of its values are states rather than kinds, so a channel moves through `SSH_CHANNEL_OPENING`, `SSH_CHANNEL_OPEN`, `SSH_CHANNEL_CLOSED` and `SSH_CHANNEL_ZOMBIE` over its lifetime while remaining the same object. Second, features that appear unrelated to a user occupy adjacent entries: `SSH_CHANNEL_DYNAMIC` is the local SOCKS proxy created by `ssh -D`, whose first bytes are a SOCKS request parsed in band before the channel can be opened, and `SSH_CHANNEL_RDYNAMIC_OPEN` is the reverse of the same idea for `ssh -R`.

### One abstraction, several channel type strings

On the wire, the kind of a channel is a string carried in `SSH2_MSG_CHANNEL_OPEN`. Incoming ones are dispatched in `channels.c` through a short chain of `strcmp` branches:

```c
if (strcmp(rtype, "direct-tcpip") == 0) {
	...
} else if (strcmp(rtype, "direct-streamlocal@openssh.com") == 0) {
	...
} else if (strcmp(rtype, "forwarded-streamlocal@openssh.com") == 0) {
```

The standard types (`session`, `direct-tcpip`, `forwarded-tcpip`, `x11`) come from RFC 4254. The vendor-prefixed ones (`direct-streamlocal@openssh.com`, `forwarded-streamlocal@openssh.com`, `auth-agent@openssh.com`, `tun@openssh.com`) are OpenSSH extensions documented in the in-tree `PROTOCOL` file.

Not every type is created inside `channels.c`. The forwarding and X11 channels are, but a `session` channel is allocated by its caller, in `ssh.c` for the client's own session, in `mux.c` for one requested by a multiplexing client, and in `serverloop.c` on the server side:

```c
c = channel_new(ssh,
    "session", SSH_CHANNEL_OPENING, in, out, err,
    ...
```

`tun@openssh.com` is handled in `clientloop.c` and `serverloop.c` in the same way. The allocation site differs, but every one of them produces the same `struct Channel` and is serviced by the same event loop, which is the property that matters. Unix-domain-socket forwarding was added by defining a new type string rather than a new subsystem, which is why `-L` and `-R` accept a socket path in the same syntax position as a port.

### Flow control is per channel

Each channel carries its own credit-based window, held in `struct Channel` as four fields:

```c
u_int	remote_window;
u_int	remote_maxpacket;
u_int	local_window;
u_int	local_window_max;
```

The defaults are set in `channels.h`:

```c
#define CHAN_SES_PACKET_DEFAULT	(32*1024)
#define CHAN_SES_WINDOW_DEFAULT	(64*CHAN_SES_PACKET_DEFAULT)
```

A session channel therefore advertises a 2 MiB window built from 64 packets of 32 KiB. The window is per channel and not per connection, so a bulk transfer on one channel and an interactive shell on another are credited separately, and a stalled forwarded connection cannot stop a shell on the same transport from making progress.

### Closing is harder than opening

A channel has two independent halves, and `struct Channel` tracks them separately:

```c
u_int   istate;		/* input from channel (state of receive half) */
u_int   ostate;		/* output to channel  (state of transmit half) */
```

Each half runs its own four-state machine, defined in `channels.h` as `CHAN_INPUT_OPEN`, `CHAN_INPUT_WAIT_DRAIN`, `CHAN_INPUT_WAIT_OCLOSE`, `CHAN_INPUT_CLOSED` and the matching `CHAN_OUTPUT_*` values. The transition rules live in `nchan.c`.

![Two four-state machines, one per direction, showing a channel moving from OPEN through WAIT_DRAIN and WAIT_OCLOSE to CLOSED before CHANNEL_CLOSE is sent]({{site.url_complet}}/assets/article/network/openssh-channel-halfclose-state.png)

The reason for the complexity is that closing early loses data. A local process may have written its output and exited while bytes are still buffered for the peer, so the transmit half has to drain before it can signal EOF, and the channel can only be freed once both halves have closed and the peer has confirmed. The intermediate `SSH_CHANNEL_ZOMBIE` state exists to hold a channel that is finished locally but not yet acknowledged. `nchan.c` ships with two design documents in the tree, `nchan.ms` and `nchan2.ms`, written in troff.

## Connection multiplexing

When `ControlMaster` is enabled, the second `ssh` invocation to a host does not perform a key exchange or an authentication, because it is not acting as an SSH client at all. It connects to a Unix domain socket at `ControlPath` and speaks a private protocol to the first `ssh` process, which owns the real connection.

That protocol is defined in `PROTOCOL.mux` and implemented in `mux.c`. Its message set is small:

```c
#define MUX_MSG_HELLO		0x00000001
#define MUX_C_NEW_SESSION	0x10000002
#define MUX_C_ALIVE_CHECK	0x10000004
#define MUX_C_TERMINATE		0x10000005
#define MUX_C_OPEN_FWD		0x10000006
#define MUX_C_CLOSE_FWD		0x10000007
#define MUX_C_NEW_STDIO_FWD	0x10000008
#define MUX_C_STOP_LISTENING	0x10000009
#define MUX_C_PROXY		0x1000000f
#define MUX_S_OK		0x80000001
#define MUX_S_SESSION_OPENED	0x80000006
#define MUX_S_EXIT_MESSAGE	0x80000004
```

The multiplexing machinery is itself built on channels. `SSH_CHANNEL_MUX_LISTENER` is the listening socket, `SSH_CHANNEL_MUX_CLIENT` is a connected client, and `struct Channel` carries `ctl_chan` and `ctl_child_id` fields specifically to associate a session channel with the mux client that requested it.

The `MUX_C_OPEN_FWD` and `MUX_C_CLOSE_FWD` messages take a type code:

```c
#define MUX_FWD_LOCAL   1
#define MUX_FWD_REMOTE  2
#define MUX_FWD_DYNAMIC 3
```

These are what make `ssh -O forward` work, so a forwarding rule can be added to a live connection that was established without it.

### Two modes, with different requirements on the client

A mux client can operate in either of two modes, and they differ in what the client has to implement.

![Sequence diagram contrasting passthrough mode, where the master relays bytes and passes file descriptors, with proxy mode, where the socket switches to carrying SSH connection-protocol messages]({{site.url_complet}}/assets/article/network/openssh-mux-modes-sequence.png)

- **Passthrough.** The client sends `MUX_C_NEW_SESSION`, passes its standard input, output and error as file descriptors over the socket, and the master relays every byte between those descriptors and the encrypted transport. The client implements only the mux message framing.
- **Proxy.** The client sends `MUX_C_PROXY`, receives `MUX_S_PROXY`, and the socket then stops speaking the multiplexing protocol entirely. `PROTOCOL.mux` describes what happens next as follows, quoting the specification: "All subsequent data over the connection will be formatted as unencrypted, unpadded, SSH transport messages."

The trade-off is stated in the same document. A proxy client "must speak a significant subset of the SSH protocol, but in return is able to access basically the full suite of connection protocol features. Moreover, as no file descriptor passing is required, the connection supporting a proxy client may itself be forwarded or relayed to another host if necessary." File-descriptor passing is a local operation that cannot cross a machine boundary, so removing the dependency on it is what allows a mux client to sit somewhere other than the master's host.

## SFTP request pipelining

SFTP is a request and response protocol carried over a single channel. Implemented without pipelining, a file transfer costs one network round trip per block, which on a link with meaningful latency puts throughput at the block size divided by the round-trip time regardless of available bandwidth. The bulk of `sftp-client.c` is the machinery that avoids this.

Two constants set the shape of the transfer:

```c
#define DEFAULT_COPY_BUFLEN	32768
#define DEFAULT_NUM_REQUESTS	64
```

Both are reachable from the command line. `sftp -B` sets the buffer size, and `sftp -R` sets the ceiling on outstanding requests, described in `sftp.1` as "how many requests may be outstanding at any one time" with a documented default of 64.

The client does not open the window to its full size immediately. In the download path it starts at one and grows:

```c
write_error = read_error = write_errno = num_req = 0;
max_req = 1;
```

and, on each reply that is not the end of the file:

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

The upload path enforces the same ceiling from the other direction, by reading an acknowledgement whenever the number of unacknowledged writes reaches the limit:

```c
if (id == startid || len == 0 ||
    id - ackid >= conn->num_requests) {
```

The download loop handles three cases that a simpler implementation would get wrong.

- **Short replies are re-requested, not treated as end of file.** A server may return fewer bytes than asked for. The client re-issues a read for the missing tail and reduces its buffer size toward `MIN_READ_SIZE`, adapting to a server that will not serve full-size blocks.
- **The window collapses to one past the expected end of file.** Once the offset passes the size reported by the initial stat, the client stops speculating and issues a single request at a time.
- **Completion is asserted, not assumed.** After the loop, the client checks the queue and treats a non-empty one as unrecoverable: `fatal("Transfer complete, but requests still in queue")`. A pipelined transfer that silently dropped a reply would otherwise produce a truncated file that looked successful.

Since OpenSSH 9.0, this code path is also what `scp` uses. The mode variable in `scp.c` is initialised to the SFTP path, and the legacy protocol is opt-in:

```c
enum scp_mode_e mode = MODE_SFTP;
```

`scp.1` documents `-O` as the flag that selects "the legacy SCP protocol for file transfers instead of the SFTP protocol", noting that it may be needed for servers without SFTP and for particular wildcard and tilde expansion behaviours.

## Certificates and revocation

An OpenSSH certificate is a signed structure that binds a public key to a set of principals for a bounded period. The parsed form is small enough to read in full:

```c
struct sshkey_cert {
	struct sshbuf	*certblob; /* Kept around for use on wire */
	u_int		 type; /* SSH2_CERT_TYPE_USER or SSH2_CERT_TYPE_HOST */
	uint64_t	 serial;
	char		*key_id;
	u_int		 nprincipals;
	char		**principals;
	uint64_t	 valid_after, valid_before;
	struct sshbuf	*critical;
	struct sshbuf	*extensions;
	struct sshkey	*signature_key;
	char		*signature_type;
};
```

There is no ASN.1 and no chain. A certificate names a validity window, a principal list capped at `SSHKEY_CERT_MAX_PRINCIPALS` (256), the CA key that signed it, and two separate option bags.

### The asymmetry between critical options and extensions

The split between `critical` and `extensions` decides how a server treats an option it does not recognise, and `auth-options.c` implements both cases in one function. Both bags are parsed by the same function, called twice with different arguments:

```c
/* Handle options and critical extensions separately */
if (cert_option_list(ret, k->cert->critical,
    OPTIONS_CRITICAL, 1) == -1) {
	sshauthopt_free(ret);
	return NULL;
}
if (cert_option_list(ret, k->cert->extensions,
    OPTIONS_EXTENSIONS, 0) == -1) {
	sshauthopt_free(ret);
	return NULL;
}
```

The final argument is a flag named `crit`, and it decides what happens when the parser meets a name it does not recognise:

```c
if (!found) {
	if (crit) {
		error("Certificate critical option \"%s\" "
		    "is not supported", name);
		goto out;
	} else {
		logit("Certificate extension \"%s\" "
		    "is not supported", name);
	}
}
```

An unknown critical option aborts the parse and the certificate is rejected. An unknown extension is logged and ignored. The rule is a direct consequence of what each bag is for. Critical options restrict (`force-command`, `source-address`, `verify-required`), so a server that cannot enforce one must not accept the certificate, because accepting it would grant access without the restriction its issuer intended. Extensions grant (`permit-pty`, `permit-port-forwarding`, `permit-agent-forwarding`, `permit-X11-forwarding`, `permit-user-rc`), so a server that does not understand one simply fails to grant a privilege, which is safe. Critical options fail closed and extensions fail open, and the same certificate remains usable against servers of different vintages without becoming more permissive on the older ones.

### Revocation lists and their encoding

Revocation is handled by a separate artefact, the Key Revocation List, specified in `PROTOCOL.krl` and implemented in `krl.c`. A KRL is a sequence of typed sections:

```c
#define KRL_SECTION_CERTIFICATES	1
#define KRL_SECTION_EXPLICIT_KEY	2
#define KRL_SECTION_FINGERPRINT_SHA1	3
#define KRL_SECTION_SIGNATURE		4
#define KRL_SECTION_FINGERPRINT_SHA256	5
```

Certificates can be revoked by serial number, and the serial subsections offer three encodings:

```c
#define KRL_SECTION_CERT_SERIAL_LIST	0x20
#define KRL_SECTION_CERT_SERIAL_RANGE	0x21
#define KRL_SECTION_CERT_SERIAL_BITMAP	0x22
```

The encoder does not pick one by policy. It runs a cost model, computing the size in bits of each candidate encoding for the run of serials it is currently emitting, including the cost of switching away from the section type it is already in:

```c
/* Estimate base cost in bits of each section type */
cost_list += 64 * contig + (final ? 0 : 8+64);
cost_range += (2 * 64) + (final ? 0 : 8+64);
cost_bitmap += last_gap + contig + (final ? 0 : MINIMUM(next_gap, 8+64));
cost_bitmap_restart += contig + (final ? 0 : MINIMUM(next_gap, 8+64));

/* Convert to byte costs for actual comparison */
cost_list = (cost_list + 7) / 8;
```

It then selects the cheapest. A handful of scattered serials encode as a list at 8 bytes each, a revoked contiguous batch collapses to a range of two values, and a dense region becomes a bitmap where each serial costs one bit. The bitmap itself is `bitmap.c`. The practical effect is that a KRL covering a large fleet stays small enough to distribute to every server, which is what makes serial-based revocation usable at all.

## Detached signatures with sshsig

`sshsig.c` implements a signature format that has nothing to do with establishing a connection. It signs arbitrary data with an SSH key and produces an armoured blob delimited by `-----BEGIN SSH SIGNATURE-----`. This is the mechanism behind `git config gpg.format ssh`, and the OpenSSH repository uses it on its own commits, which is why a `.git_allowed_signers` file sits at the root of the tree.

The operations are exposed through `ssh-keygen -Y`, whose subcommands are dispatched in `ssh-keygen.c`: `sign`, `verify`, `check-novalidate`, `find-principals` and `match-principals`.

The construction of the signed pre-image is what gives the format its main property:

```c
if ((r = sshbuf_put(tosign, MAGIC_PREAMBLE, MAGIC_PREAMBLE_LEN)) != 0 ||
    (r = sshbuf_put_cstring(tosign, sig_namespace)) != 0 ||
    (r = sshbuf_put_string(tosign, NULL, 0)) != 0 || /* reserved */
    (r = sshbuf_put_cstring(tosign, hashalg)) != 0 ||
    (r = sshbuf_put_stringb(tosign, h_message)) != 0) {
```

What is signed is not the message. It is the concatenation of a fixed `"SSHSIG"` preamble, a caller-supplied namespace string, a reserved field, the name of the hash algorithm, and only then the hash of the message. The namespace and the algorithm identifier are inside the signature, so neither can be reinterpreted after the fact.

Verification enforces the namespace as an equality check, and a mismatch is reported as an invalid signature rather than as a different class of error:

```c
if (strcmp(expect_namespace, got_namespace) != 0) {
	error("Couldn't verify signature: namespace does not match");
	debug_f("expected namespace \"%s\" received \"%s\"",
	    expect_namespace, got_namespace);
	r = SSH_ERR_SIGNATURE_INVALID;
	goto done;
}
```

This is domain separation implemented as a mandatory API parameter. A signature produced with the namespace `git` cannot be presented as a signature over a file, and an application that adopts sshsig for its own purpose picks a namespace and is thereby isolated from every other user of the same key. The hash algorithm is checked immediately afterwards in the same way, which closes the corresponding substitution. A format that omitted the namespace would allow a signature gathered in one context to be replayed in another, and the API makes that outcome unreachable by refusing to sign or verify without one.

## Conclusion

The five subsystems share a method. Each defines a small vocabulary in a header, implements it once, and expresses features as values in that vocabulary rather than as new code paths: a channel type string for every kind of forwarding, a message code for every multiplexing operation, a section type for every revocation encoding, a namespace string for every signing context. The consequence visible in the tree is that `channels.c` absorbed Unix-domain-socket forwarding and reverse SOCKS proxying as additional entries rather than as parallel implementations.

Two of the behaviours described here apply outside the context of reading this source. The asymmetry between critical options and extensions in a certificate determines whether a restriction is enforced or silently dropped by a server that does not recognise it, and the namespace field in an sshsig signature is what separates one application's signatures from another's.

![Mindmap of the OpenSSH architecture covering the channel layer, connection multiplexing, SFTP transfer, certificates, revocation lists and detached signatures]({{site.url_complet}}/assets/article/network/openssh-architecture-channels-multiplexing-sftp-certificates.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Channel** | The unit of multiplexing inside an SSH connection, represented by `struct Channel` and used for shells, forwardings, X11, agent access and tunnels alike. |
| **Channel type string** | The name carried in `SSH2_MSG_CHANNEL_OPEN` that selects what a channel is for, such as `session`, `direct-tcpip` or `tun@openssh.com`. |
| **Half-close** | The property that a channel's receive and transmit directions close independently, tracked by the `istate` and `ostate` fields and driven by `nchan.c`. |
| **Channel window** | The per-channel byte credit a peer may send before receiving a window adjustment, defaulting to 2 MiB for a session channel. |
| **ControlMaster** | The mode in which one `ssh` process owns a connection and serves further invocations over a local socket at `ControlPath`. |
| **Proxy mode** | The multiplexing mode entered with `MUX_C_PROXY`, after which the client emits SSH connection-protocol messages itself instead of passing file descriptors. |
| **Outstanding request window** | The number of SFTP requests the client keeps in flight, ramping from one to `num_requests` and capped by `sftp -R`. |
| **Critical option** | A certificate option that restricts what the holder may do, and whose presence in an unrecognised form causes the certificate to be rejected. |
| **Certificate extension** | A certificate option that grants a privilege, and which is logged and ignored when unrecognised. |
| **Namespace** | The caller-supplied context string included in an sshsig signed pre-image, which a verifier must match exactly. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| `CHANNEL_CLOSE` is sent only once both directions have reached a closed state. | The `istate` and `ostate` machines in `nchan.c`. | A direction is closed before its buffer drains, truncating data already written by the local process. |
| A peer never sends more than the advertised window without an adjustment. | The `remote_window` and `local_window` accounting in `channels.c`. | Buffering becomes unbounded, or one busy channel starves the others sharing the transport. |
| A certificate carrying an unrecognised critical option is rejected. | The `crit` flag passed to `cert_option_list` in `auth-options.c`. | A server accepts a certificate while silently failing to apply the restriction its issuer attached. |
| An SFTP client keeps at most `num_requests` operations in flight. | The `max_req` ceiling on downloads and the `id - ackid` check on uploads. | Memory use grows with file size rather than with the configured window. |
| A completed SFTP transfer leaves no request in the queue. | An explicit `fatal()` check after the transfer loop. | A dropped reply produces a truncated file that reports success. |
| A signature verifies only under the namespace it was produced for. | The namespace inside the signed pre-image and the `strcmp` in `sshsig_wrap_verify`. | A signature collected in one application is replayed against another that shares the key. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| `scp` uses the SFTP protocol by default, and its wildcard and tilde handling differs from the legacy protocol. | Test glob patterns and `~` paths against the default mode, and reserve `-O` for servers that genuinely lack an SFTP subsystem. |
| After `MUX_C_PROXY` the control socket no longer carries multiplexing messages. | Implement the SSH connection protocol in any tool that requests proxy mode, and do not keep decoding mux framing after the confirmation. |
| Unrecognised certificate extensions are logged and ignored rather than rejected. | Express a restriction that must be enforced as a critical option, and treat extensions as privileges that an older server may simply not grant. |
| Raising `sftp -R` increases memory use in proportion to the window. | Tune the value for a specific high-latency link rather than raising it globally. |
| Signing and verifying with sshsig both require a namespace, and the two must match exactly. | Choose one stable namespace string per application and record it alongside the allowed-signers file. |

## Frequently Asked Questions

**Q: Why does the channel type field in `struct Channel` mix kinds of channel with stages of a channel's life?**

Because the field is used as a dispatch key for the poll loop rather than as a classification. A channel in `SSH_CHANNEL_CONNECTING` needs different handling from one in `SSH_CHANNEL_OPEN`, and encoding that in the same field lets the event handlers select behaviour with a single lookup. The cost is that the name `type` describes only part of what the field holds, which is why entries such as `SSH_CHANNEL_ZOMBIE` and `SSH_CHANNEL_LARVAL` appear in a list that also contains `SSH_CHANNEL_PORT_LISTENER`.

**Q: What does a mux client have to implement in passthrough mode, and what changes in proxy mode?**

In passthrough mode the client implements the mux message framing only. It sends `MUX_C_NEW_SESSION`, hands its three standard file descriptors to the master over the Unix socket, and the master moves every byte on its behalf.

In proxy mode the client sends `MUX_C_PROXY` and, after the confirmation, the socket carries SSH connection-protocol messages instead of mux messages. The client must therefore implement a subset of the SSH protocol itself.

The benefit is that proxy mode passes no file descriptors, so the transport carrying the mux client does not have to be a local socket and can be forwarded to another host.

**Q: Why does the SFTP client start with one outstanding request instead of immediately using all 64?**

Opening the full window at once would commit to a transfer profile before anything is known about the server or the path. The ramp gives the client a chance to observe replies first, which matters in three situations that the code handles explicitly:

- A server that returns short reads causes the buffer size to shrink toward `MIN_READ_SIZE`, and discovering that after one request is cheaper than after 64.
- Once the offset passes the file size reported at the start, the window is deliberately reduced back to one so the client stops speculating past the end of the file.
- A small file completes before the window ever reaches its ceiling, so the growth costs nothing in the common case.

**Q: A certificate contains an option the server does not recognise. When is that fatal?**

It depends on which bag the option is in. An unrecognised name in the `critical` bag causes `cert_option_list` to log an error and abort, so the certificate is rejected and authentication fails. An unrecognised name in the `extensions` bag is logged at a lower level and skipped, and the rest of the certificate is honoured.

**Q: Why does the KRL encoder compute a cost in bits rather than choosing a serial encoding by rule?**

Because no single encoding wins across the distributions a real KRL contains. Scattered serials are cheapest as an explicit list, a revoked contiguous batch is cheapest as a pair of endpoints, and a dense region is cheapest as a bitmap at one bit per serial. The encoder therefore estimates all the candidates for the current run, including the cost of switching out of the section type it is already emitting, and picks the minimum. The result keeps a fleet-wide revocation list small enough to distribute to every server that needs it.

**Q: How do the certificate option split and the sshsig namespace solve the same class of problem?**

Both make a piece of context explicit so that it cannot be reinterpreted by a party that does not share the original intent. In a certificate, the critical and extension bags separate what must be enforced from what may be ignored, so an issuer's restriction cannot be silently dropped by a server that lacks support for it. In sshsig, the namespace is placed inside the signed pre-image and checked by equality, so a signature cannot be moved between applications that share a key.

The difference is in what each defends against. The certificate split defends against a version gap between the issuer and the verifier, while the namespace defends against a context confusion between two verifiers that are both current.

## References

### Specifications

- [RFC 4251 — The Secure Shell (SSH) Protocol Architecture](https://datatracker.ietf.org/doc/html/rfc4251)
- [RFC 4253 — The Secure Shell (SSH) Transport Layer Protocol](https://datatracker.ietf.org/doc/html/rfc4253)
- [RFC 4254 — The Secure Shell (SSH) Connection Protocol](https://datatracker.ietf.org/doc/html/rfc4254)
- [draft-ietf-secsh-filexfer-02 — SSH File Transfer Protocol](https://datatracker.ietf.org/doc/html/draft-ietf-secsh-filexfer-02)

### OpenSSH protocol documents

- [PROTOCOL](https://github.com/openssh/openssh-portable/blob/0ef0f5a839831c213f24e3f2ae434765c607fb50/PROTOCOL) — OpenSSH extensions to the base SSH protocol, including the `@openssh.com` channel types
- [PROTOCOL.mux](https://github.com/openssh/openssh-portable/blob/0ef0f5a839831c213f24e3f2ae434765c607fb50/PROTOCOL.mux) — the ControlMaster multiplexing protocol
- [PROTOCOL.krl](https://github.com/openssh/openssh-portable/blob/0ef0f5a839831c213f24e3f2ae434765c607fb50/PROTOCOL.krl) — the key revocation list format
- [PROTOCOL.sshsig](https://github.com/openssh/openssh-portable/blob/0ef0f5a839831c213f24e3f2ae434765c607fb50/PROTOCOL.sshsig) — the detached signature format
- [README.privsep](https://github.com/openssh/openssh-portable/blob/0ef0f5a839831c213f24e3f2ae434765c607fb50/README.privsep) — the server's process model, referenced but not covered here

### Manual pages

- [ssh(1)](https://man.openbsd.org/ssh.1)
- [ssh_config(5)](https://man.openbsd.org/ssh_config.5)
- [sftp(1)](https://man.openbsd.org/sftp.1)
- [scp(1)](https://man.openbsd.org/scp.1)
- [ssh-keygen(1)](https://man.openbsd.org/ssh-keygen.1)

### Analyzed source

- [openssh/openssh-portable](https://github.com/openssh/openssh-portable) — analyzed at commit [`0ef0f5a839831c213f24e3f2ae434765c607fb50`](https://github.com/openssh/openssh-portable/tree/0ef0f5a839831c213f24e3f2ae434765c607fb50), 2026-08-27. The commit carries no release tag and sits after `V_9_7_P1`; `version.h` at this revision declares `OpenSSH_10.5p1`.
