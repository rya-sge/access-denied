---
layout: post
title: "MiCA Explained — Scope, Token Categories and Timeline of Regulation (EU) 2023/1114"
date:   2026-09-17
lang: en
locale: en-GB
categories: regulation blockchain
tags: mica regulation eu crypto-assets stablecoin compliance
series: mica
series_order: 1
description: "What MiCA regulates, what it excludes, how it sorts a token into e-money token, asset-referenced token or other crypto-asset, and when each part applies."
image: /assets/article/regulation/mica/2026-09-17-mica-explained-mindmap.png
isMath: false
---

[MiCA](https://eur-lex.europa.eu/eli/reg/2023/1114/oj), Regulation (EU) 2023/1114 on markets in crypto-assets, is the European Union's single rulebook for crypto-assets that no earlier financial-services law already covered. It was adopted on 31 May 2023, applies directly in every Member State without national transposition, and replaced twenty-seven national regimes with one set of definitions, one authorisation, one passport and one enforcement floor.

The Regulation runs to 149 articles and six annexes over 222 pages in its consolidated form. Most of that text is addressed to one of four audiences: a person offering a token to the public, an issuer of a stablecoin, a firm providing services such as custody or exchange, and anyone trading a listed crypto-asset. This series follows that split. The present article is the entry point: it sets out what MiCA regulates and what it leaves alone, how it sorts a token into one of three categories, who the actors are, how the text is organised, and from which date each part applies. The four articles that follow take one audience each.

Everything below is taken from the consolidated text of 9 January 2024, which folds in the amendment made by [Regulation (EU) 2023/2869](https://eur-lex.europa.eu/eli/reg/2023/2869/oj) and the corrigendum of 2 May 2024. Article numbers refer to MiCA unless another act is named.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What MiCA sets out to do

Article 1 states the object in one paragraph and then lists five things the Regulation lays down:

- **Transparency and disclosure** for the issuance, the offer to the public and the admission to trading of crypto-assets. The instrument is the *crypto-asset white paper*, a disclosure document with mandatory content and a mandatory warning.
- **Authorisation and supervision** of three kinds of actor: crypto-asset service providers (CASPs), issuers of asset-referenced tokens and issuers of e-money tokens, together with rules on how they are run, organised and governed.
- **Protection of holders** during issuance, offer and admission to trading.
- **Protection of clients** of crypto-asset service providers.
- **Market integrity**: measures against insider dealing, unlawful disclosure of inside information and market manipulation.

Two design choices follow from that list and run through the whole text. The first is that MiCA regulates *activities and actors*, not the technology: a distributed ledger as such is not licensed, and a token that nobody offers, lists or services in the Union is not caught. The second is that MiCA is residual. It applies only where an existing regime does not, which is why the scope article spends more words on what is excluded than on what is included.

## Scope

Article 2(1) sets the perimeter: natural and legal persons, and certain other undertakings, engaged in the issuance, offer to the public or admission to trading of crypto-assets, or providing services related to crypto-assets, *in the Union*. The territorial hook is the activity, so a firm established outside the EU that serves EU clients is inside the perimeter, with one narrow exception for services a client requests at its own exclusive initiative (Article 61, covered in the [CASP article]({{site.url_complet}}/2026/09/17/mica-casp-authorisation-capital-custody/)).

### Persons and bodies outside the scope

Article 2(2) lists six categories of person to which the Regulation does not apply:

- persons who provide crypto-asset services exclusively for their parent company, their own subsidiaries or sister subsidiaries (the intra-group exemption);
- a liquidator or administrator acting in an insolvency procedure, except for the purposes of the redemption plan in Article 47;
- the European Central Bank, national central banks acting as monetary authorities, and other public authorities of the Member States;
- the European Investment Bank and its subsidiaries;
- the European Financial Stability Facility and the European Stability Mechanism;
- public international organisations.

### Assets outside the scope

Two further paragraphs exclude assets rather than persons, and they matter more in practice.

Article 2(3) excludes crypto-assets that are **unique and not fungible with other crypto-assets**. This is the NFT carve-out. The text does not use the term, and the exclusion is narrower than the label suggests: a token is out of scope only if it is unique in fact, so a large series of near-identical tokens, or a fractionalised interest in one asset, does not qualify simply because it is minted under a non-fungible standard.

Article 2(4) excludes crypto-assets that qualify as any of the following under existing law:

- **financial instruments** as defined in [MiFID II](https://eur-lex.europa.eu/eli/dir/2014/65/oj) (Directive 2014/65/EU), which is the exclusion that removes security tokens from MiCA and leaves them under prospectus, market-abuse and investment-services law;
- **deposits**, including structured deposits;
- **funds**, except where they qualify as e-money tokens;
- **securitisation positions**;
- non-life and life **insurance** products, reinsurance and retrocession contracts;
- **pension products** and schemes of several kinds, including occupational pensions and the pan-European Personal Pension Product;
- **social security schemes**.

The financial-instrument exclusion is the one that generates most classification work, because MiFID II's definition is itself open-textured. Article 2(5) therefore instructed ESMA to issue guidelines, by 30 December 2024, on the conditions and criteria for a crypto-asset to qualify as a financial instrument. The practical consequence is that every token offered in the EU is sorted twice: first against MiFID II to see whether MiCA applies at all, then within MiCA to find which title applies.

## The three categories of crypto-asset

Article 3 carries fifty-one definitions. Four of them define the taxonomy on which every later obligation depends.

A **crypto-asset** (Article 3(1)(5)) is "a digital representation of a value or of a right that is able to be transferred and stored electronically using distributed ledger technology or similar technology". The definition is technology-neutral in two ways: it does not require a blockchain, only DLT "or similar technology", and it does not require a token standard, a native asset, or any particular ledger design.

Within that set, MiCA singles out two categories of token that purport to hold a stable value, and treats everything else as a residual class.

- An **e-money token** or EMT (Article 3(1)(7)) purports to maintain a stable value by referencing the value of **one official currency**. A euro or dollar stablecoin is the standard case.
- An **asset-referenced token** or ART (Article 3(1)(6)) is a crypto-asset that is not an EMT and purports to maintain a stable value by referencing **another value or right, or a combination**, including one or more official currencies. A token referencing a basket of currencies, a commodity, or a mix of currencies and crypto-assets is an ART.
- Every crypto-asset that is neither an ART nor an EMT falls into the residual category that the Regulation calls **crypto-assets other than asset-referenced tokens or e-money tokens**. Payment tokens with no stabilisation claim, governance tokens and utility tokens are all here.

A **utility token** (Article 3(1)(9)) is a sub-type of the residual category: a crypto-asset "only intended to provide access to a good or a service supplied by its issuer". The definition matters because several exemptions in Title II are reserved for utility tokens.

Two details of the definitions catch people out. The classification is driven by what the token *purports* to do, not by whether it succeeds: an algorithmic stablecoin that claims a peg to the euro is an EMT whether or not the peg holds. And the ART category is defined by exclusion from the EMT category, so a token that references one official currency is always an EMT, never an ART, even if the issuer would prefer the ART regime.

The following diagram shows the order in which the tests apply.

![Decision flow sorting a token: Article 2(4) exclusions, non-fungibility, then e-money token if it references one official currency, asset-referenced token if another value, otherwise other crypto-asset]({{site.url_complet}}/assets/article/regulation/mica/mica-crypto-asset-classification-workflow.png)

## The actors

MiCA attaches obligations to roles, and the roles are defined more finely than everyday usage. The ones a reader needs to keep apart:

- **Issuer** (Article 3(1)(10)): the natural or legal person, or other undertaking, who issues crypto-assets. For ARTs and EMTs the issuer is the regulated party, and nobody else may offer the token without the issuer's written consent.
- **Offeror** (Article 3(1)(13)): whoever offers crypto-assets to the public, which may or may not be the issuer. For the residual category it is the offeror, not the issuer, who carries the white-paper duties.
- **Person seeking admission to trading**: the party asking a trading platform to list a crypto-asset. The same duties as an offeror apply, and they may be delegated in writing to the platform operator (Article 5(3)).
- **Crypto-asset service provider** (Article 3(1)(15)): a legal person or other undertaking providing one or more of the ten crypto-asset services listed in Article 3(1)(16) to clients on a professional basis.
- **Holder** and **client**: the counterparties protected by the Regulation. A **retail holder** (Article 3(1)(37)) is a natural person acting outside their trade, business, craft or profession, and several protections, such as the right of withdrawal, apply to retail holders only.
- **Competent authority**: the national supervisor each Member State designates under Article 93. Every actor has a **home Member State** (Article 3(1)(33)), which is where its registered office is for EU-established actors and, for third-country offerors with no branch, the state of first offer; any other Member State in which it operates is a **host Member State**.
- **EBA and ESMA**: the two European supervisory authorities. ESMA keeps the public registers and drafts most technical standards; EBA directly supervises issuers of *significant* ARTs and EMTs.

The ten crypto-asset services in Article 3(1)(16) are: custody and administration; operation of a trading platform; exchange of crypto-assets for funds; exchange for other crypto-assets; execution of orders; placing; reception and transmission of orders; advice; portfolio management; and transfer services. Each has its own definition and, in Title V, its own conduct rules.

![Who each MiCA title addresses: offerors under Title II, ART and EMT issuers under Titles III and IV, CASPs under Title V, traders under Title VI, and the authorities, EBA and ESMA under Title VII]({{site.url_complet}}/assets/article/regulation/mica/mica-titles-actors-concept.png)

## How the text is organised

The Regulation has nine titles and six annexes. Reading it is easier once the mapping between title and audience is clear, because the same obligation (a white paper, a conflicts-of-interest policy, a complaints procedure) reappears in three titles with variations for each category of token.

| Title | Articles | Subject | Covered in |
|---|---|---|---|
| I | 1–3 | Subject matter, scope, definitions | this article |
| II | 4–15 | Crypto-assets other than ARTs and EMTs: the white-paper regime | [Issuing a token under MiCA]({{site.url_complet}}/2026/09/17/mica-crypto-asset-white-paper-token-issuers/) |
| III | 16–47 | Asset-referenced tokens: authorisation, reserve, redemption, significance | [Stablecoins under MiCA]({{site.url_complet}}/2026/09/17/mica-stablecoins-asset-referenced-tokens-e-money-tokens/) |
| IV | 48–58 | E-money tokens | same |
| V | 59–85 | Authorisation and operating conditions for CASPs | [Becoming a CASP]({{site.url_complet}}/2026/09/17/mica-casp-authorisation-capital-custody/) |
| VI | 86–92 | Prevention and prohibition of market abuse | [Market abuse and enforcement]({{site.url_complet}}/2026/09/17/mica-market-abuse-enforcement-supervision/) |
| VII | 93–138 | Competent authorities, EBA and ESMA; penalties; supervision of significant issuers | same |
| VIII | 139 | Delegated acts | — |
| IX | 140–149 | Reports, transitional measures, amendments to other acts, entry into force | this article |
| Annex I–III | | Disclosure items of the white paper for each token category | articles 2 and 3 |
| Annex IV | | Minimum capital of CASPs by class | article 4 |
| Annex V–VI | | Infringements by issuers of significant ARTs and EMTs, for EBA fines | article 5 |

Two features of the drafting are worth knowing before opening it. First, most operative articles end with a mandate to EBA or ESMA to draft regulatory or implementing technical standards, usually due by 30 June 2024 or 30 December 2024; the thresholds and templates that make the Regulation workable live in those Level 2 acts, not in MiCA itself. Second, the consolidated text marks its layers: `▼B` for the base act, `▼M1` for the 2023/2869 amendment (which added Article 110a on the European Single Access Point) and `▼C1` for the corrigendum. The consolidated version is a documentation tool with no legal effect; only the Official Journal text is authentic.

## When each part applies

Article 149 splits the application of the Regulation into three dates, and Article 143 adds transitional arrangements on top. Together they produce the following timeline.

| Date | What happens |
|---|---|
| 29 June 2023 | Entry into force, twenty days after publication. Only the empowerments to adopt delegated acts and technical standards apply from this date (Article 149(4)). |
| **30 June 2024** | **Titles III and IV apply**: the ART and EMT regimes, including authorisation of issuers. |
| **30 December 2024** | **Everything else applies**: Title II (white papers), Title V (CASPs), Title VI (market abuse) and Title VII (supervision and penalties). |
| 30 June 2025 | Interim report from the Commission on the application of the Regulation (Article 140). |
| 1 July 2026 | Latest end of the transitional period for CASPs already operating under national law (Article 143(3)). |
| 30 June 2027 | Full Commission report, with a legislative proposal where appropriate (Article 140). |
| 31 December 2027 | Deadline for operators of trading platforms to have a white paper in place for crypto-assets admitted to trading before 30 December 2024 (Article 143(2)). |
| 10 January 2030 | Inside-information disclosures under Article 88 must also be submitted to the European Single Access Point (Article 110a, added by Regulation 2023/2869). |

The transitional measures in Article 143 soften the two application dates for actors that already existed:

- **Offers that ended** before 30 December 2024 are outside Title II altogether (Article 143(1)).
- **Crypto-assets already admitted to trading** before that date keep their listing; only the marketing rules apply to new communications, and the platform operator has until 31 December 2027 to produce a white paper where one is required (Article 143(2)).
- **CASPs operating under national law** before 30 December 2024 may continue until 1 July 2026 or until they are granted or refused a MiCA authorisation, whichever is sooner. Member States may shorten or waive this period if their previous national regime was less strict than MiCA, and they had to notify their choice by 30 June 2024 (Article 143(3)). Member States may also run a simplified authorisation procedure for such entities (Article 143(6)).
- **ART issuers** other than credit institutions that were issuing before 30 June 2024 may continue until their application is decided, provided they applied before 30 July 2024. Credit institutions issuing ARTs had the same deadline to notify (Article 143(4) and (5)).

![MiCA timeline from entry into force in June 2023 through the stablecoin titles in June 2024, full application in December 2024, the CASP transition to July 2026, and the 2027 and 2030 deadlines]({{site.url_complet}}/assets/article/regulation/mica/mica-application-timeline-concept.png)

## What MiCA leaves for later

Three subjects that a reader might expect in a crypto-asset regulation are not in the operative text, and Article 142 says so directly. By 30 December 2024 the Commission was to report on "the latest developments in crypto-assets", and the article names the topics: decentralised finance, the lending and borrowing of crypto-assets, non-fungible tokens beyond the Article 2(3) exclusion, and the environmental impact of consensus mechanisms. Each may become a legislative proposal; none is regulated by MiCA today.

The gap most often discussed is DeFi. MiCA regulates identifiable persons who offer, issue or provide services. A protocol with no identifiable operator has nobody to authorise, and the Regulation does not attempt to invent one. The same logic runs the other way: a front-end operator, a DAO with a legal wrapper, or a team that controls upgrade keys can be an offeror or a service provider on the ordinary definitions, and the absence of a "DeFi exemption" in the text means that question is answered case by case.

## Conclusion

MiCA is a perimeter rule before it is anything else: it defines a crypto-asset broadly, subtracts what other law already covers, and regulates the actors that remain.

- **Scope is activity-based and residual.** Article 2 applies the Regulation to issuance, offers, admissions to trading and services in the Union, and removes financial instruments, deposits, funds, insurance, pensions and tokens that are unique and non-fungible.
- **Three categories drive every obligation.** An e-money token references one official currency, an asset-referenced token references anything else that is meant to hold value, and every other crypto-asset falls into the residual class where utility tokens live.
- **Roles, not entities, carry the duties.** Offeror, issuer, person seeking admission, CASP, holder and client are distinct, and the home Member State of each determines which national authority supervises it.
- **The text maps to audiences.** Titles II, III–IV, V and VI–VII correspond to token offerors, stablecoin issuers, service providers and market participants, and this series follows that map.
- **Application came in two steps.** Stablecoin rules from 30 June 2024, everything else from 30 December 2024, with a transitional period for existing CASPs that ends no later than 1 July 2026.

![Mindmap of MiCA covering its object, scope and exclusions, the three token categories, the actors, the structure of the nine titles and the application timeline]({{site.url_complet}}/assets/article/regulation/mica/2026-09-17-mica-explained-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Crypto-asset** | A digital representation of a value or right that can be transferred and stored electronically using distributed ledger technology or similar technology (Article 3(1)(5)). |
| **Asset-referenced token (ART)** | A crypto-asset, other than an e-money token, that purports to maintain a stable value by referencing another value or right or a combination, including one or more official currencies. |
| **E-money token (EMT)** | A crypto-asset that purports to maintain a stable value by referencing the value of one official currency. |
| **Utility token** | A crypto-asset only intended to provide access to a good or service supplied by its issuer; a sub-type of the residual category. |
| **Offer to the public** | A communication, in any form, presenting enough information on the terms and the crypto-asset for a prospective holder to decide whether to buy. |
| **Crypto-asset service provider (CASP)** | A legal person or undertaking providing one or more of the ten listed crypto-asset services to clients on a professional basis, allowed to do so under Article 59. |
| **Retail holder** | A natural person acting for purposes outside their trade, business, craft or profession. |
| **Home Member State** | The Member State whose competent authority supervises an actor; for EU-established actors, the state of the registered office. |
| **Competent authority** | The national supervisor designated by each Member State under Article 93 for offerors, issuers and CASPs. |
| **Significant token** | An ART or EMT that meets at least three of the size and interconnectedness criteria in Article 43, and whose issuer is then supervised by EBA. |

### Requirements Checklist

MiCA is written as a set of conditions and obligations; the rows below transcribe the scoping tests of Title I and the transitional provisions of Title IX in the order the text presents them, so a reader can run a token or an actor through them. The regime-specific obligations of Titles II to VII are in the checklists of the following articles.

#### Article 2 — Scope

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 2(1) | The person issues, offers to the public, seeks admission to trading of, or provides services related to, crypto-assets in the Union. |
| ☐ | 2(2)(a) | Services provided exclusively to a parent, own subsidiaries or sister subsidiaries are outside the scope. |
| ☐ | 2(2)(b) | Liquidators and administrators in insolvency are outside the scope, except for the Article 47 redemption plan. |
| ☐ | 2(2)(c)–(f) | The ECB, national central banks as monetary authorities, other public authorities, the EIB, the EFSF, the ESM and public international organisations are outside the scope. |
| ☐ | 2(3) | Crypto-assets that are unique and not fungible with other crypto-assets are outside the scope. |
| ☐ | 2(4)(a) | Crypto-assets qualifying as financial instruments under MiFID II are outside the scope. |
| ☐ | 2(4)(b)–(c) | Deposits (including structured deposits) and funds (unless they are e-money tokens) are outside the scope. |
| ☐ | 2(4)(d)–(j) | Securitisation positions, insurance and reinsurance products, pension products and schemes, PEPPs and social security schemes are outside the scope. |
| ☐ | 2(5) | ESMA guidelines on the qualification of crypto-assets as financial instruments were due by 30 December 2024. |

#### Article 3 — Classification

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 3(1)(5) | The asset is a digital representation of a value or right, transferable and storable electronically using DLT or similar technology. |
| ☐ | 3(1)(7) | If it purports to maintain a stable value by referencing one official currency, it is an e-money token (Title IV). |
| ☐ | 3(1)(6) | If it is not an EMT and purports to maintain a stable value by referencing another value, right or combination, it is an asset-referenced token (Title III). |
| ☐ | 3(1)(9) | If it is only intended to give access to a good or service supplied by its issuer, it is a utility token within the residual category (Title II). |
| ☐ | 3(1)(16) | The activity matches one of the ten listed crypto-asset services; if so, Title V applies to the provider. |

#### Articles 143 and 149 — Application and transition

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 149(3) | Titles III and IV apply from 30 June 2024. |
| ☐ | 149(2) | All other titles apply from 30 December 2024. |
| ☐ | 143(1) | Articles 4 to 15 do not apply to offers to the public that ended before 30 December 2024. |
| ☐ | 143(2) | For crypto-assets admitted to trading before 30 December 2024, Articles 7 and 9 apply to new marketing communications and the platform operator must have a white paper in place by 31 December 2027. |
| ☐ | 143(3) | CASPs operating under national law before 30 December 2024 may continue until 1 July 2026 or until a MiCA decision, whichever is sooner, unless the Member State shortened or waived the period. |
| ☐ | 143(4)–(5) | ART issuers active before 30 June 2024 may continue pending a decision if they applied (or, for credit institutions, notified) before 30 July 2024. |
| ☐ | 143(6) | Member States may apply a simplified authorisation procedure to nationally authorised CASPs applying between 30 December 2024 and 1 July 2026. |

## Frequently Asked Questions

**Q: Does MiCA apply to a token issued on a private, permissioned ledger?**

Yes, if the token meets the definition in Article 3(1)(5). The definition requires only that the value or right be transferable and storable electronically using distributed ledger technology "or similar technology". Neither the openness of the ledger nor the consensus mechanism is a criterion. What removes a token from the scope is its legal nature (a financial instrument, a deposit, a fund) or its uniqueness, not the ledger it runs on.

**Q: A token references the euro but is stabilised by an algorithm and over-collateralised crypto-assets rather than a bank reserve. Is it an EMT or an ART?**

It is an e-money token. Article 3(1)(7) defines an EMT by what the token *purports* to do, namely maintain a stable value by referencing one official currency, and says nothing about the mechanism. The stabilisation method is irrelevant to the classification, though it is highly relevant to whether the issuer can meet Title IV, which requires issuance at par against funds received and redemption at par at any time. An ART is defined by exclusion from the EMT category, so a single-currency reference can never be an ART.

**Q: Why does the Regulation regulate the offeror rather than the issuer for ordinary crypto-assets, but the issuer for stablecoins?**

For the residual category, the person who communicates the offer to the public is the one in a position to draw up and stand behind a white paper, and the issuer may be a foundation, a protocol or a person outside the Union. Articles 4 and 5 therefore attach the duties to the offeror or the person seeking admission to trading.

For ARTs and EMTs, the obligations concern a reserve of assets, redemption at par and prudential capital, which only the entity that issues the token and holds the reserve can satisfy. Articles 16 and 48 therefore require that the offeror *be* the issuer, and allow others to offer the token only with the issuer's written consent.

**Q: What are the two application dates, and why are they different?**

Titles III and IV, covering asset-referenced tokens and e-money tokens, applied from 30 June 2024. Everything else applied from 30 December 2024. The legislator brought stablecoins forward by six months because they were considered the category with the most immediate consequences for financial stability: their reserves are held in the traditional financial system, and large issuers were already operating in the Union with no prudential framework.

**Q: A firm was providing custody of crypto-assets in a Member State under a national registration before December 2024. Does it need a MiCA authorisation on 30 December 2024?**

Not immediately. Article 143(3) allows a CASP that provided its services in accordance with applicable law before 30 December 2024 to continue until 1 July 2026 or until its MiCA application is granted or refused, whichever comes first. Two qualifications apply. Member States could shorten or waive that period if they judged their previous regime less strict than MiCA, and several did; the firm must check its own Member State's choice. And the transitional right covers continuation of existing services only; it does not give a passport to other Member States, which requires a MiCA authorisation and the notification under Article 65.

**Q: Combining the scope rules and the taxonomy: a company sells tokens that give discounted access to its cloud storage service, which is live today, and it also lists them on an EU exchange. Which title applies, and does it need a white paper?**

The token is a utility token in the residual category, so Title II is the relevant title. For the *offer to the public*, Article 4(3)(c) exempts utility tokens giving access to a good or service that exists or is in operation, so no white paper would be needed for the sale alone.

But Article 4(4) removes every Title II exemption where the offeror makes known an intention to seek admission to trading, and Article 5 requires a white paper for admission to trading regardless of the exemptions in Article 4. Because the company lists the token, it needs a white paper under Article 6, notified under Article 8 and published under Article 9, and the exchange must not admit the token without one (Article 76(1)).

## References

### Legal texts

- [Regulation (EU) 2023/1114 on markets in crypto-assets (MiCA)](https://eur-lex.europa.eu/eli/reg/2023/1114/oj), Official Journal L 150, 9.6.2023
- [Consolidated text of Regulation (EU) 2023/1114 as of 9 January 2024](https://eur-lex.europa.eu/eli/reg/2023/1114/2024-01-09), EUR-Lex (documentation tool, no legal effect)
- [Regulation (EU) 2023/2869](https://eur-lex.europa.eu/eli/reg/2023/2869/oj) amending several regulations as regards the European Single Access Point
- [Directive 2014/65/EU (MiFID II)](https://eur-lex.europa.eu/eli/dir/2014/65/oj), whose definition of financial instrument sets the boundary of MiCA
- [Regulation (EU) 2023/2859](https://eur-lex.europa.eu/eli/reg/2023/2859/oj) establishing the European Single Access Point (ESAP)

### Supervisory authorities

- [ESMA — Markets in Crypto-Assets Regulation (MiCA)](https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/markets-crypto-assets-regulation-mica), technical standards, guidelines and the registers
- [EBA — Markets in Crypto-Assets (MiCA)](https://www.eba.europa.eu/activities/single-rulebook/regulatory-activities/markets-crypto-assets-mica), technical standards for issuers of ARTs and EMTs

### Related articles

- [Two Ways to Build a Permissioned Token — Centrifuge's Transfer Hook Against ERC-3643]({{site.url_complet}}/2026/08/18/centrifuge-hook-vs-erc3643/)
- [Flexible Access Control in smart contracts (CMTAT)]({{site.url_complet}}/2026/01/27/cmtat-access-control/)
- [Tether USDT smart contract - Overview]({{site.url_complet}}/2025/07/06/tether-stablecoin-overview/)
- [Crypto Wallets Explained - Types, Risks, and How to select it]({{site.url_complet}}/2024/10/08/crypto-wallet-introduction/)
