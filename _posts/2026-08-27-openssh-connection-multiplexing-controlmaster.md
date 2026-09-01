---
layout: post
title: "OpenSSH Connection Multiplexing — ControlMaster, the Mux Protocol and Proxy Mode"
date:   2026-08-27
lang: en
locale: en-GB
categories: network security linux
tags: ssh linux network protocole
series: openssh
description: How ControlMaster works in OpenSSH, the mux protocol spoken over the ControlPath socket, and the difference between passenger mode and proxy mode.
image: /assets/article/network/openssh-connection-multiplexing.png
isMath: false
---

OpenSSH is the implementation of the SSH protocol that ships with almost every Unix system, and `ssh` is its client. Each time that client contacts a host it opens a TCP connection, runs a key exchange to derive session keys, and then authenticates the user. That work is repeated in full for every invocation, which is what makes a burst of short commands against the same host feel slow, and what makes a host configured for a password or a hardware token ask again on each one.

Connection multiplexing removes that cost. One `ssh` process keeps its connection open and acts as a master, and later connections to the same destination borrow it rather than building their own, so only the first invocation pays for the handshake.

With `ControlMaster` enabled, a second `ssh` to a host that already has a connection open returns almost immediately. It performs no key exchange and no authentication, which is the whole point of the feature, and the reason is that the second process is not acting as an SSH client at all. It connects to a Unix domain socket and asks the first process to do the work.

That request is a protocol of its own, specified in the `PROTOCOL.mux` file distributed with OpenSSH and implemented in `mux.c`. This article reads both. It covers the socket and its lifetime, the message set, the two modes a multiplexing client can operate in, and the way the whole mechanism is built on the same channel layer that carries ordinary sessions. The revision analysed declares `OpenSSH_10.5p1` in `version.h`.

