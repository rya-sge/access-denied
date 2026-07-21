---
layout: post
title: "The IPsec and IKE Document Roadmap (RFC 6071)"
date:   2026-07-20
lang: en
locale: en-GB
categories: network security cryptography rfc
tags: network ipsec ike vpn esp ah ikev2 rfc6071 roadmap
description: A guided tour of RFC 6071, the roadmap that maps the sprawling IPsec and IKE RFC landscape - the seven document groups, IPsec-v2 vs v3, IKEv1 vs IKEv2, extensions, and crypto requirement levels.
image: /assets/article/network/ipsec/2026-07-20-ipsec-ike-document-roadmap-rfc6071.png
isMath: false
---

IPsec secures traffic at the IP layer, and IKE negotiates the keys that make it work. Both are defined not by one specification but by dozens of RFCs that originate from several IETF working groups, extend each other, obsolete each other, and are reused by unrelated protocols. [RFC 6071](https://datatracker.ietf.org/doc/html/rfc6071), published February 2011, is the roadmap through that thicket: an informational catalog that names each relevant RFC, says what it does, and places it in the larger structure. This article is a guided tour of that roadmap, organized around the map it draws rather than the raw list it contains.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Why a roadmap RFC exists

Over the years the number of RFCs defining and using IPsec and IKE grew large, and the growth was messy because the documents came from many sources: the original IPsec working group, its spin-offs such as IPsecME (IPsec Maintenance and Extensions), and other groups that use IPsec or IKE to protect their own protocols. [RFC 6071](https://datatracker.ietf.org/doc/html/rfc6071) is a snapshot of that ecosystem as of early 2011. It obsoletes the earlier [RFC 2411](https://datatracker.ietf.org/doc/html/rfc2411), the previous IPsec roadmap, which had a narrower focus on the recommended contents of encryption and authentication algorithm documents.

The roadmap is informational, not standards-track. It defines nothing of its own: it restates the requirement levels and relationships found in the documents it points at, and if it ever conflicts with one of them, the other RFC wins. Each RFC it lists is tagged with its series category (S for Standards Track, E for Experimental, B for Best Current Practice, I for Informational) and its publication date, so a reader can judge the maturity and status of any given piece.

Two conventions from the roadmap are worth adopting up front, because the whole field uses them:

- **IPsec-v2 vs IPsec-v3.** "Old" IPsec (IPsec-v2, from the 1998 RFCs) was obsoleted by "new" IPsec (IPsec-v3, from the 2005 RFCs), but IPsec-v2 is still found in operational use. When the roadmap writes "IPsec" without a qualifier, it means both.
- **IKEv1 vs IKEv2.** "Old" IKE (IKEv1) was obsoleted by "new" IKE (IKEv2), while IKEv1 remains in the field. "IKE" without a qualifier means both.

## Core concepts: SA, SPI, and the databases

The roadmap's background section defines the vocabulary the rest of the documents assume. A **Security Association (SA)** is a one-way (inbound or outbound) agreement between two peers that specifies the IPsec protections to apply: the security protocol, the cryptographic algorithms, the keys, and which traffic is covered. Because SAs are one-way, protecting a two-way conversation always takes a pair of them.

Each SA is named by a **Security Parameters Index (SPI)**. In IPsec-v2 an SA is identified by the combination of the SPI, the protocol (AH or ESP), and the destination address; IPsec-v3 simplified this so that a unicast SA is identified by the SPI alone (optionally the protocol), while a multicast SA uses the SPI, the destination address, and optionally the source address.

Three databases organize the processing, with a fourth added in IPsec-v3:

- **SPD (Security Policy Database).** Expresses what protection each class of traffic requires. Every packet is matched against it and sorted into one of three outcomes: discard, bypass IPsec, or apply IPsec protection.
- **SAD (Security Association Database).** Each peer's repository of active SAs. IPsec-v3 replaced the former ordered SAD with a decorrelated, order-independent one.
- **PAD (Peer Authorization Database).** New in IPsec-v3, it holds the information needed to authenticate peers and forms the link between IPsec and the key management protocol such as IKE.

Every SA operates in one of two modes. **Transport mode** protects the upper-layer payload of a packet while leaving the original IP header in place, and is typically used for host-to-host traffic. **Tunnel mode** wraps the entire original packet inside a new one, protecting the inner header as well, and is what gateway-to-gateway VPNs use.

## The seven document groups

The roadmap's Figure 1 divides the IPsec protocol documents into seven groups, arranged as a dependency structure. Reading them in this shape is the fastest way to understand how a given RFC fits in.

- **Architecture.** The top-level document covering the general concepts, security requirements, definitions, and mechanisms of IPsec. Everything else hangs off it.
- **ESP Protocol.** The Encapsulating Security Payload, which provides confidentiality (encryption) and optionally integrity protection.
- **AH Protocol.** The Authentication Header, which provides integrity protection and data-origin authentication but no encryption.
- **Encryption Algorithm** documents, describing how each encryption algorithm is used with ESP.
- **Combined Algorithm** documents, describing algorithms that provide encryption and integrity protection together for ESP.
- **Integrity-Protection Algorithm** documents, describing how each authentication algorithm is used with both ESP and AH.
- **IKE** documents, the standards-track key management schemes that negotiate SAs for the other groups.

![IPsec and IKE document groups]({{site.url_complet}}/assets/article/network/ipsec/ipsec-document-groups-concept.png)

## The base documents

Each protocol group has a base document, and most of them exist in an old and a new version. The roadmap's most useful service is pinning down which RFC obsoletes which.

| Role | IPsec-v2 (1998) | IPsec-v3 (2005) |
|------|-----------------|-----------------|
| Architecture | [RFC 2401](https://datatracker.ietf.org/doc/html/rfc2401) | [RFC 4301](https://datatracker.ietf.org/doc/html/rfc4301) |
| AH | [RFC 2402](https://datatracker.ietf.org/doc/html/rfc2402) (mandatory) | [RFC 4302](https://datatracker.ietf.org/doc/html/rfc4302) (optional) |
| ESP | [RFC 2406](https://datatracker.ietf.org/doc/html/rfc2406) | [RFC 4303](https://datatracker.ietf.org/doc/html/rfc4303) |

The move from v2 to v3 was not a rewrite but a consolidation of lessons learned. The architecture document gained a more detailed processing model and the new PAD database; SA identification was simplified; SPD selectors became more flexible; extended sequence numbers (ESNs) were added for high-volume SAs; and mandatory algorithms were moved out into standalone documents. One notable status change is that AH, mandatory to implement in IPsec-v2, became optional in IPsec-v3, reflecting that ESP with integrity protection covers most needs.

IKE's base documents tell a more tangled story, because IKEv1 was assembled from several separate specifications:

- **[RFC 2409](https://datatracker.ietf.org/doc/html/rfc2409) (IKE)** defined the key exchange itself, drawing on a subset of the Oakley protocol.
- **[RFC 2408](https://datatracker.ietf.org/doc/html/rfc2408) (ISAKMP)** defined the generic procedures and packet formats for establishing SAs.
- **[RFC 2407](https://datatracker.ietf.org/doc/html/rfc2407) (IPsec DOI)** defined the Domain of Interpretation that binds ISAKMP to IPsec.
- **[RFC 2412](https://datatracker.ietf.org/doc/html/rfc2412) (Oakley)** supplied the theory and background for the key determination modes.

In practice these four were viewed as the single protocol "IKEv1." IKEv2 collapsed all of that into one document. It was first published as [RFC 4306](https://datatracker.ietf.org/doc/html/rfc4306), clarified by [RFC 4718](https://datatracker.ietf.org/doc/html/rfc4718), and the two were then merged into [RFC 5996](https://datatracker.ietf.org/doc/html/rfc5996), the single IKEv2 specification current at the time the roadmap was written.

## IKEv1 versus IKEv2

IKE is the preferred key management protocol for IPsec: it authenticates the peers, negotiates SAs, and produces the keying material for them. A completed IKE negotiation yields two kinds of SA. The first is the **IKE SA**, which protects the IKE signaling itself. The second is the **IPsec SA** that actually protects data traffic. The terminology shifts between versions, which the roadmap is careful to untangle: what IKEv1 calls the IPsec SA, IKEv2 calls a CHILD_SA. Because IKEv1 ran as two sequential negotiations called phases, its IKE SA is also known as a Phase 1 SA and its IPsec SA as a Phase 2 SA.

IKEv2 folded in the same "lessons learned" spirit as IPsec-v3, replacing multiple, sometimes contradictory documents with one. Its notable changes include:

- **A shorter, single exchange** replacing IKEv1's several alternate exchange types, with a streamlined negotiation format that avoids combinatorial bloat when offering many proposals.
- **Responder DoS protection**, so the responder commits significant resources only after the initiator's existence and identity are confirmed.
- **Reliable exchanges**, where every request expects a response.
- **Message protection based on ESP** rather than a mechanism unique to IKE.
- **Traffic selectors** distinct from peer identities and more flexible than IKEv1's.
- **EAP-based and asymmetric authentication**, letting initiator and responder authenticate by different methods.

![IKE negotiation establishing the IKE SA and IPsec SA]({{site.url_complet}}/assets/article/network/ipsec/ike-negotiation-workflow.png)

## Additions and extensions

Once the base IKEv1 and IPsec-v2 documents were finalized, gaps surfaced that separate RFCs filled. The roadmap groups these additions into recognizable themes rather than listing them at random.

- **NAT traversal.** IPsec and NAT interact badly, a real problem because IPsec is the standard corporate-VPN mechanism and NATs sit in front of most remote users. [RFC 3715](https://datatracker.ietf.org/doc/html/rfc3715) states the compatibility requirements, [RFC 3947](https://datatracker.ietf.org/doc/html/rfc3947) negotiates NAT traversal in IKEv1, and [RFC 3948](https://datatracker.ietf.org/doc/html/rfc3948) defines UDP encapsulation of ESP so packets survive a NAT.
- **Extended sequence numbers.** [RFC 4304](https://datatracker.ietf.org/doc/html/rfc4304) adds 64-bit sequence numbers for anti-replay on high-volume SAs while still sending only 32 bits on the wire.
- **Peer authentication and PKI.** The PKI4IPsec effort produced [RFC 4809](https://datatracker.ietf.org/doc/html/rfc4809) (certificate management requirements) and [RFC 4945](https://datatracker.ietf.org/doc/html/rfc4945) (the PKI profile for IKE), while [RFC 4754](https://datatracker.ietf.org/doc/html/rfc4754) adds ECDSA authentication and [RFC 4806](https://datatracker.ietf.org/doc/html/rfc4806) adds OCSP certificate-status checking to IKEv2.
- **Dead peer detection.** [RFC 3706](https://datatracker.ietf.org/doc/html/rfc3706) detects a peer that has silently gone away, so an SA is not left tunneling packets into a black hole; IKEv2 builds this in as its liveness check.
- **Remote access and mobility.** [RFC 4555](https://datatracker.ietf.org/doc/html/rfc4555) (MOBIKE) lets a host keep its SAs as its IP address changes, [RFC 5723](https://datatracker.ietf.org/doc/html/rfc5723) resumes a session without a full renegotiation, and [RFC 5685](https://datatracker.ietf.org/doc/html/rfc5685) lets a gateway redirect clients to another gateway.

## Cryptographic algorithms and requirement levels

A large part of the roadmap is a survey of the algorithm documents, and its central idea is that an algorithm needs two things before it can be used: an assigned IANA value (so IKE can name it during negotiation) and an RFC describing how to use it with the protocol. The roadmap then classifies each algorithm's requirement level separately for IKEv1, IKEv2, IPsec-v2, and IPsec-v3.

Those requirement levels use the vocabulary of [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119) plus the trend markers from [RFC 4835](https://datatracker.ietf.org/doc/html/rfc4835):

| Level | Meaning |
|-------|---------|
| MUST | Required; an interoperable implementation has to support it. |
| SHOULD+ | Recommended, and likely to be upgraded to MUST in future. |
| SHOULD | Recommended. |
| SHOULD- | Recommended, but likely to be downgraded in future. |
| MUST- | Currently required, but likely to be downgraded. |
| MAY | Optional. |
| SHOULD NOT | Discouraged. |

The mandatory-to-implement algorithms are deliberately pulled out into their own documents so they can be revised without touching the base protocol: [RFC 4835](https://datatracker.ietf.org/doc/html/rfc4835) for ESP and AH, [RFC 4307](https://datatracker.ietf.org/doc/html/rfc4307) for IKEv2, and [RFC 4109](https://datatracker.ietf.org/doc/html/rfc4109) for IKEv1. The survey covers encryption algorithms (AES-CBC in [RFC 3602](https://datatracker.ietf.org/doc/html/rfc3602), the NULL cipher in [RFC 2410](https://datatracker.ietf.org/doc/html/rfc2410)), integrity-protection algorithms, combined-mode algorithms such as AES-GCM, pseudo-random functions, Diffie-Hellman groups, and the packaged cryptographic suites of [RFC 4308](https://datatracker.ietf.org/doc/html/rfc4308) and [RFC 4869](https://datatracker.ietf.org/doc/html/rfc4869). DES, once required, is now deprecated, and the roadmap deliberately omits its RFC.

## Outgrowths and other protocols

The final sections show how far IPsec and IKE reach beyond their own base documents, and they are the reason the roadmap is genuinely useful rather than a plain bibliography.

**Outgrowths of IPsec/IKE** are efforts that grew from the core work: IPsec policy configuration, IPsec MIBs for management, IP compression (IPComp), Better-Than-Nothing Security (BTNS) for unauthenticated protection, Kerberized key negotiation (KINK), secure remote access (IPSRA), and the IPSECKEY DNS resource record for publishing keying material.

**Other protocols that use IPsec/IKE** are unrelated protocols that call on IPsec for their own protection. The roadmap catalogs how Mobile IPv4 and IPv6, OSPF, the Host Identity Protocol (HIP), SCTP, Robust Header Compression (ROHC), BGP, and even SIP lean on IPsec, along with IPsec benchmarking and NAT-interaction documents.

**Other protocols that adapt IKE** borrow IKE's machinery for non-IPsec purposes, including EAP, Fibre Channel security, and wireless security work. This last group makes the point that IKE has become a general-purpose authenticated key exchange, not only the front end to IPsec.

## Conclusion

RFC 6071 does not add to IPsec or IKE; it makes the existing pile navigable. It contributes a small number of organizing ideas: the seven-group document structure with an architecture document at the top and IKE at the bottom, the clean separation of IPsec-v2 from IPsec-v3 and IKEv1 from IKEv2, the vocabulary of SA, SPI, and the SPD/SAD/PAD databases, and a requirement-level survey that tells an implementer which algorithms are current. Because it is a February 2011 snapshot, some specifics have since moved on, IKEv2 has been re-published and algorithm requirements have shifted, but the map it draws still matches how practitioners think about IPsec today. Read as a map rather than a specification, it turns a hundred scattered RFCs into a structure a reader can hold in their head.

The mindmap below summarizes the article's structure.

![IPsec and IKE roadmap mindmap]({{site.url_complet}}/assets/article/network/ipsec/2026-07-20-ipsec-ike-document-roadmap-rfc6071.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **IPsec** | A suite of protocols that provides security at the IP layer, most commonly to build VPNs, using the AH and ESP headers. |
| **IKE** | The Internet Key Exchange, the key negotiation and management protocol that dynamically establishes and updates keying material for IPsec. |
| **AH** | The Authentication Header, an IPsec protocol providing integrity protection and data-origin authentication but no encryption. |
| **ESP** | The Encapsulating Security Payload, an IPsec protocol providing confidentiality and, optionally, integrity protection. |
| **Security Association (SA)** | A one-way agreement between two peers specifying the protections, algorithms, keys, and covered traffic for an IPsec flow. |
| **SPI** | The Security Parameters Index, the value that names a specific SA so a receiver can select the right processing. |
| **SPD / SAD / PAD** | The Security Policy Database (what protection traffic needs), the Security Association Database (active SAs), and the Peer Authorization Database (peer authentication, new in IPsec-v3). |
| **Transport vs tunnel mode** | Transport mode protects the payload and keeps the original IP header; tunnel mode wraps the whole packet in a new one, as VPN gateways do. |
| **IKE SA vs IPsec SA (CHILD_SA)** | The IKE SA protects IKE signaling; the IPsec SA (called CHILD_SA in IKEv2) protects data traffic. |
| **ISAKMP / DOI / Oakley** | The three specifications, alongside IKE itself, that together made up IKEv1 before IKEv2 consolidated them into one document. |

## Frequently Asked Questions

**Q: What problem does RFC 6071 solve, and what does it deliberately not do?**

It solves discoverability. IPsec and IKE are defined across dozens of RFCs from several working groups, some obsoleting others and many reused by unrelated protocols, so finding the right document and understanding how it relates to the rest is hard. RFC 6071 catalogs those RFCs, describes each briefly, tags it with its series category and date, and places it in an overall structure. What it deliberately does not do is define anything of its own: it restates the requirement levels and relationships already set by the documents it points at, and if it ever conflicts with one of them, the other RFC takes precedence.

**Q: What is the difference between AH and ESP?**

Both are IPsec protocols carried as headers, but they protect differently. AH, the Authentication Header, provides integrity protection and data-origin authentication over the packet, including parts of the IP header, but it does not encrypt. ESP, the Encapsulating Security Payload, provides confidentiality through encryption and can optionally add integrity protection to the data it covers. Because ESP with integrity protection covers most needs and works through NAT where AH does not, IPsec-v3 downgraded AH from mandatory (in IPsec-v2) to optional.

**Q: Why is a Security Association described as one-way, and what follows from that?**

An SA specifies the protection for traffic in a single direction: it fixes the protocol, algorithms, keys, and covered traffic for either the inbound or the outbound flow, not both. It follows that protecting a normal two-way conversation always requires a pair of SAs, one per direction. It is also why IKE is described as negotiating SAs in pairs, and why a phrase like "the IPsec SA" is, strictly, shorthand for a pair of one-way SAs.

**Q: How did the IKE base documents change from IKEv1 to IKEv2?**

IKEv1 was not a single document. It was assembled from IKE itself (RFC 2409), ISAKMP (RFC 2408) for the generic SA procedures and packet formats, the IPsec DOI (RFC 2407) binding ISAKMP to IPsec, and Oakley (RFC 2412) for the key-determination theory, and in practice these four were treated as one protocol. IKEv2 consolidated all of that into a single specification, first as RFC 4306, then clarified by RFC 4718, and finally merged into RFC 5996. Beyond consolidation, IKEv2 shortened the exchange, added responder DoS protection, made every request expect a response, and supported EAP-based and asymmetric authentication.

**Q: The roadmap lists requirement levels like SHOULD+ and MUST-. Combining the algorithm and versioning sections, why are these levels version-specific and time-sensitive?**

The plus and minus markers encode direction of travel: SHOULD+ is recommended and likely to become MUST, while MUST- is currently required but likely to be downgraded. They exist because cryptographic algorithms age, so the mandatory set has to shift over time, and the roadmap deliberately places mandatory-to-implement algorithms in their own documents (RFC 4835, RFC 4307, RFC 4109) precisely so those levels can be revised without touching the base protocol. The levels are also version-specific because IKEv1, IKEv2, IPsec-v2, and IPsec-v3 each negotiate a different algorithm set: an algorithm can be MUST in one and merely optional or not applicable in another, as with NULL encryption, which makes sense for ESP but never for IKE, which must always encrypt. Combined with the fact that the whole survey is a February 2011 snapshot, this is why the roadmap warns that later RFCs may have changed the picture.

**Q: What does it mean that other protocols "use IPsec" versus "adapt IKE"?**

They are two different kinds of reuse the roadmap separates. Protocols that use IPsec/IKE, such as Mobile IP, OSPF, HIP, SCTP, BGP, and SIP, call on IPsec to protect their own traffic while leaving IPsec and IKE unchanged. Protocols that adapt IKE, such as EAP, Fibre Channel security, and wireless security, borrow IKE's authenticated key-exchange machinery for a purpose other than setting up IPsec SAs. The second category is evidence that IKE has become a general-purpose key exchange in its own right, not only the front end to IPsec.

## References

### Roadmaps

- [RFC 6071 — IP Security (IPsec) and Internet Key Exchange (IKE) Document Roadmap](https://datatracker.ietf.org/doc/html/rfc6071)
- [RFC 2411 — IP Security Document Roadmap (obsoleted)](https://datatracker.ietf.org/doc/html/rfc2411)

### IPsec base protocol documents

- [RFC 4301 — Security Architecture for the Internet Protocol](https://datatracker.ietf.org/doc/html/rfc4301)
- [RFC 4302 — IP Authentication Header](https://datatracker.ietf.org/doc/html/rfc4302)
- [RFC 4303 — IP Encapsulating Security Payload (ESP)](https://datatracker.ietf.org/doc/html/rfc4303)

### Key management (IKE)

- [RFC 5996 — Internet Key Exchange Protocol Version 2 (IKEv2)](https://datatracker.ietf.org/doc/html/rfc5996)
- [RFC 2409 — The Internet Key Exchange (IKE)](https://datatracker.ietf.org/doc/html/rfc2409)
- [RFC 2408 — Internet Security Association and Key Management Protocol (ISAKMP)](https://datatracker.ietf.org/doc/html/rfc2408)

### Algorithm requirements and conventions

- [RFC 4835 — Cryptographic Algorithm Implementation Requirements for ESP and AH](https://datatracker.ietf.org/doc/html/rfc4835)
- [RFC 4307 — Cryptographic Algorithms for Use in IKEv2](https://datatracker.ietf.org/doc/html/rfc4307)
- [RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels](https://datatracker.ietf.org/doc/html/rfc2119)
