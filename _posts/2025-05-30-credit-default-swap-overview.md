---
layout: post
title: "Credit Default Swaps - Overview"
date: 2025-05-30
last_modified_at: 2026-11-17
lang: en
locale: en-GB
categories: finance blockchain
tags: CDS credit-default-swap derivative
description: A Credit Default Swap (CDS) is a financial derivative that functions as a form of insurance against the default of a borrower. 
image: /assets/article/finance/credit-default-swap-mindmap.png
isMath: true
---

A **Credit Default Swap (CDS)** is a financial derivative that functions as a form of insurance against the default of a borrower. It allows one party to transfer the credit risk of a fixed income product to another party in exchange for a premium. 

Since their inception in the early 1990s, CDS contracts have been used in credit markets both to hedge credit risk and to speculate on it.

[TOC]

## What you need to know first

The article assumes a few notions from fixed income and derivatives markets that it uses without defining them.

- **Face value and recovery rate**: a bond's face value is the amount the issuer promises to repay at maturity, and the recovery rate is the share of that amount a creditor still gets back after a default. The CDS payout is the face value of the bonds, and the recovery rate $$R$$ enters the default-probability estimate.
- **Basis points**: one basis point (bp) is one hundredth of a percent, so 240 bps per year is 2.4% per year. CDS spreads are quoted in basis points per year of the notional principal.
- **Credit spread**: the extra yield an investor demands to hold a risky debt instead of a risk-free one, as compensation for the risk of default. The article reads the CDS spread as a credit spread and derives a probability of default from it.
- **Payment in arrears**: a payment made at the end of the period it covers rather than at its start. Because CDS premiums are paid quarterly in arrears, a default between two payment dates leaves an accrued premium that the buyer still owes.
- **Short selling**: borrowing an asset, selling it and buying it back later, which gains when the price falls; see [Traditional Futures vs. Perpetual Futures]({{site.url_complet}}/2025/12/29/traditional-vs-perpetual-futures/). The article compares a naked CDS to a short position on the bond.
- **OTC trading and central clearing**: an over-the-counter contract is negotiated privately between two parties, while a centrally cleared one is novated to a central counterparty that stands between buyer and seller. The regulatory sections describe the post-2008 move of standardized CDS from bilateral OTC trading to central clearing.
- **Collateral and margin calls**: a party to a derivative may have to post collateral, cash or securities, that the counterparty keeps if it defaults, and must post more when its position loses value. The AIG case is a failure to meet such collateral calls.



------

## How a Credit Default Swap Works

In a CDS agreement, there are typically two parties:

- **Protection buyer**: Pays periodic fees (premiums) to the seller.

The buyer of a CDS obtain the right to sell the bonds issue by the reference entity for their face value, when there is a credit event, that is a default.

- **Protection seller**: Promises to compensate the buyer if a credit event occurs, such as a default, a bankruptcy or a restructuring of the reference entity.

The seller of a CDS is obliged to buy the bonds for their face value when the credit event occurs

- The total face value of all the bonds, which are part of the CDS is known as the **notional principal**

For example, if Company X issues bonds and an investor fears that X may default, they can buy a CDS from a bank. If X defaults, the bank pays the investor the face value of the bond. If no default occurs, the bank keeps the premiums.

### Key terms

- The company subject to default is known as reference entity
- THe default is called credit event