The mux protocol is private to OpenSSH. It is not part of [RFC 4254](https://datatracker.ietf.org/doc/html/rfc4254), it never crosses the network, and its messages are exchanged in the clear because they travel over a local socket that the operating system already protects.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The socket and who listens on it

Three options configure the feature, and they divide the responsibility cleanly. `ControlMaster` decides whether a connection offers itself as a master, `ControlPath` names the Unix domain socket it listens on, and `ControlPersist` decides how long the master outlives the session that created it.

The path is expanded per destination, which is what keeps one master per target rather than one per user. A `ControlPath` containing `%C` expands to a hash of the connection parameters, and the older token form spells the same idea out as `%r@%h:%p`.

`ControlPersist` is the option that turns the feature from a convenience within one command into a background service. Without it, the master exits when its own session ends and the saved handshake benefits only commands started while it was running. With it, the master detaches and stays available for the configured idle period.

## Everything here is still a channel

The multiplexing machinery does not sit beside the channel layer. It is built on it, using three of the type values from `channels.h`:

```c
#define SSH_CHANNEL_MUX_LISTENER	15	/* Listener for mux conn. */
#define SSH_CHANNEL_MUX_CLIENT		16	/* Conn. to mux client */
#define SSH_CHANNEL_MUX_PROXY		20	/* proxy channel for mux-client */
```

The listening socket is a channel, each connected multiplexing client is a channel, and `struct Channel` carries two fields whose only purpose is to bind a session to the multiplexing client that asked for it:

```c
int     ctl_chan;	/* control channel (multiplexed connections) */
uint32_t ctl_child_id;	/* child session for mux controllers */
int	have_ctl_child_id;/* non-zero if ctl_child_id is valid */
```

A fourth value, `SSH_CHANNEL_ABANDONED`, exists for the case where a multiplexing client disappears without closing its session cleanly. The master needs a state for a session that is still open on the remote side but no longer has a local client attached to it.

![Component diagram showing the mux master owning the transport, the ControlPath socket as a listener channel, and mux clients attached as channels bound by ctl_chan]({{site.url_complet}}/assets/article/network/openssh-connection-multiplexing-concept.png)

## The message set

Both sides open with a hello, and the specification is explicit about what happens on a mismatch:

```
	uint32	MUX_MSG_HELLO
	uint32  protocol version
	string  extension name [optional]
	string  extension value [optional]
	...
```

`PROTOCOL.mux` states that "the current version of the mux protocol is 4" and that "a client should refuse to connect to a master that speaks an unsupported protocol version". Extensions are carried as name and value pairs after the version.

The message codes themselves are declared in `mux.c`, with client requests and server replies distinguished by their high bits:

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
#define MUX_S_PERMISSION_DENIED	0x80000002
#define MUX_S_FAILURE		0x80000003
#define MUX_S_EXIT_MESSAGE	0x80000004
#define MUX_S_ALIVE		0x80000005
#define MUX_S_SESSION_OPENED	0x80000006
#define MUX_S_REMOTE_PORT	0x80000007
#define MUX_S_TTY_ALLOC_FAIL	0x80000008
#define MUX_S_PROXY		0x8000000f
```

Most of these are reachable from the command line through `ssh -O`, whose argument is mapped in `ssh.c`:

```c
if (strcmp(optarg, "check") == 0)
	muxclient_command = SSHMUX_COMMAND_ALIVE_CHECK;
else if (strcmp(optarg, "conninfo") == 0)
	muxclient_command = SSHMUX_COMMAND_CONNINFO;
else if (strcmp(optarg, "channels") == 0)
	muxclient_command = SSHMUX_COMMAND_CHANINFO;
else if (strcmp(optarg, "forward") == 0)
	muxclient_command = SSHMUX_COMMAND_FORWARD;
else if (strcmp(optarg, "exit") == 0)
	muxclient_command = SSHMUX_COMMAND_TERMINATE;
else if (strcmp(optarg, "stop") == 0)
	muxclient_command = SSHMUX_COMMAND_STOP;
else if (strcmp(optarg, "cancel") == 0)
	muxclient_command = SSHMUX_COMMAND_CANCEL_FWD;
else if (strcmp(optarg, "proxy") == 0)
	muxclient_command = SSHMUX_COMMAND_PROXY;
```

`-O exit` and `-O stop` are worth separating because the names suggest the same thing. `TERMINATE` ends the master and everything running on it, while `STOP` sends `MUX_C_STOP_LISTENING`, which closes the socket so no further clients can attach while existing sessions continue.

### Forwardings can be added to a live connection

`MUX_C_OPEN_FWD` and `MUX_C_CLOSE_FWD` carry a type code:

```c
#define MUX_FWD_LOCAL   1
#define MUX_FWD_REMOTE  2
#define MUX_FWD_DYNAMIC 3
```

These are what make `ssh -O forward` and `ssh -O cancel` work. A connection established without any forwarding can be given a `-L`, `-R` or `-D` rule afterwards, because the master already owns an authenticated transport and adding a forwarding is only a matter of opening a listener and a channel on it.

## Two modes, with different obligations on the client

The specification names the ordinary mode **passenger mode**, and it contrasts it with proxy mode.

![Sequence diagram contrasting passenger mode, where the master relays bytes and receives passed file descriptors, with proxy mode, where the socket switches to carrying SSH connection-protocol messages]({{site.url_complet}}/assets/article/network/openssh-connection-multiplexing-modes-sequence.png)

In passenger mode the client sends `MUX_C_NEW_SESSION`, passes its three standard file descriptors over the socket, and then waits. The request carries everything the master needs to open the session on its behalf:

```
	uint32	MUX_C_NEW_SESSION
	uint32  request id
	string	reserved
	bool	want tty flag
	bool	want X11 forwarding flag
	bool	want agent flag
	bool	subsystem flag
	uint32	escape char
	string	terminal type
	string	command
	string	environment string 0 [optional]
	...
```

The master opens a `session` channel on the real connection, replies with `MUX_S_SESSION_OPENED`, and relays bytes between the passed descriptors and that channel for the rest of the session. When the remote command exits, `MUX_S_EXIT_MESSAGE` carries the status back. Stdio forwarding, requested with `MUX_C_NEW_STDIO_FWD` and used by `ssh -W` and by `ProxyJump`, is described by the specification as "another example of passenger mode; the client passes the stdio file descriptors and passively waits for something to happen".

Proxy mode inverts the arrangement. After `MUX_C_PROXY` and its `MUX_S_PROXY` confirmation, `PROTOCOL.mux` says the socket changes language entirely: "All subsequent data over the connection will be formatted as unencrypted, unpadded, SSH transport messages."

The trade is stated in the specification itself. A proxy client "must speak a significant subset of the SSH protocol, but in return is able to access basically the full suite of connection protocol features. Moreover, as no file descriptor passing is required, the connection supporting a proxy client may itself be forwarded or relayed to another host if necessary."

That last clause is the substantive difference. Passing a file descriptor is a local operation that cannot cross a machine boundary, so a passenger client has to run on the same host as its master. Removing that dependency is what allows the channel between client and master to be an ordinary stream, and therefore to be forwarded somewhere else.

## Conclusion

Multiplexing reuses two things rather than reimplementing them. The transport is reused because the master already holds an authenticated connection, which is what removes the handshake from every subsequent command. The channel layer is reused because the control socket, each attached client, and each proxied session are all ordinary channels, which is why a forwarding can be added to a live connection with `-O forward` and behaves the same as one requested at startup.

The distinction between the two client modes is the part that carries beyond OpenSSH. Passenger mode keeps the client trivial by passing file descriptors and accepting that both processes must share a host. Proxy mode asks the client to implement part of the SSH connection protocol, and in exchange the client is no longer required to be local.

![Mindmap of OpenSSH connection multiplexing covering the control socket, the mux message set, passenger and proxy modes, and the channel types involved]({{site.url_complet}}/assets/article/network/openssh-connection-multiplexing.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Mux master** | The `ssh` process that owns the authenticated connection and serves multiplexing requests over a local socket. |
| **Mux client** | A later `ssh` invocation that connects to the master's socket instead of establishing its own connection. |
| **ControlPath** | The filesystem path of the Unix domain socket the master listens on, expanded per destination so that one master serves one target. |
| **ControlPersist** | The option that keeps a master alive after its own session ends, for a configured idle period. |
| **Passenger mode** | The default client mode, in which the client passes its standard file descriptors to the master and waits while the master relays bytes. |
| **Proxy mode** | The mode entered with `MUX_C_PROXY`, after which the socket carries SSH connection-protocol messages and the client drives channels itself. |
| **Stdio forwarding** | A passenger-mode request made with `MUX_C_NEW_STDIO_FWD`, used by `ssh -W` and `ProxyJump` to connect standard input and output to a remote address. |
| **Control channel** | The `ctl_chan` field binding a session channel to the multiplexing client that requested it. |
| **Abandoned session** | A session whose multiplexing client disconnected without a clean shutdown, held in `SSH_CHANNEL_ABANDONED`. |
| **Mux protocol version** | The integer exchanged in `MUX_MSG_HELLO`, currently 4, which a client must recognise before continuing. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| A mux client refuses a master whose protocol version it does not support. | The version check on `MUX_MSG_HELLO`, specified in `PROTOCOL.mux`. | Two versions exchange messages whose field layout has changed, and misparse them. |
| Every multiplexed session is bound to the client that requested it. | The `ctl_chan` and `ctl_child_id` fields on `struct Channel`. | Output is delivered to the wrong client, or a session outlives its owner without being marked abandoned. |
| After `MUX_S_PROXY`, the socket no longer carries mux messages. | The mode switch in `mux.c` following `MUX_C_PROXY`. | The master decodes connection-protocol traffic as mux framing. |
| Stopping the listener does not disturb sessions already running. | `MUX_C_STOP_LISTENING` closing only the listening socket. | `-O stop` becomes indistinguishable from `-O exit` and kills live work. |
| A multiplexed session performs no key exchange or authentication of its own. | The master owning the single authenticated transport. | The saved handshake is repeated, and the feature's purpose is lost. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| After `MUX_C_PROXY` the control socket stops speaking the multiplexing protocol. | Implement the SSH connection protocol in any tool that requests proxy mode, and stop decoding mux framing once the confirmation arrives. |
| `-O exit` terminates the master and its sessions, while `-O stop` only closes the listener. | Use `stop` to drain a master out of service and `exit` to end everything, and do not treat the two as synonyms in automation. |
| Anyone able to write to the `ControlPath` socket can open sessions on the authenticated connection. | Keep the socket in a directory only the owner can write, and treat its path as sensitive on shared hosts. |
| A master created without `ControlPersist` exits with its own session. | Set `ControlPersist` explicitly when the intent is a reusable background connection rather than a single command. |
| Forwardings can be added and removed while a connection is live. | Prefer `-O forward` and `-O cancel` over tearing down and re-establishing a connection to change a rule. |

## Frequently Asked Questions

**Q: Why does a multiplexed `ssh` return so much faster than a fresh one?**

Because it skips both expensive phases. A new connection performs a key exchange and then an authentication, each of which costs round trips and public-key operations. A multiplexing client performs neither. It connects to a local Unix socket, exchanges a hello, and asks the existing master to open a channel on a transport that was authenticated once, when the master itself started.

**Q: What is the difference between `ssh -O stop` and `ssh -O exit`?**

`-O exit` maps to `MUX_C_TERMINATE`, which ends the master and every session running on it.

`-O stop` maps to `MUX_C_STOP_LISTENING`, which closes only the listening socket. Existing sessions continue to completion, but no new client can attach.

The second is the one to use when taking a master out of service without interrupting work already in progress.

**Q: What does a client have to implement in each of the two modes?**

In passenger mode, only the mux message framing. The client sends `MUX_C_NEW_SESSION`, hands over its standard input, output and error as file descriptors, and the master moves every byte on its behalf.

In proxy mode, a subset of the SSH connection protocol. After the `MUX_S_PROXY` confirmation the socket carries connection-protocol messages, so the client opens and manages channels itself rather than delegating.

**Q: Why can a proxy-mode client run on another host when a passenger-mode client cannot?**

Passenger mode depends on passing file descriptors over the socket, and descriptor passing is a local kernel operation with no meaning across a machine boundary. Proxy mode passes no descriptors at all, so the client-to-master connection is an ordinary byte stream. The specification notes this consequence directly, saying the connection supporting a proxy client "may itself be forwarded or relayed to another host if necessary".

**Q: How does the multiplexing implementation relate to the channel layer, and why does that matter for `-O forward`?**

Multiplexing is implemented in terms of channels rather than alongside them. The `ControlPath` listener is a channel of type `SSH_CHANNEL_MUX_LISTENER`, each attached client is `SSH_CHANNEL_MUX_CLIENT`, a proxied session is `SSH_CHANNEL_MUX_PROXY`, and `struct Channel` carries `ctl_chan` specifically to associate a session with its requesting client.

This is why forwardings can be added to a running connection. The master already holds an authenticated transport and a working channel layer, so `MUX_C_OPEN_FWD` needs only to create a listener and open channels through the existing machinery. Nothing about the transport has to be renegotiated, which is what makes `-O forward` cheap and its result indistinguishable from a `-L` given at startup.

## References

### Specifications

- [RFC 4254 — The Secure Shell (SSH) Connection Protocol](https://datatracker.ietf.org/doc/html/rfc4254)

### OpenSSH documents

- [PROTOCOL.mux](https://github.com/openssh/openssh-portable/blob/0ef0f5a839831c213f24e3f2ae434765c607fb50/PROTOCOL.mux) — the multiplexing protocol, including the passenger and proxy mode descriptions quoted here
- [PROTOCOL](https://github.com/openssh/openssh-portable/blob/0ef0f5a839831c213f24e3f2ae434765c607fb50/PROTOCOL) — OpenSSH extensions to the base SSH protocol

### Manual pages

- [ssh(1)](https://man.openbsd.org/ssh.1)
- [ssh_config(5)](https://man.openbsd.org/ssh_config.5)

### Analyzed source

- [openssh/openssh-portable](https://github.com/openssh/openssh-portable) — analyzed at commit [`0ef0f5a839831c213f24e3f2ae434765c607fb50`](https://github.com/openssh/openssh-portable/tree/0ef0f5a839831c213f24e3f2ae434765c607fb50), 2026-08-27. The commit carries no release tag and sits after `V_9_7_P1`; `version.h` at this revision declares `OpenSSH_10.5p1`.
