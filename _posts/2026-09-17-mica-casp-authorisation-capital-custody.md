---
layout: post
title: "Becoming a CASP Under MiCA — Authorisation, Capital and Custody Obligations (Title V)"
date:   2026-09-17
lang: en
locale: en-GB
categories: regulation blockchain security
tags: mica regulation eu crypto-assets custody exchange compliance wallet
series: mica
series_order: 4
description: "Title V of MiCA for exchanges, custodians and brokers: who needs authorisation, capital classes, client-asset segregation, custody liability, rules per service."
image: /assets/article/regulation/mica/2026-09-17-mica-casp-mindmap.png
isMath: false
---

[MiCA](https://eur-lex.europa.eu/eli/reg/2023/1114/oj), Regulation (EU) 2023/1114, regulates crypto-assets that fall outside existing EU financial law, and the [first article of this series]({{site.url_complet}}/2026/09/17/mica-explained-scope-token-categories-timeline/) sets out its scope and vocabulary. Title V is its longest title and the one that reaches the most firms: every exchange, custodian, broker, wallet provider with control of keys, advisor and portfolio manager that serves EU clients is a *crypto-asset service provider* (CASP) and needs either a MiCA authorisation or a notification under an existing licence.

The title has five chapters. The first sets out who may provide crypto-asset services and how authorisation works; the second lists the obligations that apply to every CASP, from prudential capital to the segregation of client assets; the third adds obligations per service, so that a custodian, a trading platform and an advisor each have a specific set; the fourth deals with acquisitions of CASPs; the fifth defines a significant CASP. For a firm deciding whether and how to operate in the Union, the practical questions are three: does it need an authorisation, how much capital must it hold, and what does it owe its clients.

The source is the consolidated text of 9 January 2024. Article numbers refer to MiCA unless another act is named.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The ten services and who may provide them

Article 3(1)(16) lists ten crypto-asset services, each with its own definition:

- **custody and administration** of crypto-assets on behalf of clients: safekeeping or controlling crypto-assets, or the means of access to them, which the text specifies "where applicable in the form of private cryptographic keys";
- **operation of a trading platform**: managing a multilateral system that brings together third-party buying and selling interests so as to result in a contract;
- **exchange of crypto-assets for funds** and **exchange for other crypto-assets**: concluding purchase or sale contracts with clients using proprietary capital, that is, dealing as principal;
- **execution of orders** on behalf of clients;
- **placing** of crypto-assets: marketing them to purchasers on behalf of an offeror;
- **reception and transmission of orders** to a third party for execution;
- **advice**: personalised recommendations on crypto-assets or crypto-asset services;
- **portfolio management**: discretionary management of client portfolios that include crypto-assets;
- **transfer services**: transferring crypto-assets from one distributed-ledger address or account to another on behalf of a client.

The custody definition is the one that catches technology providers. A wallet application that holds no keys and cannot move a client's assets is not providing custody; one that holds a key share sufficient to move them, or that controls the means of access, is. The transfer-service definition likewise depends on the provider acting on the client's behalf, which a pure software tool does not.

Article 59(1) then states the rule: nobody may provide crypto-asset services in the Union unless it is either **a legal person or other undertaking authorised as a CASP under Article 63**, or **one of the financial entities allowed to do so under Article 60**. Article 59(2) adds three anchors for an authorised CASP: a registered office in a Member State where it carries out at least part of its services, its place of effective management in the Union, and at least one director resident in the Union. A letterbox entity does not qualify.

### Financial entities: notification instead of authorisation

Article 60 lets seven kinds of already-regulated entity provide crypto-asset services on the strength of their existing licence, after notifying their competent authority at least **40 working days** before starting. The scope of what each may do is mapped onto its existing permissions:

- a **credit institution** may provide all ten services;
- a **central securities depository** may provide custody and administration;
- an **investment firm** may provide the services equivalent to the [MiFID II](https://eur-lex.europa.eu/eli/dir/2014/65/oj) services it is authorised for, on a table of equivalences in Article 60(3): custody maps to the safekeeping ancillary service, operating a trading platform to operating an MTF or OTF, exchange to dealing on own account, and so on;
- a **market operator** may operate a trading platform;
- an **electronic money institution** may provide custody and transfer services, but only for the e-money tokens it issues;
- a **UCITS management company** or an **alternative investment fund manager** may provide reception and transmission of orders, advice and portfolio management.

The notification (Article 60(7)) is not trivial: it contains a programme of operations, the AML control framework, the business continuity plan, the ICT and security documentation, the segregation procedure, and the service-specific policies. The authority checks the notification for completeness within 20 working days, and the entity may not start while it is incomplete (Article 60(8)). Once notified, these entities are subject to the conduct obligations of Chapters 2 and 3 like any CASP, but not to the authorisation, withdrawal, prudential-safeguard and acquisition articles (Article 60(10)), since their own sectoral regime covers those.

### Reverse solicitation

Article 61 is the only opening for third-country firms. Where a client established in the Union initiates, "at its own exclusive initiative", a crypto-asset service from a third-country firm, the authorisation requirement does not apply to that service to that client.

Two subparagraphs close the gap that this would otherwise create. Any solicitation, promotion or advertising in the Union by the firm or anyone acting for it, by whatever means, removes the exemption, and so does any contractual clause or disclaimer purporting to deem the service client-initiated. Article 61(2) adds that the exemption does not allow the firm to market new types of crypto-assets or services to that client, and ESMA issues guidelines on where solicitation begins.

## Authorisation (Articles 62 to 65)

### The application

The application goes to the competent authority of the home Member State, which is the Member State of the registered office. Article 62(2) lists fifteen items, and they define the compliance programme a CASP will need to run:

- identity, legal entity identifier, articles of association and a **programme of operations** listing the services and where and how they will be marketed;
- proof that the **prudential safeguards** of Article 67 are met;
- a description of the **governance arrangements**;
- proof that the management body and any holder of a qualifying holding (10 % or more) are of good repute and, for the management body, have the appropriate knowledge, skills and experience;
- the **internal control mechanisms**, including the anti-money-laundering framework under [Directive (EU) 2015/849](https://eur-lex.europa.eu/eli/dir/2015/849/oj) and the risk-assessment framework;
- the **ICT systems and security arrangements**, with a non-technical description;
- the **segregation procedure** for clients' crypto-assets and funds;
- the **complaints-handling** procedure;
- service-specific documents: the custody policy, the operating rules and market-abuse detection systems of a trading platform, the non-discriminatory commercial policy and pricing method of an exchange, the execution policy, the suitability procedure for advice and portfolio management, the transfer-service procedures, and proof of the insurance policy or comparable guarantee where one is used to meet the capital requirement;
- the **business continuity** plan.

### The procedure

Article 63 fixes the clock. The authority acknowledges receipt within five working days, checks completeness within **25 working days** and sets a deadline for missing items, and decides within **40 working days** of a complete application, suspended at most once for 20 working days. Refusal grounds include an unsuitable management body or shareholders, failure to meet Title V, and third-country close links that would obstruct supervision. The authorisation lists the services covered; adding a service requires an extension processed on the same terms (Article 59(8)). Every authorisation is communicated to ESMA for the public register under Article 109.

### Withdrawal

Article 64 obliges the authority to withdraw the authorisation where the CASP has not used it within twelve months, has expressly renounced it, has not provided services for nine consecutive months, obtained it by irregular means, or no longer meets its conditions and has not remedied that within the time set. Withdrawal is also mandatory where the CASP lacks effective anti-money-laundering systems or has seriously infringed the Regulation, and the authority must consult the authorities of host Member States before withdrawing.

### Passport

An authorisation is valid throughout the Union (Article 59(7)). To operate in another Member State the CASP submits to its home authority a list of the target Member States, the services, the start date and its other activities; the home authority forwards this within ten working days to the host authorities, ESMA and EBA, and the CASP may begin from the date of that forwarding or, at the latest, fifteen calendar days after its submission (Article 65). No host-state authorisation, registration or fee is involved.

![CASP authorisation sequence: application, acknowledgement in 5 working days, completeness check in 25, decision in 40, ESMA register entry, then the passport notification forwarded to host authorities]({{site.url_complet}}/assets/article/regulation/mica/mica-casp-authorisation-passport-sequence.png)

## Obligations of every CASP (Chapter 2)

### Conduct and disclosure (Article 66)

A CASP acts honestly, fairly and professionally in the best interests of its clients, provides information that is fair, clear and not misleading, identifies marketing as such, and does not mislead clients "in relation to the real or perceived advantages of any crypto-assets". It warns clients of the risks of crypto-asset transactions and, when it operates a platform, exchanges, advises or manages portfolios, gives clients hyperlinks to the white papers of the crypto-assets concerned.

Two publication duties are specific to MiCA:

- the CASP's policies on **pricing, costs and fees** must be public in a prominent place on its website;
- so must information on the **principal adverse climate and environmental impacts** of the consensus mechanism of each crypto-asset it services, which may be taken from the white papers.

### Prudential safeguards (Article 67 and Annex IV)

A CASP holds at all times prudential safeguards equal to at least the **higher** of:

- the minimum capital of its class under Annex IV; or
- **one quarter of the fixed overheads** of the preceding year, reviewed annually, with projected overheads used in the first year.

The three classes are cumulative: each includes the services of the class below.

| Class | Services | Minimum capital |
|:---:|---|---:|
| 1 | Execution of orders; placing; transfer services; reception and transmission of orders; advice; portfolio management | **EUR 50 000** |
| 2 | Class 1 services plus custody and administration; exchange for funds; exchange for other crypto-assets | **EUR 125 000** |
| 3 | Class 2 services plus operation of a trading platform | **EUR 150 000** |

The safeguards may be held as **own funds**, meaning Common Equity Tier 1 items under the [Capital Requirements Regulation](https://eur-lex.europa.eu/eli/reg/2013/575/oj) after full deductions, or as an **insurance policy** or comparable guarantee covering the territories where services are provided, or a combination.

The insurance must have an initial term of at least one year, a cancellation notice of at least 90 days, and be issued by an authorised insurer that is a third party. It must cover at minimum:

- loss of documents and misrepresentation;
- breaches of legal and conduct obligations, and failure of the conflicts-of-interest procedures;
- business disruption and system failures;
- gross negligence in safeguarding client assets, where the business model involves it;
- the CASP's custody liability under Article 75(8).

The figures are low by the standards of banking regulation, and deliberately so; the protection of clients is meant to come from segregation and liability rather than from the CASP's balance sheet.

### Governance and organisation (Articles 68, 69, 73, 74)

The management body must be of good repute, collectively competent and able to commit sufficient time; qualifying shareholders must be of good repute, and the authority may act against shareholders whose influence would prejudice sound management.

The CASP employs staff with the necessary skills, keeps its systems and security access protocols to Union standards, and maintains business continuity. It keeps records of all services, orders and transactions for **five years**, or seven if the authority asks, and its ICT systems must meet the digital operational resilience requirements of [Regulation (EU) 2022/2554](https://eur-lex.europa.eu/eli/reg/2022/2554/oj) (DORA), which Article 68(7) applies by reference. Changes to the management body and to the conditions of authorisation are notified to the authority (Article 69).

Outsourcing (Article 73) does not delegate responsibility: the CASP remains fully liable, must keep the expertise to supervise the outsourced function, and must be able to terminate the arrangement without harming clients. Custodians, platform operators, exchanges, executors and placers must have an **orderly wind-down plan** demonstrating that they can cease activity without undue economic harm to clients (Article 74).

### Segregation of client assets (Article 70)

Article 70 is the article that answers "what happens to my assets if the exchange fails", and it applies to every CASP that holds client crypto-assets, means of access or funds:

- **Crypto-assets.** The CASP makes adequate arrangements to safeguard clients' ownership rights, especially in the event of its own insolvency, and to prevent the use of clients' crypto-assets for its own account (Article 70(1)).
- **Funds.** Client funds other than e-money tokens are placed with a credit institution or a central bank by the end of the business day following receipt, in an account separately identifiable from the CASP's own accounts (Article 70(2) and (3)).
- **Payment services** related to the crypto-asset service may be provided by the CASP or a third party only under a [PSD2](https://eur-lex.europa.eu/eli/dir/2015/2366/oj) authorisation, and clients are told who provides them (Article 70(4)).

Credit institutions, e-money institutions and payment institutions are exempt from the fund-safeguarding paragraphs because their own regimes cover them (Article 70(5)). The crypto-asset paragraph is expanded, for custodians, by the segregation and liability rules of Article 75.

### Complaints and conflicts (Articles 71 and 72)

Complaints are handled under a published procedure, free of charge for clients, with records kept and an answer given in a reasonable time. Conflicts of interest between the CASP and its shareholders, management, employees, clients, or between clients, are identified, prevented, managed and disclosed, with the disclosure prominent on the website and specific enough for the client to decide whether to use the service.

## Obligations per service (Chapter 3)

### Custody and administration (Article 75)

The custody article is the most detailed of the chapter and the one with the most direct consequence for how a custodian is built.

- **Agreement.** A written agreement with each client specifying the parties, the service, the custody policy, the means of communication including the client's authentication system, the security systems, the fees, and the applicable law (Article 75(1)).
- **Register of positions.** A register opened in the name of each client, recording each client's rights and every movement following the client's instructions, so that any movement of the crypto-assets is evidenced by a transaction in the register (Article 75(2)).
- **Custody policy.** Internal rules to minimise the risk of loss "due to fraud, cyber threats or negligence", with a summary available to clients (Article 75(3)).
- **Rights and statements.** The custodian facilitates the exercise of rights attached to the crypto-assets and passes on any event requiring a response; it provides a statement of position at least every three months, in electronic form (Article 75(4) and (5)).
- **Return.** Procedures to return the crypto-assets, or the means of access, to clients as soon as possible (Article 75(6)).
- **Segregation.** Client holdings are segregated from the custodian's own holdings and the means of access are clearly identified as belonging to clients. On the distributed ledger, clients' crypto-assets are held **separately from the custodian's own**, and the holdings are **legally segregated** from the custodian's estate so that its creditors have no recourse to them, in particular in insolvency, and **operationally segregated** as well (Article 75(7)).
- **Liability.** The custodian is liable to clients for the loss of crypto-assets or of the means of access "as a result of an incident that is attributable to them", **capped at the market value at the time of the loss**. Incidents not attributable to the custodian are those it shows occurred independently of its service or operations, "such as a problem inherent in the operation of the distributed ledger that the crypto-asset service provider does not control" (Article 75(8)).
- **Sub-custody.** A custodian that uses another custodian may only use one authorised under Article 59, and must tell its clients (Article 75(9)).

The segregation paragraph is the one that dictates how a custodian is built. Holding client assets and proprietary assets in the same on-chain address is not permitted; an omnibus client address is, provided the register of positions reconciles it to each client. The liability paragraph means that a key-management failure, an insider theft or a compromised signing server is the custodian's loss up to the market value of what was taken, while a consensus failure or a reorganisation of the underlying chain is not.

![MiCA custodian model: client assets on separate on-chain addresses reconciled to a per-client register, insolvency-remote from the custodian, with attributable losses compensated up to market value]({{site.url_complet}}/assets/article/regulation/mica/mica-custody-segregation-concept.png)

### Operation of a trading platform (Article 76)

The trading-platform article reads as a condensed venue rulebook.

- **Operating rules** that set the admission process, including customer due diligence on the applicant proportionate to its money-laundering risk; any exclusion categories; the admission policies and fees; objective and non-discriminatory participation criteria; requirements for orderly trading and efficient execution; conditions for remaining tradable, including liquidity thresholds and periodic disclosure; the conditions for suspension; and settlement procedures. The rules must state that a crypto-asset is **not admitted where no white paper has been published** in the cases where one is required (Article 76(1)).
- **Suitability assessment** of each crypto-asset before admission, looking at the reliability of the technical solution and the potential association with illicit activity, in the light of the track record of the issuer and its development team (Article 76(2)).
- **No anonymised crypto-assets.** The rules must prevent the admission of crypto-assets with an in-built anonymisation function unless the holders and their transaction history can be identified by the operator (Article 76(3)).
- **No dealing on own account** on the platform the operator runs, including where it also provides exchange services (Article 76(5)). Matched principal trading is permitted only with the client's consent and under the authority's monitoring (Article 76(6)).
- **Resilient systems** with capacity for peak volumes, orderly trading under stress, rejection of erroneous orders, testing, business continuity and market-abuse detection (Article 76(7)); the operator reports market abuse it identifies to the authority (Article 76(8)).
- **Transparency.** Bid and ask prices and the depth of interest are published continuously during trading hours; price, volume and time of executed transactions are published as close to real time as technically possible; both are made available free of charge fifteen minutes after publication in machine-readable form and kept for two years (Article 76(9) to (11)).
- **Settlement** of a transaction is initiated on the distributed ledger within **24 hours** of execution or, for off-ledger settlement, by the close of the day (Article 76(12)).
- **Fees** are transparent, fair and non-discriminatory and do not create incentives to place, modify or cancel orders in a way that contributes to disorderly trading or market abuse (Article 76(13)).
- **Records** of all orders are kept at the authority's disposal for five years, or the authority is given access to the order book (Article 76(15)).

### Exchange (Article 77)

A CASP dealing as principal establishes a non-discriminatory commercial policy stating which clients it deals with and on what conditions, publishes a firm price or a pricing method together with any limit on the amount, executes orders at the price displayed when the order becomes final, tells clients when an order is final, and publishes its transaction volumes and prices.

### Execution, placing, and reception and transmission (Articles 78 to 80)

An executing CASP obtains the best possible result for the client on price, costs, speed, likelihood of execution and settlement, size, nature, custody conditions and any other relevant consideration, under a published execution policy, and may not receive remuneration for routing orders to a particular venue. A placing CASP discloses to the offeror the type of placement, the fees, the timing, process and price, and the targeted purchasers, and manages the conflicts that arise from placing with its own clients. A CASP receiving and transmitting orders transmits them promptly and may not be paid for routing them to a particular platform or CASP.

### Advice and portfolio management (Article 81)

An advisor or portfolio manager assesses whether the service or the crypto-asset is **suitable** for the client, considering knowledge and experience, investment objectives including risk tolerance, and financial situation including the ability to bear losses, and reviews that assessment at least every two years. Around that test the article adds:

- **Independence.** Advice is presented as independent or not; independent advice must be based on a sufficient range of crypto-assets and may not be remunerated by third-party inducements.
- **Warnings.** Where the client provides no information, or the service is unsuitable, the CASP warns the client and does not recommend it.
- **Reporting.** Portfolio managers report periodically on the activities carried out and the portfolio's performance.
- **Competence and costs.** Staff giving advice must have the necessary knowledge and competence, and clients are told the costs, including those of advice and of the crypto-assets recommended.

### Transfer services (Article 82)

A transfer-service provider concludes an agreement specifying the parties, the modalities of the service, the security systems, the fees and the applicable law, and ESMA issues guidelines on the procedures and policies for such providers.

## Acquisitions and significant CASPs (Chapters 4 and 5)

Anyone intending to acquire a qualifying holding in a CASP, or to increase one so as to reach or exceed 20 %, 30 % or 50 %, notifies the competent authority, which assesses the proposed acquirer within 60 working days on reputation, the suitability of the proposed management, financial soundness, the CASP's continued compliance, and money-laundering risk (Articles 83 and 84). Reductions below those thresholds are also notified.

A CASP is **significant** where it has at least **15 million active users** in the Union on average in a calendar year, calculated as the average of the daily number of active users over the previous year (Article 85(1)). It notifies its authority within two months of reaching the threshold, the authority informs ESMA, and the home authorities give ESMA's Board of Supervisors annual updates on authorisations, withdrawals and passporting concerning significant CASPs. Unlike a significant stablecoin issuer, a significant CASP is not moved to European supervision; it stays with its national authority under closer coordination.

## Transition

Article 143(3) allows a CASP that was providing its services in accordance with national law before 30 December 2024 to continue until **1 July 2026** or until it is granted or refused a MiCA authorisation, whichever is sooner. Member States could shorten or waive that period, and may run a simplified procedure for such applicants between 30 December 2024 and 1 July 2026, provided Chapters 2 and 3 of Title V are complied with before the authorisation is granted (Article 143(6)). The transitional right covers existing services in the home Member State only; the passport requires the MiCA authorisation.

## Conclusion

Title V converts a service that used to be a matter of national registration, or of no registration at all, into a licensed activity with a Union-wide passport and a fixed set of client protections.

- **Ten defined services, one authorisation or one notification.** A firm that provides any of them to EU clients is a CASP and needs a MiCA authorisation under Article 63, unless it is a bank, investment firm, CSD, market operator, e-money institution or fund manager notifying under Article 60. Reverse solicitation is the only third-country route, and any solicitation closes it.
- **Substance in the Union.** A registered office in a Member State, effective management in the Union and at least one EU-resident director.
- **Capital is a floor, not the protection.** EUR 50 000, 125 000 or 150 000 by class, or a quarter of fixed overheads if higher, held as CET1 or insurance.
- **Client assets are segregated and insolvency-remote.** Funds go to a bank by the next business day; crypto-assets are held on separate addresses, reconciled in a per-client register, and legally outside the custodian's estate.
- **Custodians are liable for attributable losses** up to market value; losses inherent in the ledger are not theirs.
- **A trading platform cannot trade against its clients**, cannot list anonymised tokens or tokens without a required white paper, must publish pre- and post-trade data, and must settle on-ledger within 24 hours.
- **Advice and portfolio management require a suitability test**, as in securities law.
- **Existing firms had until 1 July 2026** at the latest to obtain the authorisation.

![Mindmap of Title V covering the ten services, entry routes, authorisation and passport, capital classes, client-asset segregation, custody, trading-platform and other service rules, and significant CASPs]({{site.url_complet}}/assets/article/regulation/mica/2026-09-17-mica-casp-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Crypto-asset service provider (CASP)** | A legal person or undertaking whose business is providing one or more of the ten crypto-asset services to clients on a professional basis, allowed to do so under Article 59. |
| **Custody and administration** | Safekeeping or controlling, on behalf of clients, crypto-assets or the means of access to them, where applicable in the form of private cryptographic keys. |
| **Trading platform for crypto-assets** | A multilateral system that brings together third-party buying and selling interests in crypto-assets so as to result in a contract, operated under Article 76. |
| **Matched principal trading** | A transaction in which the facilitator interposes itself between buyer and seller so that it is never exposed to market risk, permitted on a platform only with client consent. |
| **Prudential safeguards** | The own funds or insurance a CASP must hold at all times, equal to the higher of the Annex IV minimum capital and one quarter of fixed overheads. |
| **Register of positions** | The per-client record a custodian keeps of each client's rights to crypto-assets and of every movement made on the client's instructions. |
| **Means of access** | The private keys or other credentials that allow crypto-assets to be moved; their loss triggers the custodian's liability in the same way as loss of the assets. |
| **Reverse solicitation** | The Article 61 exemption for services a third-country firm provides at the exclusive initiative of an EU client, lost on any solicitation. |
| **Passport** | The right of an authorised CASP to provide its services in every Member State after a notification forwarded by its home authority under Article 65. |
| **Significant CASP** | A CASP with at least 15 million active users in the Union on average over a calendar year, subject to enhanced reporting to ESMA. |

### Requirements Checklist

Title V is a licensing regime with ongoing obligations. The rows below transcribe them by article so that an applicant, or a client assessing a provider, can check a firm against the text.

#### Articles 59 to 61 — Who may provide services

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 59(1) | The provider is authorised as a CASP under Art. 63, or is a financial entity allowed under Art. 60. |
| ☐ | 59(2) | Registered office in a Member State where at least part of the services are carried out; effective management in the Union; at least one EU-resident director. |
| ☐ | 59(6), (8) | The authorisation specifies the services covered; an extension for additional services is requested and processed under Art. 63. |
| ☐ | 60(1)–(6) | A credit institution, CSD, investment firm, market operator, e-money institution, UCITS manager or AIFM notifies its authority at least 40 working days before starting, within the scope of its existing licence. |
| ☐ | 60(7) | The notification includes the programme of operations, AML and business continuity frameworks, ICT documentation, segregation procedure and service-specific policies. |
| ☐ | 60(8), (10) | Completeness checked within 20 working days; no services while incomplete; Arts 62, 63, 64, 67, 83 and 84 do not apply to notifying entities. |
| ☐ | 61(1) | A third-country firm serves an EU client without authorisation only at the client's own exclusive initiative; any solicitation, promotion or advertising in the Union removes the exemption, whatever the contract says. |
| ☐ | 61(2) | The exemption does not allow marketing of new types of crypto-assets or services to that client. |

#### Articles 62 to 65 — Authorisation, withdrawal and passport

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 62(2) | The application contains the programme of operations, proof of prudential safeguards, governance, suitability of management and qualifying shareholders, internal controls and AML framework, ICT and security documentation, segregation procedure, complaints procedure, service-specific policies and business continuity plan. |
| ☐ | 63(1)–(2) | Receipt acknowledged within 5 working days; completeness assessed within 25 working days. |
| ☐ | 63(9) | Reasoned decision within 40 working days of a complete application, notified within 5 working days. |
| ☐ | 64(1) | Authorisation withdrawn if unused for 12 months, renounced, no services for 9 consecutive months, obtained irregularly, or conditions no longer met without remedy. |
| ☐ | 65(1)–(3) | Cross-border services after notification of the target Member States, services, start date and other activities to the home authority, forwarded within 10 working days; services may start after that or 15 calendar days after submission. |

#### Articles 66 to 74 — Obligations of all CASPs

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 66(1)–(3) | Act honestly, fairly and professionally; information fair, clear and not misleading; marketing identified; risk warnings; hyperlinks to white papers. |
| ☐ | 66(4)–(5) | Pricing, cost and fee policies, and climate and environmental impact information per crypto-asset, published prominently on the website. |
| ☐ | 67(1) | Prudential safeguards at all times at least the higher of the Annex IV minimum and one quarter of last year's fixed overheads. |
| ☐ | Annex IV | Class 1 EUR 50 000; Class 2 EUR 125 000; Class 3 EUR 150 000. |
| ☐ | 67(4)–(6) | Held as CET1 own funds, or an insurance policy or comparable guarantee of at least one year with 90 days' notice from a third-party authorised insurer, covering the listed risks including Art. 75(8) liability. |
| ☐ | 68(1)–(3) | Management body and qualifying shareholders of good repute; management collectively competent and able to commit sufficient time. |
| ☐ | 68(4)–(9) | Competent staff; systems and security to Union standards; business continuity; records of services, orders and transactions kept 5 years (7 on request); ICT under Regulation (EU) 2022/2554. |
| ☐ | 69 | Changes to the management body and to the conditions of authorisation notified to the authority. |
| ☐ | 70(1) | Adequate arrangements safeguard clients' ownership rights in crypto-assets, in particular in insolvency; no use of clients' crypto-assets for own account. |
| ☐ | 70(2)–(3) | Clients' funds other than EMTs placed with a credit institution or central bank by the end of the next business day, in separately identifiable accounts. |
| ☐ | 70(4) | Payment services only under a PSD2 authorisation, with clients informed who provides them. |
| ☐ | 71 | Published complaints procedure, free of charge, with records and timely answers. |
| ☐ | 72 | Conflicts of interest identified, prevented, managed and disclosed prominently on the website. |
| ☐ | 73 | Outsourcing does not delegate responsibility; the CASP keeps the expertise to supervise it and can terminate it without harming clients. |
| ☐ | 74 | Custodians, platforms, exchanges, executors and placers maintain an orderly wind-down plan. |

#### Article 75 — Custody and administration

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 75(1) | Written agreement covering the parties, the service, custody policy, communication and authentication, security systems, fees and applicable law. |
| ☐ | 75(2) | Register of positions per client recording rights and every instructed movement. |
| ☐ | 75(3) | Custody policy minimising loss from fraud, cyber threats or negligence; summary available to clients. |
| ☐ | 75(4)–(5) | Exercise of rights facilitated; events requiring a response passed on; statement of position at least every three months in electronic form. |
| ☐ | 75(6) | Procedures to return crypto-assets or means of access as soon as possible. |
| ☐ | 75(7) | Client holdings segregated from own holdings and held separately on the ledger; legally and operationally segregated from the custodian's estate. |
| ☐ | 75(8) | Liability for loss of crypto-assets or means of access from attributable incidents, capped at market value at the time of loss. |
| ☐ | 75(9) | Sub-custody only with CASPs authorised under Art. 59, and clients informed. |

#### Article 76 — Operation of a trading platform

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 76(1) | Operating rules on admission (with due diligence), exclusions, fees, participation, orderly trading, continued tradability, suspension and settlement; no admission without a required white paper. |
| ☐ | 76(2) | Suitability of each crypto-asset assessed before admission: technical reliability, illicit-activity risk, track record of issuer and developers. |
| ☐ | 76(3) | No admission of crypto-assets with an in-built anonymisation function unless holders and history can be identified. |
| ☐ | 76(5)–(6) | No dealing on own account on the platform; matched principal trading only with client consent and under supervision. |
| ☐ | 76(7)–(8) | Resilient, tested trading systems with capacity, stress handling, erroneous-order rejection, continuity and market-abuse detection; abuse reported to the authority. |
| ☐ | 76(9)–(11) | Pre-trade quotes and depth, and post-trade price, volume and time, published continuously and near real time; free after 15 minutes in machine-readable form for two years. |
| ☐ | 76(12) | Final settlement initiated on the ledger within 24 hours of execution (or by close of day off-ledger). |
| ☐ | 76(13) | Fee structure transparent, fair, non-discriminatory and not incentivising disorderly trading or abuse. |
| ☐ | 76(15) | Order data kept 5 years or order-book access given to the authority. |

#### Articles 77 to 85 — Other services, acquisitions, significance

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 77 | Exchange: non-discriminatory commercial policy; firm price or pricing method and limits published; execution at the displayed price when final; transaction data published. |
| ☐ | 78 | Execution: best possible result under a published execution policy; no remuneration for routing to a venue. |
| ☐ | 79 | Placing: disclosure to the offeror of placement type, fees, timing, process, price and targeted purchasers; conflicts managed. |
| ☐ | 80 | Reception and transmission: prompt transmission; no remuneration for routing to a particular platform or CASP. |
| ☐ | 81(1) | Advice and portfolio management: suitability assessed on knowledge, experience, objectives, risk tolerance and ability to bear losses. |
| ☐ | 81(2)–(3) | Advice declared independent or not; independent advice covers a sufficient range and takes no third-party inducements. |
| ☐ | 81 | Warnings where information is missing or the service unsuitable; periodic portfolio reports; competent staff; costs disclosed. |
| ☐ | 82 | Transfer services: agreement covering parties, modalities, security systems, fees and applicable law. |
| ☐ | 83–84 | Acquisitions reaching 20 %, 30 % or 50 % of a CASP notified and assessed within 60 working days. |
| ☐ | 85 | A CASP with at least 15 million active EU users on average notifies its authority within two months; the authority informs ESMA. |

## Frequently Asked Questions

**Q: Does a non-custodial wallet application need a CASP authorisation?**

Not for the wallet itself. Custody and administration is defined in Article 3(1)(17) as safekeeping or controlling crypto-assets or the means of access to them on behalf of clients, and a provider that never holds keys or key shares capable of moving the assets does not control the means of access. The analysis changes if the provider holds a share of a multi-party key sufficient to sign, can freeze or recover assets, or executes transfers on the user's behalf, which would be custody or transfer services. Article 4(5) also exempts custody and transfer of tokens whose offer is outside Title II, unless the token is listed or otherwise offered.

**Q: How much capital does an exchange that also holds client assets need?**

Operating a trading platform puts the firm in Class 3 of Annex IV, so the minimum is EUR 150 000, which also covers custody and exchange. Article 67(1) requires the higher of that minimum and one quarter of the preceding year's fixed overheads, so for any firm of size the overheads figure governs. The safeguards may be held as CET1 own funds or as a qualifying insurance policy, or a mix.

**Q: What does "legally segregated" mean for a custodian, and what does it change in practice?**

Article 75(7) requires that the crypto-assets held in custody be legally segregated from the custodian's estate, so that its creditors have no recourse to them, in particular in insolvency, and that clients' crypto-assets be held on the distributed ledger separately from the custodian's own.

In practice the custodian cannot pool client and proprietary assets in one address, must maintain a per-client register of positions that reconciles to the on-chain holdings, and must document the arrangement under the applicable national insolvency law so that a liquidator returns the assets to clients rather than distributing them to creditors. Article 70(1) imposes the same aim on every CASP that holds client assets, custodian or not.

**Q: A custodian loses client assets because a validator set on the underlying chain finalised a malicious fork. Is the custodian liable?**

Under Article 75(8) the custodian is liable for loss resulting from an incident attributable to it, capped at the market value of the crypto-asset at the time of the loss. An incident is not attributable where the custodian demonstrates that it occurred independently of its service and operations, and the article gives as its example "a problem inherent in the operation of the distributed ledger that the crypto-asset service provider does not control". A consensus failure of the chain is that example. A compromise of the custodian's signing infrastructure, by contrast, is attributable, and the insurance policy used under Article 67 must cover that liability.

**Q: Can a trading platform run a market-making desk on its own venue?**

No. Article 76(5) prohibits a platform operator from dealing on own account on the platform it operates, including where it also provides exchange services. The only permitted principal activity is matched principal trading under Article 76(6), where the operator interposes itself between two client orders without market risk, and only with the client's consent and under the competent authority's monitoring. A group may run a separate exchange service under Article 77, but not on its own order book.

**Q: Combining the entry routes: a non-EU exchange has EU users who found it themselves, an EU-licensed investment firm subsidiary, and plans to launch a euro stablecoin. What does each activity require?**

Each activity has its own route:

- **The non-EU exchange** may rely on Article 61 only for clients who approached it at their own exclusive initiative, and only until it markets anything to them or to the Union. At that point it needs a CASP authorisation, with a registered office, effective management and a director in the Union.
- **The investment-firm subsidiary** may provide, after a 40-working-day notification under Article 60(3), the crypto-asset services equivalent to its MiFID II permissions, for example custody if it holds the safekeeping ancillary service and platform operation if it is authorised for an MTF. Services outside its MiFID II permissions require an extension or a CASP authorisation.
- **The euro stablecoin** is an e-money token under Title IV, which neither the exchange nor the investment firm may issue. That requires a credit institution or an electronic money institution, and the group's CASPs may then not pay interest on it (Article 50), as the [stablecoin article]({{site.url_complet}}/2026/09/17/mica-stablecoins-asset-referenced-tokens-e-money-tokens/) explains.

## References

### Legal texts

- [Regulation (EU) 2023/1114 on markets in crypto-assets (MiCA)](https://eur-lex.europa.eu/eli/reg/2023/1114/oj), Title V, Articles 59 to 85, and Annex IV
- [Consolidated text of Regulation (EU) 2023/1114 as of 9 January 2024](https://eur-lex.europa.eu/eli/reg/2023/1114/2024-01-09), EUR-Lex
- [Directive 2014/65/EU (MiFID II)](https://eur-lex.europa.eu/eli/dir/2014/65/oj), for the equivalence table of Article 60(3)
- [Regulation (EU) No 575/2013 (Capital Requirements Regulation)](https://eur-lex.europa.eu/eli/reg/2013/575/oj), for Common Equity Tier 1 own funds
- [Regulation (EU) 2022/2554 (DORA)](https://eur-lex.europa.eu/eli/reg/2022/2554/oj), applied to CASPs' ICT systems by Article 68(7)
- [Directive (EU) 2015/2366 (PSD2)](https://eur-lex.europa.eu/eli/dir/2015/2366/oj), for payment services provided alongside crypto-asset services
- [Directive (EU) 2015/849 (Anti-Money Laundering Directive)](https://eur-lex.europa.eu/eli/dir/2015/849/oj), whose controls form part of the application

### Supervisory authorities

- [ESMA — Markets in Crypto-Assets Regulation (MiCA)](https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/markets-crypto-assets-regulation-mica), authorisation templates, guidelines on reverse solicitation and suitability, and the CASP register

### Related articles

- [Security of Cryptocurrency Exchanges - Overview]({{site.url_complet}}/2025/11/06/crypto-exchange-security-overview/)
- [Crypto Wallets Explained - Types, Risks, and How to select it]({{site.url_complet}}/2024/10/08/crypto-wallet-introduction/)
- [Blockchain wallets on AWS with Fireblocks and Circle]({{site.url_complet}}/2025/07/29/aws-blockchain-wallets/)
- [Hyperliquid's Onchain Order Book - Matching, Ordering, and How It Differs from a CEX and from GMX]({{site.url_complet}}/2026/09/02/hyperliquid-order-book-matching-engine/)
