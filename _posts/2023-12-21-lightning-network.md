---
layout: post
title:  "Main Concepts Behind the Lightning Network "
date:   2023-12-21
lang: en
locale: en-GB
categories: blockchain 
tags: blockchain bitcoin lightning-network htlc channel routing onion
description: This article lists and describes the main concepts behind the Lightning Network (LN), a layer-2 built on the Bitcoin blockchain.
image: /assets/article/blockchain/bitcoin/560px-Bitcoin_lightning_logo.svg.png
---

This article lists and describes the main concepts behind the Lightning Network, a layer-2 built on the Bitcoin blockchain.

The concepts are organised in five topics: *Fundamentals and Architecture, Node Operation and Security, Privacy and Routing, Channel management*, *Network Analysis and Tools*

## Short presentation

Transactions on the Bitcoin blockchain can be expensive (AVG ~8$) and their confirmations are slow ([~10 minutes](https://coinmarketcap.com/academy/article/how-long-does-a-bitcoin-transaction-take)) 

**Lightning Network (LN)** aims to offer faster and cheapest transactions, in seconds rather than minutes,  and for a few cents.

LN is based on the following technologies: 

- Private channels between two parties, a 2-of-2 multisignature account, that enable off-chain transactions. 
- Hash Time-lock Contracts: HTCL reduces the counterparty risk by locking the funds in an escrow that requires for unlocking the hash of a secret number or unlocked after a date limit.

In short, the LN works in three steps :

1. **Opening a payment channel**:  the parties which want to perform transactions together open a channel between them by creating a special Bitcoin transaction.

2. **Transacting off-chain**: Once the channel is opened, the two parties can use it to perform payments between them without recording transactions on the main blockchain.
3. **Settling on the blockchain**: When one party wishes to close the channel, the final state of their transactions is recorded on the main Bitcoin blockchain.

Reference: [bitinfocharts.com - bitcoin-transactionfees.html](https://bitinfocharts.com/comparison/bitcoin-transactionfees.html), [What is Lightning Network and How Does it Work With Bitcoin?](https://trustmachines.co/learn/what-is-lightning-network/)

## Fundamentals and Architecture

### Lightning Network

The lightning network is a second-layer (or layer-2) solution for the Bitcoin blockchain, aiming to enhance transaction speed and reduce fees by conducting off-chain transactions through payment channels.

### Payment Channels

Private channels between two parties, a 2-of-2 multisignature account, that enable off-chain transactions. Participants can transact without recording every transaction on the main Bitcoin blockchain until the channel is closed. 

Reference: [docs.lightning.engineering - Payment channel](https://docs.lightning.engineering/the-lightning-network/payment-channels/etymology#docs-internal-guid-def45c7d-7fff-45bc-4e4e-ad87940fad49)

### Hash Time-lock Contracts (HTLC)

HTLC is a concept to make the lightning payment atomic and secure. HTCL reduces the counterparty risk by locking the funds in an escrow that requires for unlocking 

- A cryptographic passphrase, the hash of a secret number  

Or

- After a certain amount of time has passed

References: 

[docs.lightning.engineering - Hashed Timelock Contract (HTLC)](https://docs.lightning.engineering/the-lightning-network/multihop-payments/hash-time-lock-contract-htlc), [Hashed Timelock Contract (HTLC): Overview and Examples in Crypto](https://www.investopedia.com/terms/h/hashed-timelock-contract.asp)

## Node Operation and Security

### Lightning Network Nodes

Participants in the Lightning Network responsible for maintaining payment channels and facilitating transactions by routing payments through the network.

### Lightning Network Daemon (LND)

One of the implementations of the Lightning Network protocol. LND allows users to run Lightning nodes and participate in the Lightning Network.

Reference: [lightning.engineering - LND](https://lightning.engineering/api-docs/api/lnd/)

### Watchtowers

Services that monitor Lightning Network channels for potential fraud. They act as safeguards, intervening if one party attempts to close a channel dishonestly.

References: 

- [docs.lightning.engineering - watchtowers](https://docs.lightning.engineering/the-lightning-network/payment-channels/watchtowers)
- [voltage.cloud - Watchtowers on Lightning Network](https://voltage.cloud/blog/lightning-network-faq/watchtowers/)

## Privacy and Routing

#### Onion Routing

The Onion routing is a technique used in the Lightning Network to make the transmission between the different nodes private and secure. Payments are encrypted in layers, and each node in the network can only decrypt its specific layer, ensuring privacy and security.

The goal is to restrict the information known by a node to the following cases:

- A node only knows their predecessor and successor nodes.
- A node don’t know the length of the route.
- A node do not know its position within the route.

The version used by the Lightning Network is a variation of the Onion routing technolgy employed by Tor and it is called [Sphinx](http://www.cypherpunks.ca/~iang/pubs/Sphinx_Oakland09.pdf).

References:

[What is Onion Routing & How does it work?](https://voltage.cloud/blog/lightning-network-faq/what-is-onion-routing-how-does-it-work/), [lightning-onion](https://github.com/lightningnetwork/lightning-onion)

#### Trampoline Payments

An optimization technique allowing payments to efficiently traverse the network by hopping through well-connected nodes.

*How it works ?* The spender routes the payment to an intermediate node who can select the rest of the path to the final receiver. It is a solution for these different challenges affecting potentially a node :

- Miss updates about the payment channels network.
- Limited storage and computing power  to track the network’s structure

Reference: [bitcoinops.org - Trampoline payments](https://bitcoinops.org/en/topics/trampoline-payments/), [UNDERSTANDING TRAMPOLINE PAYMENTS](https://voltage.cloud/blog/lightning-network-faq/what-are-trampoline-payments-on-lightning-network/)

#### Routing Fees

Fees paid to Lightning Network nodes for routing payments. Nodes charge fees for facilitating transactions through their channels.

Reference: [Channel Fees](https://docs.lightning.engineering/lightning-network-tools/lnd/channel-fees)



## Channel Management

#### Channel Liquidity

The amount of funds available for transactions within a payment channel. Balancing liquidity is essential for ensuring smooth transaction routing across the Lightning Network.

*Inbound liquidity*: amount of bitcoin that the user is able to receive over a lightning channel. 

*Outbound liquidity*: amount of bitcoin that the user is able to send over a lightning channel.

Reference: [bitcoin.design - Lightning liquidity](https://bitcoin.design/guide/how-it-works/liquidity/)

#### Channel Funding

The process of committing funds to a payment channel to initiate off-chain transactions. Both parties contribute to the channel's initial funding.

Reference: [Lifecycle of a Payment Channel - Opening a channel](https://docs.lightning.engineering/the-lightning-network/payment-channels/lifecycle-of-a-payment-channel#docs-internal-guid-9d39ae87-7fff-839a-c0ec-60c6ea73aa0b)

#### Channel Closing

The process of settling the final state of a payment channel on the Bitcoin blockchain. Channels can be closed cooperatively or unilaterally.

Reference: [Lifecycle of a Payment Channel - Closing a channel](https://docs.lightning.engineering/the-lightning-network/payment-channels/lifecycle-of-a-payment-channel#docs-internal-guid-05067e10-7fff-49ae-141e-183d040b5b8c)

#### Splicing

The ability to adjust the amount of funds in a Lightning Network channel without closing and reopening it. Splicing allows users to add or remove funds dynamically.

[WHAT IS SPLICING AND HOW DOES IT WORK?](https://voltage.cloud/blog/lightning-network-faq/what-is-splicing-lightning-network-how-it-works/), [Lightning Splicing](https://lightningsplice.com/splicing_explained.html)

#### Channel Rebalancing

The process of adjusting the distribution of funds within a payment channel to ensure optimal liquidity. Rebalancing helps in maintaining efficient payment routing.

if a LN node has not enough [outbound liquidity](https://voltage.cloud/blog/lightning-network-faq/why-do-lightning-nodes-need-inbound-and-outbound-liquidity/) to route a payment, it can use different methods to rebalance its liquidity in order to be able to route payment again.

Reference: [How Lightning Channel Rebalances Work](https://voltage.cloud/blog/lightning-network-faq/how-lightning-node-channel-rebalancing-works-simplified/), [How To Rebalance A Lightning Channel](https://thebitcoinmanual.com/articles/rebalance-ln-channel/)

### **Network Analysis and Tools:**

#### Lightning Network Explorer

Since the lightning transactions are private, there are no public explorer as for Bitcoin mainet (e.g [blockchain.com](https://www.blockchain.com/explorer)). Nevertheless, you have online tools whih track the number of nodes, channels and the total capacity, e.g [mempool.space/lightning](https://mempool.space/lightning)

# Reference

- [docs.lightning.engineering/](https://docs.lightning.engineering/)
- [voltage.cloud/](https://voltage.cloud/)
- [bitinfocharts.com/comparison/bitcoin-transactionfees.html](https://bitinfocharts.com/comparison/bitcoin-transactionfees.html)
- [How Long Does a Bitcoin Transaction Take?](https://coinmarketcap.com/academy/article/how-long-does-a-bitcoin-transaction-take)
- [dci.mit.edu/lightning-network](https://dci.mit.edu/lightning-network)
- [What You Need to Know About Our Bitcoin Lightning Network Integration](https://www.binance.com/en/blog/ecosystem/what-you-need-to-know-about-our-bitcoin-lightning-network-integration-9199943838366033281)
- ChatGPT with the input 

*Make a list of 20 concepts related to the Bitcoin lightning network and provide for each of them a short description. Regroup them in difference topics*

- Cover image: [commons.wikimedia.org/wiki/File:Bitcoin_lightning_logo.svg](https://commons.wikimedia.org/wiki/File:Bitcoin_lightning_logo.svg)