Reference: [TW3421x - Week 7 - Credit Default Swaps](https://www.youtube.com/watch?v=F5ojp6Kzxes)

#### CDS spread

The **CDS spread** is the total amount paid every year by the buyer as a percent of the nominal principal.

- The CDS spread is the "price" (the extra rate) required by the seller of the CDS to bear the risk of default of the reference entity.
- The CDS spread, like any credit spread, can be used to quickly estimate the **probability of default** (PD) of a counterparty
  - In general, we can compute the average PD of the reference entity, conditional on no previous default, as

$$
\begin{aligned}
PD = \frac {CS} {1 - R}
\end{aligned}
$$

Where:

PD is the probability of default

CS is the CDS spread

R is the recovery rate

- This estimation is not extremely precise, and it is subject to rather strong assumptions from a probabilistic point of view, but it is surely quick and may be helpful to have a first idea about the creditworthiness of a counterparty.

Reference: [TW3421x - Week 7 - Credit Default Swaps](https://www.youtube.com/watch?v=F5ojp6Kzxes)

##### Example

**Example 1**

Suppose that a 5-year CDS spread (CS) for a given company (the reference entity) is 240 bps per year, i.e 2.4% per year.

- Assume that the recovery rate(R) in case of default is 40%.
- The average (yearly) PD over the 5-year period, conditional on no earlier default is estimated as:

$$
\begin{aligned}
\frac{0.024}{1-0.4} = 0.04 = 4%
\end{aligned}
$$



**Example 2**

Suppose that, for the same reference entity, the 3-year CDS spread is 50 bps while the 5-year CDS spread is 60 bps with a recovery rate of 60%.

- The average PD over 3 year is 0.005 / (1-0.6) = 0.0125
- The average PD over 5 years is 0.006 / (1-0.6) = 0.015

The average PD between year 3 and year 5 is:
$$
\begin{aligned}
\frac {5 * 0.015 - 3 * 0.0125}2 = 0.01875 = 1.875%
\end{aligned}
$$

- The general formula for inferring the intermediate average PD between an y-ear CDS and x-year CDS, with y > x, is

$$
\begin{aligned}
\frac{y * PD_y - x * PD_x}{y-x}
\end{aligned}
$$

Where PDx is the average PD for the x-year CDS.

### Example

On June 20, 2014, tow parties agree to enter into a 5-year CDS with respect to a specific reference entitiy

- The notional principal is $100 million.

- The buyer agrees to pay 90 basis points per year, in quartlerly arrears for protection against default by the reference entity
- The CDS spread is 90 bps, that is 0.9%.

#### No default

In case of no default, that is no credit event, the buyer receives no payout, while s/he pays the seller about $225k on September 20, December 20, March 20 and June 20 in 2014, 2015, 2016, 2017, 2018, 2019.

90 bps of 100'000'000 is 900'000. 
Then 900'000 / 4 = 225'000

#### Default

Now image that there is a credit event, i.e a default.

This default happens in month 5 of year 3, that is around November 20 2016.

In that case, the buyer stops paying the seller and claims the notional principal.

The seller is obliged to pay the notional principal (or any other arrangement) to the buyer, by buying all the bonds involved in the CDS.

Since the buyer's payments are in arrears, and the default event happens in November, a final accrual payment is requires.

In particular, the buyer must pay his/her insurance for October and November 2016, until the credit event. That is:

900'000 / 12 * 2 = 150'000

## CDS as a derivative: Naked CDS vs. Covered CDS

A net short position can also be achieved by the use of derivatives, including Credit Default Swaps (CDS). 

For example, if an investor buys a CDS without being exposed to the credit risk of the underlying bond issuer (a so-called "naked CDS"), he is expecting, and potentially gaining from, rising credit risk. This is equivalent to short selling the underlying bond.

Reference: [Regulation on Short Selling and Credit Default Swaps - Frequently asked questions](https://ec.europa.eu/commission/presscorner/detail/en/memo_11_713)

#### Covered CDS

A **covered CDS** is when you own the underlying bond **and** buy a CDS to protect against its default. It's like insuring something you own.

#### Naked CDS

A **naked CDS** is when you buy the CDS **without owning the bond**. You're not protecting against a loss — you're speculating.

- This means the investor does not hold the bond but buys the CDS betting that the **issuer’s creditworthiness will worsen** (i.e., default risk increases).
- If the market thinks the issuer is more likely to default, the **value of the CDS increases**, and the buyer can potentially sell it at a profit.

##### Why it's like short selling

- In **short selling a bond**, you're betting its price will fall — which happens when the issuer is at greater risk of default.
- Similarly, a **naked CDS buyer** profits when the issuer looks more likely to default.
- Both strategies **benefit from worsening credit conditions** for the bond issuer.

Reference: ChatGPT + [CFI - Naked Credit Default Swaps](https://corporatefinanceinstitute.com/resources/derivatives/naked-credit-default-swaps/)

------

## CDS risk

CDS markets can enhance liquidity and allow institutions to manage risk efficiently. However, they also pose significant **systemic risks**, which became especially evident during the 2008 financial crisis. Some major risks include:

### Counterparty Risk

The protection seller may itself default, rendering the CDS protection worthless. This is what happened with AIG in 2008, which had sold massive amounts of CDS without sufficient capital backing.

### Lack of Transparency

Traditionally, CDS contracts have been traded over-the-counter (OTC), meaning they are privately negotiated and not standardized. This obscures the true extent of exposures and interconnections in the financial system.

### Speculation and Leverage

CDSs can be used not only for hedging but also for speculation. Investors can buy CDS contracts on debt they don’t own, akin to buying insurance on a neighbor’s house. This speculative use can amplify losses in a downturn.

------

### Case Study: The AIG Collapse and CDS Fallout

The story of **AIG (American International Group)** is one of the most infamous examples of CDS risk gone wrong.

In the early 2000s, AIG's **Financial Products division** aggressively entered the CDS market, selling protection on billions of dollars' worth of mortgage-backed securities (MBS), particularly **collateralized debt obligations (CDOs)**. Many of these securities were rated AAA, so AIG saw them as low-risk and didn't require collateral or set aside sufficient capital reserves.

However, when the U.S. housing market began to collapse in 2007–2008, the value of these mortgage securities plummeted, and rating agencies began downgrading them. As a result, AIG was required to post **massive amounts of collateral** to counterparties under the terms of its CDS agreements. The company quickly found itself unable to meet these obligations.

At its peak, AIG had over **$400 billion** in CDS exposure. As panic spread, counterparties lost confidence, demanding more collateral and cash that AIG simply didn’t have. The company faced imminent collapse.

To prevent a domino effect across the global financial system—since many major banks held CDS contracts with AIG—the **U.S. government stepped in with a historic bailout**, providing over **$180 billion** in loans and capital injections. In effect, AIG was "too interconnected to fail."

This episode highlighted the **unregulated, opaque nature** of the CDS market and the **devastating systemic risk** that arises when such contracts are concentrated in a few major institutions without proper oversight.

Reference: [U.S Department of the Treasury - AIG](https://home.treasury.gov/data/troubled-assets-relief-program/aig/status), [Wikipedia - AIG](https://en.wikipedia.org/wiki/American_International_Group)

------

## Bringing CDS to the Blockchain: Is It Feasible?

The application of **blockchain technology** to credit default swaps is increasingly being explored as a way to address transparency and efficiency issues.

#### Benefits of CDS on Blockchain

- **Transparency**: A blockchain ledger can make CDS positions and exposures visible in real-time through the use of public blockchain.
- **Smart Contracts**: CDS terms could be codified into smart contracts, ensuring automatic execution of payouts when predefined transactions are triggered.
- **Reduced Counterparty Risk**: Using decentralized finance (DeFi) principles and collateralized protocols, blockchain-based CDS could reduce the risk of one party defaulting.
- **Auditability and Traceability**: Each transaction is permanently recorded, making audits simpler and reducing potential fraud.

#### Challenges and Risks

- **Oracle Risk**: Smart contracts require reliable external data ("oracles") to verify credit events like defaults. Manipulated or inaccurate oracles could cause incorrect payouts.
- **Regulatory Uncertainty**: Financial derivatives on blockchains raise complex regulatory questions, especially when spanning multiple jurisdictions.
- **Liquidity Concerns**: A decentralized CDS market might struggle to match the liquidity of traditional financial institutions, at least initially.
- **Complexity of Events**: Credit events are often nuanced and legally complex, sometimes requiring subjective judgment or court rulings—difficult to automate via code.

------

## Difference between US and UE

There **are key differences** between how **Credit Default Swaps (CDS)** operate in the **United States (US)** and the **European Union (EU)**, though the instruments are fundamentally similar. The distinctions mainly arise from **regulation**, **market structure**, and **legal definitions of credit events**.

------

### Regulatory Framework

#### United States (US)*

- **Regulated by two agencies** under Title VII of the Dodd-Frank Act, passed after the 2008 crisis. The **Securities and Exchange Commission** (SEC) oversees single-name CDS and CDS on narrow-based indices, which are security-based swaps. The **Commodity Futures Trading Commission** (CFTC) oversees CDS on broad-based indices, which are swaps.
- Dodd-Frank mandates:
  - Central clearing of standardized CDS through clearinghouses.
  - Trade reporting to swap data repositories (SDRs).
  - Margin requirements and position limits.
  - Registration of major swap participants.

#### European Union (EU)

CDS are regulated under several frameworks:
- **EMIR (European Market Infrastructure Regulation)** – requires central clearing, reporting, and risk mitigation for OTC derivatives.
- **MiFID II/MiFIR** – imposes transparency and market conduct rules. See  [ESMA finalises MiFID II’s derivatives trading obligation](https://www.esma.europa.eu/press-news/esma-news/esma-finalises-mifid-ii’s-derivatives-trading-obligation) (2017)
- **MAR (Market Abuse Regulation)** – applies to insider trading or market manipulation involving CDS.
- **Short Selling Regulation (SSR)** – uniquely, the EU restricts "naked" sovereign CDS trading (see below). See [esma.europa.eu - Short Selling](https://www.esma.europa.eu/esmas-activities/markets-and-infrastructure/short-selling)

------

### Sovereign CDS: The EU's Special Rules

One of the most **important differences** lies in how the **EU treats sovereign CDS** (i.e., CDS on government debt).

- In the **EU**, under the **Short Selling Regulation**, it is **prohibited to buy sovereign CDS without holding an insurable interest** (i.e., no "naked" positions).
  - This rule was introduced after the Eurozone debt crisis, as policymakers believed speculation via CDS was exacerbating the stress on countries like Greece, Portugal, and Spain.
  - Reference: [ESMEA - Short Selling](https://www.esma.europa.eu/esmas-activities/markets-and-infrastructure/short-selling)
- In contrast, the **US does not prohibit naked CDS** positions, whether on corporate or sovereign debt.

------

### Credit Event Determination

Both regions use the **ISDA (International Swaps and Derivatives Association)** framework to define credit events like default, restructuring, and failure to pay. However:

- **EU contracts are more likely to be governed by English law**, while US CDS contracts typically fall under **New York law**. This can affect interpretations, especially for complex restructuring events.
- There have been notable cases (e.g., Greece’s debt restructuring in 2012) where the definition of a credit event was **controversial**, and market participants in the EU faced uncertainty due to different legal and regulatory environments.

------

### Market Structure and Participants

- The **US CDS market** is larger and more liquid overall, particularly in corporate CDS.
- In the **EU**, the CDS market is smaller and subject to stricter controls, particularly on sovereign debt. European banks and institutions also tend to be more cautious with CDS exposure due to regulatory pressure and public perception.
- **European Central Counterparties (CCPs)** such as LCH and Eurex play a key role in clearing, just as **ICE Clear Credit** does in the US.

------

### Summary of Key Differences

| Aspect                 | United States                                                | European Union                               |
| ---------------------- | ------------------------------------------------------------ | -------------------------------------------- |
| Regulatory Body        | SEC for single-name CDS, CFTC for broad-based index CDS ([Dodd-Frank](https://www.cftc.gov/LawRegulation/DoddFrankAct/index.htm) / [CFTC Issues Clearing Determination for Certain Credit Default Swaps and Interest Rate Swaps](https://www.cftc.gov/PressRoom/PressReleases/6429-12)) | ESMA, local regulators (EMIR, MiFID II, SSR) |
| Central Clearing       | Mandatory for standardized CDS                               | Mandatory for standardized CDS               |
| Naked Sovereign CDS    | Allowed                                                      | **Prohibited**                               |
| Governing Law          | Usually New York law                                         | Often English law                            |
| Market Size            | Larger, more liquid                                          | Smaller, more regulated                      |
| Credit Event Handling  | ISDA (NY law)                                                | ISDA (often UK law)                          |
| Reporting Requirements | Swap Data Repositories                                       | Trade Repositories (under EMIR)              |



------

### Summary

While CDS contracts in the US and EU share the same core mechanics, their **regulatory environments differ significantly**, especially when it comes to sovereign CDS and speculative activity. 

- The **EU's stricter controls** reflect a more conservative and politically sensitive approach
-  The **US allows greater flexibility**, especially for hedge funds and speculative investors. 

These differences impact **how investors hedge, speculate, and manage risk** across jurisdictions.

### Mindmap

Made with the help of ChatGPT

![credit-default-swap-mindmap]({{site.url_complet}}/assets/article/finance/credit-default-swap-mindmap.png)



## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Credit Default Swap (CDS)** | A derivative in which a protection buyer pays periodic premiums to a protection seller, who compensates the buyer if the reference entity suffers a credit event. |
| **Protection buyer** | The party that pays the premiums and, after a credit event, can sell the reference entity's bonds to the seller for their face value. |
| **Protection seller** | The party that receives the premiums and must buy the bonds at face value, or pay an equivalent amount, when a credit event occurs. |
| **Reference entity** | The company or government whose default the CDS covers. |
| **Credit event** | The event that triggers the CDS payout, such as a default, a bankruptcy or a restructuring of the reference entity. |
| **Notional principal** | The total face value of the bonds covered by the CDS, on which the premiums are computed. |
| **CDS spread** | The yearly premium paid by the buyer, expressed as a percentage or in basis points of the notional principal. |
| **Recovery rate** | The share of face value a creditor recovers after a default, written $$R$$ in the estimate $$PD = CS / (1 - R)$$. |
| **Probability of default (PD)** | The average yearly likelihood that the reference entity defaults, conditional on no earlier default, estimated here from the CDS spread. |
| **Covered CDS** | A CDS bought by an investor who also holds the underlying bond, used as insurance against its default. |
| **Naked CDS** | A CDS bought without holding the underlying bond, which gains when the issuer's credit risk rises and works like a short position on the bond. |
| **Counterparty risk** | The risk that the protection seller itself defaults and cannot pay, as AIG nearly did in 2008. |
| **Central clearing** | The settlement of a contract through a central counterparty, required for standardized CDS in both the US and the EU. |
| **ISDA** | The International Swaps and Derivatives Association, whose framework defines credit events in US and EU CDS contracts. |
| **Short Selling Regulation (SSR)** | The EU regulation that prohibits naked positions in sovereign CDS. |

## Reference

- ChatGPT with the input "Write me an article about credit default swap. Talk also about the risk and if it is possible to put it on the blockchain"

- [TW3421x - Week 7 - Credit Default Swaps](https://www.youtube.com/watch?v=F5ojp6Kzxes)
- [Credit default swaps  - Finance & Capital Markets - Khan Academy](https://www.youtube.com/watch?v=a1lVOO9Y080)
- [Credit default swaps 2 - Finance & Capital Markets - Khan Academy](https://www.youtube.com/watch?v=neAFEvNsiqw)
- [Wikipedia - Credit default swap](https://en.wikipedia.org/wiki/Credit_default_swap)
- [CFI - Naked Credit Default Swaps](https://corporatefinanceinstitute.com/resources/derivatives/naked-credit-default-swaps/)
- [SEC - SEC Adopts Rule Defining Swaps-Related Terms for Regulating Derivatives, Fact Sheet (2012)](https://www.sec.gov/opa/press-release-2012-67-related-materials)


### Related articles

- [Building a Compliant EU Money Market Fund Portfolio — Eligible Assets, Diversification Limits, Credit Assessment and WAM/WAL]({{site.url_complet}}/2026/10/01/eu-money-market-fund-portfolio-construction-limits/)
