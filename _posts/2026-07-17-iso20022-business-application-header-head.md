---
layout: post
title: "ISO 20022 and the Business Application Header — The head Message Set"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation ISO20022
tags: iso20022 bah head routing signature envelope
description: What the ISO 20022 Business Application Header (head.001) is and why it matters, covering the routing envelope that accompanies every business message, its fields, its signature, and the head.002 business file header that groups many messages.
image: /assets/article/finance/iso20022-business-application-header-head.png
isMath: false
---



Across this series of articles, one phrase keeps recurring: the business message is "paired with a Business Application Header". That header is not part of any one business area; it is the shared envelope that every ISO 20022 message travels in. This article is about the `head` area itself: the **Business Application Header** (`head.001`) that carries the routing and control information for a message, and the **Business File Header** (`head.002`) that groups many messages into a file. It is a small area, but understanding it explains how ISO 20022 messages are routed, linked, and signed.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Why a separate header

An ISO 20022 business message, a `pacs.008` payment or a `camt.053` statement, describes a business fact. It says nothing about who is sending it to whom, when, or how it should be handled. That routing and control information is deliberately kept out of the business payload and placed in a separate document that travels alongside it: the **Business Application Header (BAH)**, message `head.001`.

![The BAH wraps a business message]({{site.url_complet}}/assets/article/finance/head-bah-anatomy-concept.png)

The separation is the whole idea. A business message answers "what happened"; the header answers "who, to whom, which definition, and is it authentic". Keeping them apart means an intermediary can route or log a message by reading only its header, without parsing (or being able to parse) the business content, and it means the same header structure serves every message type in the standard.

## What the header carries

The BAH is itself an ISO 20022 message with its own defined fields. Taking the `head.001.001.04` version, its elements divide into three purposes: routing, context, and integrity.

The **routing** fields are the core and are mandatory:

- **From (`Fr`)** and **To (`To`)** identify the sender and the receiver of the message, each as a party or financial institution.
- **Business Message Identifier (`BizMsgIdr`)** is the unique reference for this message, the handle used to refer to it later.
- **Message Definition Identifier (`MsgDefIdr`)** names exactly which message definition the payload is, for example `pacs.008.001.10`, so the receiver knows how to parse it.
- **Creation Date (`CreDt`)** timestamps the header.

The **context** fields, all optional, refine how the message is handled:

- **Business Service (`BizSvc`)** names the service or agreement the message is sent under, such as a particular scheme.
- **Market Practice (`MktPrctc`)** references the usage guideline the message follows, so the receiver knows which market-practice rules apply.
- **Priority (`Prty`)** and **Business Processing Date (`BizPrcgDt`)** influence scheduling.
- **Copy/Duplicate (`CpyDplct`)** and **Possible Duplicate (`PssblDplct`)** flag messages that are copies or that may already have been sent, so a receiver can avoid double-processing.

The **integrity and linking** fields close the set:

- **Signature (`Sgntr`)** carries a digital signature over the message, letting the receiver verify that it was not altered and that it came from the stated sender.
- **Related (`Rltd`)** embeds the header of a related message, linking this one to a prior exchange, which is how a response is tied to its request across the header layer.

## How the header is used

The BAH earns its place at routing time.

![How the BAH routes a message through an intermediary]({{site.url_complet}}/assets/article/finance/head-routing-workflow.png)

A sender composes the business message, wraps it with a BAH stating the sender, receiver, message definition, and a signature, and sends the pair. An intermediary that only needs to route the message reads the header's `To` and forwards it, without parsing the payload, which is both faster and a cleaner separation of concerns. The receiver validates the signature over the message, reads the `MsgDefIdr` to know exactly which definition to apply, and only then processes the business content. If the message is a response, its `Rltd` field points back at the header of the request it answers.

This is why the header is mandatory in most market infrastructures and cross-border schemes: it gives every message a uniform, signable, routable envelope regardless of what business area the payload belongs to.

## Grouping messages: the Business File Header

Sometimes many messages travel together as one file, for example a batch of reports delivered overnight. The **Business File Header (`head.002`)** is the envelope for that case. It opens with a **payload description (`PyldDesc`)** that describes the messages inside the file, so a receiver can understand the file's contents and split it into individual messages for processing. Where the BAH describes a single message, the business file header describes a container of them.

## Conclusion

