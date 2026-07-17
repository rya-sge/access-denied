---
layout: post
title: "ISO 20022 for Card Network Management — The canm Message Set"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation ISO20022
tags: iso20022 cards canm network-management key-exchange
description: How ISO 20022 models card network management through the canm business area, a four-message set that keeps the link between a terminal and its acquirer host signed on, keyed, and alive so that card transactions can flow.
image: /assets/article/finance/iso20022-network-management-canm.png
isMath: false
---



Before a payment terminal can authorise a single card transaction, it has to establish and maintain a working relationship with its acquirer host: sign on, agree cryptographic keys, and periodically prove the link is still alive. That housekeeping carries no money, but nothing works without it, and ISO 20022 gives it a dedicated business area, `canm`: **network management**. This article covers the four `canm` messages, the two jobs they do, and how they keep the card network running underneath the transaction traffic.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What canm is for

The `canm` area belongs to the ISO 20022 card family, the same group that carries authorisation and clearing. But where those messages move transactions, `canm` manages the **link** they run over. A terminal (or acceptor) and its acquirer host need to sign on before trading, exchange and refresh the keys that protect card data, and check periodically that the connection is healthy. `canm` is the message set for that control plane.

![Network management between a terminal and its acquirer host]({{site.url_complet}}/assets/article/finance/canm-link-concept.png)

It is the ISO 20022 counterpart to the network-management functions that ISO 8583 has long provided through its 0800 network-management message class: sign-on, sign-off, echo test, and key change.

## The four messages

The area is two request-and-response pairs, one for general network management and one specifically for keys.

| Identifier | Message | Pair |
|------------|---------|------|
| `canm.001` | NetworkManagementInitiation | Network management |
| `canm.002` | NetworkManagementResponse | Network management |
| `canm.003` | KeyExchangeInitiation | Key exchange |
| `canm.004` | KeyExchangeResponse | Key exchange |

The **`canm.001` NetworkManagementInitiation** and its `canm.002` response carry the general control functions: signing on at the start of a session, signing off, running an echo test (a keep-alive that confirms the host is reachable), and cutover or status operations. Which function a given message performs is indicated in its header. The **`canm.003` KeyExchangeInitiation** and its `canm.004` response handle cryptographic key management: loading new keys and rotating existing ones, so the keys that protect PIN and card data in the transaction messages stay current.

Like the rest of the card family, each message opens with the shared header (carrying the message function) and includes control fields visible in the schema such as a **system trace audit number (`SysTracAudtNb`)** and a **transmission date-time (`TrnsmssnDtTm`)**, which identify and time-stamp the exchange. Key material is carried in protected form and messages are authenticated.

## Keeping the link running

The messages are best seen across the life of a terminal session.

![Sign-on, key exchange, and keep-alive]({{site.url_complet}}/assets/article/finance/canm-signon-keyexchange-workflow.png)

**Sign-on.** When a terminal starts a session it signs on with a `canm.001` NetworkManagementInitiation, and the host confirms with a `canm.002` response. Only once signed on is the terminal recognised and able to transact.

**Key exchange.** The terminal and host establish or refresh their shared keys through a `canm.003` KeyExchangeInitiation and its `canm.004` response. This is what keeps the cryptographic protection of the transaction messages valid; keys are rotated on a schedule, and this pair is how a new key is delivered and acknowledged.

**Keep-alive.** Through the session, the terminal periodically sends a `canm.001` echo test, answered by a `canm.002`, to confirm the link is still up. A host that stops hearing echo tests knows a terminal has dropped; a terminal that gets no response knows to reconnect. At the end, a sign-off closes the session cleanly.

None of this moves money, but all of it is a precondition for the transaction messages to work: an unsigned-on terminal cannot transact, and an expired key means a transaction cannot be protected. `canm` is the control layer that keeps the rest possible.

## Conclusion

