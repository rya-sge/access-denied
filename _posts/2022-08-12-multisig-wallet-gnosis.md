---
layout: post
title: How to create a multisig wallet with Gnosis Safe
date:   2022-08-12
locale: en-GB
lang: en
last-update: 
categories: blockchain 
tags: solana spl-token airdrop phantom
description: This tutorial present the different steps to create a multi signature wallet with Gnosis Safe on Ethereum.
isMath: false
image: /assets/article/blockchain/wallet/gnosis-safe/1-create-new-gnosis.PNG
---



This tutorial presents the different steps to create a multi signature wallet with Gnosis Safe on Ethereum.

For tutorial purposes, the multisig wallet will be created on a testnet network (rinkeby) with a test wallet belonging to me.



## Introduction

### Presentation of product

- Gnosis Safe supports ETH, ERC20 (Tokens) and ERC721 (Collectibles) [Gnosis 2022a].
- Gnosis Safe is a smart contract wallet running on Ethereum that requires a minimum number of people to approve a transaction before it can occur (M-of-N) [Schor 2022].
- Gnosis is based in Gibraltar, therefore the use of the software has to respect the law of Gibraltar [Gnosis 2022d].

## Welcome page

On this page you can start the process by clicking on the "create a new Safe" button

![1-create-new-gnosis]({{site.url_complet}}/assets/article/blockchain/wallet/gnosis-safe/1-create-new-gnosis.PNG)



There will be four main steps to create your wallet

![1a-list-step]({{site.url_complet}}/assets/article/blockchain/wallet/gnosis-safe/1a-list-step.PNG)



## Steps

### 1. Connect your wallet & select network

In this step, you have to connect your wallet and configure the network used

### Choose your wallet

#### Supported wallet

To connect your wallet, Gnosis use the solution provided by blocknative.com: https://www.blocknative.com/onboard

![3-supported-wallet]({{site.url_complet}}/assets/article/blockchain/wallet/gnosis-safe/3-supported-wallet.PNG)



With Metamask you have to authorize the website

![4-connect-your-wallet]({{site.url_complet}}/assets/article/blockchain/wallet/gnosis-safe/4-connect-your-wallet.PNG)

### Select network

List of all available network on August 11, 2022.

![1b-select-your-network]({{site.url_complet}}/assets/article/blockchain/wallet/gnosis-safe/1b-select-your-network.PNG)

I choosed the rinkeby network for my tests.

![1c-choose-rinkeby]({{site.url_complet}}/assets/article/blockchain/wallet/gnosis-safe/1c-choose-rinkeby.PNG)



### 2. Name

In this step, you have to choose a name for your safe wallet and accept the terms  of use and privacy policy

![5-safe-name]({{site.url_complet}}/assets/article/blockchain/wallet/gnosis-safe/5-safe-name.PNG)

#### Terms & privacy 

It is very important to read the terms of use carefully because a multi-signature wallet is critical software.

For information, Gnosis is based in Gibraltar, therefore the use of the software has to respect the law of Gibraltar

Interesting information: 

in point 3.2.c in the privacy document, it is indicated that the IP address is kept in the logs . This could potentially link your IP address to your wallet address and therefore identify you.

