---
layout: post
title:  Introduction to Arweave, a decentralized storage layer
date:   2023-11-14
lang: en
locale: en-GB
categories: blockchain 
tags: blockchain arweave storage
description: Arweave is a network acting as a decentralized storage layer to upload files permanently with a single payment.  
image: /assets/article/blockchain/arweave-logo.png
---

## Introduction

Store files directly in the blockchain is a good way to guarantee the immutability of files and their accessibility.

But there is a problem, as always, most  blockchains are not designed to store files...

This is for example the case for Ethereum, and it is the reason why for NFT, the JSON file containing the NFT metadata is not directly stored on blockchain.

Here comes a solution: decentralized storage network like IPFS or Arweave...

[Arweave](https://www.arweave.org/) is a network acting as a decentralized storage layer to upload files permanently with a single payment. 

In Arweave, you can store smart contracts, web applications, and websites.

The main selling argument is, you only pay once, and the files are stored forever. 

## Architecture

The [permaweb](https://arwiki.wiki/#/en/the-permaweb), Arweave’s network of decentralized websites and applications, are composed of two major parts:

- The application itself, which is uploaded to Arweave.
- Gateways,  content delivery servers, which are like the "front door" to the Permaweb.

## Consensus

Arweave introduces a new consensus mechanism called **Proof-of-Access**  (PoA). Unlike traditional Proof-of-Work (PoW) or Proof-of-Stake (PoS)  mechanisms, PoA doesn't rely on computational power or stakeholding.  

Instead, it rewards miners based on the amount of data they store and  the length of time they retain it. 

## Uploaded files

Files uploaded to Arweave are stored on thousands of computers hosted by people across the world. Smart contracts, web applications, and websites can be hosted on Arweave.

To protect your privacy,  files can also be encrypted. In this case, only you can read the contents of your files and even the miners can not access the decrypted files. 

Warning: The fact that your files will on Arweave permanently means it is possible that a secure method to encrypt your files will not be secure in the future, e.g. in the case of the appearance of a quantum computer.

## Cost

Miners store files uploaded to Arweave in return for **$AR**, the cryptocurrency securing the Arweave network. Thus, it costs a small amount of $AR to upload and store files and this cost changes based on the current demand. 

To offer permanent storage, Arweave uses a concept called [**storage endowment**](https://arwiki.wiki/#/en/storage-endowment). It is an estimation of how the price of storage will decrease in the future to distribute appropriate quantities of tokens to miners over time, in order to guarantee the perpetual storage of arbitrary quantities of data.

The goal of this mechanism is to distribute  appropriately quantities of tokens to miners over time, in order  to encourage miners to keep datas (perpetual storage).

Of the $AR fees paid to upload files, 5% goes to the miners while the other 95% goes into a storage endowment. 

## Bundling transactions

Data can be uploaded directly to Arweave, or posted through a layer 2 network typically referred to as a bundler.

A bundler groups the transactions uploaded on its service into a  “bundle”, which  is eventually settled on the base Arweave network. Bundles offers several advantages to Arweave:

- **Instant availability** - bundlers cache your data while it is waiting to be confirmed on Arweave.
- **Reliability** - bundlers will continually attempt to post your data to Arweave to avoid failure upload.
- **Scalability** - Bundles end up as only a single item in an Arweave block allowing Arweave to scale.

Popular bundling services, such as [Irys](https://irys.xyz) (previously Bundlr), also allow users to pay in a multitude of different cryptocurrencies such as $ETH and $SOL

## Smart Contract

The protocol to support smart contracts on Arweave is called SmartWeave [Protocol](https://academy.warp.cc/docs/sdk/advanced/smartweave-protocol)

Smart contracts can be written in AssemblyScript, Go & Rust and 

All the data (the contracts' code and interactions) are kept on-chain, but the evaluation of the state happens off-chain. This has a huge advantage in terms of scalability (in comparison to monolithic systems - like Ethereum) - as the execution layer may be developed and scaled independently of the main (consensus) layer.

References:

- [academy.warp.cc/docs/sdk/overview](https://academy.warp.cc/docs/sdk/overview)
- [warp.cc/](https://warp.cc/)

## Challenges & risk

- Even if Arweave promises permanent storage, if the network is shut down, the files will be probably no longer available.

- Of course, there is always a risk that the rewards will no longer be sufficient to encourage minors to store data...

- A second point is the risk of uploading files which can not be deleted (privacy !!!). Once it is uploaded, you have no longer control over the files.

- As already said, the fact that your files will be on Arweave permanently means it is possible that a secure method to encrypt your files will not be secure in the future, e.g. in the case of the appearance of a quantum computer.

- Lastly, Arweave could be used to upload illegal content which poses a reputational risk.



## References

- This lesson from LearnWeb3: [https://learnweb3.io/minis/what-is-arweave](https://learnweb3.io/minis/what-is-arweave)
- [warp - Smart contracts
   on Arweave](https://warp.cc/)
- [academy.warp.cc/docs/sdk/overview](https://academy.warp.cc/docs/sdk/overview)
- [arwiki.wiki/#/en/main](https://arwiki.wiki/#/en/main)
- ChatGPT with the input

*Write a short article (about 500-1500) words on Arweave, the  decentralized storage layer. Divide your article in topic with title*