The `canm` business area manages the network link beneath card transactions. Its four messages form two pairs: one that signs a terminal on and off and keeps the connection alive with echo tests, and one that loads and rotates the cryptographic keys the transaction messages depend on. It is the ISO 20022 successor to ISO 8583's network-management class, and though it carries no financial value itself, it is what makes the value-bearing traffic possible. Read next to the acquirer-to-issuer transaction area whose link it maintains and whose keys it manages, `canm` is the card standard's control plane.

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **canm** | The ISO 20022 card network management business area, comprising the four messages `canm.001` to `canm.004`. |
| **Network management** | The control functions that keep a terminal's link to its host working: sign-on, sign-off, echo test, and status. |
| **Sign-on** | The act by which a terminal establishes a working session with its acquirer host before it can transact. |
| **Echo test** | A keep-alive exchange (a `canm.001` and its response) that confirms the link between terminal and host is still up. |
| **Key exchange** | The loading and rotation of cryptographic keys between terminal and host, carried by `canm.003` and `canm.004`. |
| **Acquirer host** | The back-end system that drives a terminal, authorises its transactions, and manages its network session and keys. |
| **System trace audit number** | A control field (`SysTracAudtNb`) identifying an individual network-management exchange. |
| **Transmission date-time** | A control field (`TrnsmssnDtTm`) time-stamping a network-management message. |
| **Message function** | The header code indicating which network-management function a message performs, such as sign-on or echo test. |
| **ISO 8583 network management** | The legacy card-message network-management class (the 0800 messages) that `canm` succeeds in ISO 20022. |

## Frequently Asked Questions

**Q: What does the canm area do that the transaction messages do not?**

`canm` manages the link, not the transactions. Before a terminal can authorise or clear anything, it must sign on to its acquirer host, agree the cryptographic keys that protect card data, and periodically confirm the connection is alive. The transaction messages assume all of that is already in place. `canm` provides the four messages that establish and maintain it: network-management initiation and response for sign-on and echo tests, and key-exchange initiation and response for keys.

**Q: Why is key management its own pair of messages?**

Because rotating cryptographic keys is a distinct, security-critical operation that needs its own request and acknowledgement. The `canm.003` KeyExchangeInitiation and `canm.004` KeyExchangeResponse deliver and confirm new keys between terminal and host. Keeping key exchange separate from the general network-management pair makes the operation explicit and auditable: a system can see exactly when keys were loaded or rotated, independently of the routine sign-on and echo-test traffic that shares the other pair.

**Q: What is an echo test and why does it matter?**

An echo test is a keep-alive: the terminal sends a `canm.001` network-management message whose function is an echo test, and the host answers with a `canm.002`. It carries no business content; its only purpose is to prove the link is still working. It matters because a card terminal must know its host is reachable before it accepts a transaction, and the host must know which terminals are live. Missed echo tests tell either side that the connection has dropped and needs re-establishing.

**Q: How does canm relate to ISO 8583?**

`canm` is the ISO 20022 successor to the network-management functions that ISO 8583 provides through its 0800 message class. In ISO 8583, sign-on, sign-off, echo test, and key change are network-management messages distinct from the financial ones. `canm` expresses the same functions, general network management and key exchange, in ISO 20022 form, as two request-and-response pairs with the function indicated in the header. The role is identical; the syntax is modernised.

**Q: Does canm carry any money?**

No. `canm` carries no financial value at all. It signs terminals on and off, keeps their links alive, and manages their keys. Its importance is entirely as a precondition: without a signed-on session and current keys, the value-bearing transaction messages cannot run. It is the control plane beneath the card traffic, essential precisely because everything else depends on it working.

## References

- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [ISO 20022 card and payment messages](https://www.iso20022.org/payments)
- [SWIFT — ISO 20022 for financial institutions](https://www.swift.com/standards/iso-20022)
- [nexo standards — card payment message specifications](https://www.nexo-standards.org/)
- [Claude Code](https://claude.com/product/claude-code)
