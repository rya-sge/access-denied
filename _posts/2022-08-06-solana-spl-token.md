---
layout: post
title: Introduction to Solana and the spl-token command line
date:   2022-08-06
locale: en-GB
lang: en
last-update: 
categories: blockchain 
tags: solana spl-token airdrop phantom
description: This article is an introduction to the Solana ecosystem, the Solana Tool Suite and the spl-token command-line utility.
isMath: false
image: /assets/article/blockchain/solana/introduction-cli/phantom-add-custom-token.PNG
---

This article is an introduction to the Solana ecosystem, the Solana Tool Suite and the `spl-token` command-line utility. It was made by following the Moralis course : https://aca[demy.moralis.io/courses/solana-programming-101](https://academy.moralis.io/courses/solana-programming-101)

- Create your own key with the command line
- Create your own key with Phantom
- Operation on token with the cli



## Installation

You can install Solana in your OS by following the official installation guide: [https://docs.solana.com/cli/install-solana-cli-tools](https://docs.solana.com/cli/install-solana-cli-tools)

### Key generation

The first thing to do is to create a pair of public/private keys.

When you use the spl-token command line, this generated key will be used

- Key generation

```
solana-keygen new --force
```

My result :Wrote new keypair to /home/YOUR_USER/.config/solana/id.json

My public key is `BgAoyQvL1ejQNrj4BewgJxfTHZ2cLjgxq8tza5oTcxyK`

- Getting the public key of a wallet


```
solana-keygen pubkey
```



### Install spl-token-cli

As stated in the documentation: "The spl-token command-line utility can be used to experiment with SPL tokens."

You can find the documentation here : [https://spl.solana.com/token](https://spl.solana.com/token)

- Install the cli tools


```bash
cargo install spl-token-cli
```

During the installation, it is possible you have some errors with libudev. You can find more information with this link: [stackoverflow.com - libudev-development-package-not-found](https://stackoverflow.com/questions/55945023/libudev-development-package-not-found)

the solution for me was to install libudev with this command :

```bash
sudo apt-get install libudev-dev
```



### Airdrop 

To perform operator, you need to have some SOL in your wallet. It is possible to have some SOL on devnet with the command airdrop

- Command

```bash
solana airdrop 1 --url devnet
```

- Checking the balance


```bash
solana balance --url devnet
```

- Screenshot

![solana-airdrop-dev]({{site.url_complet}}/assets/article/blockchain/solana/introduction-cli/solana-airdrop-dev.PNG)

There is a limitation on the number of SOL you can obtain. It is currently one by call

On the screenshot below, you can see the balance is unchanged.

![solana-airdrop-dev-unchanged]({{site.url_complet}}/assets/article/blockchain/solana/introduction-cli/solana-airdrop-dev-unchanged.PNG)



## Spl-token

### Creating a token

```bash
spl-token create-token -url devnet
```

![spl-create-token]({{site.url_complet}}/assets/article/blockchain/solana/introduction-cli/spl-create-token.PNG)

The address of the token is :  `H3goZSZ99PjQCBmFqy93jX683G3hgSE1BSnyY5DBEvws`

#### Solana explorer

Information about the token on Solana explorer : 

[explorer.solana.com - tx](https://explorer.solana.com/address/H3goZSZ99PjQCBmFqy93jX683G3hgSE1BSnyY5DBEvws?cluster=devnet)

![info-token-solana-explorer]({{site.url_complet}}/assets/article/blockchain/solana/introduction-cli/info-token-solana-explorer.PNG)

#### 

#### Create an account

Account in a wallet holds a token. Accounts have to be created within wallets

Reminder : In Solana, everything is an account

```bash
spl-token create-account <TOKEN_ADDRESS> --url devnet
```

The returned id is the token account address

![spl-create-account]({{site.url_complet}}/assets/article/blockchain/solana/introduction-cli/spl-create-account.PNG)

There is one account by token. An error is generated if you try to create a second account![spl-create-account-2]({{site.url_complet}}/assets/article/blockchain/solana/introduction-cli/spl-create-account-2.PNG)

#### Solana explorer

![create-account-solana-explorer]({{site.url_complet}}/assets/article/blockchain/solana/introduction-cli/create-account-solana-explorer.PNG)





### Mint

```bash
spl-token mint <TOKEN_ADDRESS> <NUMBER> --url devnet
```

![spl-mint-token]({{site.url_complet}}/assets/article/blockchain/solana/introduction-cli/spl-mint-token.PNG)



- Check the balance

```bash
spl-token balance H3goZSZ99PjQCBmFqy93jX683G3hgSE1BSnyY5DBEvws --url devnet
```



![spl-mint-token-balance]({{site.url_complet}}/assets/article/blockchain/solana/introduction-cli/spl-mint-token-balance.PNG)



- Check the supply

```bash
spl-token supply H3goZSZ99PjQCBmFqy93jX683G3hgSE1BSnyY5DBEvws --url devnet
```

![spl-token-supply]({{site.url_complet}}/assets/article/blockchain/solana/introduction-cli/spl-token-supply.PNG)



#### Solana explorer

Check on Solana explorer


Link : [explorer.solana.com - tx]( https://explorer.solana.com/tx/4cieBRVtpe4ivuAn41C26sTfRzJ3LDSYN9kEQ7kr6H14EYYwbi6eJhYK214d4vrXxTD9cvoeaTaDCyzaLtMxbYKL?cluster=devnet)

![mint-token-solana-explorer]({{site.url_complet}}/assets/article/blockchain/solana/introduction-cli/mint-token-solana-explorer.PNG)

### Disable authorization

- Renouncing the ability to mint tokens :


```bash
spl-token authorize <TOKEN_ADDRESS> mint --disable --url devnet
```

![spl-authorize-mint-disable]({{site.url_complet}}/assets/article/blockchain/solana/introduction-cli/spl-authorize-mint-disable.PNG)



- Check the result :

![spl-authorize-mint-disable-check]({{site.url_complet}}/assets/article/blockchain/solana/introduction-cli/spl-authorize-mint-disable-check.PNG)

### Burn token

Only our own tokens can be burned

```bash
spl-token burn <ACCOUNT_ADDRESS> <number> --url devnet
```

![spl-token-burn]({{site.url_complet}}/assets/article/blockchain/solana/introduction-cli/spl-token-burn.PNG)



### Send token to another account

You can create a second account with phantom wallet to test this command

```bash
spl-token transfer <SOURCE_TOKEN_ADDRESS> <AMOUNT> <TARGET_TOKEN_ADDRESS> --url devnet --fund-recipient
```

Without the fund-recipient flag, you'd not be able to add balance to an unfunded address



#### Transfer token to a phantom wallet

For the next test, I created a new token with an account because I had revoked the authorizations for the previous one (not very smart haha)

Token address : `EHNLcqxdBLGGMwqVSR3tf1PsSo6HxNgxftD4j3wnHNQL`

Account : `2dWvomUHStpCZbdVfLvxKC4neJmUYNEaozpru65kfHyH`



- Add the token to Phantom

![phantom-add-custom-token]({{site.url_complet}}/assets/article/blockchain/solana/introduction-cli/phantom-add-custom-token.PNG)

- Transfer some tokens to the phantom wallet


We transfer some tokens

![spl-transfer-token]({{site.url_complet}}/assets/article/blockchain/solana/introduction-cli/spl-transfer-token.PNG)

![phantom-token-transfer]({{site.url_complet}}/assets/article/blockchain/solana/introduction-cli/phantom-token-transfer.PNG)



![spl-transfer-check]({{site.url_complet}}/assets/article/blockchain/solana/introduction-cli/spl-transfer-check.PNG)

##### Solana explorer

See on Solana explorer : [explorer.solana - tx](https://explorer.solana.com/tx/5ebyFnQTeLUAFLrLPkoVwffer1YQrRpnHBxPF34AZFxSr91cZNiugyqDGBgVEafQVZ5ZGxLXVHgsjmxjsVX6mUFb?cluster=devnet)



![solana-explorer-transfer]({{site.url_complet}}/assets/article/blockchain/solana/introduction-cli/solana-explorer-transfer.PNG)



## References

Main references are :

- SOLANA-LABS, 2022a. Token Program. *Solana Program Library*. Online. 2022. [Accessed 3 August 2022]. Retrieved from: [https://spl.solana.com/token](https://spl.solana.com/token)
- SOLANA-LABS, 2022b. Install the Solana Tool Suite. *Solana Documentation*. Online. 2022. [Accessed 3 August 2022]. Retrieved from: [https://docs.solana.com/cli/install-solana-cli-tools](https://docs.solana.com/cli/install-solana-cli-tools)
- ZSOLT NAGY, no date. Solana Programming 101. *Moralis academy*. Online. [Accessed 3 August 2022]. Retrieved from: [https://academy.moralis.io/courses/solana-programming-101](https://academy.moralis.io/courses/solana-programming-101)
