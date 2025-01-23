---
layout: post
title:  How to build a blockchain oracle
date:   2024-04-16
lang: en
locale: en-GB
categories: blockchain blockchainBestOf ethereum
tags: chainlink oracle blockchain
description: This article presents the reasoning to build a blockchain oracle providing external information (e.g. price of an asset) to a smart contract. 
image: /assets/article/blockchain/oracle/chainlink-price-feed.png
isMath: false
---

This article presents the reasoning to build a blockchain oracle providing external information (e.g. price of an asset) to a smart contract. It is mainly based on this excellent [1.presentation](https://www.youtube.com/watch?v=vFcW18ZpPZ4) from Berkely, part of the [defi-learning course (1)](https://defi-learning.org/f22) and on the Chainlink oracle architecture.

[TOC]

## Introduction

**Blockchain oracles** such a Chainlink or Pyth are key elements of crypto and defi infrastructure. Many *defi* protocols rely on these oracles to fetch the price of an asset, required e.g. for lending protocols.

> But why an oracle is so important ?

Smart contracts runs on the blockchain and the outside world is not available for them.

But the price of an assets depends on several different resources, notably CEX like Binance or Coinbase.

To obtain this information, the smart contract can not just perform a direct call to a website or an external sever. It would be too easy.

The smart contract can only call another smart contract to get this information...**

And this is exactly what provides a blockchain oracle: a **smart contract** to get these information.

But how concretely build a blockchain oracle ? It is not an easy task and you have several challenges to take into consideration:

- Which sources used to know the price (CEX, DEX, aggregator) ?
- What happen if the sources are down ?
- How to compute the price from these different sources ?
- How to set the price inside the oracle smart contract ? Which takes this decision and when ?
- How provide trust to users ? What happen if the oracle is malicious ? 

One of the most known and battle tested oracle is the one set up by Chainlink, one of whose products is [Chainlink Data feeds (2.)](https://docs.chain.link/data-feeds). Its operation, without going into details, is as follows:

- The oracle is composed of many decentralized nodes from different organization (Swisscom) to avoid an unique point of failure and a price manipulation by a malicious node.
- These nodes fetch the prices from known price aggregators like CoinCeko or GSR
- Each node has to provide observations, signed by themselves.
- These observations are aggregated into a report by a node (leader) and this report is sent to the smart contract by a designed node (round robin).
- The smart contract verifies the different signatures, compute the median value from the different observations before making them available for other smart contracts.

**You can also use a [TWAP oracle](https://www.halborn.com/blog/post/what-are-twap-oracles), but it is another topic.

## Push/pull oracles

You have traditionally two types of oracles: 

- **Push oracles**: these oracles proactively provide data to smart contracts without being  explicitly requested, e.g. when a  specified event or condition occurs. 

- **Pull oracles** require smart contracts to request data explicitly. They pull data from external sources in response to a query from the smart contract.

Chainlink provides a pull based oracle ([Chainlink data streams (3)](https://docs.chain.link/data-streams)) and a push based oracle ([Chainlink data feeds](https://chain.link/data-feeds))

Here a schema from [Chainlink documentation](https://docs.chain.link/data-streams)

![chainlink-push-pull-oracle]({{site.url_complet}}/assets/article/blockchain/oracle/chainlink-push-pull-oracle.png)

The reasoning taken in this article is mainly based on the push base oracle with the [Price Feeds (4)](https://docs.chain.link/data-feeds#price-feeds), but can also apply to a pull base oracle.

Reference: [5. Arbitrum - Oracle overview](https://docs.arbitrum.io/build-decentralized-apps/oracles/overview)                                                                         

> How to implement a good oracle?

### Step 1 - Directly into the Consensus Protocol

The first thing could be to add the oracle directly into the consensus protocol (block production mechanism). In this case, the miner will search directly for information asked by the smart contract.

> **Problem:** The miner could be lying or cheating.

In this case, the miner is the only one which provides and knows the information. The other members on the blockchain (nodes) can not verify the integrity of the information provided by the miner

### Step 2 - Oracle Network

In this second step, the miners are replaced by an oracle network, with several different nodes. In this configuration, one node is charged to report the information.

**>Problem:** What if sending node lies / cheats?

### Step 3 - Report with signature

When we want to ensure that information has not been altered, the common method is to use digital signature.

Thus, to avoid cheating, we add to the report the different signature from enough nodes (.e.g a threshold).

This principle is put in place by Chainlink oracles with their offchain reporting (OCR) where each node reports its price observation and signs it. When the report is sent by the oracle node to the aggregator contract, the contract verifies that there is enough signature (quorum), see [6. docs.chain.link - off-chain-reporting](https://docs.chain.link/architecture-overview/off-chain-reporting).

As indicated in their [technical paper (16)](https://research.chain.link/ocr.pdf), the algorithm used for signatures is  the standard EdDSA and ECDSA schemes.

> **Problem:** What if sending node goes down?

### Step 4 - Backup 

If the sender node is down, the network should allow for backup transmissions.

With Chainlink, if the node charged to transmit the report fails and does not transmit the report within a determined period,  a new node is chosen through a [round-robin protocol](https://csrc.nist.gov/glossary/term/round_robin_consensus_model) to transmit the report

Reference: [6. docs.chain.link - off-chain-reporting](https://docs.chain.link/architecture-overview/off-chain-reporting)

**Problem:**

We have now our oracle network and we are protected:

- Against a malicious node thanks to the signature, 
- Against a failure with the sender node thanks to the backup.

> But what happens if the data source goes down?



### Step 5 - Source liveness

If the nodes fetch information from the same website/data source, the oracle will no longer be able to retrieve the information if the original data source breaks down.

For example, the exchange FTX was used by several oracles, including Chainlin. When the exchange crashed, the price of the exchange could no longer be considered reliable.

Solution: the oracle has to fetch information from multiple websites to avoid a single point of failure.

- For Chainlink, you have the list of data providers in their [ecosystem page (7)](https://www.chainlinkecosystem.com/ecosystem) and [in this article (8)](https://blog.chain.link/chainlink-price-feeds-secure-defi/). For example, there is [CoinCecko](https://www.chainlinkecosystem.com/ecosystem/coin-gecko) and  [kaio](https://www.chainlinkecosystem.com/ecosystem/kaiko)

During a certain time, there were also CoinMarketCap and CryptoCompare but their name is no longer present in the chainlink ecosystem list.

- For Pyth, they have also several different data providers:  [GTS](https://pythnetwork.medium.com/new-pyth-data-provider-gts-555c4d0e362b), Jane Street, Hudson River Trading, see [9. docs.pyth.network/price-feeds/whitepaper](https://docs.pyth.network/price-feeds/whitepaper)

Problem:

> We have decentralization and good liveness. But now we have a new problem: nodes fetch information from several different sources, what if a node disagree?



### Step 6 - Take the majority

To decide what information to take, we can take data transmitted by the majority! 

**Problem:**  It is simple if the value is a categorical value, for example you want to know if an airplane is on time or not. The answer is True or false, and you can easily take the majority.

But it is more complicated when you have numerical values.

> What if nodes report differing numerical values?



### Step 7 - combining report, median

Instead, the majority, we can take here the [median](https://en.wikipedia.org/wiki/Median),  which is the value separating the higher half from the lower half.

Given a minority of bad values, median is an honest value or bounded by honest values.

- Chainlink uses the median value as indicated in their [documentation (6)](https://docs.chain.link/architecture-overview/off-chain-reporting#how-does-ocr-work)


> The aggregator verifies that a quorum of nodes signed the report and  exposes the **median** value to consumers as an answer with a block  timestamp and a round ID

- The median value is also used by [Pyth Network (10)](https://pyth.network/blog/pyth-price-aggregation-proposal). But they have added a second parameter, the confidence internal, which is the largest value between the distance from the aggregate price to the 25th and 75th percentiles of the node votes.

## Example

### Chainlink 

![chainlink schema]({{site.url_complet}}/assets/article/blockchain/oracle/chainlink-price-feed.png)

1) External data providers (coincecko, GSR, ..) aggregate raw price data from many centralized and decentralized exchanges, accounting for time, volume, and outliers.

2. Chainlink nodes fetch these data provided by these different external data providers. The results are combined in a unique value (median) inside a report
3. Finally, this value is reported to a smart contract, making available for all others smart contracts.    

Reference: [15. chain.link/data-feeds#price-and-market-feeds]( https://chain.link/data-feeds#price-and-market-feeds)   

### Pyth Network

The Pyth oracle is responsible to

1. Maintaining the set of price feeds.
2. Storing the contributions of data providers to each price feed.
3. Combining the individual data providers' prices into a single aggregate price and confidence interval.
4. Performing any additional stateful computations on the resulting price series, such as computing moving averages.

Reference: [11. docs.pyth.network - oracle-program](https://docs.pyth.network/price-feeds/how-pyth-works/oracle-program)

## FAQ

### Node payment

> How do we ensure nodes get paid for service? 

For each request, in addition to the request gas cost, fees are paid to the node.

For price feeds, you have a part which are fee to use since there are sponsorship by different actors and provide view functions callable by anyone, see [12. stackoverflow - Is Chainlink's price reference data free to consume?](https://ethereum.stackexchange.com/questions/87473/is-chainlinks-price-reference-data-free-to-consume)

- Gas cost: This cost is paid back to the transmitter oracle in LINK for fulfilling the request.
- Premium fees: These fees are paid in LINK to compensate nodes for their work and for the maintenance of the FunctionsRouter contract.

### Timely way

> How to ensure that oracle reports are mined in a timely way? 

In the case of Chainlink, the value is updated if the value deviated a specified threshold or when the heartbeat idle time has passed. 

Reference: [13. Chainlink - Check the timestamp of the latest answer](https://docs.chain.link/data-feeds#check-the-timestamp-of-the-latest-answer), [14. ethereum stackexchange - Chainlink Stale Data latestRoundData() guide](https://ethereum.stackexchange.com/questions/154261/chainlink-stale-data-latestrounddata-guide)

### Honest majority of node

> How do we ensure that a majority of nodes are honest?

In the case of Chainlink, there are several different nodes maintained by known organization, for example [swisscom](https://www.chainlinkecosystem.com/ecosystem/swisscom) (telecoms company), [kraken](https://www.chainlinkecosystem.com/ecosystem/kraken) and [Coinbase-cloud](https://www.chainlinkecosystem.com/ecosystem/coinbase-cloud). In principle, these companies have no incentive to behave maliciously because they are known to the public.

## References

- [1.defi-learning course](https://defi-learning.org/f22)
  -  [Oracle Lecture—DeFi course.pdf](https://rdi.berkeley.edu/berkeley-defi/assets/material/COMPRESSED%20Oracle%20Lecture—DeFi%20course.pdf)
- Chainlink
  -  [2.Chainlink Data feeds](https://docs.chain.link/data-feeds)
  - [3.Chainlink data streams](https://docs.chain.link/data-streams)
  - [4.Price Feeds](https://docs.chain.link/data-feeds#price-feeds)
  - [6.docs.chain.link - off-chain-reporting](https://docs.chain.link/architecture-overview/off-chain-reporting)           
  - [7.ecosystem page](https://www.chainlinkecosystem.com/ecosystem)
  - [8.How Chainlink Price Feeds Secure the DeFi Ecosystem](https://blog.chain.link/chainlink-price-feeds-secure-defi/)
  - [13.Chainlink - Check the timestamp of the latest answer](https://docs.chain.link/data-feeds#check-the-timestamp-of-the-latest-answer)
  - [15. chain.link/data-feeds#price-and-market-feeds]( https://chain.link/data-feeds#price-and-market-feeds)
  - [16. research.chain.link/ocr.pdf](https://research.chain.link/ocr.pdf)
  - [docs.chain.link/architecture-overview/architecture-request-model](https://docs.chain.link/architecture-overview/architecture-request-model)
- [5.Arbitrum - Oracle overview](https://docs.arbitrum.io/build-decentralized-apps/oracles/overview)
- Pyth
  - [9. docs.pyth.network/price-feeds/whitepaper](https://docs.pyth.network/price-feeds/whitepaper)
  - [10. Pyth Price aggregation](https://pyth.network/blog/pyth-price-aggregation-proposal)
  - [11. docs.pyth.network - oracle-program](https://docs.pyth.network/price-feeds/how-pyth-works/oracle-program)

- [12. stackoverflow - Is Chainlink's price reference data free to consume?](https://ethereum.stackexchange.com/questions/87473/is-chainlinks-price-reference-data-free-to-consume)
- [14. ethereum stackexchange - Chainlink Stale Data latestRoundData() guide](https://ethereum.stackexchange.com/questions/154261/chainlink-stale-data-latestrounddata-guide)
- [rareskills.io - How Chainlink Price Feeds Work](https://www.rareskills.io/post/chainlink-price-feed-contract)
