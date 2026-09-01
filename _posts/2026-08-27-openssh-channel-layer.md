---
layout: post
title: "The OpenSSH Channel Layer — One Abstraction Behind Forwarding, X11, Agent Access and Tunnels"
date:   2026-08-27
lang: en
locale: en-GB
categories: network security linux
tags: ssh linux network protocole
series: openssh
description: How channels.c implements port forwarding, X11, SOCKS proxying, agent access and tunnels as one abstraction, with per-channel windows and half-close.
image: /assets/article/network/openssh-channel-layer.png
isMath: false
---

Once an SSH connection finishes authenticating, everything that happens on it is a channel. A remote shell is a channel, a `-L` forwarding is a channel, X11 traffic is a channel, and so is the agent socket that lets a remote command sign with a local key. Portable OpenSSH implements all of them in one file, `channels.c`, which at roughly 150 KB is the largest hand-written C source in the tree.

This article reads that file and its header. It covers the type list that acts as the layer's vocabulary, the way channel kinds are named on the wire, the per-channel flow-control window, and the half-close protocol that makes closing a channel considerably more involved than opening one. The revision analysed declares `OpenSSH_10.5p1` in `version.h`.

The connection protocol itself is specified in [RFC 4254](https://datatracker.ietf.org/doc/html/rfc4254), and OpenSSH's additions to it are documented in the `PROTOCOL` file distributed with the source.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## A single type list as the layer's vocabulary

The clearest statement of the design is the type enumeration in `channels.h`, which puts 23 values into one namespace:

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

Two things follow from reading it as a whole.

The field is named `type`, but several of its values are lifecycle stages rather than kinds. A channel passes through `SSH_CHANNEL_OPENING`, `SSH_CHANNEL_OPEN`, `SSH_CHANNEL_CLOSED` and `SSH_CHANNEL_ZOMBIE` while remaining the same object throughout. The mixing is deliberate: the value is used as the dispatch key for the event loop, so encoding both the kind and the stage in one field lets a handler be selected with a single lookup.

Features that a user would describe as unrelated sit next to each other. `SSH_CHANNEL_DYNAMIC` is the local SOCKS proxy created by `ssh -D`, whose opening bytes are a SOCKS request that must be parsed in band before the real destination is known. `SSH_CHANNEL_RDYNAMIC_OPEN` and `SSH_CHANNEL_RDYNAMIC_FINISH` are the same idea in reverse for `ssh -R`. `SSH_CHANNEL_AUTH_SOCKET` is agent forwarding. None of these needed a subsystem of its own.

![Component diagram showing ssh, sshd and the shared protocol core, with channels.c sitting above packet.c and serving every forwarding, X11, agent and session feature]({{site.url_complet}}/assets/article/network/openssh-channel-layer-concept.png)

## Channel kinds are strings on the wire

The `type` field is internal. On the wire, the kind of a channel is a string carried in `SSH2_MSG_CHANNEL_OPEN`, and incoming requests are dispatched in `channels.c` through a short chain of comparisons:

```c
if (strcmp(rtype, "direct-tcpip") == 0) {
	...
} else if (strcmp(rtype, "direct-streamlocal@openssh.com") == 0) {
	...
} else if (strcmp(rtype, "forwarded-streamlocal@openssh.com") == 0) {
```

Four of the type strings come from RFC 4254: `session`, `direct-tcpip`, `forwarded-tcpip` and `x11`. The rest carry a vendor suffix and are OpenSSH extensions documented in `PROTOCOL`: `direct-streamlocal@openssh.com` and `forwarded-streamlocal@openssh.com` for Unix-domain-socket forwarding, `auth-agent@openssh.com` for agent forwarding, and `tun@openssh.com` for layer 2 and layer 3 tunnels.

Not every kind is allocated inside `channels.c`. Forwarding and X11 channels are, but a `session` channel is created by its caller, which is `ssh.c` for the client's own session, `mux.c` for one requested by a multiplexing client, and `serverloop.c` on the server side:

```c
c = channel_new(ssh,
    "session", SSH_CHANNEL_OPENING, in, out, err,
    ...
```

`tun@openssh.com` is likewise handled in `clientloop.c` and `serverloop.c`. The allocation site varies, but every one of them produces the same `struct Channel` and is then serviced by the same event loop, which is the property that matters.

The consequence is visible in the command-line syntax. Unix-domain-socket forwarding was added by defining two new type strings rather than a new subsystem, which is why `-L` and `-R` accept a socket path in the same argument position as a port number, and why the two forms share their option parsing, their permission checks and their teardown.

## Flow control is per channel, not per connection

Several channels share one encrypted transport, so a channel that stops reading must not be able to stall the others. The connection protocol solves this with a credit window advertised per channel, held in `struct Channel` as four fields:

```c
u_int	remote_window;
u_int	remote_maxpacket;
u_int	local_window;
u_int	local_window_max;
```

A peer may send up to `remote_window` bytes before it must wait for a `SSH2_MSG_CHANNEL_WINDOW_ADJUST`. The defaults come from `channels.h`:

```c
#define CHAN_SES_PACKET_DEFAULT	(32*1024)
#define CHAN_SES_WINDOW_DEFAULT	(64*CHAN_SES_PACKET_DEFAULT)
```

A session channel therefore advertises a 2 MiB window made of 64 packets of 32 KiB each. X11 channels are configured far more tightly, at four packets rather than 64, which suits a workload of many small round trips rather than bulk transfer.

Because the accounting is per channel, a large `scp` running over one channel and an interactive shell running over another are credited separately. A forwarded TCP connection whose far end has stopped reading will exhaust its own window and stop, and the shell sharing the same transport keeps running. There is also a hard ceiling on buffered input independent of the window:

```c
#define CHAN_INPUT_MAX	(16*1024*1024)
```

## Closing a channel is harder than opening one

Opening a channel is a request and a confirmation. Closing one is a protocol, because each direction has to be shut down separately and neither may discard data that has already been written. `struct Channel` tracks the two directions independently:

```c
u_int   istate;		/* input from channel (state of receive half) */
u_int   ostate;		/* output to channel  (state of transmit half) */
```

Each runs a four-state machine defined in `channels.h`:

```c
#define CHAN_INPUT_OPEN			0
#define CHAN_INPUT_WAIT_DRAIN		1
#define CHAN_INPUT_WAIT_OCLOSE		2
#define CHAN_INPUT_CLOSED		3

#define CHAN_OUTPUT_OPEN		0
#define CHAN_OUTPUT_WAIT_DRAIN		1
#define CHAN_OUTPUT_WAIT_IEOF		2
#define CHAN_OUTPUT_CLOSED		3
```

The transitions live in `nchan.c`.

![Two four-state machines, one per direction, showing a channel moving from OPEN through WAIT_DRAIN and WAIT_OCLOSE to CLOSED before CHANNEL_CLOSE is sent]({{site.url_complet}}/assets/article/network/openssh-channel-halfclose-state.png)

The `WAIT_DRAIN` states are the reason the machine exists. A local process can write its output and exit while bytes are still buffered locally, so a direction that closed as soon as its file descriptor reported EOF would discard exactly the output the user cares about. The transmit half therefore flushes what it holds before signalling EOF to the peer, and the receive half does the same in the other direction.

Only once both halves reach `CLOSED` is `SSH2_MSG_CHANNEL_CLOSE` sent, and the channel is not freed until the peer's own close arrives. `SSH_CHANNEL_ZOMBIE` holds a channel in that final interval, and `SSH_CHANNEL_ABANDONED` covers the case of a multiplexed session whose client went away without a clean shutdown.

The design predates the current code and is documented in the tree itself. `nchan.c` ships alongside `nchan.ms` and `nchan2.ms`, two design notes written in troff that describe the state machine and its revision.

## Conclusion

The channel layer works by keeping one object and one event loop, then expressing each feature as a value in a shared vocabulary. A new kind of forwarding costs a type string, a branch in the dispatch chain, and a listener state, rather than a parallel implementation with its own buffering and teardown. Unix-domain-socket forwarding and reverse SOCKS proxying were both added on those terms.

The two mechanisms worth taking away separately are the per-channel window, which is what stops one stalled forwarding from freezing an interactive session on the same connection, and the half-close machine, which is what prevents a process that exits immediately after writing from losing its output.

![Mindmap of the OpenSSH channel layer covering the type list, wire type strings, per-channel flow control and the half-close state machine]({{site.url_complet}}/assets/article/network/openssh-channel-layer.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Channel** | The unit of multiplexing inside an authenticated SSH connection, represented by `struct Channel` and used for sessions, forwardings, X11, agent access and tunnels alike. |
| **Channel type string** | The name carried in `SSH2_MSG_CHANNEL_OPEN` that states what a channel is for, such as `session`, `direct-tcpip` or `tun@openssh.com`. |
| **Larval channel** | A session channel that has been allocated but not yet started, held in `SSH_CHANNEL_LARVAL` until a shell, command or subsystem request arrives. |
| **Dynamic channel** | The channel type behind `ssh -D`, whose first bytes are a SOCKS request parsed in band to discover the destination. |
| **Window** | The per-channel byte credit a peer may send before it must wait for a window adjustment, defaulting to 2 MiB on a session channel. |
| **Maximum packet size** | The largest payload a single channel data message may carry, 32 KiB by default for a session channel. |
| **Half-close** | The property that the two directions of a channel close independently, tracked by the `istate` and `ostate` fields. |
| **Drain** | The phase in which a direction flushes buffered bytes before signalling EOF, represented by the `WAIT_DRAIN` states. |
| **Zombie channel** | A channel closed locally but not yet acknowledged by the peer, held in `SSH_CHANNEL_ZOMBIE` until it can be freed. |
| **Event loop dispatch** | The pattern of selecting per-channel behaviour from the `type` field, which is why lifecycle stages share a namespace with channel kinds. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| `SSH2_MSG_CHANNEL_CLOSE` is sent only after both directions have reached a closed state. | The `istate` and `ostate` machines in `nchan.c`. | A direction closes before draining, discarding output already written by a process that has exited. |
| A peer never sends more than the advertised window without receiving an adjustment. | The `remote_window` and `local_window` accounting in `channels.c`. | One channel buffers without bound, or a stalled forwarding starves the others sharing the transport. |
| Buffered channel input stays below a fixed ceiling regardless of the window. | The `CHAN_INPUT_MAX` limit of 16 MiB. | Memory use tracks peer behaviour rather than local configuration. |
| A channel is freed only after the peer's close has been received. | The `SSH_CHANNEL_ZOMBIE` holding state. | A channel identifier is reused while the peer still considers it live. |
| Every channel kind, wherever it is allocated, is serviced by the same event loop. | All allocation sites calling `channel_new` and returning a `struct Channel`. | A feature acquires its own buffering and teardown path, and diverges from the others under load. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| Window credit is per channel, so a single channel cannot use the whole connection's capacity. | Expect one bulk transfer to be bounded by its own 2 MiB window, and use several channels rather than one when throughput matters. |
| X11 channels are configured with a much smaller window than session channels. | Do not benchmark X11 forwarding as if it shared the session channel's buffering profile. |
| A channel that has sent EOF in one direction is still open in the other. | Treat EOF as a per-direction event, and do not tear down local state until the close arrives. |
| `-L` and `-R` accept a socket path wherever they accept a port. | Use the streamlocal forms directly rather than bridging a Unix socket to a TCP port by hand. |
| Agent forwarding is an ordinary channel reaching a local socket. | Treat an exposed agent as a live credential path for anyone with access to the remote socket, not as a passive setting. |

## Frequently Asked Questions

**Q: Why does the `type` field mix channel kinds with lifecycle stages?**

Because it is used as a dispatch key rather than as a classification. The event loop selects the handling for a channel by looking at one field, and a channel waiting for a connection to complete needs different treatment from one that is open and moving data. Encoding both facts in a single value keeps that selection to one lookup, at the cost of a list where `SSH_CHANNEL_PORT_LISTENER` and `SSH_CHANNEL_ZOMBIE` appear as peers.

**Q: What is a larval channel?**

It is a session channel that exists but has not yet been given work. The server allocates it in `SSH_CHANNEL_LARVAL` when the client opens a `session` channel, and it stays there until a request arrives to start a shell, run a command, or attach a subsystem such as SFTP. The state exists because opening the channel and deciding what it is for are two separate protocol exchanges.

**Q: If several channels share one encrypted connection, what stops a stalled forwarding from blocking an interactive shell?**

The per-channel window. Each channel advertises its own credit, and a peer that has consumed the credit for one channel must stop sending on that channel until a window adjustment arrives. Because the accounting is per channel rather than per connection, the stalled forwarding exhausts only its own window while the shell continues to spend its own credit.

**Q: Why can a channel not simply close both directions at once?**

Because the two directions do not finish at the same time, and closing early loses data. Three cases arise in practice:

- A local process writes its output and exits immediately, leaving bytes buffered that have not reached the peer.
- The peer has stopped reading but is still sending, so the receive half is active while the transmit half has nothing left to do.
- One side wants to signal end of input while continuing to read replies, which is what `ssh host command < file` does.

The `WAIT_DRAIN` states give each direction a chance to flush before it signals EOF, and `SSH2_MSG_CHANNEL_CLOSE` follows only when both are finished.

**Q: How does adding a new kind of forwarding affect the code, and what does that imply about Unix-socket forwarding?**

It costs a type string, a branch in the dispatch chain in `channels.c`, and a listener state in the type list. It does not require new buffering, new flow control, or a new teardown path, because those belong to `struct Channel` and are shared.

Unix-domain-socket forwarding was added on exactly those terms, as `direct-streamlocal@openssh.com` and `forwarded-streamlocal@openssh.com`. That is the reason `-L` and `-R` take a socket path in the same argument position as a port, and the reason both forms behave identically with respect to windows, half-close and cleanup.

## References

### Specifications

- [RFC 4251 — The Secure Shell (SSH) Protocol Architecture](https://datatracker.ietf.org/doc/html/rfc4251)
- [RFC 4254 — The Secure Shell (SSH) Connection Protocol](https://datatracker.ietf.org/doc/html/rfc4254)

### OpenSSH documents

- [PROTOCOL](https://github.com/openssh/openssh-portable/blob/0ef0f5a839831c213f24e3f2ae434765c607fb50/PROTOCOL) — OpenSSH extensions to the base SSH protocol, including the `@openssh.com` channel types
- [nchan.ms](https://github.com/openssh/openssh-portable/blob/0ef0f5a839831c213f24e3f2ae434765c607fb50/nchan.ms) and [nchan2.ms](https://github.com/openssh/openssh-portable/blob/0ef0f5a839831c213f24e3f2ae434765c607fb50/nchan2.ms) — the in-tree design notes for the channel close state machine

### Manual pages

- [ssh(1)](https://man.openbsd.org/ssh.1)
- [ssh_config(5)](https://man.openbsd.org/ssh_config.5)
- [sshd_config(5)](https://man.openbsd.org/sshd_config.5)

### Analyzed source

- [openssh/openssh-portable](https://github.com/openssh/openssh-portable) — analyzed at commit [`0ef0f5a839831c213f24e3f2ae434765c607fb50`](https://github.com/openssh/openssh-portable/tree/0ef0f5a839831c213f24e3f2ae434765c607fb50), 2026-08-27. The commit carries no release tag and sits after `V_9_7_P1`; `version.h` at this revision declares `OpenSSH_10.5p1`.
