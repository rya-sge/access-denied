---
layout: post
title:  Virtual Protocol, create co-ownership AI agents
date:   2024-12-5
lang: en
locale: en-GB
categories: blockchain ethereum defi ai
tags: ai virtual agent
description: Virtuals Protocol is a co-ownership layer for AI agents in gaming and entertainment. These agents can operate across a wide range of applications and games, significantly expanding their revenue surface area. AI agents can be to be tokenized and co-owned via blockchain.
image: /assets/article/blockchain/ai/virtual-protocol/virtual-protocol.png
isMath: false
---

Virtuals Protocol is a co-ownership layer for AI agents in gaming and entertainment. These agents can operate across a wide range of applications and games, significantly expanding their revenue surface area.  These AI agents to be tokenized and co-owned via blockchain.

This article is about one specific point of the protocol:Co-contribution and provenance

> Warning: this article is still in draft state and its content is still mainly taken from the documentation. Its content should become more personal later.
>
> The content is mainly taken from Virtual Protocol documentation, part [Virtual Protocol - Co-contribution and provenance](https://whitepaper.virtuals.io/the-protocol/co-contribution-and-provenance) with a few edits of my own.

The Virtual protocol want to achieve  for

- Model contributors, 
- Data contributors, and 
- IP contributors 

to benefit from their co-contributions and the productive enablement of AI agents in the real world. 

Hence, they have implemented the following:

**Modular Consensus Framework**:

The Virtual Protocol framework provides tools and libraries for building, managing, governing, hosting, and using VIRTUAL agents. Its modular design ensures transparency, flexibility, and customization for stakeholders to meet their specific needs.

**Immutable Contribution Vault** (ICV):

The protocol possesses all validated contributions, represented in the form of **Non-Fungible Tokens (NFTs)**, securely stored within the Immutable Contribution Vault (ICV). This collection of contribution NFTs is a testament to the collaborative efforts and intellectual contributions within the ecosystem.

This diagram explains how Modular Consensus Framework works with Protocol and the components within each stack. 

![virtual-protocol]({{site.url_complet}}/assets/article/blockchain/ai/virtual-protocol/virtual-protocol.png)

[TOC]

## Introduction

The Modular Consensus Framework standardizes and facilitates various processes for different stakeholders:

1. **Contributors**:
   - **Contribution Process**: Contributors submit their proposals through our frontend, utilizing the modular consensus framework. Each proposal generates a contribution NFT regardless of acceptance, authenticating the submission's origin.
   - **State Finality in ICV**: Accepted contributions are minted as service NFTs on-chain and assigned to the appropriate Virtual address within the ICV, validating their integration into the Virtual ecosystem.
2. **Validators**:
   - **Strategy and Resource Allocation**: Liquidity providers determine the strategic direction of the protocol by staking on specific Agents, influencing DAO resource allocation based on staking weightage.
   - **Validation and Finalization**: Utilizing a **Delegated Proof of Stake** mechanism, token holders delegate tokens to qualified validators, who are responsible for finalizing the state of each Agent.

## Global overview

Overview from [Virtual Protocol](https://www.virtuals.io/protocol)

![virtual-architecture](../assets/article/blockchain/ai/virtual-protocol/virtual-architecture.png)

### Virtual Agent Composer

#### Agentic Behavior

This framework defines the AI agents' core capabilities. 

- The Perception Subsystem processes sensory data;
- The Action Executor translates commands into actions, 
- The Strategic Planning Engine optimizes multi-step plans using algorithms like MDPs. The Learning Module refines behavior through reinforcement learning. 
- Additionally, agents manage on-chain activities via the On-Chain Wallet Operator for digital assets and transactions.

#### Long Term Memory Processor

A subsystem dedicated to the storage, retrieval, and management of persistent data structures, such as knowledge graphs or memory embeddings, enabling agents to maintain continuity and contextual awareness across sessions.

#### Stateful AI Runner (SAR)

Stateful AI Runners are servers hosting AI agents' personalities, voices, and visuals. They include Sequencer that processes and links models sequentially or in parallel to achieve desired outcomes; and various Models like LLMs, Text-to-Speech, Audio-to-Facial, Audio-to-Gesture, Music-to-Dance, and Image Generation models for creating multimodal AI agents.

#### Model Storage

A decentralized, distributed storage solution for persisting AI models, ensuring high availability and redundancy.

##### Modular Stateful AI Runner (SAR)

These are modular, containerized instances of SAR, packaged for deployment across heterogeneous virtual environments or GPU clusters, allowing for scalable and flexible integration into different infrastructure ecosystems.

#### Long Term Memory

A component dedicated to archiving historical data, decisions, and interactions. It employs persistent storage technologies to ensure the security and accessibility of data, enabling agents to utilize past experiences in future decisions.

### On-Chain

#### Real-Time Value Streaming

Each AI agent is equipped with an ERC 6551 wallet, enabling continuous revenue accrual and seamless distribution back to the owners.

#### Immutable Contribution Vault

Users can upload custom models and datasets, securely stored in the Immutable Contribution Vault (ICV) on the blockchain. The Model Enrichment Pipeline enhances AI models with new data, secured through cryptographic proofs and stored immutably. The Voice and Text Data Repositories within the ICV ensure data integrity and provenance through decentralized blockchain storage.

----

## Decentralized contribution

Decentralized contribution allows external contributors to help drive exponential growth by enhancing the capabilities of AI agents. Contributors can improve various aspects of an agent’s functionality, and successful contributions are minted as NFTs and transferred to the contributor. This serves as proof of contribution and facilitates reward distribution. 

### Overview

The contribution process is streamlined for contributors to easily submit their models or datasets through our platform. Once submitted, the following actions take place:

![virtual-protocol-decentralized-contribution]({{site.url_complet}}/assets/article/blockchain/ai/virtual-protocol/virtual-protocol-decentralized-contribution.png)

**1. Contribution NFT Creation with Metadata File**

For each contribution, an NFT is minted containing detailed metadata about the contribution (e.g., description, version, type). 

This NFT is automatically published on **IPFS** to ensure decentralized and permanent storage of contribution details.

![virtual-protocol-contribution-nft]({{site.url_complet}}/assets/article/blockchain/ai/virtual-protocol/virtual-protocol-contribution-nft.png)

**2. Smart Contract Interaction**

The entire process, from submission to NFT minting, is managed by smart contracts. These smart contracts handle on-chain verification of the contribution, ensuring that all contributions are recorded and tracked on the blockchain.

**3. Ownership and Access Rights**

Ownership of the Contribution NFT grants the contributor certain rights, including control over the work and any rewards generated by it. Transferring the NFT to another party will transfer these ownership rights, including the ability to claim rewards or incentives tied to the contribution

### Contributing to Core Capabilities

Each agent’s capabilities are modularized, making it easier for contributors to enhance specific areas. Contributions can target one or more of the following core capabilities:

- Cognitive core
- Voice core
- Visual Core
- Futures core

See also [whitepaper.virtuals.io - agent-contribution#contributing-to-core-capabilities](https://whitepaper.virtuals.io/developer-documents/agent-contribution#contributing-to-core-capabilities)

### Cognitive Core

The Cognitive Core is the central component  of a VIRTUAL agent, acts as its "brain" and powered by a Large Language Model (LLM). It defines the agent's intelligence, personality, and task-execution abilities. Contributions to this core can involve fine-tuning large language models (LLMs) or providing domain-specific datasets.

#### Large Language Models (LLMs) 

The current LLM leverages on open sourced models. Each Virtual agent personality and central intelligence are being incorporated using the approach below:

- **Personality Development**

  The backstory, personality, and traits of a Virtual agent are crafted using the **Retrieval-Augmented Generation (RAG)** method. This combines a language model's generative power with a retrieval system to pull relevant knowledge, enabling diverse, lifelike, and engaging interactions.

- **Central Intelligence**

  For Virtual agents with substantial datasets, direct finetuning of open source model is employed. 

  - This process involves adjusting the model's parameters specifically for the large dataset, enhancing its ability to respond accurately and effectively in the context of the Virtual agent's designated domain. 
  - Instruction-based finetuning is applied as necessary. This involves training the model to follow specific instructions or guidelines, further refining its responses and actions according to predefined rules or objectives.  
  

If the dataset is smaller, the information is stored in a vector database. This data is then fed into the model using the RAG method, allowing the AI to access this more limited set of information efficiently.

#### Data Pre-processing

Relevant datasets include text, videos, and audio, but text-based Large Language Models (LLMs) primarily rely on text data. Non-text formats, like videos or audio, must be transcribed into text and processed before training. Standard data processing rules will be applied prior to model training.

- **Data Cleaning**: In this step, datasets are cleaned to remove any noise and nullities. Data rules are applied to maintain data integrity and improve data quality.
- **Data Transformation**: Datasets undergo transformation and standardization to become interpretable and usable for model training.

#### Remembering user conversation for better user experience

The Virtual is engineered with a persistent memory system, aiming to closely mimic human-like memory capabilities and facilitate personalized interactions with users. To accomplish this, the system addresses two primary challenges:

- **User and Conversation Identification and Recall**:

The system is designed to reliably identify each user and their respective conversations, ensuring the ability to remember and reference these interactions accurately.

- **Long Conversation Storage and Memory Processing**:

Managing and storing extended conversations presents a challenge in terms of memory processing. The system is tailored to handle these long dialogues efficiently (how ?).

#### Unique Identifier

Each user engaging with a Virtual is assigned a unique identifier. This identifier is pivotal for maintaining conversation continuity and user specificity.

### Voice Core

This core governs the voice of the agent, allowing it to communicate with users. 

VIRTUAL Agent is designed to have a distinct voice that aligns with its personality and role. Therefore, training the voice models is a critical process to ensure that each character's voice is not only realistic but also consistent with their designed persona.

#### Modules

There are two modules used in Voice Core. 

**Speech-to-text module**: STT module is trained with a wide range of voice data. This training allows the module to accurately transcribe various accents, dialects, and speech patterns, making it versatile and reliable in different user scenarios.

**Text-to-speech module**: For the TTS module, the protocol utilizes Variational Inference for Text-to-Speech (VITS) training. 

VITS is known for its ability to produce high-quality, natural-sounding speech. This training is particularly important for the platform, as each AI character requires a specific voice that matches its unique personality and characteristics. 

The VITS model allows for this level of customization and quality in voice synthesis.

#### Techniques used for data preprocessing

Before model is trained, data processing is performed. 

For optimal machine learning performance, audio data must follow these standards:

- **format consistency** (all files as WAV, 22050 Hz, mono) prevents variability that can confuse models  and degrade performance; 
- **sampling rate normalization** (22050 Hz): the sampling rate determines how many samples per second are in the audio file. A standard sampling rate like 22050 Hz is often used because it's sufficient to capture the frequency range of human speech while keeping the file size manageable. It also aligns with the Nyquist theorem for capturing all frequencies up to 11025 Hz, which covers most of the human hearing range.
- **mono channel**: Converting stereo or multi-channel audio files to mono ensures that the model trains on a single channel, which simplifies the learning process. 

### Visual Core

The Visual Core gives the agent a 3D visual appearance. 

- VIRTUAL Agent comes with a rigged 3D character (MMD file format) with animation and facial expressions.
- With the output, dApps can utilise frontend frameworks such as ThreeJS MMD loader to display the 3D Characters. 

Contributions to this core enhance how the agent looks and moves, providing more immersive interactions.

- **Facial Core**: This aspect handles the agent's facial expressions. Contributors can provide models or data that translate the agent's voice into appropriate facial movements, allowing it to show emotion during interactions.
- **Animation Core**: This module allows the agent to perform gestures based on voice inputs. Contributions can include gesture data or animation models that synchronize body movements with speech, giving the agent a more natural, lifelike presence.

### Future Cores / Functional Agents

Future Cores like Skillset Cores allow AI to own other skillsets for example, image recognition, image generation, multilingual responses and many more. 



------

## Immutable Contribution Vault

### Why this?

1. **Transparency**: The Virtuals Protocol has also taken several measures to be transparent:
   - By utilizing a public blockchain, the Virtuals Protocol guarantees that the entire development process is transparent and accountable. 
   - This level of openness is crucial for preventing misuse and maintaining the integrity of the system, as it allows for the tracking and verification of every output produced by the AI.
2. **Composability**: The Virtuals Protocol employs the principle of composability to encourages a collaborative environment where developers and creators can build upon and enhance the work done within the protocol. 
3. **Attribution**: Recognizing and incentivising each contribution is a key aspect of the Virtuals Protocol. This is achieved through an on-chain registry that turns individual contributions into unique digital assets, represented as Non-Fungible Tokens (NFTs). 
   - These NFTs serve not only to acknowledge the unique value of each contribution but also to provide a precise way to measure its impact. 
   - This system ensures that rewards are fairly distributed, corresponding to the significance of each contributor's input.

------

**Immutable Contribution Vault (ICV): A Multilayered On-Chain Repository**

The ICV represents a core component of the Virtuals Protocol, functioning as a protocol-owned vault that archives all historically approved contributions of VIRTUAL agents on-chain. This smart contract wallet allows transparency and historical tracking in the Virtuals ecosystem.

![virtual-protocol-immutable-contribution-vault]({{site.url_complet}}/assets/article/blockchain/ai/virtual-protocol/virtual-protocol-immutable-contribution-vault.png)

**Multilayered Structure of the ICV**

1. **First Layer - Smart Contract Wallet Ownership (the ICV)**:

The foundational layer is a smart contract wallet, known as ICV, that asserts ownership over all subsequent layers, ensuring unified and secure management.

2. **Second Layer - Individual VIRTUAL agent as ERC-6551 NFTs**:

Each VIRTUAL agent is minted and represented as an [ERC-6551](https://eips.ethereum.org/EIPS/eip-6551) NFT, which also serves as a unique wallet address. This dual functionality underscores the fusion of identity and transactional capability in the Virtual ecosystem.

3. **Third Layer - Core Components of VIRTUAL agents**:

Beneath each VIRTUAL agent, five core elements are housed: cognitive, voice & visual cores. These cores will be registered in the smart contract.

4. **Fourth Layer - Service NFTs within Each Core**:

Within each Virtual agent, approved contributions are stored in the form of service NFTs, and the relationship between these service NFTs and the Core is registered through a smart contract.

**Key Functions and Benefits of the ICV**

- **Real-Time and Historical Insights**: The ICV elegantly presents the current state of each VIRTUAL agent and traces its historical evolution on-chain. This feature is crucial for both provenance and root cause analysis across every module within the Virtuals ecosystem.
- **Transparency and Composability**: By open-sourcing the codebase models for VIRTUAL agents, the ICV facilitates transparency and composability, allowing developers and contributors to build upon and integrate with existing VIRTUAL agents seamlessly.

### ERC-6551: Non-fungible Token Bound Accounts

Each VIRTUAL agent is minted and represented as an [ERC-6551](https://eips.ethereum.org/EIPS/eip-6551), but what is this standard ?

#### ERC-721 limitation

NFTs represented as  [ERC-721](https://eips.ethereum.org/EIPS/eip-721) cannot act as agents or associate with other on-chain assets. This limitation makes it difficult to represent many real-world non-fungible assets as NFTs. For example:

- A character in a role-playing game that accumulates assets and abilities over time based on actions they have taken
- An automobile composed of many fungible and non-fungible components
- An investment portfolio composed of multiple fungible assets

#### ERC-6551 solution

This standard aims to give every NFT the same rights as an Ethereum user. This includes the ability to self-custody assets, execute arbitrary operations, control multiple independent accounts, and use accounts across multiple chains. By doing so, this proposal allows complex real-world assets to be represented as NFTs using a common pattern that mirrors Etherem’s existing ownership model.

This is accomplished by defining a singleton registry which assigns unique, deterministic smart contract account addresses to all existing and future NFTs. Each account is permanently bound to a single NFT, with control of the account granted to the holder of that NFT.

Reference: [eips.ethereum.org/EIPS/eip-6551](https://eips.ethereum.org/EIPS/eip-6551)

## Reference

- Official documentation:
  - [Whitepaper](https://whitepaper.virtuals.io/)
  - [Virtual Protocol](https://www.virtuals.io/protocol)
- [Shoal - Virtuals Protocol: Launching AI Agents with the Pump.fun Model](https://www.shoal.gg/p/virtuals-protocol-launching-ai-agents)
- [0xCygaar Tweet](https://x.com/0xCygaar/status/1864182285278355881?t=LBINpmIuUA8rpnzxS2nNmw&s=35)
- [Eli5Defi Tweet](https://x.com/eli5_defi/status/1765330652470338018)
- ChatGPT to summarize some paragraph