The `head` area is small but foundational. The Business Application Header (`head.001`) is the routing and control envelope that accompanies every ISO 20022 business message: it names the sender and receiver, identifies the exact message definition, timestamps and prioritises the message, links it to related exchanges, and carries the signature that makes it authentic, all without touching the business payload. The Business File Header (`head.002`) does the same job for a file of many messages. Because it is shared across every business area, the BAH is the piece that makes ISO 20022 messages uniformly routable and verifiable, which is why it appears beside the payload in every other area of the standard.

![Mindmap summarising the ISO 20022 Business Application Header]({{site.url_complet}}/assets/article/finance/iso20022-business-application-header-head.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **Business Application Header (BAH)** | The `head.001` message that accompanies a business message with its routing, context, and integrity information. |
| **head.002** | The Business File Header, the envelope describing a file that contains many business messages. |
| **From (`Fr`)** | The header field identifying the sender of the message. |
| **To (`To`)** | The header field identifying the receiver of the message. |
| **Business Message Identifier (`BizMsgIdr`)** | The unique reference for a message, used to refer to it later. |
| **Message Definition Identifier (`MsgDefIdr`)** | The field naming exactly which message definition the payload is, so the receiver can parse it. |
| **Business Service (`BizSvc`)** | The optional field naming the service or agreement the message is sent under. |
| **Signature (`Sgntr`)** | The header field carrying a digital signature over the message, used to verify authenticity and integrity. |
| **Related (`Rltd`)** | The field embedding a prior message's header, linking a message to a related exchange such as its request. |
| **Payload description (`PyldDesc`)** | The Business File Header field describing the messages contained in a file. |

## Frequently Asked Questions

**Q: What is the Business Application Header, and why is it separate from the message?**

The BAH is a routing and control envelope, message `head.001`, that travels alongside a business message rather than inside it. The business message says what happened; the header says who is sending it, to whom, which message definition it is, when it was created, and whether it is authentic. Keeping them separate means an intermediary can route or log a message by reading only the header without parsing the payload, and the same header structure works for every message type in the standard. It is the piece that makes ISO 20022 messages uniformly routable.

**Q: Which BAH fields are mandatory, and what do they do?**

The routing core is mandatory: From (`Fr`) and To (`To`) identify the sender and receiver; the Business Message Identifier (`BizMsgIdr`) is the message's unique reference; the Message Definition Identifier (`MsgDefIdr`) names exactly which definition the payload is; and the Creation Date (`CreDt`) timestamps it. Together they let a receiver know who sent the message, that it is addressed to it, precisely how to parse the payload, and when it was made. The other fields, such as business service, priority, signature, and related, are optional refinements.

**Q: How does the signature in the BAH work?**

The signature field (`Sgntr`) carries a digital signature computed over the message. When a receiver gets the message, it verifies the signature to confirm two things: that the content was not altered in transit, and that it genuinely came from the party named in the From field. Because the signature sits in the header rather than the payload, the same signing mechanism protects any business message regardless of its area. This is how many market infrastructures and schemes ensure the authenticity and integrity of ISO 20022 traffic.

**Q: What is the Related field for?**

The Related field (`Rltd`) embeds the header of a prior message, linking the current message to an earlier exchange. Its most common use is tying a response to its request: a status advice or a response message can carry, in its `Rltd`, the header of the message it answers, so the two are connected at the routing layer without relying only on identifiers buried in the payload. It lets systems reconstruct a conversation from the headers alone.

**Q: What is the difference between head.001 and head.002?**

They are envelopes at different scales. The `head.001` Business Application Header accompanies a single business message with its routing and control data. The `head.002` Business File Header describes a file that contains many business messages, opening with a payload description of what the file holds. You use the BAH for message-by-message exchange and the business file header when many messages are delivered together as one file, such as a batch of reports, so the receiver can identify and split the contents.

**Q: Does every ISO 20022 message need a BAH?**

Not universally, but in practice most market infrastructures and cross-border schemes require it. The standard allows a business message to be exchanged with or without a BAH, depending on the environment, but the header provides routing, deduplication, market-practice identification, and signing that shared infrastructures depend on. That is why the other areas in this series describe their messages as travelling paired with a `head.001`: in the environments those messages run in, the header is the expected envelope.

## References

- [ISO 20022 Business Application Header specification](https://www.iso20022.org/catalogue-messages/additional-content-messages/business-application-header)
- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [SWIFT — ISO 20022 for financial institutions](https://www.swift.com/standards/iso-20022)
- [Claude Code](https://claude.com/product/claude-code)
