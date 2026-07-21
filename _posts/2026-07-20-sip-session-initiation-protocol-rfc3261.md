---
layout: post
title: "SIP - The Session Initiation Protocol (RFC 3261)"
date:   2026-07-20
lang: en
locale: en-GB
categories: network security rfc
tags: network sip voip signaling rfc3261 telephony proxy registrar
description: How SIP (RFC 3261) sets up, modifies, and tears down multimedia sessions using a text request/response model, its elements, layered design, transactions, dialogs, and security.
image: /assets/article/network/sip/2026-07-20-sip-session-initiation-protocol-rfc3261.png
isMath: false
---

The Session Initiation Protocol (SIP) is the signaling protocol behind most Internet telephony, video calling, and presence systems. It does not carry voice or video itself; it locates the other party, negotiates how the media will flow, and manages the session over its lifetime. This article walks through [RFC 3261](https://datatracker.ietf.org/doc/html/rfc3261), the June 2002 Standards Track specification that defines SIP, covering its architecture, its layered design, its request/response message model, the transaction and dialog abstractions, registration, and the threat model that shapes its security mechanisms.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What SIP is, and what it is not

SIP is an application-layer control protocol for creating, modifying, and terminating sessions with one or more participants. A session might be an Internet telephone call, a multimedia distribution, or a multimedia conference. SIP was published as [RFC 3261](https://datatracker.ietf.org/doc/html/rfc3261) in June 2002, obsoleting the earlier [RFC 2543](https://datatracker.ietf.org/doc/html/rfc2543), and it remains the base specification that dozens of later extensions build on.

The specification frames SIP around five facets of establishing and terminating multimedia communication:

- **User location.** Determining which end system a user is currently reachable at, so a call placed to a stable identity can follow the user across devices and networks.
- **User availability.** Determining whether the called party is willing to engage in the communication, which is what "ringing" and "busy" express.
- **User capabilities.** Determining the media and media parameters both sides can use, so the endpoints agree on codecs and formats.
- **Session setup.** Establishing session parameters at both the calling and called party, the "ringing" and pickup phase.
- **Session management.** Transferring and terminating sessions, modifying parameters mid-call, and invoking supplementary services.

Two boundaries are worth stating clearly, because they explain much of SIP's design. First, SIP is not a vertically integrated communications system: it is one component that works alongside other IETF protocols to build a complete multimedia architecture. Media transport uses the Real-time Transport Protocol ([RTP, RFC 3550](https://datatracker.ietf.org/doc/html/rfc3550)), streaming uses RTSP, gateway control uses MEGACO, and the session itself is described using the Session Description Protocol ([SDP, RFC 4566](https://datatracker.ietf.org/doc/html/rfc4566)). SIP carries that SDP description in its message bodies but does not interpret the media.

Second, SIP does not provide services; it provides primitives that can be used to build services. A single primitive, delivering an opaque object to a user's current location, becomes a session invitation when the object is an SDP body and a caller-ID feature when the object is the caller's photo. This primitive-not-service philosophy is why SIP is small at its core and extensible at its edges. It runs over several transports (UDP, TCP, TLS, SCTP) and works with both IPv4 and IPv6.

## The SIP trapezoid: a worked example

The canonical example in RFC 3261 is a call from Alice to Bob that traverses two proxy servers, one for each party's domain. The dotted lines connecting the two user agents and the two proxies trace a shape often called the "SIP trapezoid."

Alice calls Bob using his SIP URI, `sip:bob@biloxi.com`, an identifier with the same form as an email address. Her softphone does not know where Bob is, so it sends an `INVITE` request to the proxy that serves her own domain, `atlanta.com`. That proxy returns a `100 (Trying)` response, performs a DNS lookup to find the proxy serving `biloxi.com`, adds its own address in a `Via` header field, and forwards the request. The `biloxi.com` proxy consults a location service to find Bob's current IP address, adds its own `Via`, and forwards the `INVITE` to Bob's phone.

Bob's phone rings and returns `180 (Ringing)`, which flows back through both proxies in reverse, each proxy using the `Via` header to route the response and stripping its own address off the top. When Bob answers, his phone sends `200 (OK)` carrying his SDP media description. Alice's softphone confirms with an `ACK` sent directly to Bob, and the two endpoints then exchange media over RTP, bypassing the proxies entirely. When Bob hangs up, his phone sends a `BYE` directly to Alice, and Alice answers `200 (OK)`. The session is over.

The diagram below traces the whole exchange, with each message labelled `F1` through `F14` as in the specification.

![SIP trapezoid message flow]({{site.url_complet}}/assets/article/network/sip/sip-trapezoid-message-flow.png)

A skeleton `INVITE` from this exchange shows the request line, the mandatory header fields, and the body separator:

```
INVITE sip:bob@biloxi.com SIP/2.0
Via: SIP/2.0/UDP pc33.atlanta.com;branch=z9hG4bK776asdhds
Max-Forwards: 70
To: Bob <sip:bob@biloxi.com>
From: Alice <sip:alice@atlanta.com>;tag=1928301774
Call-ID: a84b4c76e66710@pc33.atlanta.com
CSeq: 314159 INVITE
Contact: <sip:alice@pc33.atlanta.com>
Content-Type: application/sdp
Content-Length: 142

(Alice's SDP not shown)
```

The three header fields `To`, `From`, and `Call-ID`, together with the tag parameters, are what later identify the peer-to-peer relationship the call establishes. That relationship is called a dialog, and it is central to the rest of the protocol.

## SIP architecture: the logical elements

SIP defines a small set of logical elements. They are logical because one physical device or process can play several roles, sometimes changing role from one transaction to the next.

The starting point is the **user agent (UA)**, an endpoint such as a softphone or an IP desk phone. A UA acts as a **user agent client (UAC)** when it originates a request and as a **user agent server (UAS)** when it responds to one. The roles are per-transaction: the same softphone is a UAC when it sends the initial `INVITE` and a UAS when it receives the `BYE` that ends the call.

Between user agents sit intermediary servers that route signaling:

- **Proxy server.** An intermediary that acts as both a server and a client, forwarding requests toward the target and responses back. A proxy's main job is routing; it may also enforce policy, such as checking that a user is authorized to place a call. A **stateful proxy** maintains transaction state machines for the requests it handles, while a **stateless proxy** simply forwards each message and keeps no state.
- **Redirect server.** A UAS that answers a request with a `3xx` response telling the client to try a different set of URIs, rather than forwarding the request itself. The client then re-issues the request to the new targets.
- **Registrar.** A server that accepts `REGISTER` requests and records the location information they carry in a location service. A registrar handles registration only; it plays no part in authorizing outgoing requests.
- **Back-to-back user agent (B2BUA).** A logical element that receives a request as a UAS and, to decide how to answer it, acts as a UAC and generates its own requests. Unlike a proxy, a B2BUA maintains dialog state and participates in every request on the dialogs it establishes. Session border controllers are commonly built this way.

Supporting these is the **location service**, an abstract database that maps an address-of-record (a user's stable public URI) to one or more contact URIs where the user can currently be reached. Registrations populate it, but so can any administrator-configured mapping. It is important that registration in SIP is used to route incoming requests and has no role in authorizing outgoing ones; authentication and authorization are handled per request or by a lower-layer scheme.

![SIP trapezoid and logical elements]({{site.url_complet}}/assets/article/network/sip/sip-trapezoid-concept.png)

## The layered protocol model

RFC 3261 describes SIP as a layered protocol, meaning its behavior is defined as a set of loosely coupled processing stages. The layering is a description device rather than an implementation mandate, and not every element contains every layer. Reading the protocol as four layers makes the rest of the specification much easier to follow.

- **Syntax and encoding.** The lowest layer is the message grammar, specified as an augmented Backus-Naur Form (ABNF). SIP is a text-based protocol using the UTF-8 charset, deliberately close to HTTP and SMTP in look and feel.
- **Transport.** This layer defines how a client sends requests and receives responses, and how a server receives requests and sends responses, over the network. Every SIP element contains a transport layer. It handles the framing differences between datagram transports like UDP and stream transports like TCP.
- **Transaction.** A transaction is a single request together with all responses to that request, including any provisional `1xx` responses and the final response. The transaction layer handles application-layer retransmission, matching responses to requests, and timeouts. User agents and stateful proxies contain a transaction layer; stateless proxies do not.
- **Transaction user (TU).** Above the transaction layer sits the transaction user, the "core" logic specific to each type of element: the UAC core, the UAS core, and the proxy core. When a TU wants to send a request, it creates a client transaction instance and hands it the message plus the destination.

The stateless proxy is the one element with no transaction layer and therefore no TU: it forwards every request it receives downstream and every response upstream, holding no state at all. Everything else builds its behavior on top of transactions.

![SIP layered protocol stack]({{site.url_complet}}/assets/article/network/sip/sip-layered-stack-concept.png)

## SIP messages: requests and responses

A SIP message is either a request or a response, and both share the same structure: a start line, a set of header fields, an empty line, and an optional message body. The body is opaque to SIP; for a session invitation it typically holds an SDP description, carried much as an attachment is carried in an email.

### Methods

A request's start line names a method, the primary function the request invokes on the server. RFC 3261 defines six methods, and later RFCs add more. The base six are:

- **INVITE.** Establishes a session between participants, or, when sent inside an existing dialog (a re-INVITE), modifies one. It is the most important method in SIP.
- **ACK.** Confirms that a client has received a final response to an `INVITE`. It completes the three-way handshake that makes `INVITE` reliable even over UDP.
- **BYE.** Terminates an established session. Either party can send it.
- **CANCEL.** Asks a server to stop processing a request, such as an `INVITE` that has not yet been answered. It constitutes its own transaction but references the transaction it cancels.
- **REGISTER.** Uploads a user's current contact information to a registrar, populating the location service.
- **OPTIONS.** Queries a server or user agent for its capabilities without establishing a session.

Extensions defined outside RFC 3261 add methods such as `SUBSCRIBE`/`NOTIFY` for event notification, `REFER` for call transfer, `MESSAGE` for instant messaging, `INFO`, `UPDATE`, `PRACK`, and `PUBLISH`. A UA advertises and negotiates support for such extensions through option tags in the `Supported`, `Require`, and `Allow` header fields.

### Response classes

A response's start line carries a three-digit status code and a reason phrase, borrowing directly from HTTP. The first digit sets the class, and only the class is semantically fixed; a client that does not recognize a specific code treats it as the `x00` code of its class.

| Class | Meaning | Examples |
|-------|---------|----------|
| `1xx` | Provisional: request received, processing continues | `100 Trying`, `180 Ringing`, `183 Session Progress` |
| `2xx` | Success: the request succeeded | `200 OK` |
| `3xx` | Redirection: further action is needed to complete the request | `301 Moved Permanently`, `302 Moved Temporarily` |
| `4xx` | Request failure: the request was faulty and cannot be fulfilled at this server | `401 Unauthorized`, `404 Not Found`, `486 Busy Here` |
| `5xx` | Server failure: the server failed to fulfill an apparently valid request | `500 Server Internal Error`, `503 Service Unavailable` |
| `6xx` | Global failure: the request cannot be fulfilled at any server | `600 Busy Everywhere`, `603 Decline` |

Provisional (`1xx`) responses do not terminate a transaction; every other class is final. The distinction drives the transaction state machines described below.

### Header fields

Header fields are named attributes carried between the start line and the body. A handful of them appear in nearly every message and carry the protocol's core routing and identity semantics:

- **Via.** Records the path a request has taken. Each proxy adds a `Via` value with its own address on the way out and includes a `branch` parameter identifying the transaction; responses follow the `Via` list back in reverse.
- **To** and **From.** The logical recipient and originator of the request. Both may carry a `tag` parameter; the `From` tag is added by the originator and the `To` tag by the answering UAS.
- **Call-ID.** A globally unique identifier shared by all messages of a single call.
- **CSeq.** A command sequence number plus a method name, incremented per request within a dialog to order requests and match responses.
- **Contact.** A direct URI at which the sending element can be reached for future requests, as opposed to `Via`, which is only for routing this transaction's responses.
- **Max-Forwards.** An integer decremented at each hop, bounding how far a request can travel and breaking routing loops.

## Transactions and dialogs

Two abstractions organize SIP's stateful behavior: the transaction, which is short-lived and covers one request/response exchange, and the dialog, which is long-lived and spans a whole conversation.

### Transactions

A transaction is the unit the transaction layer manages. It comes in a client half and a server half, each modeled as a finite state machine, and SIP defines two flavors because `INVITE` behaves differently from everything else.

The **INVITE transaction** uses a three-way handshake. The client sends `INVITE`, the server may send any number of provisional `1xx` responses, and it eventually sends a final response. The client then confirms the final response with `ACK`. The separate `ACK` exists because a human takes time to answer a call: an `INVITE` can sit unanswered for many seconds, far longer than a normal request/response, so its reliability is handled specially and the acknowledgment is explicit.

The **non-INVITE transaction** (used by `BYE`, `REGISTER`, `OPTIONS`, and others) is a simpler request/final-response exchange with no separate acknowledgment. Over unreliable transports like UDP, both flavors rely on retransmission driven by timers. The base retransmission interval is `T1`, an estimate of the round-trip time that defaults to 500 milliseconds, and a client retransmits with an exponential backoff (`T1`, `2·T1`, `4·T1`, and so on) until it receives a response or the transaction times out.

### Dialogs

A dialog is a peer-to-peer relationship between two user agents that persists for some time and provides context for ordering and routing the requests exchanged within it. In RFC 3261 the only method that establishes a dialog is `INVITE`. A dialog is identified by the combination of three values:

- the **Call-ID**,
- the **local tag** (this UA's tag, from its `From` or `To`),
- and the **remote tag** (the peer's tag).

Because both tags are needed, a dialog only becomes fully specified once the answering UAS has contributed its `To` tag in a response. Once established, requests sent within the dialog, such as a re-INVITE to change the media or a `BYE` to end it, carry the same `Call-ID` and an increasing `CSeq`, and they follow a route set the dialog remembers. The three-part identifier is what lets a UA distinguish one conversation from another and reject a forged mid-dialog request whose tags do not match.

![INVITE session establishment and teardown]({{site.url_complet}}/assets/article/network/sip/sip-invite-session-workflow.png)

## Registration and the location service

Registration is how the location service learns where a user currently is. A user has an address-of-record (AOR), a stable public URI such as `sip:bob@biloxi.com` that others use to reach them. It does not point at a device; it points at a domain whose location service can map it to whatever device the user is on right now.

To create that mapping, the UA sends a `REGISTER` request to the domain's registrar. The request's `To` header carries the AOR being registered, the `Contact` header carries the device URIs to bind to it, and an `Expires` value (or a `Contact` `expires` parameter) sets how long the binding lasts before the UA must refresh it. A UA can register several contacts for one AOR, which is how a single identity rings multiple devices, and it can remove bindings by registering with an expiry of zero.

When a proxy later receives a request for that AOR, it queries the location service, retrieves the current contacts, and forwards the request there. The registrar assesses the identity asserted in the `From` header of a `REGISTER` to decide whether the sender may modify the bindings for that AOR. As the security section explains, that assessment is exactly where authentication matters, because the `From` field can be set to anything by a malicious sender.

## Routing: proxies, Via, and loose routing

Request routing in SIP is a cooperation between the `Request-URI`, the `Via` header, and, for in-dialog requests, the route set. On the way toward the callee, each proxy adds a `Via` value; on the way back, each response is routed hop by hop using that stack of `Via` values, with each proxy removing its own entry. This is what lets a `180 (Ringing)` reach the caller without any element having to look up the path a second time, and it guarantees that any proxy that saw the request also sees its responses.

A proxy that wants to stay on the path for future in-dialog requests, rather than just this one transaction, inserts a `Record-Route` header. The endpoints copy the accumulated `Record-Route` values into their route sets and address subsequent requests through those proxies using the `Route` header. RFC 3261 mandates **loose routing** for this, where the request's ultimate destination (in the `Request-URI`) is kept separate from the list of proxies to traverse (in `Route`). This replaces the older **strict routing** of RFC 2543, which overwrote the `Request-URI` at each hop and proved fragile. The `Max-Forwards` counter, decremented at every proxy, backs all of this up by bounding loops that routing mistakes might otherwise create.

## Security: threat model and mechanisms

RFC 3261 is candid that SIP is not an easy protocol to secure. Its reliance on intermediaries, its trust relationships that vary from element to element, and its expected deployment on the public Internet all work against simple solutions. The specification therefore starts from a set of classic threats and derives the security services needed to counter them.

### The threat model

The specification presents five illustrative attacks, each motivating a specific security service:

- **Registration hijacking.** A registrar decides who may change an AOR's bindings by looking at the `From` header of a `REGISTER`. Since the `From` field can be forged, an attacker who impersonates the victim can de-register the real contacts and register their own device, redirecting all of the victim's calls. This motivates authenticating the originator of a request.
- **Impersonating a server.** A UA sends a request to a domain, but an attacker impersonates the server for that domain and answers with forged responses, for example a bogus `301 (Moved Permanently)` that reroutes all future requests to the attacker. This motivates letting UAs authenticate the servers they contact.
- **Tampering with message bodies.** A UA routes requests through proxies it trusts to forward but not necessarily to read or alter the body. A malicious proxy could modify an SDP body to point the media stream at a wiretapping device, or change a session key. This motivates end-to-end confidentiality and integrity for bodies, independent of hop-by-hop protection.
- **Tearing down sessions.** After a dialog is established, an attacker who has observed the `Call-ID` and tags can inject a forged `BYE` to end the session prematurely, or a forged re-INVITE to weaken its security or redirect its media. This motivates authenticating that in-dialog requests came from the dialog peer.
- **Denial of service and amplification.** An attacker can put a victim's address in a forged `Via` or `Route` and send the request to many SIP elements, turning them into a reflector that floods the victim; forking proxies amplify the effect. Registrars that do not authenticate `REGISTER` are a further vector. This motivates being careful with these fields and authenticating registration.

### The mechanisms

From those threats the specification identifies the required security services (confidentiality and integrity of signaling, protection against replay and spoofing, authentication and privacy of participants, and DoS resistance) and, rather than inventing new cryptography, reuses mechanisms from the HTTP and SMTP world.

- **Transport and network layer security (TLS, IPsec).** Encrypting the signaling on the wire gives hop-by-hop confidentiality and integrity. Because fields such as the `Request-URI`, `Route`, and `Via` must stay visible to proxies for routing, SIP cannot simply encrypt whole messages end-to-end; it secures them hop by hop instead. When TLS is used, `TLS_RSA_WITH_AES_128_CBC_SHA` must be supported at minimum.
- **The SIPS URI scheme.** A SIPS URI (`sips:bob@biloxi.com`) signals that the request must be delivered over TLS-secured hops all the way to the target domain, after which local policy governs the final leg. It is the caller-visible way to demand secure transport.
- **HTTP Digest authentication.** SIP reuses the HTTP Digest challenge/response, keyed on the `401` and `407` status codes and their `WWW-Authenticate`/`Proxy-Authenticate` header fields. It provides replay protection through a server nonce and one-way authentication of the requester, and it is the workhorse for authenticating `REGISTER` and other requests.
- **S/MIME.** Because intermediaries must read certain headers, whole-message end-to-end encryption is impractical, but S/MIME lets UAs encrypt and sign the MIME bodies end-to-end, giving confidentiality, integrity, and mutual authentication for the media parameters that proxies have no business reading. Tunneling a whole SIP message inside an S/MIME body can extend that protection to some header fields.

No single mechanism covers everything. The specification's own framing is that SIP's diverse deployments need several distinct mechanisms applied to different aspects of its operation, which is why a real system typically combines TLS on the access hops, Digest for authentication, and S/MIME or later frameworks for end-to-end body protection.

## Conclusion

RFC 3261 defines SIP as a text-based, HTTP-like signaling protocol whose job is to locate participants and manage the lifetime of a session, while leaving the media itself to protocols like RTP and the session description to SDP. Its design rests on a few reusable ideas: logical elements that a device can adopt per transaction, a layered model that separates syntax, transport, transactions, and the transaction-user core, and the transaction and dialog abstractions that give short exchanges and long conversations their structure. Registration feeds a location service that turns a stable address-of-record into a current device, and a threat model built around impersonation, tampering, session teardown, and denial of service justifies the TLS, SIPS, Digest, and S/MIME mechanisms the protocol adopts. The specification is over twenty years old and has accumulated many extensions, but the core it establishes is still the vocabulary of Internet real-time communication.

The mindmap below summarizes the article's structure.

![SIP RFC 3261 mindmap]({{site.url_complet}}/assets/article/network/sip/2026-07-20-sip-session-initiation-protocol-rfc3261.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **SIP** | Application-layer signaling protocol (RFC 3261) that creates, modifies, and terminates multimedia sessions without carrying the media itself. |
| **User agent (UA)** | A SIP endpoint such as a phone or softphone; it is a UAC when it originates a request and a UAS when it answers one. |
| **Proxy server** | An intermediary that routes SIP requests toward the target and responses back, optionally enforcing policy; it may be stateful or stateless. |
| **Registrar** | A server that accepts REGISTER requests and records their contact bindings in the location service for a domain. |
| **Address-of-record (AOR)** | A user's stable public SIP URI that points to a domain whose location service maps it to the user's current device. |
| **Location service** | An abstract database that maps an AOR to one or more current contact URIs, populated by registration or by administrative configuration. |
| **Transaction** | A single request plus all of its responses, managed by the transaction layer with retransmission, matching, and timeouts. |
| **Dialog** | A persistent peer-to-peer relationship between two UAs, identified by Call-ID, local tag, and remote tag, established by an INVITE. |
| **SIP URI / SIPS URI** | An email-like identifier for a SIP resource; the SIPS form additionally demands TLS-secured delivery to the target domain. |
| **SDP** | The Session Description Protocol, carried in SIP message bodies to describe and negotiate the media of a session. |

## Frequently Asked Questions

**Q: What is the difference between SIP and RTP?**

They operate at different layers of a call. SIP is the signaling protocol: it locates the other party, negotiates what media will be exchanged, and sets up, modifies, or tears down the session. RTP is the media transport protocol that actually carries the voice or video packets once the session is established. SIP messages carry an SDP body describing the media, and after the endpoints agree, the RTP streams flow directly between them, often bypassing the proxies that handled the signaling.

**Q: Why does an INVITE need a separate ACK when other requests do not?**

Because answering a call involves a human and can take many seconds, far longer than a normal request/response round trip. The INVITE transaction therefore uses a three-way handshake: the caller sends `INVITE`, the callee eventually sends a final response such as `200 (OK)`, and the caller confirms it with `ACK`. This explicit acknowledgment makes the exchange reliable even over an unreliable transport like UDP, where a `200 (OK)` might be lost and need retransmission. Non-INVITE transactions like `BYE` complete quickly and need no separate acknowledgment.

**Q: What three values identify a dialog, and why does that matter?**

A dialog is identified by the `Call-ID`, the local tag, and the remote tag. Because the remote tag is contributed by the answering UAS, a dialog is only fully specified once the callee has responded. This three-part identifier matters for security as much as for routing: a UA can reject a mid-dialog request, such as a forged `BYE` meant to tear down the session, if its tags do not match an existing dialog. An attacker who has not observed all three values cannot fabricate a request the endpoint will accept.

**Q: Why can a SIP proxy not simply encrypt the entire message end-to-end?**

Because proxies must read and sometimes modify certain header fields to route the message. Fields such as the `Request-URI`, `Route`, and `Via` have to stay visible so that intermediaries can forward the request toward its destination and route responses back; proxies also add their own `Via` values. Encrypting the whole message end-to-end would make it non-routable. SIP resolves this by securing signaling hop by hop with TLS or IPsec, while using S/MIME to encrypt only the message body end-to-end, protecting the media parameters that proxies have no need to read.

**Q: A registrar decides who may change an address-of-record's bindings by reading the From header. Combining the registration and security sections, what goes wrong, and how is it fixed?**

The `From` header can be set to any value by the sender, so on its own it proves nothing. This is the registration hijacking threat: an attacker forges a `REGISTER` whose `From` claims to be the victim, de-registers the victim's real contacts, and registers their own device, so all of the victim's incoming calls are redirected to the attacker. Because registration feeds the location service that proxies query to route requests, one forged registration can silently steal a user's calls. The fix is to authenticate the originator of the `REGISTER` rather than trusting the `From` field, typically with HTTP Digest, so the registrar accepts binding changes only from a sender who can prove they hold the shared secret for that address-of-record.

**Q: What does the SIPS URI scheme guarantee, and what does it not?**

A SIPS URI signals that the request must be carried over TLS-secured hops all the way to the domain responsible for the target. It guarantees confidentiality and integrity of the signaling on every hop up to that domain. It does not guarantee TLS on the final leg from the target domain to the callee's device, which is left to that domain's local policy, and it does not by itself encrypt or authenticate the message body. End-to-end body protection is a separate concern addressed by S/MIME.

## References

- [RFC 3261 — SIP: Session Initiation Protocol](https://datatracker.ietf.org/doc/html/rfc3261)
- [RFC 2543 — SIP: Session Initiation Protocol (obsoleted)](https://datatracker.ietf.org/doc/html/rfc2543)
- [RFC 4566 — SDP: Session Description Protocol](https://datatracker.ietf.org/doc/html/rfc4566)
- [RFC 3550 — RTP: A Transport Protocol for Real-Time Applications](https://datatracker.ietf.org/doc/html/rfc3550)
- [RFC 2617 — HTTP Authentication: Basic and Digest Access Authentication](https://datatracker.ietf.org/doc/html/rfc2617)
- [RFC 3263 — Locating SIP Servers](https://datatracker.ietf.org/doc/html/rfc3263)
- [Claude Code](https://claude.com/product/claude-code)
