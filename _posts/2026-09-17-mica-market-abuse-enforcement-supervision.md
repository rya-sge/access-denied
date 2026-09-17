---
layout: post
title: "Market Abuse and Enforcement Under MiCA — Insider Dealing, Manipulation, Penalties and Supervision (Titles VI and VII)"
date:   2026-09-17
lang: en
locale: en-GB
categories: regulation blockchain security
tags: mica regulation eu crypto-assets market-abuse compliance enforcement
series: mica
series_order: 5
description: "MiCA's market-abuse rules for crypto-assets, the fine floors Member States must set, the powers of national authorities and ESMA, and EBA's stablecoin oversight"
image: /assets/article/regulation/mica/2026-09-17-mica-market-abuse-mindmap.png
isMath: false
---

[MiCA](https://eur-lex.europa.eu/eli/reg/2023/1114/oj), Regulation (EU) 2023/1114, is the EU's framework for crypto-assets outside existing financial law; the [first article of this series]({{site.url_complet}}/2026/09/17/mica-explained-scope-token-categories-timeline/) covers its scope and structure. The previous three articles dealt with the actors MiCA authorises or makes file a document: token offerors, stablecoin issuers and service providers. The last two operative titles concern everyone else, and the supervisory and penalty provisions that give the whole text effect.

Title VI, in seven articles, transposes the core of the EU's market-abuse regime for securities to crypto-assets: a definition of inside information, a disclosure duty on issuers, and prohibitions on insider dealing, unlawful disclosure and market manipulation, applying to any person, anywhere, in respect of a crypto-asset admitted to trading in the Union. Title VII, in forty-six articles, is the enforcement layer: which national authority supervises what, the investigative and intervention powers it must have, the floors for administrative fines, the public registers ESMA keeps, and a separate regime under which the European Banking Authority directly supervises, inspects and fines the issuers of significant stablecoins.

This article takes the two titles in that order. The source is the consolidated text of 9 January 2024, and article numbers refer to MiCA unless another act is named.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Title VI: the market-abuse regime

### Scope (Article 86)

The title applies to acts by **any person** concerning crypto-assets that are **admitted to trading**, or for which a request for admission has been made. It applies whether or not the transaction, order or behaviour takes place on a trading platform, and to actions and omissions **in the Union and in third countries**. Three consequences follow:

- an unlisted token is outside the title, so a primary sale with no listing is governed only by the white-paper rules of Title II;
- over-the-counter and on-chain dealing in a listed token is inside it;
- a person outside the EU who manipulates the price of a token listed on an EU platform is inside it, whatever the enforcement difficulties.

The drafting mirrors the [Market Abuse Regulation](https://eur-lex.europa.eu/eli/reg/2014/596/oj) (Regulation (EU) No 596/2014) for financial instruments, and the same concepts carry over with two adaptations for the technology: information about the functioning of the ledger can be inside information, and behaviour affecting the consensus mechanism can be reportable.

### Inside information (Article 87)

Inside information is information of a **precise nature**, **not made public**, relating directly or indirectly to one or more issuers, offerors, persons seeking admission or crypto-assets, which **if made public would likely have a significant effect on the price** of those crypto-assets or of a related crypto-asset. For a person executing client orders, it also covers information conveyed by a client about the client's pending orders.

Information is precise if it indicates circumstances or an event that exist or may reasonably be expected to come into existence, and is specific enough to draw a conclusion about the effect on price. Intermediate steps of a protracted process count, and an intermediate step is itself inside information if it meets the test on its own. "Significant effect on the price" means information a reasonable holder would likely use as part of the basis of an investment decision.

In crypto-asset markets this includes an unannounced listing or delisting, a change to token supply or emissions, a protocol upgrade or fork, a treasury movement, an exploit, or a reserve problem at a stablecoin issuer.

### Disclosure by issuers (Article 88)

Issuers, offerors and persons seeking admission must inform the public **as soon as possible** of inside information that directly concerns them, in a way that allows fast access and a complete, correct and timely assessment. Disclosure may not be combined with marketing. The information is posted on the website and kept there for **at least five years**.

Disclosure may be **delayed**, on the issuer's own responsibility, only where immediate disclosure would prejudice its legitimate interests, the delay is not likely to mislead the public, and confidentiality can be ensured (Article 88(2)). Immediately after the information is eventually disclosed, the issuer informs the competent authority that disclosure was delayed and explains in writing how the three conditions were met, unless the Member State has opted for that record to be provided only on request (Article 88(3)).

From **10 January 2030** the same information must also be submitted to the collection body for the European Single Access Point under Article 110a, in machine-readable form with prescribed metadata. That article was added by [Regulation (EU) 2023/2869](https://eur-lex.europa.eu/eli/reg/2023/2869/oj) and is the only substantive amendment in the consolidated text.

### Insider dealing and unlawful disclosure (Articles 89 and 90)

Insider dealing arises where a person possesses inside information and **uses it** by acquiring or disposing of the crypto-assets to which it relates, for its own account or a third party's, directly or indirectly. Cancelling or amending an order placed before the person obtained the information is also use, as is submitting, modifying or withdrawing a bid. Nobody may engage or attempt to engage in insider dealing, recommend or induce another person to do so, or, holding inside information, recommend that another person acquire, dispose of, cancel or amend. Using such a recommendation is itself insider dealing where the recipient knows or ought to know its basis.

Article 89(5) lists who is covered: members of the issuer's governing bodies, holders of its capital, persons with access through employment, profession or duties "or in relation to its role in the distributed ledger technology", persons involved in criminal activities, and anyone else who knows or ought to know that the information is inside information. The reference to a role in the DLT brings validators, sequencers, core developers and node operators within the class of primary insiders. Where the person is a legal person, the article applies to the natural persons who took part in the decision (Article 89(6)).

Article 90 prohibits **unlawful disclosure**: disclosing inside information to any other person except in the normal exercise of employment, profession or duties, and passing on recommendations or inducements based on it.

### Market manipulation (Article 91)

No person may engage or attempt to engage in market manipulation. The definition has three limbs:

- entering into a transaction, placing an order or engaging in any other behaviour that gives or is likely to give **false or misleading signals** as to supply, demand or price, or that **secures the price at an abnormal or artificial level**, unless carried out for legitimate reasons;
- doing any of those things **while employing a fictitious device or any other form of deception or contrivance**;
- **disseminating information** through the media, including the internet, that gives false or misleading signals or secures an artificial price, including rumours, where the person knew or ought to have known that the information was false or misleading.

Article 91(3) then names behaviours that are manipulation in any event:

- securing a **dominant position** over supply or demand so as to fix prices or create unfair trading conditions;
- placing, cancelling or modifying orders on a trading platform in a way that **disrupts or delays** the platform, **makes genuine orders harder to identify**, or **creates a false signal**, in particular by entering orders to initiate or exacerbate a trend. Spoofing, layering, quote stuffing and wash trading fall here;
- **voicing an opinion** about a crypto-asset in the traditional or electronic media, having previously taken a position in it, and profiting from the effect of that opinion on the price without having properly disclosed the conflict of interest. This is the article that reaches paid promotion and undisclosed positions on social media.

![Title VI model: inside information feeds the Article 88 disclosure duty and the prohibitions of Articles 89 to 91, while intermediaries detect and report suspicious orders to the authority under Article 92]({{site.url_complet}}/assets/article/regulation/mica/mica-market-abuse-concept.png)

### Detection and reporting (Article 92)

Any person **professionally arranging or executing transactions** in crypto-assets must have effective arrangements, systems and procedures to prevent and detect market abuse, and must report **without delay** to the competent authority of its Member State any reasonable suspicion regarding an order or transaction, including cancellations and modifications, and "other aspects of the functioning of the distributed ledger technology such as the consensus mechanism" where circumstances indicate that market abuse has been, is being or is likely to be committed. The receiving authority forwards the report to the authorities of the trading platforms concerned.

ESMA's technical standards, due by 30 December 2024, set the arrangements, the reporting template and the coordination procedure for cross-border cases.

The obligation sits on trading platforms, exchanges, brokers and portfolio managers, and Article 76(7) and (8) already requires a platform's systems to detect market abuse and its operator to report it. What MiCA adds to the securities model is the reference to the ledger: a platform that observes a validator reordering or censoring transactions to move a price is expected to report that too.

## Title VII: the enforcement layer

### Competent authorities and their powers (Chapter 1)

Each Member State designates one or more competent authorities and a single point of contact for cross-border cooperation (Article 93). Article 94 then lists the minimum supervisory and investigative powers they must have under national law, and the list is long because the Regulation replaces national regimes that had none. Among them:

- require information and documents from any person;
- **suspend** the provision of crypto-asset services, or an offer or admission to trading, for up to **30 consecutive working days** at a time on reasonable suspicion of an infringement, and **prohibit** them where an infringement is found;
- require the amendment of a white paper or of marketing communications, or the inclusion of additional information;
- make public that a CASP fails to fulfil its obligations, and require the disclosure of material information affecting clients;
- order the **immediate cessation** of unauthorised crypto-asset services, without prior warning;
- require the transfer of client contracts to another CASP on withdrawal of an authorisation;
- suspend or require the suspension of trading in a crypto-asset, and require a platform to remove one;
- carry out **on-site inspections**, enter premises to seize documents and data on suspicion of insider dealing or manipulation, require existing data-traffic records from telecommunications operators where national law permits, request the **freezing or sequestration** of assets, and refer matters for criminal prosecution;
- require ISPs and hosting providers to **remove content or restrict access** to an online interface, and make public any measure taken.

Chapter 1 also organises cooperation: between national authorities (Article 95), with EBA and ESMA (Article 96), on the **classification of crypto-assets**, where ESMA, EBA and the authorities work towards a common view of which tokens are financial instruments (Article 97), with other authorities such as anti-money-laundering supervisors and the ECB (Article 98), and with third countries (Article 107). A host authority with clear grounds to suspect irregularities notifies the home authority and ESMA and, if the home authority does not act, may take **precautionary measures** itself (Article 102).

### Product intervention (Articles 103 to 106)

Three levels of authority may **temporarily prohibit or restrict** the marketing, distribution or sale of crypto-assets, or an activity or practice related to them:

- ESMA, for crypto-assets other than ARTs and EMTs (Article 103);
- EBA, for ARTs and EMTs (Article 104);
- any national authority, in or from its Member State (Article 105).

The European measures require a significant investor-protection concern or a threat to market integrity or financial stability that existing rules do not address and that no national authority has adequately addressed; they are reviewed at least every six months and prevail over any national measure. National measures require a similar finding and are notified to ESMA or EBA a month in advance, or with 24 hours' notice in urgent cases.

### The registers (Chapter 2)

ESMA keeps two public registers. The first (Article 109) lists every notified white paper for ordinary crypto-assets, every authorised issuer of an ART or EMT with its white paper, and every authorised CASP with its services, passported Member States and website, together with withdrawals. The second (Article 110) is a **register of non-compliant entities**: firms that provide crypto-asset services in the Union without authorisation, or that market to EU clients under cover of reverse solicitation, listed by name or website with the authority that reported them, in machine-readable form. Both are the reference a client or counterparty can check.

### Administrative penalties (Chapter 3)

Article 111 requires Member States to give their authorities the power to impose administrative penalties for infringements of the operative articles of Titles II to VI, unless the infringement is already a criminal offence under national law. It then sets **minimum maximum** fines: the ceiling in national law may be higher, but not lower.

For infringements of Titles II to V (Article 111(2) and (3)):

- a public statement naming the person and the infringement, and an order to cease and desist;
- for **natural persons**, fines of at least **EUR 700 000**;
- for **legal persons**, fines of at least **EUR 5 000 000**, or a percentage of total annual turnover: **3 %** for Title II infringements, **5 %** for Title V infringements, and **12.5 %** for Title III and IV infringements;
- in all cases at least **twice the profit gained or loss avoided**, where determinable, even above those amounts;
- for Title V infringements, a temporary ban on the responsible individuals from exercising management functions in a CASP.

For infringements of Title VI (Article 111(5)):

- the same public statement and cease-and-desist order, plus disgorgement of profits;
- a temporary ban from management functions in a CASP and from dealing on own account, and a ban of **at least ten years** for a repeated infringement of Articles 89 to 92;
- fines of at least **three times** the profit gained or loss avoided;
- for natural persons, at least **EUR 1 000 000** for a breach of the disclosure duty (Article 88) and **EUR 5 000 000** for insider dealing, unlawful disclosure, manipulation or failure to detect and report (Articles 89 to 92);
- for legal persons, at least **EUR 2 500 000 or 2 %** of annual turnover for Article 88, and **EUR 15 000 000 or 15 %** of annual turnover for Articles 89 to 92.

Turnover is consolidated at the level of the ultimate parent where group accounts are prepared. Article 112 lists the factors an authority weighs: gravity, duration, degree of responsibility, financial strength, profits, losses to third parties, cooperation and previous infringements. Article 113 guarantees a right of appeal, Article 114 requires decisions to be **published**, in anonymised form where identification would be disproportionate, and Article 116 applies the [Whistleblower Directive](https://eur-lex.europa.eu/eli/dir/2019/1937/oj) (Directive (EU) 2019/1937) to reports of MiCA infringements.

| Infringement | Natural person, at least | Legal person, at least |
|---|---|---|
| Title II (Arts 4–14) | EUR 700 000 | EUR 5 000 000 or 3 % of turnover |
| Titles III–IV (issuers of ARTs and EMTs) | EUR 700 000 | EUR 5 000 000 or 12.5 % of turnover |
| Title V (CASPs, Arts 59–83) | EUR 700 000 | EUR 5 000 000 or 5 % of turnover |
| Art. 88 (disclosure of inside information) | EUR 1 000 000 | EUR 2 500 000 or 2 % of turnover |
| Arts 89–92 (insider dealing, disclosure, manipulation, detection) | EUR 5 000 000 | EUR 15 000 000 or 15 % of turnover |
| Any of the above, where profit is determinable | 2× (3× for Title VI) the profit gained or loss avoided | same |

### EBA's supervision of significant stablecoin issuers (Chapters 4 and 5)

The [stablecoin article]({{site.url_complet}}/2026/09/17/mica-stablecoins-asset-referenced-tokens-e-money-tokens/) of this series explains when a token becomes significant. Once it does, Article 117 transfers supervision of its issuer from the national authority to **EBA**, for the articles on reporting, white-paper modification, marketing, governance, own funds, reserve audit, acquisitions, recovery and redemption plans. Other activities of the same issuer stay with the national authority, and for a significant EMT denominated in a non-euro Member State currency with 80 % of holders and volume at home, supervision stays national.

The apparatus around that transfer:

- an **EBA crypto-asset committee** takes the decisions (Article 118);
- a **consultative supervisory college** is set up within 30 days of each classification, chaired by EBA and composed of the home authority, the authorities of the most relevant CASPs, custodians and trading platforms, the ECB and relevant central banks, and ESMA (Article 119); its opinions are non-binding but the authority must explain any departure from them (Article 120);
- EBA has direct powers to **request information** (Article 122), conduct **general investigations** including interviews and records (Article 123), and carry out **on-site inspections** with the authorisation of a national court where national law requires it (Article 124), subject to legal privilege (Article 121) and professional secrecy (Article 129);
- EBA may impose **supervisory measures**: cease-and-desist decisions, orders to transmit information, suspension of an offer for up to 30 working days, prohibition of an offer, suspension or prohibition of a service, and public statements (Article 130);
- EBA may impose **fines** of up to **12.5 %** of annual turnover for a significant ART issuer and **10 %** for a significant EMT issuer, or twice the profit gained or loss avoided, for the infringements listed in Annexes V and VI (Article 131), and **periodic penalty payments** of **3 %** of average daily turnover (2 % of average daily income for natural persons) to compel compliance with an order (Article 132);
- fines are published, enforceable as civil judgments, and allocated to the EU budget (Article 133); the person concerned has a right to be heard (Article 135) and to review by the Court of Justice, which has unlimited jurisdiction over fines (Article 136);
- EBA charges **supervisory fees** to significant issuers to cover its costs (Article 137) and may **delegate** specific tasks to a national authority (Article 138).

Annexes V and VI list the infringements EBA may fine, item by item, from failing to report quarterly on a token above EUR 100 million to failing to segregate the reserve, to granting interest, to not submitting the recovery plan. They are the operational checklist of Titles III and IV rewritten as offences.

![MiCA supervision: national authorities supervise offerors, issuers and CASPs, ESMA keeps the registers and intervention powers, and EBA supervises and fines significant stablecoin issuers through a college]({{site.url_complet}}/assets/article/regulation/mica/mica-supervision-architecture-concept.png)

## What the two titles change in practice

For a **trading platform**, Title VI adds surveillance to the venue rules of Title V. Systems to detect layering, wash trades and coordinated pumps are required by Article 92 and Article 76(7), and their absence is itself an infringement with a 15 % turnover ceiling. Suspicious-order reports go to the national authority within the meaning of Article 92(1).

For a **project team or foundation** with a listed token, Article 88 imposes a continuous disclosure duty of the kind listed companies live under. Announcing a partnership, a token burn or a security incident selectively, to a Discord channel before the public, or to a market maker before the community, is unlawful disclosure by the discloser and insider dealing by any recipient who trades. A delay must be documented and justified on the three conditions of Article 88(2).

For **individuals**, the criminal-law analogy holds. Trading on knowledge of an unannounced listing, front-running a client's order, or promoting a token one holds without disclosing the position, is now an administrative offence throughout the Union with fines starting at EUR 5 000 000 for a natural person, whether or not the Member State also treats it as a crime.

For **anyone checking a counterparty**, the ESMA registers are the first stop: an entity that claims to be a MiCA CASP either appears in the Article 109 register or does not, and one that appears in the Article 110 register is one an authority has already reported as non-compliant.

## Conclusion

Titles VI and VII give MiCA the two things a disclosure-and-authorisation regime needs to work: a prohibition that reaches everyone who trades, and a supervisor with the power to find out and to fine.

- **Market abuse is defined as in securities law**, for any crypto-asset admitted to trading, any person, on or off platform, inside or outside the Union.
- **Issuers have a continuous disclosure duty** for inside information, with a narrow right to delay, a five-year archive and, from 2030, ESAP filing.
- **Insider dealing includes ledger insiders.** Validators, developers and node operators are primary insiders, and cancelling an order on inside information is use.
- **Manipulation includes order-book games and undisclosed promotion.** Spoofing, layering, cornering and voicing an opinion while holding a position are named in the text.
- **Intermediaries must detect and report**, including anomalies in the consensus mechanism.
- **Fines have floors, not ceilings.** EUR 700 000 for individuals and 3 % to 12.5 % of turnover for firms across Titles II to V; EUR 5 000 000 and 15 % of turnover for market abuse, and at least three times the profit.
- **Supervision is national with two European layers.** ESMA keeps the registers and can intervene on ordinary crypto-assets; EBA directly supervises, inspects and fines significant stablecoin issuers.

![Mindmap of Titles VI and VII covering market-abuse scope, inside information, insider dealing and manipulation, detection, authority powers, intervention, registers, penalties and EBA supervision]({{site.url_complet}}/assets/article/regulation/mica/2026-09-17-mica-market-abuse-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Inside information** | Precise, non-public information relating to issuers, offerors or crypto-assets that would likely have a significant effect on their price if made public (Article 87). |
| **Insider dealing** | Using inside information to acquire or dispose of the crypto-assets it relates to, or to cancel or amend an order, for one's own or a third party's account (Article 89). |
| **Unlawful disclosure** | Disclosing inside information to another person outside the normal exercise of employment, profession or duties (Article 90). |
| **Market manipulation** | Transactions, orders, behaviour or dissemination of information that give false or misleading signals, fix an artificial price or use a deceptive device (Article 91). |
| **Person professionally arranging or executing transactions** | A CASP or other intermediary that must maintain systems to detect market abuse and report suspicious orders to its competent authority (Article 92). |
| **Competent authority** | The national body designated under Article 93, holding at least the supervisory and investigative powers of Article 94. |
| **Product intervention** | The temporary prohibition or restriction of the marketing, distribution or sale of crypto-assets by ESMA, EBA or a national authority under Articles 103 to 105. |
| **Register of non-compliant entities** | ESMA's public list under Article 110 of entities providing crypto-asset services in the Union without authorisation. |
| **Supervisory college** | The consultative body chaired by EBA under Article 119 that coordinates supervision of an issuer of a significant ART or EMT. |
| **Periodic penalty payment** | A daily payment of 3 % of average daily turnover imposed by EBA to compel an issuer to end an infringement or comply with a request (Article 132). |

### Requirements Checklist

Title VI is a set of prohibitions and duties on market participants; Title VII is a set of powers and penalties Member States must provide. The rows below transcribe the provisions that bind persons and firms, and the penalty floors, so a compliance function can check a programme against the text.

#### Articles 86 to 92 — Market abuse

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 86 | The rules apply to any person, to any crypto-asset admitted or requested for admission to trading, on or off platform, in the Union and in third countries. |
| ☐ | 87 | Inside information: precise, non-public, price-sensitive information on issuers, offerors or crypto-assets, including client pending orders for executing firms. |
| ☐ | 88(1) | Issuers, offerors and persons seeking admission disclose inside information directly concerning them as soon as possible, separately from marketing, and keep it online for at least five years. |
| ☐ | 88(2)–(3) | Delay only where legitimate interests would be prejudiced, the public is not misled and confidentiality is ensured; the authority is informed of the delay with a written explanation. |
| ☐ | 110a | From 10 January 2030, Article 88 information is also submitted to the ESAP collection body in machine-readable form. |
| ☐ | 89(1)–(4) | No insider dealing, attempt, recommendation or inducement; cancelling or amending an order on inside information is use. |
| ☐ | 89(5)–(6) | Applies to governing-body members, shareholders, persons with access through employment, profession, duties or a role in the DLT, persons involved in crime, and anyone who knows or ought to know; for legal persons, to the natural persons who decided. |
| ☐ | 90 | No disclosure of inside information outside the normal exercise of employment, profession or duties; no onward disclosure of inside-based recommendations. |
| ☐ | 91(1)–(2) | No market manipulation or attempt: false or misleading signals, artificial price levels, deceptive devices, dissemination of false information. |
| ☐ | 91(3) | Named manipulations: dominant position fixing prices; orders that disrupt the platform, hide genuine orders or create false signals; voicing opinions while holding undisclosed positions. |
| ☐ | 92(1) | Persons professionally arranging or executing transactions maintain systems to prevent and detect market abuse and report reasonable suspicions without delay, including anomalies in the consensus mechanism. |

#### Articles 93 to 110 — Authorities, cooperation, intervention and registers

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 93 | Each Member State designates competent authorities and a single point of contact. |
| ☐ | 94(1) | Authorities hold at least the listed powers: information requests, suspension up to 30 working days, prohibition, white-paper and marketing amendments, cessation of unauthorised services, inspections, freezing of assets, content removal, publication. |
| ☐ | 95–98 | Cooperation between authorities, with EBA and ESMA, on classification convergence, and with AML supervisors, central banks and other bodies. |
| ☐ | 100–101 | Professional secrecy and data-protection rules apply to information exchanged. |
| ☐ | 102 | A host authority notifies suspected irregularities to the home authority and ESMA and may take precautionary measures if the home authority does not act. |
| ☐ | 103–104 | ESMA (ordinary crypto-assets) and EBA (ARTs and EMTs) may temporarily prohibit or restrict marketing, distribution, sale or practices where investor protection, market integrity or financial stability is threatened and existing rules and national action do not address it. |
| ☐ | 105–106 | National authorities may prohibit or restrict in or from their Member State after notice to ESMA or EBA; European measures prevail. |
| ☐ | 107 | Cooperation agreements with third-country authorities. |
| ☐ | 109 | ESMA maintains the public register of white papers, ART and EMT issuers and CASPs. |
| ☐ | 110 | ESMA maintains the public, machine-readable register of non-compliant entities. |

#### Articles 111 to 116 — Administrative penalties

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 111(1) | Administrative penalties for infringements of Arts 4–14, 16–47 (listed), 48–55 (listed), 59–83 (listed), 88–92 and failure to cooperate, unless already criminal under national law. |
| ☐ | 111(2) | For Titles II–V: public statement; cease-and-desist order; fines of at least twice the profit or loss avoided; natural persons at least EUR 700 000. |
| ☐ | 111(3) | Legal persons: at least EUR 5 000 000, or 3 % of turnover (Title II), 5 % (Title V), 12.5 % (Titles III–IV), consolidated at the ultimate parent. |
| ☐ | 111(4) | Title V infringements: temporary ban on management functions in a CASP. |
| ☐ | 111(5) | Title VI: public statement; cease-and-desist; disgorgement; management and own-account dealing bans, at least 10 years on repetition; at least three times the profit; natural persons EUR 1 000 000 (Art. 88) or EUR 5 000 000 (Arts 89–92); legal persons EUR 2 500 000 or 2 % (Art. 88), EUR 15 000 000 or 15 % (Arts 89–92). |
| ☐ | 112 | Penalties weigh gravity, duration, responsibility, financial strength, profits, third-party losses, cooperation and previous infringements. |
| ☐ | 113–114 | Right of appeal; publication of decisions, anonymised where identification would be disproportionate. |
| ☐ | 116 | Directive (EU) 2019/1937 protects persons reporting infringements. |

#### Articles 117 to 138 — EBA supervision of significant issuers

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 117(1) | Issuers of significant ARTs and EMTs are supervised by EBA for the listed articles; other activities remain with the national authority. |
| ☐ | 118–119 | An EBA crypto-asset committee takes decisions; a consultative college is established within 30 days of each classification. |
| ☐ | 120 | College opinions are non-binding; departures must be explained. |
| ☐ | 121–124 | EBA may request information, conduct general investigations and on-site inspections, subject to legal privilege and, where national law requires, court authorisation. |
| ☐ | 130 | EBA supervisory measures: cease-and-desist, information orders, suspension of an offer for up to 30 working days, prohibition, suspension or prohibition of a service, public statements. |
| ☐ | 131 | Fines up to 12.5 % of annual turnover (significant ART) or 10 % (significant EMT), or twice the profit or loss avoided, for Annex V and VI infringements. |
| ☐ | 132 | Periodic penalty payments of 3 % of average daily turnover (2 % of daily income for natural persons). |
| ☐ | 133–136 | Fines published, enforceable and paid to the EU budget; right to be heard; review by the Court of Justice with unlimited jurisdiction over fines. |
| ☐ | 137–138 | Supervisory fees charged to significant issuers; tasks may be delegated to national authorities. |

## Frequently Asked Questions

**Q: Does Title VI apply to a token that is traded only on decentralised exchanges and has never been listed on a MiCA-authorised platform?**

Only if the token is admitted to trading, or a request for admission has been made, on a trading platform for crypto-assets within the meaning of MiCA. Article 86(1) ties the title to that status, not to where the trading happens. A token with no such admission is outside Title VI, though its offer remains subject to Title II. Once a token is admitted anywhere in the Union, Article 86(2) and (3) extend the prohibitions to every transaction in it, on any venue, on-chain or off, inside or outside the Union.

**Q: What are the three conditions for delaying the disclosure of inside information?**

Under Article 88(2), an issuer may delay disclosure on its own responsibility only where immediate disclosure is likely to prejudice its legitimate interests, the delay is not likely to mislead the public, and the issuer can ensure the confidentiality of the information. All three must hold, the issuer must inform the competent authority that disclosure was delayed and give a written explanation, and the delay ends the moment confidentiality is lost. A security vulnerability under active remediation is the standard example of a legitimate delay; a poor quarterly reserve figure is not.

**Q: Who counts as an insider under MiCA, and why does the text mention the distributed ledger?**

Article 89(5) covers members of the issuer's governing bodies, shareholders, persons with access to the information through their employment, profession or duties "or in relation to its role in the distributed ledger technology", persons involved in criminal activity, and any other person who knows or ought to know that the information is inside information. The reference to the DLT was added because in crypto-asset markets some of the persons best placed to know about an upgrade, a fork, a pending large transaction or a governance outcome are validators, sequencers, core developers and node operators rather than corporate officers.

**Q: Is promoting a token on social media market manipulation?**

It can be. Article 91(3)(c) treats as manipulation the act of voicing an opinion about a crypto-asset in the traditional or electronic media, having previously taken a position in it, and profiting from the effect of that opinion on its price, without having disclosed the conflict of interest to the public in a proper and effective way. The elements are a prior position, a public opinion, a subsequent profit and no adequate disclosure. Disclosure of the position at the time of the opinion takes the conduct outside the provision; false statements about the token would fall under Article 91(2)(c) regardless.

**Q: How do the fines for market abuse compare with those for breaching the CASP rules?**

Article 111 sets minimum maximum fines, and market abuse sits at the top.

A CASP infringing Title V faces a fine of at least EUR 5 000 000 or 5 % of turnover, and a natural person at least EUR 700 000.

Insider dealing, unlawful disclosure, manipulation or failure to detect and report under Articles 89 to 92 carries at least EUR 15 000 000 or 15 % of turnover for a legal person and EUR 5 000 000 for a natural person, plus at least three times the profit gained or loss avoided, management and dealing bans, and a ban of at least ten years on repetition. Member States may set higher ceilings, and criminal law may apply in addition.

**Q: Combining the titles: a trading platform's employee learns from the listing committee that a token will be listed next week, buys it on another venue, and tells a friend who does the same. What has happened under MiCA, and who acts?**

The listing decision is inside information under Article 87: precise, non-public and price-sensitive. From there the titles apply in sequence:

- **The employee** possesses the information through employment (Article 89(5)(c)), and buying the token on another venue is insider dealing under Article 89(1), since Article 86(2) covers transactions off the platform.
- **Telling the friend** is unlawful disclosure under Article 90, and the friend's purchase is insider dealing under Article 89(4) if they knew or ought to have known the source.
- **The platform** must have had systems under Article 92 and Article 76(7) capable of flagging the pattern, and any CASP that executed the orders must report the suspicion to its national competent authority.
- **The authority** investigates under Article 94, may freeze assets, and imposes penalties under Article 111(5): for each individual, a fine of at least EUR 5 000 000 or three times the profit, a management and dealing ban, and publication of the decision under Article 114.

If the platform's surveillance was inadequate, the platform itself has infringed Article 92, with a floor of EUR 15 000 000 or 15 % of turnover.

## References

### Legal texts

- [Regulation (EU) 2023/1114 on markets in crypto-assets (MiCA)](https://eur-lex.europa.eu/eli/reg/2023/1114/oj), Titles VI and VII, Articles 86 to 138, and Annexes V and VI
- [Consolidated text of Regulation (EU) 2023/1114 as of 9 January 2024](https://eur-lex.europa.eu/eli/reg/2023/1114/2024-01-09), EUR-Lex
- [Regulation (EU) No 596/2014 (Market Abuse Regulation)](https://eur-lex.europa.eu/eli/reg/2014/596/oj), the securities-market model for Title VI
- [Regulation (EU) 2023/2869](https://eur-lex.europa.eu/eli/reg/2023/2869/oj), which inserted Article 110a on the European Single Access Point
- [Directive (EU) 2019/1937 (Whistleblower Directive)](https://eur-lex.europa.eu/eli/dir/2019/1937/oj), applied by Article 116
- [Regulation (EU) No 1093/2010](https://eur-lex.europa.eu/eli/reg/2010/1093/oj) establishing EBA and [Regulation (EU) No 1095/2010](https://eur-lex.europa.eu/eli/reg/2010/1095/oj) establishing ESMA, both amended by MiCA

### Supervisory authorities

- [ESMA — Markets in Crypto-Assets Regulation (MiCA)](https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/markets-crypto-assets-regulation-mica), including the Article 109 and 110 registers and the market-abuse technical standards
- [EBA — Markets in Crypto-Assets (MiCA)](https://www.eba.europa.eu/activities/single-rulebook/regulatory-activities/markets-crypto-assets-mica), supervision of significant issuers

### Related articles

- [Security of Cryptocurrency Exchanges - Overview]({{site.url_complet}}/2025/11/06/crypto-exchange-security-overview/)
- [Hyperliquid's Onchain Order Book - Matching, Ordering, and How It Differs from a CEX and from GMX]({{site.url_complet}}/2026/09/02/hyperliquid-order-book-matching-engine/)
- [CoW Protocol - Intent & MEV protection]({{site.url_complet}}/2024/11/21/cow-protocol-overview/)
