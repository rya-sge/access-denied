---
layout: post
title: Bittensor, decentralized production of artificial intelligence
date:   2024-12-16
lang: en
locale: en-GB
categories: blockchain
tags: machine-learning bittensor tao
description: Bittensor is an open source platform on which you can produce competitive digital commodities. These digital commodities can be machine intelligence, storage space, compute power, protein folding, financial markets prediction, and many more. 
image: 
isMath: false
---

Bittensor is an open source platform on which you can produce competitive digital commodities. These digital commodities can be machine intelligence, storage space, compute power, protein folding, financial markets prediction, and many more. 

Providers of digital commodities are rewarder in **TAO**, the native token of Bittensor

> Warning: this article is still in draft state and its content is still mainly taken from the documentation. Its content should become more personal later.

![Simplified Bittensor Network](https://docs.bittensor.com/img/docs/bittensor-block-diagram.svg)

[TOC]



## Introduction

The Bittensor ecosystem consists of the following three components (refer to the above diagram):

1. **An incentive-based competition mechanism**: You can either create your custom incentive mechanism for your own competition or join a competition that already exists in the Bittensor ecosystem. Each such incentive-based competition market is called a **subnet**. Subnets constitute the core of the Bittensor ecosystem.

Example:

For example, the [text prompting subnet](https://github.com/opentensor/prompting), developed by the Open Tensor foundation, incentivizes subnet miners that produce the best prompt completions in response to the prompts sent by the subnet validators in that subnet.

2. A **blockchain** that runs the above subnets and supports their proper functioning so that the incentive-based competition market is decentralized, is permissionless and is collusion-resistant, i.e., is resistant to market manipulation.

3. The **Bittensor API** that connects all the essential elements within the above two components, and also connects the subnets and the blockchain.

![https://docs.bittensor.com/img/docs/bittensor-block-diagram.svg](https://docs.bittensor.com/img/docs/bittensor-block-diagram.svg)



## Participating in Bittensor ecosystem

You participate in the Bittensor ecosystem by participating in a subnet.

See [docs.bittensor.com#participating-in-bittensor-ecosystem](https://docs.bittensor.com/learn/introduction#participating-in-bittensor-ecosystem)

### How a subnet works

Subnets exist to operationalize the incentive-based competition mechanisms. See the below diagram.

![Simplified Bittensor Network](https://docs.bittensor.com/img/docs/subnet-high-level.svg)

Here is an explanation of the primary components of a subnet. Note that this explanation is **highly simplified**, and is intended only to convey the essential conceptual core of the subnet.

The item numbers below correspond to the numbers in the above diagram.

1. A subnet is defined by the incentive mechanism it supports. The incentive mechanism is unique to the subnet.
2. Entities in the subnet, called **subnet miners**, each perform a useful task, i.e., solve some problem, as defined in the incentive mechanism of the subnet.
3. Separate entities in the same subnet, called **subnet validators**, each independently evaluate the task performed by the subnet miners.
4. The subnet validators then each express their opinion on the quality of the miners. These opinions of the subnet validators are then provided as a collective input to the **Yuma Consensus** mechanism on the blockchain by using the Bittensor API.
5. The output of the Yuma Consensus mechanism from the blockchain will then determine how the rewards for the subnet miners and subnet validators are to be distributed. **The rewards are in the form of TAO tokens.**

When you participate in the Bittensor ecosystem, most of your activity occurs within the subnet you participate in. This is true whether you created your own incentive mechanism, i.e., your own subnet, or joined an existing subnet either as a subnet validator or as a subnet miner. Nevertheless, you can interact with other subnet entities.

You can use Python with the Bittensor API to write your incentive mechanism.

See [docs.bittensor.com/learn/introduction#how-a-subnet-works](https://docs.bittensor.com/learn/introduction#how-a-subnet-works)

### Bittensor personas

You can participate in the Bittensor ecosystem as the following personas:

| Personas            | Description                                                  |
| ------------------- | ------------------------------------------------------------ |
| Subnet owner        | When you only want to create a subnet but transfer the tasks of operating the subnet to others. |
| Subnet validator    | When you are responsible for running the subnet validator.<br />each validator independently evaluates the task performed by the subnet miners. |
| Subnet miner        | When you are responsible for running the subnet miner.       |
| Blockchain operator | When you run the blockchain. This mostly applies during the offline testing of your subnet and your incentive mechanism, when you need a local emulation of the Bittensor blockchain because you are disconnected from the Bittensor network. |

See [docs.bittensor.com/learn/introduction#bittensor-personas](https://docs.bittensor.com/learn/introduction#bittensor-personas)

### Participating in a subnet

When creating a subnet you should always start by:

1. Developing and testing the subnet incentive mechanism **locally**;
2.  Then connecting to the Bittensor **testchain**;
3.  And finally go live by connecting to the Bittensor **mainchain**. 

See the below conceptual deployment diagram showing the three stages.

Testing the incentive mechanism means running one or more validators and miners to ensure that rewards are distributed in the intended way.

![Simplified Bittensor Network](https://docs.bittensor.com/img/docs/subnet-deploy-stages.svg)

See [docs.bittensor.com/learn/introduction#participating-in-a-subnet](https://docs.bittensor.com/learn/introduction#participating-in-a-subnet)

## Bittensor Building Blocks

The Bittensor API provides basic building blocks you can use to develop your incentive mechanism. This section presents:

- An overview of a subnet.
- Introduction to the Bittensor building blocks.

### Subnet

A subnet closely follows how a classical feedforward neural network is connected. Consider the below diagram showing a comparison of a classical neural network with a subnet.

![Incentive Mechanism Big Picture](https://docs.bittensor.com/img/docs/building-blocks-first.svg)

Reference: [docs.bittensor.com/learn/bittensor-building-blocks#subnet](https://docs.bittensor.com/learn/bittensor-building-blocks#subnet)

#### Node (Neuron)

A node in a neural network is represented in a Bittensor subnet as either a subnet validator or a subnet miner. A node is also referred as a **neuron** in a subnet terminology. A neuron is the basic computing node in a Bittensor subnet.

See [Minimum compute requirements](https://github.com/opentensor/bittensor-subnet-template/blob/main/min_compute.yml) for compute, memory, bandwidth and storage requirements for a subnet node, i.e., for a subnet neuron.

- The classical neural network graph (shown on the left) is bipartite, i.e., a node in the input layer is connected only to a node in the next layer (hidden layer). A subnet graph (shown on the right) is also bipartite. Hence:
  - A subnet validator in a subnet is only connected to a subnet miner.
  - No two subnet validators are connected. Similarly, no two subnet miners are connected.
- In the classical neural network, the inputs from the external world are connected only to the input layer, and the hidden nodes are isolated from the external world (hence, "hidden"). Similarly, in a Bittensor subnet:
  - Inputs from the external world can connect only to the subnet validators.
  - Only subnet validators are allowed to connect to subnet miners, hence isolating subnet miners from the external world.
- **Many-to-many bidirectional**: 

Notice that in the classical neural network shown on the left, the connection from input layer to the hidden layer is only feedforward. 

However, in a Bittensor subnet, shown on the right, a subnet miner can directly communicate to the subnet validator. This bidirectional communication between a subnet validator and a subnet miner forms the core of a protocol in an incentive mechanism. This closely resembles the architecture of a [Restricted Boltzmann Machine (RBM)](https://en.wikipedia.org/wiki/Restricted_Boltzmann_machine).

### Neuron-to-neuron communication

Neurons exchange information by:

- Encapsulating the information in a Synapse object.
- Instantiating server (Axon) and client (dendrite) network elements and exchanging Synapse objects using this server-client (Axon-dendrite) protocol. See the below diagram.

#### Summary

| Term      | Description                                                  |
| --------- | ------------------------------------------------------------ |
| Neuron    | A neuron is the basic computing node in a Bittensor subnet.  |
| Synapse   | Synapse is a data object. Subnet validators and subnet miners use Synapse data objects as the main vehicle to exchange information. T |
| Axon      | Instantiating server                                         |
| Dentrite  | client network elements                                      |
| Metagraph | A metagraph is a data structure that contains comprehensive information about current state of the subnet. |
| Subtensor | A subtensor is a Bittensor object that handles the interactions with the blockchain, whether the chain is local or testchain or mainchain. |



#### Schema



![Incentive Mechanism Big Picture](https://docs.bittensor.com/img/docs/second-building-blocks.svg)

See [docs.bittensor.com/learn/bittensor-building-blocks#neuron-to-neuron-communicatio](https://docs.bittensor.com/learn/bittensor-building-blocks#neuron-to-neuron-communicatio)n

#### Axon

The `axon` module in Bittensor API uses FastAPI library to create and run API servers. For example, when a subnet miner calls,

```python
axon = bt.axon(wallet=self.wallet, config=self.config)
```

then an API server with the name `axon` is spawned on the subnet miner node. This `axon` API server receives incoming Synapse objects from subnet validators, i.e., the `axon` starts to serve on behalf of the subnet miner.

Similarly, in your subnet miner code you must use the `axon` API to spawn an API server to receive incoming Synapse objects from the subnet validators.

See [docs.bittensor.com/learn/bittensor-building-blocks#axon](https://docs.bittensor.com/learn/bittensor-building-blocks#axon)

#### Dendrite

Axon is a **server** instance. Hence, a subnet validator will instantiate a `dendrite` **client** on itself to transmit information to axons that are on the subnet miners. For example, when a subnet validator runs the below code fragment:

```python
    responses: List[bt.Synapse] = await self.dendrite(
        axons=axons,
        synapse=synapse,
        timeout=timeout,
    )
```



then the subnet validator:

- Has instantiated a `dendrite` client on itself.
- Transmitted `synapse` objects to a set of `axons` (that are attached to subnet miners).
- Waits until `timeout` expires.

See https://docs.bittensor.com/learn/bittensor-building-blocks#dendrite

### Synapse

Synapse is a data object. Subnet validators and subnet miners use Synapse data objects as the main vehicle to exchange information. The Synapse class inherits from the `BaseModel` of the Pydantic data validation library.

For example, in the [Text Prompting Subnet](https://github.com/opentensor/prompting/blob/6c493cbce0c621e28ded203d947ce47a9ae062ea/prompting/protocol.py#L27), the subnet validator creates a Synapse object, called Prompting, with three fields. The fields `roles` and `messages` are set by the subnet validator during the initialization of this Prompting data object, and they cannot be changed after that. A third field, `completion`, is mutable. When a subnet miner receives this Prompting object from the subnet validator, the subnet miner updates this `completion` field. The subnet validator then reads this updated `completion` field.

See [docs.bittensor.com/learn/bittensor-building-blocks#synapse](https://docs.bittensor.com/learn/bittensor-building-blocks#synapse)

### Metagraph

A metagraph is a data structure that contains comprehensive information about current state of the subnet. When you inspect the metagraph of a subnet, you will find detailed information on all the nodes (neurons) in the subnet. A subnet validator should first sync with a subnet's metagraph to know all the subnet miners that are in the subnet. The metagraph can be inspected without participating in a subnet.

See [docs.bittensor.com/learn/bittensor-building-blocks#metagraph](https://docs.bittensor.com/learn/bittensor-building-blocks#metagraph)

## Subtensor

A subtensor is a Bittensor object that handles the interactions with the blockchain, whether the chain is local or testchain or mainchain.

See [docs.bittensor.com/learn/bittensor-building-blocks#subtensor](https://docs.bittensor.com/learn/bittensor-building-blocks#subtensor)

## Anatomy of Incentive Mechanism

This section describes a conceptual “anatomy” of a subnet incentive mechanism.

### Overview

In a Bittensor subnet:

- The task-performing entities are called **subnet miners**.
- Entities that create the tasks, score the output of the subnet miners and reward them, are called **subnet validators**.

Incentive mechanisms are a fundamental part of Bittensor. 

- They drive the behaviour of the subnet miners and govern the consensus amongst the subnet validators. 
- Each subnet has its own incentive mechanism. 
- Subnet developers should design incentive mechanisms carefully so that these mechanisms comprehensively and explicitly promote all the desired behaviors and penalize undesired behaviors.

#### Machine Learning Analogy

In machine learning analogy, incentive mechanisms are effectively loss functions that steer the behaviour of subnet miners towards desirable outcomes. 

Miner earnings are dependent on their loss value, hence the miners are incentivized to act in ways that minimize such loss value. Furthermore, competition between subnet miners will drive the miners to seek optimal strategies within the given subnet incentive landscape.

A subnet incentive mechanism, when running optimally on a subnet, will continuously produce high quality results because the subnet miners and subnet validators are incentivized to do so. 

See [docs.bittensor.com/learn/anatomy-of-incentive-mechanism#overview](https://docs.bittensor.com/learn/anatomy-of-incentive-mechanism#overview)

### Subnet owner responsibilities

A subnet owner is responsible for:

- Defining the specific digital task to be performed by the subnet miners.
- Implementing an incentive mechanism that aligns miners with the desired task outcomes.

See [docs.bittensor.com/learn/anatomy-of-incentive-mechanism#subnet-owner-responsibilities](https://docs.bittensor.com/learn/anatomy-of-incentive-mechanism#subnet-owner-responsibilities)

### Design with Yuma Consensus as a black box

Though a subnet incentive mechanism works in conjunction with the Yuma Consensus in the Bittensor network, you must design your subnet incentive mechanism **by treating Yuma Consensus as a black box**.

See [docs.bittensor.com/learn/anatomy-of-incentive-mechanism#design-with-yuma-consensus-as-a-black-box](https://docs.bittensor.com/learn/anatomy-of-incentive-mechanism#design-with-yuma-consensus-as-a-black-box)

### Make it easy for participation

#### Participating in your subnet

When a developer is getting ready to participate in a subnet, they will follow a checklist like the one in [Checklist for Subnet](https://docs.bittensor.com/subnets/checklist-for-validating-mining). 

After a subnet validator registers into your subnet, they will run the validator module to begin the validation operation. 

Similarly a subnet miner will register and then run the miner module. 

For example, see the following documents in the text prompting subnet for a quick view of these steps:

- [Running a validator](https://github.com/opentensor/prompting/blob/main/docs/SN1_validation.md).
- [Running a miner](https://github.com/opentensor/prompting/blob/main/docs/stream_miner_template.md).

See [docs.bittensor.com/learn/anatomy-of-incentive-mechanism#make-it-easy-for-participation](https://docs.bittensor.com/learn/anatomy-of-incentive-mechanism#make-it-easy-for-participation)

## Components of incentive mechanism

A subnet incentive mechanism must contain the definition and implementation of the following behaviors. See the numbered items in the below diagram:

![Components of Incentive Mechanism](https://docs.bittensor.com/img/docs/components-of-incentive-mechanism.svg)

See https://docs.bittensor.com/learn/anatomy-of-incentive-mechanism#components-of-incentive-mechanism

### Subnet protocol

See **1** and **3** in the above diagram. A subnet protocol, which is unique to the subnet, must define how a subnet validator will query the subnet miners, and how a subnet miner should respond to the query.

For example:

1.  A subnet validator might send a query containing the task description to the subnet miners.
2. The subnet miners will perform the task and then respond to the subnet validators with the results of the task the miners performed. 

Note, however, that query-response is only one of the ways of subnet miner-and-subnet validator interaction. An alternative example is when the subnet validators and subnet miners use additional shared resources such as databases, and these resources can be used to evaluate miner performance.

See [docs.bittensor.com/learn/anatomy-of-incentive-mechanism#subnet-protocol](https://docs.bittensor.com/learn/anatomy-of-incentive-mechanism#subnet-protocol) and also [Neuron to neuron communication](https://docs.bittensor.com/learn/bittensor-building-blocks#neuron-to-neuron-communication).

### Subnet task

See **2** in the above diagram. The task is one of the key components of any incentive mechanism as it defines what miners will perform as work. The task should be chosen so that miners are maximally effective at the intended use case for the subnet. In other words, **the task should mimic an intended user interaction with a subnet**. Examples of tasks are responding to natural language prompts and storing encrypted files.

ALIGNING MINERS WITH THE SUBNET GOALS

The task defines the scope of work that miners will undertake, and what utility the subnet can provide to users. In some cases this should be very specific (such as storage) and in other cases it can be varied (many types of natural language query).

See https://docs.bittensor.com/learn/anatomy-of-incentive-mechanism#subnet-task

### Subnet reward model

See **4** and **5** in the above diagram. Just as the task describes **what** miners should do, the reward model dictates **how** it should be done. Similarly, just as tasks should mimic user interactions, reward models should mimic user preferences or desired outcomes.

As with any machine learning model, a subnet has an objective function that it is continuously optimizing. The reward model defines the quality of all miner behaviour in the subnet (both intended and unintended).

Operationally, it is the mathematical object that converts miner responses into numerical scores. A reward model can in fact contain as many different reward mechanisms as are necessary to align miners with the intended task.

Miners will continuously compete to achieve the highest reward possible. If the reward is capped at an upper limit, miners may not be motivated to improve further. Hence care should be taken to enable continuous improvement of the miner, rather than stagnation.

THE ZEN OF INCENTIVE MECHANISMS

Subnets should be endlessly improving.

See https://docs.bittensor.com/learn/anatomy-of-incentive-mechanism#subnet-reward-model

### Discourage exploits

The incentive mechanism is ultimately the judge of subnet miner performance. When the incentive mechanism is well calibrated, it can result in a virtuous cycle in which the subnet miners continuously improve at the desired task due to competition.

On the contrary, a poorly designed incentive mechanism can result in exploits and shortcuts, which can detrimentally impact the overall quality of the subnet and discourage fair miners.

See https://docs.bittensor.com/learn/anatomy-of-incentive-mechanism#discourage-exploits

## Distribution of rewards

Distribution of rewards among the subnet miners and subnet validators works like this. Consider an example subnet:

- Three subnet miners occupy the UID slots 37, 42 and 27 in the subnet.
- Four subnet validators occupy the UID slots 10, 32, 93 and 74 in the subnet, as shown in the below simplified conceptual diagram. Assume that the **subnet protocol** box in the diagram includes all the components of the incentive mechanism that were identified above.

![Incentive Mechanism Big Picture](https://docs.bittensor.com/img/docs/distribution-of-rewards-big-picture.svg)

The item numbers below correspond to the circled numbers in the above diagram.

1. Each subnet validator maintains a vector of weights. Each element of the vector represents the weight assigned to a subnet miner. This weight represents how well the subnet miner is performing **according to this subnet validator**.

   Each subnet validator ranks all the subnet miners by means of this weight vector. Each subnet validator within the subnet, acting independently, transmits its miner ranking weight vector to the blockchain. These ranking weight vectors can arrive at the blockchain at different times. Typically each subnet validator transmits an updated ranking weight vector to the blockchain every 100-200 blocks.

2. The blockchain (subtensor) waits until the latest ranking weight vectors from all the subnet validators of the given subnet arrive at the blockchain. A ranking weight matrix formed from these ranking weight vectors is then provided as input to the Yuma Consensus module on-chain.

3. The Yuma Consensus (YC) on-chain then uses this weight matrix, along with the amount of stake associated with the UIDs on this subnet, to calculate rewards. The YC calculates how the reward TAO tokens should be distributed amongst the subnet validators and subnet miners in the subnet, i.e., amongst each UID in the subnet.

ALL REWARD TAO TOKENS ARE NEWLY MINTED.

1. Finally, the YC calculates a consensus distribution of TAO (the ‘emission’) and distributes the newly minted reward TAO immediately into the accounts associated with the UIDs.

See [docs.bittensor.com/learn/anatomy-of-incentive-mechanism#distribution-of-rewards](https://docs.bittensor.com/learn/anatomy-of-incentive-mechanism#distribution-of-rewards)

### Tempo

Note that subnet validators can transmit their rank weight vectors to the blockchain any time. However, for any user-created subnet, the YC for the subnet begins at every 360 blocks (=4320 seconds or 72 minutes, at 12 seconds per block) using the latest weight matrix available at the YC for the subnet.

If a ranking weight vector from the subnet validator arrives after the start of a 360-block period, then this weight vector will be used in the subsequent YC start, i.e., after the current 360 blocks have elapsed.

At the end of any 360-block period, called **tempo**, the YC concludes and the emissions (distribution of reward TAO) are complete. This tempo value of 360 blocks is the same for all the user-created subnets. However, the YC-starts for each user-created subnet can commence at different times.

See [docs.bittensor.com/learn/anatomy-of-incentive-mechanism#tempo](https://docs.bittensor.com/learn/anatomy-of-incentive-mechanism#tempo)