---
layout: post
title: "Stablecoins Under MiCA — Asset-Referenced Tokens and E-Money Tokens (Titles III and IV)"
date:   2026-09-17
lang: en
locale: en-GB
categories: regulation blockchain defi
tags: mica regulation eu stablecoin crypto-assets compliance reserve
series: mica
series_order: 3
description: "How MiCA regulates stablecoins: who may issue an ART or EMT, the reserve, own-funds and redemption rules, the interest ban and when a token becomes significant."
image: /assets/article/regulation/mica/2026-09-17-mica-stablecoins-mindmap.png
isMath: false
---

[MiCA](https://eur-lex.europa.eu/eli/reg/2023/1114/oj), Regulation (EU) 2023/1114, is the EU's framework for crypto-assets outside existing financial law, and its [first article in this series]({{site.url_complet}}/2026/09/17/mica-explained-scope-token-categories-timeline/) sets out how it sorts a token into one of three categories. Two of those categories are stablecoins, and they received the heaviest regime in the text and the earliest application date: Titles III and IV have applied since 30 June 2024, six months before the rest of the Regulation.

The Regulation does not use the word "stablecoin". It distinguishes an **e-money token** (EMT), which references one official currency, from an **asset-referenced token** (ART), which references anything else that is meant to hold value: a basket of currencies, a commodity, other crypto-assets or a combination. The distinction is not cosmetic. An EMT is treated as electronic money, may only be issued by a bank or an e-money institution, and must be redeemable at par. An ART needs its own authorisation, a segregated reserve, prudential capital and a policy for redeeming at the market value of what it references. Both are forbidden from paying interest, and both become "significant" above certain sizes, at which point supervision moves from the national authority to the European Banking Authority.

This article walks through the two titles in the order a prospective issuer would meet them: who may issue, what the white paper and the authorisation require, how the reserve and redemption work, what the capital rules are, and what changes when a token is classified as significant. Article numbers refer to MiCA unless another act is named; the source is the consolidated text of 9 January 2024.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Two categories, two entry tickets

The threshold question for any stablecoin is which title applies, and the answer follows from the reference asset.

| | Asset-referenced token (Title III) | E-money token (Title IV) |
|---|---|---|
| Reference | Another value or right, or a combination, including one or more official currencies (Art. 3(1)(6)) | One official currency (Art. 3(1)(7)) |
| Who may issue | An EU legal person authorised under Article 21, or a credit institution that complies with Article 17 | A credit institution or an electronic money institution (Art. 48(1)) |
| Entry act | Authorisation by the home competent authority, which also approves the white paper | Notification of the white paper to the competent authority; no separate MiCA authorisation |
| Legal nature | A crypto-asset with a redemption claim at market value of the reference | Deemed electronic money (Art. 48(2)); claim at par |
| Backing | A reserve of assets under Articles 36 to 38 | Funds safeguarded under the E-Money Directive, with the Article 54 investment limits |
| Interest | Prohibited (Art. 40) | Prohibited (Art. 50) |
| Small-issuer relief | Below EUR 5 000 000 average outstanding, or qualified investors only, no authorisation (Art. 16(2)) | E-money institutions exempt under Article 9(1) of the E-Money Directive are exempt from Article 48(1) (Art. 48(4)) |

The ART definition is residual, so a token referencing exactly one official currency is always an EMT, whatever mechanism stabilises it. A euro token that is over-collateralised by crypto-assets and stabilised by an algorithm is an EMT, and its issuer must be a bank or an e-money institution that issues at par against funds received. A token that references the euro *and* gold, or the euro and the dollar, is an ART.

In both titles, only the **issuer** may offer the token to the public or seek its admission to trading. Other persons may do so only with the issuer's written consent, and they then take on the marketing and no-interest rules (Articles 16(1) and 48(1), second subparagraphs).

## Asset-referenced tokens: authorisation (Title III, Chapter 1)

### Who is exempt

Article 16(2) removes the authorisation requirement in two cases: where, over a twelve-month period measured at the end of each calendar day, the average outstanding value of the token never exceeds **EUR 5 000 000** and the issuer is not linked to a network of other exempt issuers; and where the offer is addressed solely to qualified investors who alone may hold the token. An exempt issuer still draws up a white paper under Article 19 and notifies it, and any marketing on request, to the competent authority.

### The application

A legal person wishing to issue an ART applies to the competent authority of its home Member State. Article 18(2) lists what the application contains, and the list reads like a licence application in banking rather than a token filing:

- the address and legal entity identifier of the applicant, and its articles of association;
- a programme of operations setting out the business model;
- a **legal opinion** that the token is neither a crypto-asset excluded under Article 2(4) nor an e-money token;
- a detailed description of the governance arrangements required by Article 34;
- where the issuer cooperates with specific CASPs, a description of the internal controls for anti-money-laundering compliance under [Directive (EU) 2015/849](https://eur-lex.europa.eu/eli/dir/2015/849/oj);
- the identity of the management body and proof that its members are of good repute with the appropriate knowledge, skills and experience;
- proof that holders of qualifying holdings (10 % or more) are of good repute;
- the white paper itself, together with the policies and procedures on reserve, custody, redemption, complaints, conflicts of interest and business continuity, and the recovery and redemption plans.

### The assessment and the central-bank veto

The procedure in Articles 20 and 21 involves four institutions and a fixed clock:

- Within **25 working days** the authority confirms the application is complete.
- Within **60 working days** of a complete application it assesses it and prepares a draft decision; requests for missing information suspend the clock, once, for at most 20 working days.
- After the 60 days the draft decision goes to **EBA, ESMA and the ECB**, and to the national central bank where the issuer is in a non-euro Member State or the token references a non-euro Member State currency (Article 20(4)).
- EBA and ESMA may give an opinion within 20 working days on the legal opinion classifying the token. The ECB or central bank gives an opinion within the same period on the risks to financial stability, payment systems, monetary policy transmission and monetary sovereignty (Article 20(5)).
- Within **25 working days** of receiving those opinions the authority takes a reasoned decision (Article 21(1)).

The opinions are non-binding, with one exception that gives central banks a veto: the authority *must* refuse authorisation if the ECB or central bank gives a negative opinion on the grounds of a risk to the smooth operation of payment systems, monetary policy transmission or monetary sovereignty (Article 21(4)). The other refusal grounds in Article 21(2) are the usual ones: an unsuitable management body or shareholders, failure to meet the requirements of Title III, or a business model posing a serious threat to market integrity, financial stability, payment systems, or money-laundering risk.

An authorisation is valid throughout the Union and doubles as approval of the white paper (Articles 16(3) and 21(1)). Credit institutions do not need this authorisation; under Article 17 they instead have the white paper approved by their competent authority and notify at least 90 working days before the first issuance with a programme of operations, a legal opinion and the policies listed above.

![ART authorisation sequence: application to the home authority, completeness in 25 working days, assessment in 60, opinions of EBA, ESMA and the ECB in 20, decision in 25, with a central-bank veto on monetary grounds]({{site.url_complet}}/assets/article/regulation/mica/mica-art-authorisation-sequence.png)

### The white paper for an ART

Article 19 and Annex II set the content: information about the issuer, the token, the offer or admission, the rights and obligations attached to it, the underlying technology, the risks, and, specifically for this category, **the reserve of assets** (Annex II, Part G). Unlike the Title II document, this white paper is approved as part of the authorisation, and modifications go through the authority under Article 25 with a 30-working-day review. The issuer and its management body are liable to holders for misleading content on the same terms as in Title II, and any contractual limitation of that liability is void (Article 26).

### Reporting and the limit on use as money

Two provisions in Chapter 1 exist because the legislator was thinking about a global stablecoin displacing the euro in payments.

Article 22 requires the issuer of any ART with an issue value above **EUR 100 000 000** to report quarterly the number of holders, the value issued and the size of the reserve, the average number and value of transactions per day, and an estimate of how many of those transactions are uses as a **means of exchange** within a single currency area. Transfers to or from the issuer or a CASP for exchange are not counted as means-of-exchange uses.

Article 23 then draws a line. If the estimated quarterly average exceeds **1 million transactions and EUR 200 000 000 per day** as a means of exchange within a single currency area, the issuer must **stop issuing** the token and, within 40 working days, submit a plan to bring usage back under both thresholds, which the authority may modify, for instance by imposing a minimum denomination. Issuance may resume only when the authority has evidence that both figures are below the thresholds again. The article applies to ARTs and, through Article 58, to EMTs not denominated in an EU currency.

## Obligations of the issuer (Title III, Chapter 2)

Chapter 2 lists the ongoing conduct and organisational duties. Most are familiar from other financial regulation, and three are specific to stablecoins.

- **Conduct** (Article 27): act honestly, fairly and professionally, and communicate with holders in a fair, clear and not misleading manner; treat holders equally unless preferential treatment is disclosed.
- **Publication** (Article 28) of the approved white paper, and **marketing** (Article 29) that is identified as such, consistent with the white paper and states that all holders have a right of redemption.
- **Ongoing information** (Article 30): publish on the website, updated at least monthly, the amount of tokens in circulation and the value and composition of the reserve; publish the reserve audit report in full; disclose as soon as possible any event likely to have a significant effect on the token's value or the reserve.
- **Complaints handling** (Article 31), **conflicts of interest** (Article 32) with shareholders, management, employees, holders and outsourced service providers, and **notification of changes to the management body** (Article 33).
- **Governance** (Article 34): a clear organisational structure, risk management and internal controls, fit-and-proper management and shareholders, business continuity, ICT security, and an independent audit of the reserve.

### Own funds (Article 35)

An ART issuer must at all times hold own funds equal to at least the highest of:

- **EUR 350 000**;
- **2 %** of the average amount of the reserve of assets, calculated over the preceding six months at the end of each calendar day, and summed across tokens where the issuer has several;
- **one quarter** of the fixed overheads of the preceding year.

The own funds consist of Common Equity Tier 1 items under the [Capital Requirements Regulation](https://eur-lex.europa.eu/eli/reg/2013/575/oj) (Regulation (EU) No 575/2013) after full deductions. The competent authority may require up to **20 % more** than the 2 % figure where its assessment of the governance, the reserve, the token's use or the quality of risk management shows a higher degree of risk, and may require between 20 % and 40 % more in stress situations. Issuers must also run stress tests, the results of which feed that assessment.

### The reserve of assets (Chapter 3)

Chapter 3 is the substantive core of Title III and the part that distinguishes a MiCA stablecoin from an unregulated one.

**Composition and segregation** (Article 36). The issuer constitutes and maintains a reserve of assets at all times, composed so that the risks of the referenced assets are covered and the liquidity risk of permanent redemption is addressed. The reserve is **legally segregated** from the issuer's estate and from the reserves of any other tokens, so that the issuer's creditors have no recourse to it, in particular in insolvency, and it is **operationally segregated** as well. EBA's technical standards set liquidity requirements by maturity bucket, and the minimum share of each referenced currency that must be held as **deposits at credit institutions cannot be lower than 30 %**. The reserve is **audited independently every six months**; the result is reported to the authority within six weeks and published within two weeks of that, unless the authority orders a delay to protect holders or financial stability.

**Custody** (Article 37). Reserve assets may not be encumbered or pledged, must be held in custody by a CASP, a credit institution or an investment firm, and must be accessible promptly to meet redemptions. The custodian holds them in segregated accounts opened in the name of the issuer for each token, so that the assets of each reserve can be identified, and must compensate the issuer for any lost instrument or crypto-asset unless it proves the loss resulted from an external event beyond its reasonable control (Article 37(10)).

**Investment** (Article 38). Any part of the reserve that is invested may only be placed in **highly liquid financial instruments with minimal market, credit and concentration risk**, capable of rapid liquidation with minimal price effect. All profits and losses, and any counterparty or operational risk of the investment, are borne by the issuer.

**Redemption** (Article 39). Holders have a **permanent right of redemption** against the issuer, and against the reserve assets if the issuer cannot meet its obligations. On request the issuer redeems either by paying funds (other than electronic money) equal to the **market value of the referenced assets** or by delivering those assets. If the issuer accepted payment in a given official currency, it must always offer redemption in that currency. Redemption is **not subject to a fee** (Article 39(3)), the only exception being the liquidity fees a recovery plan may introduce under Article 46, and the issuer's policy must set the conditions, thresholds and timeframes, the procedures for stressed markets, the valuation method and the settlement conditions.

**No interest** (Article 40). Neither the issuer nor any CASP may grant interest in relation to an ART. The text defines interest widely as "any remuneration or any other benefit related to the length of time during which a holder ... holds such asset-referenced tokens", including net compensation or discounts with an equivalent effect, whether paid by the issuer or by third parties. A yield programme on a MiCA stablecoin, whoever pays it, is what this article forbids.

![ART reserve model: holders redeem at market value against the issuer, whose segregated reserve sits at custodians as bank deposits and liquid instruments, audited every six months and disclosed monthly]({{site.url_complet}}/assets/article/regulation/mica/mica-art-reserve-redemption-concept.png)

### Recovery and redemption plans (Chapter 6)

Every ART issuer maintains two plans and notifies them to the authority within six months of authorisation.

The **recovery plan** (Article 46) describes how the issuer will restore compliance with the reserve requirements if it breaches them and how it will keep operating through disruption. It must include a range of options, and the text names three: liquidity fees on redemptions, limits on the amount redeemable per working day, and suspension of redemptions.

The **redemption plan** (Article 47) is the orderly wind-down: it demonstrates that the issuer can redeem the outstanding tokens without undue harm to holders or to the markets of the reserve assets, provides for a temporary administrator, and ensures equitable treatment of holders and timely payment from the sale of the reserve. It is implemented on a decision by the authority that the issuer is or is likely to be unable to fulfil its obligations, including in insolvency or on withdrawal of the authorisation.

The two plans, together with the segregation of the reserve, are the mechanism by which MiCA converts a stablecoin run from a solvency problem for holders into a queue.

## Significant asset-referenced tokens (Chapter 5)

Article 43 lists seven criteria, and EBA classifies an ART as significant when **at least three** are met, either in the first reporting period after authorisation or over two consecutive reports:

- more than **10 million holders**;
- value issued, market capitalisation or reserve size above **EUR 5 000 000 000**;
- more than **2.5 million transactions and EUR 500 000 000** per day on average;
- the issuer is a gatekeeper under the [Digital Markets Act](https://eur-lex.europa.eu/eli/reg/2022/1925/oj);
- significance of the issuer's activities internationally, including use for payments and remittances;
- interconnectedness with the financial system;
- the same issuer issues at least one other ART or EMT and provides at least one crypto-asset service.

An issuer may also request the classification voluntarily (Article 44). The consequences, in Article 45, are a heavier regime supervised directly by EBA:

- a remuneration policy that does not create incentives to relax risk standards;
- the token must be able to be held in custody by different CASPs, including ones outside the issuer's group, on fair, reasonable and non-discriminatory terms;
- a liquidity management policy and regular liquidity stress testing, with EBA able to tighten the requirements on the basis of the results;
- own funds of **3 %** of the average reserve instead of 2 %;
- minimum deposits per referenced currency of **at least 60 %** instead of 30 %.

Supervision of the issuer passes from the national authority to EBA under Article 117, with a college of supervisors under Article 119 and EBA's own powers to fine under Articles 130 to 132, which the [enforcement article]({{site.url_complet}}/2026/09/17/mica-market-abuse-enforcement-supervision/) of this series covers.

## E-money tokens (Title IV)

Title IV is shorter because it borrows most of its content from the [E-Money Directive](https://eur-lex.europa.eu/eli/dir/2009/110/oj) (Directive 2009/110/EC). Article 48(3) applies Titles II and III of that Directive to e-money tokens unless MiCA says otherwise, and Article 48(2) declares that e-money tokens "shall be deemed to be electronic money".

### Who may issue, and how

Only a **credit institution** or an **electronic money institution** may offer an EMT to the public or seek its admission to trading (Article 48(1)). There is no MiCA-specific authorisation; the issuer's existing banking or e-money licence is the entry ticket. Before the first offer it notifies the competent authority of its intention at least **40 working days** ahead (Article 48(6)) and notifies the white paper at least **20 working days** before publication (Article 51(11)). The white paper is not approved but is notified, and its content is set by Article 51 and Annex III.

An EMT referencing an official currency of a Member State is deemed to be offered to the public in the Union (Article 48(2)), which brings a euro token issued from outside the EU into Title IV as soon as it exists.

### Par value, at issue and at redemption

Article 49 replaces the corresponding article of the E-Money Directive with a stricter set of rules:

- holders have a **claim** against the issuer;
- tokens are issued **at par value** and **on receipt of funds**;
- on request the issuer redeems **at any time and at par value**, in funds other than electronic money;
- redemption is **not subject to a fee** (Article 49(6));
- the redemption conditions are stated prominently in the white paper.

Interest is prohibited by Article 50 on the same broad definition as for ARTs, and Article 50 states this "notwithstanding Article 12 of Directive 2009/110/EC", which is the provision that already forbids interest on electronic money.

### Where the funds go

An EMT issuer safeguards the funds received under Article 7(1) of the E-Money Directive, and Article 54 adds two constraints:

- at least **30 %** of the funds received is always deposited in separate accounts at credit institutions;
- the remainder is invested in secure, low-risk assets that qualify as highly liquid financial instruments with minimal market, credit and concentration risk under Article 38(1), **denominated in the same official currency** as the token.

The recovery and redemption plans of Title III apply by reference (Article 55), with the recovery plan due within six months of the first offer rather than of authorisation.

### Significant e-money tokens

EBA classifies an EMT as significant on the same seven criteria and the same three-of-seven rule (Article 56), and a bank or e-money institution may request the classification (Article 57).

Article 58 then imports the ART reserve regime: an e-money institution issuing a significant EMT is subject to Articles 36, 37, 38 and 45(1) to (4) instead of the safeguarding article of the E-Money Directive, and to the own-funds rules of Articles 35(2), (3) and (5) and 45(5) instead of the Directive's capital rule, so that its own funds rise to 3 % of the reserve. Competent authorities may impose any of those requirements on a non-significant EMT issuer as well where the risks warrant it (Article 58(2)).

One carve-out keeps supervision national: for a significant EMT denominated in a **non-euro Member State currency**, where at least **80 %** of holders and of transaction volume are in the home Member State, supervision does not pass to EBA (Article 56(7)).

## Transition

Titles III and IV applied from 30 June 2024. Article 143(4) and (5) allowed issuers already issuing ARTs under national law before that date to continue until their application was decided, provided they applied (or, for credit institutions, notified under Article 17) before **30 July 2024**. There is no equivalent transitional period for EMTs: an EMT issuer had to be a credit institution or e-money institution with a notified white paper from the application date.

## Conclusion

MiCA treats a stablecoin as a claim on an identified issuer backed by ring-fenced assets, and it builds the two titles around making that claim good in all conditions.

- **The reference asset decides the regime.** One official currency makes an e-money token issued by a bank or e-money institution at par; anything else makes an asset-referenced token that needs its own authorisation.
- **An ART authorisation is a prudential licence.** Governance, fit-and-proper tests, a legal opinion on classification, a white paper approved with the authorisation, and a central-bank veto on monetary-policy grounds.
- **The reserve is segregated, liquid, custodied and audited.** Legally and operationally separate from the issuer, at least 30 % in bank deposits per currency, invested only in highly liquid low-risk instruments, audited every six months and reported monthly.
- **Own funds scale with the reserve.** The highest of EUR 350 000, 2 % of the reserve or a quarter of fixed overheads, with add-ons up to 40 % and a 3 % floor for significant tokens.
- **Redemption is a permanent right.** At market value for an ART, at par and free of charge for an EMT, with recovery and redemption plans that turn a run into an orderly queue.
- **Interest is prohibited** in both titles, on a definition wide enough to catch yield paid by third parties.
- **Size moves supervision to EBA.** Three of seven criteria, among them 10 million holders, EUR 5 billion in value or 2.5 million transactions a day, make a token significant and raise the reserve and capital floors.

![Mindmap of Titles III and IV covering ART and EMT definitions, authorisation, reserve, custody, redemption, own funds, the interest ban, significance criteria and the e-money token regime]({{site.url_complet}}/assets/article/regulation/mica/2026-09-17-mica-stablecoins-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Asset-referenced token (ART)** | A crypto-asset, other than an e-money token, that purports to maintain a stable value by referencing another value or right or a combination, including one or more official currencies. |
| **E-money token (EMT)** | A crypto-asset that purports to maintain a stable value by referencing one official currency; deemed electronic money under Article 48(2). |
| **Reserve of assets** | The basket of reserve assets securing the claim against the issuer of an ART, legally and operationally segregated from the issuer's estate (Articles 3(1)(32) and 36). |
| **Own funds** | Common Equity Tier 1 capital an ART issuer must hold at all times, equal to at least the highest of EUR 350 000, 2 % of the average reserve or a quarter of fixed overheads. |
| **Right of redemption** | The permanent right of an ART holder to be paid the market value of the referenced assets, or to receive those assets, on request; for an EMT, redemption at par at any time without fee. |
| **Electronic money institution** | A legal person authorised under Directive 2009/110/EC to issue electronic money; one of the two categories of entity permitted to issue e-money tokens. |
| **Credit institution** | A bank authorised under Directive 2013/36/EU; may issue ARTs after white-paper approval under Article 17 and EMTs under Article 48. |
| **Significant token** | An ART or EMT meeting at least three of the seven criteria of Article 43(1), whose issuer is then supervised by EBA and subject to Articles 45 and 58. |
| **Means of exchange** | Use of a token to settle transactions within a single currency area; above 1 million transactions and EUR 200 million per day the issuer must stop issuing (Article 23). |
| **Redemption plan** | The operational plan under Article 47 for the orderly redemption of all outstanding tokens if the issuer cannot meet its obligations, implemented on a decision by the competent authority. |

### Requirements Checklist

Titles III and IV are written as conditions and ongoing obligations for issuers. The rows below transcribe them by article so that an issuer, or an auditor of one, can check a stablecoin against the text.

#### Articles 16 to 23 — ART authorisation and reporting

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 16(1) | The offeror is the issuer, and is either an EU legal person authorised under Art. 21 or a credit institution complying with Art. 17. |
| ☐ | 16(1) | Any other person offers the token only with the issuer's written consent and complies with Arts 27, 29 and 40. |
| ☐ | 16(2) | Exemption from authorisation: average outstanding value never above EUR 5 000 000 over 12 months and no network of exempt issuers, or qualified investors only; a white paper is still notified. |
| ☐ | 17(1) | A credit institution has its white paper approved and notifies the authority at least 90 working days before first issuance with the programme of operations, legal opinion and policies. |
| ☐ | 18(2) | The application contains the LEI, articles, business plan, legal opinion on classification, governance description, AML controls, identity and suitability of management and qualifying shareholders, white paper, policies and plans. |
| ☐ | 19 | The white paper contains the Annex II items, including Part G on the reserve of assets, and the prescribed statements. |
| ☐ | 20–21 | The authority assesses within the fixed periods, consults EBA, ESMA and the ECB, and refuses on a negative central-bank opinion on payment systems, monetary policy or monetary sovereignty. |
| ☐ | 22(1) | For a token with issue value above EUR 100 000 000, quarterly reporting of holders, value issued, reserve size, daily transactions and means-of-exchange use. |
| ☐ | 23(1) | If means-of-exchange use exceeds 1 million transactions and EUR 200 000 000 per day in a single currency area, stop issuing and submit a plan within 40 working days. |

#### Articles 27 to 35 — Conduct, information, governance and own funds

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 27 | Act honestly, fairly and professionally; communicate fairly; treat holders equally unless preferential treatment is disclosed. |
| ☐ | 28–29 | Publish the approved white paper; marketing is identified, consistent with it and states the right of redemption. |
| ☐ | 30(1) | Publish at least monthly the tokens in circulation and the value and composition of the reserve. |
| ☐ | 30(2)–(3) | Publish the reserve audit report in full and disclose events likely to affect the token or the reserve. |
| ☐ | 31–33 | Complaints-handling procedures; identification and disclosure of conflicts of interest; notification of management-body changes. |
| ☐ | 34 | Robust governance, fit-and-proper management and qualifying shareholders, business continuity, ICT security, independent audit. |
| ☐ | 35(1) | Own funds at all times at least the highest of EUR 350 000, 2 % of the average reserve, or one quarter of last year's fixed overheads. |
| ☐ | 35(2) | Own funds consist of Common Equity Tier 1 items after full deductions under Regulation (EU) No 575/2013. |
| ☐ | 35(3)–(5) | The authority may require up to 20 % more (20–40 % in stress situations); the issuer runs stress tests. |

#### Articles 36 to 40 — Reserve, custody, investment, redemption, interest

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 36(1) | A reserve of assets is constituted and maintained at all times, covering the risks of the referenced assets and the liquidity risk of redemption. |
| ☐ | 36(2)–(3) | The reserve is legally and operationally segregated from the issuer's estate and from other reserves; creditors have no recourse to it. |
| ☐ | 36(4) | Liquidity requirements per EBA standards; deposits at credit institutions of at least 30 % of the amount referenced in each official currency. |
| ☐ | 36(9)–(10) | Independent audit of the reserve every six months; result notified within six weeks and published within two weeks of notification. |
| ☐ | 37(1) | Reserve assets are not encumbered or pledged, are held in custody, and are promptly accessible for redemptions. |
| ☐ | 37 | Custody with a CASP, a credit institution or an investment firm, in accounts opened in the issuer's name per token. |
| ☐ | 38(1) | Investments only in highly liquid financial instruments with minimal market, credit and concentration risk, rapidly liquidable. |
| ☐ | 38(4) | All profits, losses and counterparty or operational risks of the investment are borne by the issuer. |
| ☐ | 39(1)–(2) | Holders have a permanent right of redemption at the market value of the referenced assets, in funds or in kind, under a published policy. |
| ☐ | 39(2) | Where payment was accepted in an official currency, redemption in that currency is always offered. |
| ☐ | 39(3) | Redemption is not subject to a fee, without prejudice to the liquidity fees of a recovery plan under Art. 46. |
| ☐ | 40 | No interest, and no time-related remuneration or benefit, from the issuer or any CASP. |

#### Articles 43 to 47 — Significance, recovery and redemption plans

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 43(1)–(2) | EBA classifies the token as significant when at least three criteria are met: 10 million holders; EUR 5 billion value or reserve; 2.5 million transactions and EUR 500 million per day; DMA gatekeeper; international significance; interconnectedness; multiple tokens plus a crypto-asset service. |
| ☐ | 45(1)–(2) | Significant issuers adopt a risk-aligned remuneration policy and allow custody by CASPs outside their group on fair terms. |
| ☐ | 45(3)–(4) | Liquidity management policy and regular liquidity stress testing. |
| ☐ | 45(5) | Own funds of 3 % of the average reserve. |
| ☐ | 45(7)(b) | Minimum deposits of at least 60 % of the amount referenced in each official currency. |
| ☐ | 46(1)–(2) | A recovery plan with liquidity fees, redemption limits and suspension among its options, notified within six months of authorisation. |
| ☐ | 47(1)–(2) | A redemption plan demonstrating orderly redemption of all tokens, with a temporary administrator and equitable treatment of holders. |

#### Articles 48 to 58 — E-money tokens

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | 48(1) | The issuer is a credit institution or an electronic money institution and has notified and published a white paper under Art. 51. |
| ☐ | 48(2)–(3) | The token is deemed electronic money; Titles II and III of Directive 2009/110/EC apply unless MiCA provides otherwise. |
| ☐ | 48(6) | The authority is notified of the intention to offer at least 40 working days in advance. |
| ☐ | 49(2)–(3) | Holders have a claim against the issuer; tokens are issued at par value on receipt of funds. |
| ☐ | 49(4), (6) | Redemption at any time at par value in funds, with no fee. |
| ☐ | 50 | No interest from the issuer or any CASP. |
| ☐ | 51(11) | The white paper is notified at least 20 working days before publication; no prior approval. |
| ☐ | 52–53 | Issuer liability for the white paper; marketing rules as for ARTs. |
| ☐ | 54(a) | At least 30 % of funds received is deposited in separate accounts at credit institutions. |
| ☐ | 54(b) | The remainder is invested in highly liquid low-risk instruments denominated in the referenced currency. |
| ☐ | 55 | Recovery and redemption plans as in Title III, Chapter 6; recovery plan within six months of the first offer. |
| ☐ | 56–57 | Significance on the Art. 43(1) criteria, three of seven; voluntary classification possible. |
| ☐ | 56(7) | No transfer to EBA for a non-euro EU-currency token with at least 80 % of holders and volume in the home Member State. |
| ☐ | 58(1) | Significant EMT issuers apply Arts 36, 37, 38 and 45(1)–(4), and Arts 35(2), (3), (5) and 45(5), instead of Arts 7 and 5 of the Directive. |

## Frequently Asked Questions

**Q: A token is pegged 1:1 to the US dollar and fully backed by dollar treasury bills. Is it an ART or an EMT under MiCA?**

An EMT. Article 3(1)(7) defines an e-money token by reference to one official currency, and the dollar is an official currency even though it is not an EU currency. Only a credit institution or an electronic money institution may offer it in the Union, it must be issued and redeemed at par, and the funds must be safeguarded with at least 30 % in bank deposits and the rest in highly liquid dollar-denominated instruments. The treasury-bill backing is compatible with Article 54(b), but a non-bank issuer without an e-money licence cannot offer the token in the EU at all.

**Q: What is the difference between how an ART and an EMT are redeemed?**

An EMT is redeemed at par value, at any time, in funds, and without a fee (Article 49). An ART is redeemed at the market value of the assets it references, either in funds or by delivering those assets, under a policy that sets thresholds and timeframes, and likewise without a fee outside a recovery plan (Article 39). The difference follows from the reference: an EMT is a claim to a fixed amount of one currency, while an ART is a claim to whatever the reference basket is worth on the day of redemption.

**Q: Can a CASP offer a rewards programme on balances held in a MiCA stablecoin?**

No, if the reward depends on how long the holder keeps the token. Articles 40 and 50 prohibit the issuer and any CASP from granting interest in relation to an ART or an EMT, and define interest as any remuneration or benefit related to the length of time the holder holds the token, including discounts or net compensation with an equivalent effect and benefits paid by third parties. A time-based yield on stablecoin balances falls within that definition regardless of who funds it.

**Q: Why can a central bank block an ART authorisation when the opinions of EBA and ESMA are non-binding?**

Article 20(5) makes all the opinions non-binding in principle, but Article 21(4) creates one exception: the competent authority must refuse authorisation if the ECB or the relevant national central bank gives a negative opinion on the grounds of a risk to the smooth operation of payment systems, monetary policy transmission or monetary sovereignty. The legislator reserved those three grounds to the monetary authority because they concern the currency itself rather than investor protection or market integrity, which are the competences of the financial supervisors.

**Q: What happens when an ART reaches 1 million transactions and EUR 200 million per day as a means of exchange?**

Under Article 23 the issuer must stop issuing the token and, within 40 working days, submit a plan to bring both figures back below the thresholds. The competent authority may require modifications, such as a minimum denomination, and permits issuance to resume only when it has evidence that use is below the thresholds. The article is the operational form of the "monetary sovereignty" concern: it caps the extent to which a private token can replace the currency in everyday payments within a currency area.

**Q: Combining the significance and capital rules: an e-money institution issues a euro EMT with 12 million holders and EUR 6 billion outstanding. What changes for it?**

The token meets at least three of the Article 43(1) criteria: holders, value, and almost certainly transaction volume. EBA therefore classifies it as significant under Article 56 and supervision of the issuer moves to EBA under Article 117, since the carve-out of Article 56(7) applies only to non-euro currencies. Under Article 58 the issuer must now:

- hold a **reserve of assets** under Articles 36 to 38 instead of safeguarding funds under the E-Money Directive, with at least 60 % of the euro amount in bank deposits (Article 45(7)(b));
- hold **own funds of 3 %** of the average reserve instead of the Directive's capital rule;
- adopt a **liquidity management policy** with stress testing;
- allow **custody by CASPs outside its group** on fair terms;
- mandate the **six-monthly reserve audit** from the date of the classification decision.

## References

### Legal texts

- [Regulation (EU) 2023/1114 on markets in crypto-assets (MiCA)](https://eur-lex.europa.eu/eli/reg/2023/1114/oj), Titles III and IV, Articles 16 to 58, and Annexes II and III
- [Consolidated text of Regulation (EU) 2023/1114 as of 9 January 2024](https://eur-lex.europa.eu/eli/reg/2023/1114/2024-01-09), EUR-Lex
- [Directive 2009/110/EC (E-Money Directive)](https://eur-lex.europa.eu/eli/dir/2009/110/oj), applied to e-money tokens by Article 48(3)
- [Regulation (EU) No 575/2013 (Capital Requirements Regulation)](https://eur-lex.europa.eu/eli/reg/2013/575/oj), for the definition of Common Equity Tier 1 own funds
- [Directive (EU) 2015/849 (Anti-Money Laundering Directive)](https://eur-lex.europa.eu/eli/dir/2015/849/oj), referenced in the application content
- [Regulation (EU) 2022/1925 (Digital Markets Act)](https://eur-lex.europa.eu/eli/reg/2022/1925/oj), whose gatekeeper designation is a significance criterion

### Supervisory authorities

- [EBA — Markets in Crypto-Assets (MiCA)](https://www.eba.europa.eu/activities/single-rulebook/regulatory-activities/markets-crypto-assets-mica), technical standards on reserve liquidity, own funds, significance and the supervision of significant issuers
- [ESMA — Markets in Crypto-Assets Regulation (MiCA)](https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/markets-crypto-assets-regulation-mica)

### Related articles

- [Tether USDT smart contract - Overview]({{site.url_complet}}/2025/07/06/tether-stablecoin-overview/)
- [USD₮0 - Omnichain Fungible Token]({{site.url_complet}}/2025/11/07/usdt0-Omnichain-fungible-token/)
- [Introduction to MakerDAO]({{site.url_complet}}/2023/11/20/makerdao/)
- [10 Key Differences Between MakerDAO and Liquity]({{site.url_complet}}/2024/12/16/10-Key-Differences-Between-MakerDAO-and-Liquity/)
