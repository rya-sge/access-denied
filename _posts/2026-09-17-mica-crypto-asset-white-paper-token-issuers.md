---
layout: post
title: "Issuing a Token Under MiCA — The Crypto-Asset White Paper and Its Exemptions (Title II)"
date:   2026-09-17
lang: en
locale: en-GB
categories: regulation blockchain
tags: mica regulation eu crypto-assets token compliance white-paper
series: mica
series_order: 2
description: "What Title II of MiCA asks of anyone offering or listing a token in the EU: white-paper content, notification, exemptions, 14-day withdrawal right, liability."
image: /assets/article/regulation/mica/2026-09-17-mica-white-paper-mindmap.png
isMath: false
---

[MiCA](https://eur-lex.europa.eu/eli/reg/2023/1114/oj), Regulation (EU) 2023/1114, is the EU's rulebook for crypto-assets that fall outside existing financial law. The [first article of this series]({{site.url_complet}}/2026/09/17/mica-explained-scope-token-categories-timeline/) covers its scope and the three categories of token it defines. This one covers the category that most projects belong to: crypto-assets that are neither asset-referenced tokens nor e-money tokens, which is where governance tokens, payment tokens with no stabilisation claim and utility tokens sit.

For that category MiCA does not require authorisation, a licence or capital. It requires a document. Title II, Articles 4 to 15, sets out who must produce a crypto-asset white paper, what it must contain, how it is notified and published, when it can be skipped, what rights a retail buyer has and who is liable if the document is wrong. The regime is deliberately light compared to the stablecoin and service-provider titles, and most of the practical questions are about the exemptions rather than the obligations.

The text below follows the consolidated version of 9 January 2024. Article numbers refer to MiCA unless another act is named.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Who is caught: offers to the public and admissions to trading

Title II attaches to two events, and the person responsible is different for each.

**An offer to the public** (Article 4) is made by an *offeror*, who may or may not be the issuer of the token. Article 4(1) lists seven conditions the offeror must meet before making the offer in the Union:

- be a legal person;
- have drawn up a white paper in accordance with Article 6;
- have notified it under Article 8;
- have published it under Article 9;
- have drafted any marketing communications in accordance with Article 7;
- have published those communications under Article 9;
- comply with the conduct obligations of Article 14.

The first condition is often overlooked. A natural person cannot make an offer to the public of a crypto-asset in the Union at all, whatever the size of the offer. Neither, on the face of the text, can an unincorporated collective.

**An admission to trading** (Article 5) is sought by a *person seeking admission to trading*, and the same seven conditions apply. Two variations matter for exchanges:

- If a trading platform admits a crypto-asset on its own initiative and no white paper has been published, the platform operator must itself comply with Article 5(1) (Article 5(2)).
- The person seeking admission and the platform operator may agree in writing that the operator takes over all or part of the white-paper duties. The agreement must oblige the person seeking admission to supply the information the operator needs (Article 5(3)).

Article 5(4) also removes the white-paper conditions where the crypto-asset is already admitted to trading on another EU platform, provided the existing white paper is up to date and its author consents in writing to its reuse. One white paper therefore serves every EU listing of the same token, and Article 4(7) applies the same logic to subsequent offers of the same token.

The definition of "offer to the public" in Article 3(1)(12) is broad: any communication, in any form and by any means, presenting enough information on the terms and the crypto-asset to let prospective holders decide whether to buy. A website with a price and a purchase button qualifies; so does a Telegram message with the same content.

## The exemptions

Article 4 contains two separate lists of exemptions, and they do different things.

### Small and restricted offers (Article 4(2))

The first list removes the white-paper obligations, that is, drawing up, notifying and publishing the white paper and publishing the marketing communications. It leaves the rest of Article 4(1) in place, so the offeror must still be a legal person and still comply with Article 14. It covers offers that are:

- made to **fewer than 150 natural or legal persons per Member State**, acting on their own account;
- of a **total consideration not exceeding EUR 1 000 000** in the Union over twelve months from the start of the offer, counted in euro, another official currency or crypto-assets;
- addressed **solely to qualified investors**, where the crypto-asset can only be held by such investors. Qualified investors are those in Section I, points (1) to (4), of Annex II to [MiFID II](https://eur-lex.europa.eu/eli/dir/2014/65/oj), that is professional clients such as authorised financial institutions, large undertakings and public bodies.

### Offers outside Title II altogether (Article 4(3))

The second list is stronger: Title II does not apply at all. It covers offers where:

- the crypto-asset is **offered for free**;
- the crypto-asset is **automatically created as a reward** for maintaining the distributed ledger or validating transactions, which covers block rewards and staking rewards paid by the protocol;
- the offer concerns a **utility token giving access to a good or service that exists or is in operation**;
- the holder may use the crypto-asset **only in exchange for goods and services in a limited network of merchants** with contractual arrangements with the offeror.

Two anti-avoidance rules narrow the first and last items. A crypto-asset is not "free" if purchasers must provide personal data in exchange, or if the offeror receives any fee, commission or monetary or non-monetary benefit for it (Article 4(3), second subparagraph). An airdrop that requires a wallet connection and an email address is therefore not free. And the limited-network exemption comes with a notification duty: once the total consideration in such offers exceeds EUR 1 000 000 in any twelve-month period, the offeror must notify the competent authority and explain why the exemption applies, and the authority may decide that it does not (Article 4(3), third and fourth subparagraphs).

### Two limits on all exemptions

Article 4(4) removes every exemption in paragraphs 2 and 3 as soon as the offeror, or anyone acting on its behalf, makes known in any communication an intention to seek admission to trading. A project that announces a listing while running a "free" or sub-EUR 1 million sale has lost its exemption for that sale.

Article 4(8) provides that a white paper drawn up voluntarily for an exempt offer brings the whole of Title II into play, including the notification, publication and liability rules. An offeror cannot publish a document called a white paper for marketing purposes and disclaim the regime.

### Custody and transfer of exempt tokens

Article 4(5) contains a spillover into Title V. Providing custody and administration, or transfer services, for a crypto-asset whose offer is exempt under Article 4(3) does not require a CASP authorisation, unless there is another non-exempt offer of the same token or the token is admitted to trading. The rule matters for wallet providers that hold protocol reward tokens with no listing.

The following diagram traces the decisions from the first communication to the published white paper.

![Title II offer workflow: Article 4(3) exclusions, Article 4(2) small-offer exemptions lost on a listing announcement, then drafting, 20-day notification, publication and Article 12 modifications]({{site.url_complet}}/assets/article/regulation/mica/mica-white-paper-offer-workflow.png)

## What the white paper must contain (Article 6)

Article 6(1) lists ten blocks of information, each expanded in Annex I into numbered items:

- information about the offeror or person seeking admission to trading (Annex I, Part A);
- information about the issuer, if different (Part B);
- information about the operator of the trading platform, where it drew up the document (Part C);
- information about the crypto-asset project (Part D);
- information about the offer to the public or the admission to trading (Part E);
- information about the crypto-asset (Part F);
- the rights and obligations attached to the crypto-asset (Part G);
- information on the underlying technology (Part H);
- information on the risks (Part I);
- the principal adverse impacts on the climate and the environment of the consensus mechanism used to issue the crypto-asset.

The last item is specific to MiCA. It is an environmental disclosure, and ESMA was mandated (Article 6(12)) to draft technical standards on the sustainability indicators, considering the various consensus mechanisms, their incentive structures, energy use, waste and emissions. A proof-of-work token has more to disclose here than a proof-of-stake one, but neither is exempt.

Around the ten blocks, Article 6 imposes form requirements that are easy to check and frequently missed:

- **A prominent statement on the first page** (Article 6(3)) in fixed wording: "This crypto-asset white paper has not been approved by any competent authority in any Member State of the European Union. The offeror of the crypto-asset is solely responsible for the content of this crypto-asset white paper."
- **No assertions about future value** (Article 6(4)), other than the mandatory warning in the next item.
- **A risk statement** (Article 6(5)) that the crypto-asset may lose its value in part or in full, may not always be transferable, may not be liquid, that a utility token may not be exchangeable for the promised good or service if the project fails, and that the crypto-asset is covered neither by the investor-compensation schemes nor by the deposit-guarantee schemes.
- **A management-body statement** (Article 6(6)) confirming that the white paper complies with Title II and that the information is, to the best of the body's knowledge, fair, clear and not misleading, without omissions likely to affect its import.
- **A summary** (Article 6(7)) in brief, non-technical language, with its own warning that it is only an introduction, that the decision to buy should rest on the whole document, and that the white paper is not a prospectus under [Regulation (EU) 2017/1129](https://eur-lex.europa.eu/eli/reg/2017/1129/oj).
- **The date of notification and a table of contents** (Article 6(8)).
- **Language** (Article 6(9)): an official language of the home Member State or a language customary in international finance, and additionally an official language of each host Member State (or that same international language) where the token is offered there.
- **Machine-readable format** (Article 6(10)), with the templates set by ESMA implementing standards.

Everything must be "fair, clear and not misleading", without material omissions, and "presented in a concise and comprehensible form" (Article 6(2)). The last phrase is the one that separates a MiCA white paper from the long technical documents the industry has called white papers for years: the Regulation wants a disclosure document, not a design paper.

## Marketing communications (Article 7)

Marketing is regulated alongside the white paper. Any marketing communication relating to an offer or an admission must (Article 7(1)):

- be clearly identifiable as marketing;
- be fair, clear and not misleading;
- be consistent with the white paper, where one is required;
- state that a white paper has been published and give the website, a telephone number and an email address of the responsible person;
- carry its own fixed-wording statement that it "has not been reviewed or approved by any competent authority in any Member State of the European Union".

Where a white paper is required, no marketing may be disseminated before the white paper is published, though market soundings remain allowed (Article 7(2)). The authority of the Member State where the marketing is disseminated, not only the home authority, has the power to assess it (Article 7(3)).

## Notification and publication (Articles 8 and 9)

MiCA's most distinctive design choice for this category is in Article 8(3): competent authorities "shall not require prior approval of crypto-asset white papers, nor of any marketing communications". There is no review, no comment period and no approval letter. The regime is one of notification.

The notification goes to the competent authority of the home Member State at least **20 working days before publication** (Article 8(5)). It must be accompanied by an explanation of why the crypto-asset is *not* a financial instrument or otherwise excluded under Article 2(4), *not* an e-money token and *not* an asset-referenced token (Article 8(4)). That explanation is the offeror's own classification analysis, and it is the document a supervisor will later hold the offeror to. The notification also lists the host Member States where the offer will be made and the intended start date (Article 8(6)). Marketing communications are notified only on request (Article 8(2)).

The home authority forwards the white paper to the host authorities within five working days and to ESMA, which publishes it in the register under Article 109 by the start date of the offer (Article 8(7)).

Publication (Article 9) is on the offeror's own website, publicly accessible, "at a reasonable time in advance of" and in any event before the start of the offer or the admission. The published version must be identical to the notified one, and it must stay online for as long as the crypto-asset is held by the public.

Once published, Article 11 gives the offeror a Union-wide right: the crypto-asset may be offered throughout the EU and admitted to trading on any EU platform, and no Member State may impose further information requirements. This is the passport of Title II, and it costs one notification.

## After the offer: results, custody and modifications

Three articles cover the life of the document after publication.

**Results and safeguarding** (Article 10). An offeror that set a time limit on the offer publishes its result within 20 working days of the end of the subscription period; one that set no time limit publishes the number of units in circulation at least monthly. During a time-limited offer, the funds or crypto-assets raised must be kept in custody by a credit institution (for funds) or by a CASP providing custody (for crypto-assets); for an open-ended offer that duty lasts until the retail right of withdrawal has expired.

**Modifications** (Article 12). Whenever a significant new factor, material mistake or material inaccuracy capable of affecting the assessment of the crypto-asset arises, the white paper and any marketing must be modified, for the duration of the offer or for as long as the token is admitted to trading. The modified document is notified at least seven working days before publication with the reasons, the offeror announces the notification on its website, and the published version is time-stamped and marked as the applicable one. Older versions stay online for at least ten years with a warning that they are no longer valid. A modification cannot extend the twelve-month limit that Article 4(6) sets for offers of utility tokens whose service does not yet exist.

**Conduct** (Article 14). Offerors and persons seeking admission must act honestly, fairly and professionally, communicate in a fair, clear and not misleading way, manage conflicts of interest, and keep their systems and security access protocols in line with Union standards specified by ESMA guidelines. They must act in the best interests of holders and treat them equally unless preferential treatment of specific holders is disclosed in the white paper. If the offer is cancelled, funds collected must be returned within 25 calendar days.

## The retail right of withdrawal (Article 13)

A retail holder who buys the crypto-asset directly from the offeror, or from a CASP placing it on the offeror's behalf, has **14 calendar days** to withdraw from the purchase without cost and without giving reasons. The period runs from the date of the agreement to purchase. Payments, including any charges, are reimbursed within 14 days of the offeror learning of the withdrawal, by the same means of payment unless the holder agrees otherwise.

The right is narrower than it first appears:

- it does not apply where the crypto-asset was admitted to trading before the retail holder bought it (Article 13(4)), so purchases of an already-listed token, on or off an exchange, carry no withdrawal right;
- for a time-limited offer, it cannot be exercised after the end of the subscription period (Article 13(5));
- it belongs to retail holders only, as defined in Article 3(1)(37).

In practice the right applies to primary sales of unlisted tokens, which is the situation in which a buyer has only the white paper to rely on.

## Liability (Article 15)

Where the white paper, or a modified white paper, contains information that is not complete, fair or clear, or is misleading, the offeror, person seeking admission or platform operator **and the members of its administrative, management or supervisory body** are liable to a holder for any loss incurred (Article 15(1)). Any contractual exclusion or limitation of that liability is void (Article 15(2)).

The allocation of proof is on the holder: they must present evidence that Article 6 was infringed and that reliance on the information affected their decision to purchase, sell or exchange (Article 15(4)). Liability does not attach to the summary alone unless the summary is misleading, inaccurate or inconsistent with the rest of the document, or omits key information (Article 15(5)). Where the platform drew up the white paper under a delegation, the person seeking admission is also responsible for the information it supplied (Article 15(3)). National civil liability is unaffected (Article 15(6)).

Combined with the management-body statement of Article 6(6), this is the enforcement mechanism of a no-approval regime: the authority does not vet the document, so the directors who sign it carry the risk.

The next diagram shows the parties and the documents around a Title II offer.

![Parties around a Title II offer: the offeror drafts and publishes the white paper, notifies the home authority which forwards it to host authorities and the ESMA register, and answers to holders]({{site.url_complet}}/assets/article/regulation/mica/mica-white-paper-parties-concept.png)

## Transitional rules for existing tokens

Article 143 softens Title II for tokens that pre-date it. Articles 4 to 15 do not apply to offers that ended before 30 December 2024 (Article 143(1)). For crypto-assets admitted to trading before that date, only two things apply: Articles 7 and 9 to marketing communications published after it, and a duty on the platform operator to have a white paper drawn up, notified and published by 31 December 2027 in the cases where the Regulation requires one (Article 143(2)). A token listed in the EU in 2023 therefore needs a MiCA white paper by the end of 2027, and the exchange, not the original issuer, carries that duty.

## Conclusion

Title II replaces licensing with disclosure. An offeror of an ordinary crypto-asset in the EU needs no authorisation, but it needs a legal entity, a document in a prescribed form, and directors willing to be liable for it.

- **Two triggers, one document.** An offer to the public and an admission to trading each require a white paper under Article 6, and one white paper serves every subsequent offer and every EU listing of the same token.
- **The exemptions are where the analysis happens.** Small offers skip the white paper: under 150 persons per Member State, under EUR 1 million in twelve months, or qualified investors only; free tokens, protocol rewards, live utility tokens and limited-network tokens are outside Title II entirely. Every exemption is lost the moment a listing is announced.
- **Notification, not approval.** The white paper is filed with the home authority 20 working days before publication together with the offeror's own classification analysis, and no authority reviews it before it goes live.
- **Fixed-wording warnings and a management statement** are mandatory, as is a disclosure on the climate impact of the consensus mechanism.
- **Retail buyers in a primary sale get 14 days** to withdraw; buyers of an already-listed token get nothing.
- **Liability is personal and cannot be contracted away.** The offeror and its board answer to holders for a misleading white paper.

![Mindmap of Title II covering the offer and admission triggers, exemptions, white-paper content, marketing, notification, modifications, withdrawal right, liability and transition]({{site.url_complet}}/assets/article/regulation/mica/2026-09-17-mica-white-paper-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Crypto-asset white paper** | The disclosure document required by Article 6 for an offer to the public or admission to trading of a crypto-asset other than an ART or EMT, with content set by Annex I. |
| **Offer to the public** | A communication in any form presenting enough information on the terms and the crypto-asset for prospective holders to decide whether to purchase (Article 3(1)(12)). |
| **Offeror** | The natural or legal person, other undertaking, or the issuer, who offers crypto-assets to the public; must be a legal person to make an offer under Article 4. |
| **Person seeking admission to trading** | The party asking a trading platform for crypto-assets to list a token; carries the Article 5 duties unless they are delegated in writing to the platform operator. |
| **Qualified investor** | A person or entity listed in Section I, points (1) to (4), of Annex II to MiFID II, that is a professional client by nature. |
| **Utility token** | A crypto-asset only intended to provide access to a good or service supplied by its issuer; exempt from Title II when the good or service already exists. |
| **Limited network** | A set of merchants with contractual arrangements with the offeror within which a token can be spent; offers of such tokens are outside Title II, subject to notification above EUR 1 million. |
| **Home Member State** | For an offeror established in the Union, the Member State of its registered office; its competent authority receives the white-paper notification. |
| **Retail holder** | A natural person acting outside their trade, business, craft or profession; the beneficiary of the Article 13 right of withdrawal. |
| **Marketing communication** | Any promotional communication relating to an offer or admission; must be identified as such, be consistent with the white paper and carry the Article 7 statement. |

### Requirements Checklist

Title II is written as a set of conditions an offeror or person seeking admission must meet before and during an offer. The rows below transcribe them article by article so a token launch can be checked against the text.

#### Article 4 — Offers to the public

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 4(1)(a) | The offeror is a legal person. |
| ☐ | 4(1)(b)–(d) | A white paper has been drawn up (Art. 6), notified (Art. 8) and published (Art. 9). |
| ☐ | 4(1)(e)–(f) | Marketing communications, if any, comply with Art. 7 and are published under Art. 9. |
| ☐ | 4(1)(g) | The offeror complies with the conduct obligations of Art. 14. |
| ☐ | 4(2)(a) | Exemption from (b)–(d) and (f): fewer than 150 persons per Member State acting on their own account. |
| ☐ | 4(2)(b) | Exemption: total consideration in the Union at most EUR 1 000 000 over 12 months from the start of the offer. |
| ☐ | 4(2)(c) | Exemption: offer solely to qualified investors, and the token can only be held by them. |
| ☐ | 4(3)(a) | Title II does not apply: token offered for free (no personal data, fee, commission or benefit received). |
| ☐ | 4(3)(b) | Title II does not apply: token automatically created as a reward for maintaining the ledger or validating transactions. |
| ☐ | 4(3)(c) | Title II does not apply: utility token giving access to a good or service that exists or is in operation. |
| ☐ | 4(3)(d) | Title II does not apply: token usable only in a limited network of merchants; notify the authority once consideration exceeds EUR 1 000 000 in 12 months. |
| ☐ | 4(4) | No exemption applies once an intention to seek admission to trading is communicated. |
| ☐ | 4(5) | Custody and transfer services for tokens exempt under 4(3) need no CASP authorisation unless another non-exempt offer exists or the token is admitted to trading. |
| ☐ | 4(6) | An offer of a utility token for a good or service not yet in operation lasts at most 12 months from publication of the white paper. |
| ☐ | 4(7) | A subsequent offer of the same token is a separate offer, but no new white paper is needed if one is published, updated and its author consents in writing. |
| ☐ | 4(8) | A white paper drawn up voluntarily for an exempt offer brings the whole of Title II into application. |

#### Article 5 — Admission to trading

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 5(1) | The person seeking admission meets the same seven conditions as an offeror under Art. 4(1). |
| ☐ | 5(2) | Where a platform admits a token on its own initiative without a published white paper, the operator complies with 5(1) itself. |
| ☐ | 5(3) | The person seeking admission and the operator may agree in writing that the operator takes over the white-paper duties; the agreement obliges the former to supply the necessary information. |
| ☐ | 5(4) | No new white paper where the token is already admitted on another EU platform and the existing white paper is compliant, updated and its author consents. |

#### Article 6 — Content and form of the white paper

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 6(1)(a)–(c) | Information about the offeror or person seeking admission, the issuer if different, and the platform operator if it drew up the document (Annex I, Parts A–C). |
| ☐ | 6(1)(d)–(g) | Information about the project, the offer or admission, the crypto-asset, and the rights and obligations attached to it (Parts D–G). |
| ☐ | 6(1)(h)–(i) | Information on the underlying technology and on the risks (Parts H–I). |
| ☐ | 6(1)(j) | Information on the principal adverse climate and environmental impacts of the consensus mechanism. |
| ☐ | 6(1) | If drawn up by someone else, the identity of that person and the reason. |
| ☐ | 6(2) | All information fair, clear and not misleading; no material omissions; concise and comprehensible. |
| ☐ | 6(3) | First-page statement that the white paper has not been approved by any competent authority and that the offeror is solely responsible. |
| ☐ | 6(4) | No assertions about the future value of the crypto-asset. |
| ☐ | 6(5) | Statement that the token may lose value, may not be transferable or liquid, a utility token may not be exchangeable if the project fails, and no investor-compensation or deposit-guarantee scheme applies. |
| ☐ | 6(6) | Management-body statement of compliance and of the fairness and completeness of the information. |
| ☐ | 6(7) | A non-technical summary with the prescribed warnings, including that the document is not a prospectus. |
| ☐ | 6(8) | Date of notification and a table of contents. |
| ☐ | 6(9) | Drawn up in an official language of the home Member State (and of each host Member State) or a language customary in international finance. |
| ☐ | 6(10) | Made available in a machine-readable format. |

#### Article 7 — Marketing communications

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 7(1)(a)–(b) | Clearly identifiable as marketing; fair, clear and not misleading. |
| ☐ | 7(1)(c)–(d) | Consistent with the white paper; states that a white paper is published and gives website, telephone and email of the responsible person. |
| ☐ | 7(1)(e) | Carries the prescribed statement that it has not been reviewed or approved by any competent authority. |
| ☐ | 7(2) | No marketing disseminated before the white paper is published (market soundings excepted). |

#### Articles 8 and 9 — Notification and publication

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 8(1) | The white paper is notified to the competent authority of the home Member State. |
| ☐ | 8(2) | Marketing communications are notified to home and host authorities on request. |
| ☐ | 8(4) | The notification explains why the token is not excluded under Art. 2(4), not an EMT and not an ART. |
| ☐ | 8(5) | Notification at least 20 working days before publication. |
| ☐ | 8(6) | The notification lists the host Member States and the intended start date, and any change to that date is communicated. |
| ☐ | 9(1) | White paper and marketing published on the offeror's publicly accessible website before the start of the offer or admission, and kept online while the token is held by the public. |
| ☐ | 9(2) | The published version is identical to the notified (or modified) version. |

#### Articles 10 to 15 — Life of the offer, withdrawal and liability

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 10(1) | Time-limited offer: result published within 20 working days of the end of the subscription period. |
| ☐ | 10(2) | Open-ended offer: number of units in circulation published at least monthly. |
| ☐ | 10(3)–(4) | Funds or crypto-assets raised are held in custody by a credit institution or a custodian CASP; for an open-ended offer, until the withdrawal right has expired. |
| ☐ | 12(1)–(2) | The white paper and marketing are modified on any significant new factor, material mistake or inaccuracy, and the modification is notified at least seven working days before publication with reasons. |
| ☐ | 12(3), (6)–(7) | The notification is announced on the website; the modified version is published, time-stamped and marked as applicable. |
| ☐ | 12(9) | Older versions remain online for at least 10 years with a warning that they are no longer valid. |
| ☐ | 13(1)–(2) | Retail holders buying from the offeror or a placing CASP have 14 calendar days to withdraw without cost; reimbursement within 14 days by the same means of payment. |
| ☐ | 13(3)–(5) | The right is described in the white paper; it does not apply to tokens already admitted to trading, nor after the end of a subscription period. |
| ☐ | 14(1) | Act honestly, fairly and professionally; communicate fairly; manage conflicts of interest; keep systems and security access protocols to Union standards. |
| ☐ | 14(2) | Act in the best interests of holders and treat them equally unless preferential treatment is disclosed. |
| ☐ | 14(3) | If the offer is cancelled, funds are returned within 25 calendar days. |
| ☐ | 15(1)–(2) | The offeror and the members of its management body are liable to holders for incomplete, unfair, unclear or misleading information; contractual exclusions of that liability are void. |

## Frequently Asked Questions

**Q: Does an offeror need a licence or approval to sell an ordinary crypto-asset in the EU under MiCA?**

No. Title II requires no authorisation. The offeror must be a legal person, draw up a white paper meeting Article 6, notify it to the home competent authority 20 working days before publication, publish it on its website and comply with the marketing and conduct rules. Article 8(3) expressly forbids competent authorities from requiring prior approval of the white paper or the marketing communications.

**Q: What is the difference between the exemptions in Article 4(2) and those in Article 4(3)?**

Article 4(2) exempts small and restricted offers from the white-paper obligations only, so the offeror must still be a legal person and still comply with the conduct rules of Article 14. Article 4(3) places certain offers outside Title II altogether: free tokens, protocol rewards, live utility tokens and limited-network tokens. Both sets of exemptions are lost under Article 4(4) as soon as an intention to seek admission to trading is communicated, and a voluntary white paper for an exempt offer brings the whole title back into application under Article 4(8).

**Q: An airdrop asks users to connect a wallet, follow a social-media account and enter an email address. Is it "offered for free"?**

No. The second subparagraph of Article 4(3) states that a crypto-asset is not offered for free where purchasers are required to provide personal data to the offeror in exchange for it, or where the offeror receives any fee, commission, or monetary or non-monetary benefit. An email address is personal data, and a follow is a non-monetary benefit. Such an airdrop is an offer to the public and needs a white paper unless another exemption applies, for instance the 150-person or EUR 1 million thresholds of Article 4(2).

**Q: Who is liable if the white paper is wrong, and can the offeror limit that liability in its terms of sale?**

Under Article 15(1), the offeror, person seeking admission or platform operator *and the members of its administrative, management or supervisory body* are liable to a holder for losses caused by information that is not complete, fair or clear, or that is misleading. Article 15(2) deprives any contractual exclusion or limitation of that liability of legal effect. The holder must show the infringement and that their reliance on the information affected their decision, and the summary alone does not ground liability unless it is misleading or inconsistent when read with the rest of the document.

**Q: When does the 14-day right of withdrawal apply, and when does it not?**

It applies to a retail holder who buys the crypto-asset directly from the offeror, or from a CASP placing it on the offeror's behalf, in the 14 calendar days from the agreement to purchase, without cost or reasons. It does not apply if the crypto-asset was admitted to trading before the purchase, it cannot be exercised after the end of a time-limited subscription period, and it does not benefit professional buyers.

**Q: Combining the rules: a foundation outside the EU launches a governance token that is already listed on a non-EU exchange, and an EU platform now wants to list it. Who must do what?**

The token is in the residual category, so Title II applies to the admission to trading on the EU platform, and someone must satisfy Article 5(1) by drawing up, notifying and publishing a white paper. There are two ways to allocate that duty:

- **The foundation** acts as person seeking admission, if it is a legal person. Its home Member State, having no EU registered office or branch, is the Member State where the first application for admission is made (Article 3(1)(33)(c)).
- **The EU platform** takes over the duties by written agreement (Article 5(3)) or, if it lists on its own initiative, must comply itself (Article 5(2)).

In either case the platform's operating rules must refuse admission until a white paper is published (Article 76(1)), and the liability of Article 15 falls on whoever drew up the document, with the foundation also responsible for the information it supplied.

## References

### Legal texts

- [Regulation (EU) 2023/1114 on markets in crypto-assets (MiCA)](https://eur-lex.europa.eu/eli/reg/2023/1114/oj), Title II, Articles 4 to 15, and Annex I
- [Consolidated text of Regulation (EU) 2023/1114 as of 9 January 2024](https://eur-lex.europa.eu/eli/reg/2023/1114/2024-01-09), EUR-Lex
- [Directive 2014/65/EU (MiFID II)](https://eur-lex.europa.eu/eli/dir/2014/65/oj), Annex II, for the definition of qualified investors
- [Regulation (EU) 2017/1129 (Prospectus Regulation)](https://eur-lex.europa.eu/eli/reg/2017/1129/oj), which the white paper is expressly not

### Supervisory authorities

- [ESMA — Markets in Crypto-Assets Regulation (MiCA)](https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/markets-crypto-assets-regulation-mica), white-paper templates and the Article 109 register

### Related articles

- [Two Ways to Build a Permissioned Token — Centrifuge's Transfer Hook Against ERC-3643]({{site.url_complet}}/2026/08/18/centrifuge-hook-vs-erc3643/)
- [CIP-113 Programmable Tokens on Cardano]({{site.url_complet}}/2026/08/26/cip-113-programmable-tokens-cardano/)
- [Security of Cryptocurrency Exchanges - Overview]({{site.url_complet}}/2025/11/06/crypto-exchange-security-overview/)