Terms :  [https://gnosis-safe.io/terms/](https://gnosis-safe.io/terms/)

Privacy : [https://gnosis-safe.io/privacy/]( https://gnosis-safe.io/privacy/)

### 3. Owners and confirmation

In this step, you define the list of owners and the list of signatures needed to sign a transaction

To determine the right parameters, you can find out by reading this article : [https://help.gnosis-safe.io/en/articles/4772567-what-safe-setup-should-i-use](https://help.gnosis-safe.io/en/articles/4772567-what-safe-setup-should-i-use)

It is a vital step to guarantee the safety of your wallet

![6-owners]({{site.url_complet}}/assets/article/blockchain/wallet/gnosis-safe/6-owners.PNG)





### 4. Review

In this step you can review the different parameter, then you can confirm the transaction

![7-review]({{site.url_complet}}/assets/article/blockchain/wallet/gnosis-safe/7-review.PNG)



#### Accept the transaction

![9-confirm-transaction]({{site.url_complet}}/assets/article/blockchain/wallet/gnosis-safe/9-confirm-transaction.PNG)

#### Pop-up Metamask



![9-confirm-transaction-a]({{site.url_complet}}/assets/article/blockchain/wallet/gnosis-safe/9-confirm-transaction-a.PNG)



![9-confirm-transaction-b]({{site.url_complet}}/assets/article/blockchain/wallet/gnosis-safe/9-confirm-transaction-b.PNG)

Before signing the transaction, it is also important to verify the authenticity and legitimacy of the contract

During my tests, it was the contract with the following address : `0xa6B71E26C5e0845f74c812102Ca7114b6a896AB2`

With Etherscan, I can get some information about the contract : [https://etherscan.io/address/0xa6B71E26C5e0845f74c812102Ca7114b6a896AB2](https://etherscan.io/address/0xa6B71E26C5e0845f74c812102Ca7114b6a896AB2)

Even if it is not an absolute guarantee, the two information framed in red already give guarantees on the legitimacy of the contract

![8-check-contract]({{site.url_complet}}/assets/article/blockchain/wallet/gnosis-safe/8-check-contract.PNG)





#### Confirmation success

![10-confirmation-success]({{site.url_complet}}/assets/article/blockchain/wallet/gnosis-safe/10-confirmation-success.PNG)



## Dashboard

One you have created the multi signature wallet, you can access to the dashboard

### View

![11-dashboard]({{site.url_complet}}/assets/article/blockchain/wallet/gnosis-safe/11-dashboard.PNG)



### Action available

You have three possible actions with your wallet : send funds (ether), send NFT and interact with a contract

![12-action-available]({{site.url_complet}}/assets/article/blockchain/wallet/gnosis-safe/12-action-available.PNG)

#### Interact with a contract

If you choose the third action "Contractual interaction", a new form opens where you need to indicate the contract address, the ABI and select the desired function.

![13-contract-interaction]({{site.url_complet}}/assets/article/blockchain/wallet/gnosis-safe/13-contract-interaction.PNG)





You can then sign the request with your wallet.

![14-sign-transaction]({{site.url_complet}}/assets/article/blockchain/wallet/gnosis-safe/14-sign-transaction.PNG)





On the dashboard, the information about the transaction is available. On the screenshot we can see that we need a signature from the second owner to reach the threshold in my case.

![15-dashboard]({{site.url_complet}}/assets/article/blockchain/wallet/gnosis-safe/15-dashboard.PNG)

## Reference

BLOCKNATIVE, 2022. Maximum Web3 Wallet Integration. *blocknative*. Online. 2022. [Accessed 12 August 2022]. Retrieved from: [https://www.blocknative.com/onboard](https://www.blocknative.com/onboard)

ETHERSCAN, 2022. *Etherscan*. Online. 2022. [Accessed 12 August 2022]. Retrieved from: [https://etherscan.io](https://etherscan.io)

GNOSIS, 2022a. *Gnosis Safe*. Online. 2022. [Accessed 12 August 2022]. Retrieved from: [https://gnosis-safe.io/](https://gnosis-safe.io/)

GNOSIS, 2022b. *help.gnosis-safe*. Online. 2022. [Accessed 12 August 2022]. Retrieved from: [https://help.gnosis-safe.io/en/](https://help.gnosis-safe.io/en/)

GNOSIS, 2022c. Privacy Policy. *Gnosis Safe*. Online. 2022. [Accessed 12 August 2022]. Retrieved from: [https://gnosis-safe.io/privacy/](https://gnosis-safe.io/privacy/)

GNOSIS, 2022d. Terms and Conditions. *Gnosis Safe*. Online. 2022. [Accessed 12 August 2022]. Retrieved from: [https://gnosis-safe.io/terms/](https://gnosis-safe.io/terms/)

SCHOR, Lukas, 2022. What is Gnosis Safe? *help.gnosis-safe*. Online. 2022. [Accessed 12 August 2022]. Retrieved from: [https://help.gnosis-safe.io/en/articles/3876456-what-is-gnosis-safe](https://help.gnosis-safe.io/en/articles/3876456-what-is-gnosis-safe)

SCHUBOTZ, Tobias, 2022. What Safe setup should I use? *help.gnosis-safe*. Online. 2022. [Accessed 12 August 2022]. Retrieved from: [https://help.gnosis-safe.io/en/articles/4772567-what-safe-setup-should-i-use](https://help.gnosis-safe.io/en/articles/4772567-what-safe-setup-should-i-use)