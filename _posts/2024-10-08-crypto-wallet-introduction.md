---
layout: post
title: Crypto Wallets Explained - Types, Risks, and How to select it
date:   2024-10-08
lang: en
locale: en-GB
categories: blockchain cryptography
tags: blockchain wallet trezor ledger metamask
description: This article presents the different types of crypto wallets (hot, warm, cold) and their associated risks
image: /assets/article/blockchain/wallet/wallet-introduction/crypto-wallet-category.png
isMath: false
---

Cryptocurrencies such as Bitcoin or Ethereum require a private key to prove ownership of the asset. Most often, this key is generated and stored by a software called a crypto wallet. 

[TOC]

A crypto wallet is generally responsible to: 

- Generate seed phrase and associated private keys 

- Store the private keys securely 

- Provide a way to sign transactions, interact with applications (dApps), move the funds, ... 

![account]({{site.url_complet}}/assets/article/blockchain/wallet/wallet-introduction/crypto-wallet-goal.drawio.png)

From a cryptography perspective, these blockchains use most often public key cryptography (asymmetric) with two main keys involved:

1. **Public Key**: This is similar to an account number. You can share your public key with others to receive payments.
2. **Private Key**: The private key functions as a password, granting access to your crypto holdings. You must keep this key secure, as anyone with access to it can control your funds.

![account]({{site.url_complet}}/assets/article/blockchain/wallet/wallet-introduction/crypto-wallet-origin.drawio.png)

----

## Internet exposure of Crypto Wallets

Crypto wallets come in various forms, each catering to different user needs based on convenience, security, and usage scenarios. 

Crypto wallets are generally categorized based on their connectivity and their exposure to the internet, and consequently to cyber threats such as malware, phishing, etc.

The three main categories are **hot**, **warm** and cold wallets.

![account]({{site.url_complet}}/assets/article/blockchain/wallet/wallet-introduction/crypto-wallet-category.png)

### 1. Hot Wallets

Hot wallets are connected to the internet and allow for quick and easy access to your crypto assets. These wallets are typically more user-friendly, making them ideal for beginners or frequent traders. However, their constant internet connection makes them vulnerable to hacking attempts.

There are two main types of hot wallets: web wallets and smart contract based wallet

#### Web wallet

- Centralized Web Wallets  

They are hosted on cloud servers and can be accessed from any device with an internet connection. Web wallets are easy to set up but often require you to trust a third party with your private keys.

Example: [bitget](https://web3.bitget.com/en), [cropty.io - web-wallet](https://www.cropty.io/web-wallet)

- MPC wallet

These wallet uses MPC with a Multi-signature scheme. MPC wallet will split the private key into several shares owned by different entities. Some MPC wallet are non-custodial, the user controls who have the different shares, others are custodial and the provider owns the shares.

In principle, MPC wallets are always connected to the internet, but their access will most often be protected via firewall rules and governance rules. Additionally, the different shares used to compute the private key can be store in different ways, on an hardware device, similar to a cold wallet or on a mobile/computer device similar to a warm wallet.

An example is [zengo wallet](https://zengo.com), which provide a self-custodial MPC wallet with two shares: where one share is stored on Zengo's server and the other share is stored on the user mobile device

Reference: [liminal - What are MultiSig and MPC Wallets?](https://www.liminalcustody.com/knowledge-center/what-are-multisig-and-mpc-wallets/)

- smart contract based wallet

These wallets are managed by smart contracts. They are particularly present on Ethereum and EVM blockchains. One of the most known wallet is the one from [Safe](https://app.safe.global/welcome) which allows multi-signature access and are self-custodial. Since smart contracts are always accessible through blockchain, they are therefore considered as hot wallets.

With account abstraction, some smart contract based wallets are used in conjunction with an MPC protocol

Example: [bitget](https://web3.bitget.com/en), [cropty.io - web-wallet](https://www.cropty.io/web-wallet)

#### Risks

- **Hacking and Cyber Attacks**: Since hot wallets are connected to the internet, they are vulnerable to hacking, phishing, and malware attacks. If the wallet provider or your device gets compromised, attackers can steal your private keys and access your funds.
- **Phishing Scams**: Fake websites, apps, or emails can trick users into entering their credentials, leading to the loss of their private keys.
- **Third-Party Risk**: Many web wallets are custodial, meaning that the service provider holds your private keys. If the service provider gets hacked, you could lose your funds.
- **Device Vulnerabilities**: If the device running the wallet (mobile phone or computer) is infected with malware or is physically stolen, your private keys and funds are at risk.
- **Data Breaches**: Using hot wallets on centralized providers can expose your data to potential breaches, resulting in identity theft or loss of funds through a phishing attack against you.

### 2. Warm Wallets

This type of wallets is installed and stored the private keys on devices generally used in everyday life.

They are not permanently connected to internet, for example because the device can be turned off, but are subject to threats posed by internet, such as downloading malware.

A warm wallet can be turned into a cold wallet if it is installed on a dedicated device but we don't see it very offen in practice. As an exemple, see [Metamask as a cold wallet](https://www.reddit.com/r/ethereum/comments/101tfe2/using_metamask_as_a_cold_wallet/)

There are three way to have these wallets:

- **Browser extension**: These wallets are installed as extensions inside your browser. These types of wallet are very common and used to interact with decentralized application. Metamask is one of the most known wallets installed as a browser extension.

- **Mobile Wallets**: Mobile wallets are apps installed on smartphones. They are convenient for everyday use, allowing you to quickly transfer and receive crypto on the go. Examples include Trust Wallet or MetaMask.
- **Desktop Wallets**: These are software programs downloaded and installed on your computer. Desktop wallets are more secure than web wallets, but they are still susceptible to malware and hacks if your computer is compromised.

#### Risks

- **Limited Offline Protection**: While warm wallets may have certain offline features (such as two-factor authentication or hardware authentication), they are still exposed to online threats.
- **Physical Security**: If you lose the device where the warm wallet is installed, your funds could be compromised unless you have recovery mechanisms (e.g., a recovery phrase or encrypted backups).
- **Malware and Spyware**: Warm wallets can still be affected by malware or keyloggers that target your private keys when you connect to the internet to perform transactions or during everyday use (e.g. your mobile phone)
- **Human Error**: Sending funds to the wrong address or making a transaction error in a warm wallet cannot be reversed. There is no central authority to mediate in case of a mistake.

Reference:

[Ceffu - Cold vs. Warm vs. Hot Wallets: Which Crypto Wallet Solution Should You Choose?](https://www.ceffu.com/blog/cold-warm-hot-wallet-which-crypto-wallet-solution-should-you-choose), [Fireblocks - Hot vs. cold vs. warm wallets: Which crypto wallet is right for me?](https://www.fireblocks.com/blog/hot-vs-warm-vs-cold-which-crypto-wallet-is-right-for-me/)

### 3. Cold Wallets

Cold wallets are not connected to the internet, making them much safer from online threats like hacking. These are preferred for long-term storage of significant amounts of cryptocurrency. 

- Advantage: Cold wallets are ideal to hold cryptos for extended periods without frequent transactions.
- Cold wallets are considered more secure than hot and warm wallet because:
  - They are not connected permanently to internet, contrary to hot wallet
  - They are not installed on a device used in everyday life and regularly exposed to the internet, contrary to warm wallet
  - They require to be connected to another device, e.g a computer, to make the link between the device and internet

- Disadvantage: 
  - These wallet support less blockchain than for a warm and hot wallet, sometime they only support Bitcoin and derived (e.g Litecoin) or Ethereum and EVM blockchain. They are slow to support new blockchain due to Hardware constraint.
  - Since they are not installed on an everyday device, they are less practical for trading and to quickly react to market movements


Example: [Ledger](https://www.ledger.com/), [Trezor](https://trezor.io/), and [KeepKey](https://www.keepkey.com/).

#### Types of Cold Wallets

##### Hardware wallet

Hardware wallets are physical devices that store private keys offline. These are considered one of the safest methods to store crypto. Examples include devices from brands like Ledger or Trezor. If you are interested about Trezor, you can read my article [Trezor Crypto Wallet – Cryptography and Security](https://rya-sge.github.io/access-denied/2024/10/15/trezor-wallet-security/)

It looks like a USB with an OLED screen and side buttons to perform actions with the private keys

The Most popular hardware wallets are from Ledger and Trezor.

###### Pros

- **Highly Secure**: Since they store private keys offline, hardware wallets are immune to online hacking.
- **User-friendly**:  Many hardware wallets have intuitive interfaces and are designed for easy use even by beginners.

###### Pros vs other type of cold wallet:

Some Hardware wallet (e.g. Trezor or Ledger) support more blockchains than paper wallet or an air-gap wallet.

**Cons**

- **Cost**: They are not free and can range in price depending on the model and features.
- **Physical Theft**: If someone steals your hardware wallet and knows your PIN or manage to brute-force it, they can access your funds. This point will depend on the measures put in place by the hardware wallet to improve security,e.g with a wallet reset if an attacker tries to brute-force the PIN.
- **Limited Access**: You need physical access to your hardware wallet to make transactions, which can be inconvenient if you need to make frequent transactions.
- **Firmware Updates**: Requires periodic updates to support new features and eventually remain secure if a vulnerability is discovered, which can be a hassle for less tech-savvy users.

###### Ambivalent opinion

- **Backup and Recovery**: 
  - The recovery/seed phrase can be generally obtained to perform a backup.
  - ...But it is your responsability to perform the backup proprely. Some solutions are in early stage like [Ledger Recover](https://www.ledger.com/academy/what-is-ledger-recover)
  - The decentralized nature of crypto means that the responsibility for safeguarding your funds rests solely with you.

##### Paper wallet

A paper wallet consists of a piece of paper with your public and private keys printed on it as plain text or QR code. If is under the form of a QR code, several wallets support the import of public or private key through a scan.

Advantage: This is completely offline and immune to cyberattacks as long as the wallet is not used to sign transactions

Disadvantage:  

- They can be easily lost, destroyed, or stolen if not carefully protected. 
- Additionally, they can not be updated to support multi-blockchain. 

##### AirGap wallet

- **Air-gapped Computers**: These are computers or devices completely isolated from the internet, often used by highly security-conscious users for cold storage.

The company [AirGap](https://airgap.it) offers one of these wallets with this approach:

- you can **sign transactions completely offline** on a device without any network connectivity with the **AirGap Vault** application 
- Then broadcast them with your every-day smartphone with the **AirGap Wallet** app.

See [airgap.it/offline-device/](https://airgap.it/offline-device/)

Reference: [coinbase.com - What is an air-gapped wallet?](https://www.coinbase.com/learn/wallet/what-is-an-air-gapped-wallet)

#### Risks

- **Physical Theft or Loss**: While cold wallets are secure from online attacks when there are not connected to a device, they are at risk of physical theft. If someone gains access to your hardware wallet, paper wallet, or air-gapped computer and knows the PIN, they can steal your funds.
- **No Backup or Recovery**: If you lose your hardware wallet or paper wallet, or it is damaged, you may lose access to your funds permanently unless you have a secure backup of your recovery phrase. Paper wallets, in particular, are prone to damage and loss
- **Firmware Vulnerabilities**: For hardware wallets, 
  - Outdated firmware could introduce security vulnerabilities that might be exploited by attackers.
  - New firmware update can also introduce new vulnerability through a new features or a supply chain attack (malicious firmware update)
- **Counterfeit Devices**: Purchasing hardware wallets from unofficial or third-party sources may expose you to the risk of counterfeit devices designed to steal your private keys.

-----

## How to Use a Crypto Wallet

Here the common to step to use a crypto wallet:

1. **Setting up the wallet**: Download the appropriate software for your wallet type or purchase a hardware wallet. Follow the instructions to generate your public and private keys. Make sure to store securely a backup of your private key / recovery phrase .
2. **Receiving crypto**: Share your public key (wallet address) with the sender. Once the transaction is initiated, the cryptocurrency will appear in your wallet after the network verifies it.
3. **Sending crypto**: Enter the recipient’s public key, specify the amount, and confirm the transaction. The process takes a few minutes to hours, depending on the network's congestion and the blockchain you are using.
4. **Monitoring your balance**: Use your wallet interface to check your balance and track incoming and outgoing transactions. You can also interact with decentralized applications (dApps) or stake your assets (depending on the blockchain) using your wallet if it is supported.

-----

## Main Risks and Security Concerns

While crypto wallets offer secure management of digital assets, they are not without risks. It’s crucial to be aware of potential pitfalls:

### 1. Scam and Phishing Attacks

Hot wallets, due to their internet connectivity, are susceptible to hacks. Attackers can steal private keys or use phishing attacks to trick users into giving up their credentials. Always double-check URLs when accessing web wallets and be cautious of unsolicited communication from exchanges or wallet providers.

Scams in the crypto world are also common, with fraudsters luring victims through fake wallet apps, fraudulent exchanges, or Ponzi schemes. Use well-vetted wallets and platforms to avoid these risks.

### 2. Lost Private Keys

Unlike bank accounts, self-custodial crypto wallets (e.g Trezor) do not have a customer support number to recover lost credentials. If you lose access to your private key or seed phrase, you lose access to your funds permanently. Keeping a backup of your private key in a secure place is essential.

### 3. Malware

Malware can infect your device and steal your private keys or reroute transactions to a scammer’s address. This particularly concerns `warm/hot wallets` which are installed and accessed on a device used in everyday life, e.g. your personal computer or your telephone.

### 4. Human Error

Sending crypto to the wrong address or making mistakes in transactions is irreversible. Unlike traditional banking systems, there’s no centralized authority to reverse errors. Double-check all details before initiating transfers.

-----

## Best Practices for Wallet Security

- **Use Strong Passwords**: For wallets that require passwords, use strong, unique passwords
  - For hot wallet, when available, enable two-factor authentication (2FA). If not available, the question of using this wallet should arise.
  - For warm wallet, the password is often used to encrypt your seed phrase and private keys locally on our machine, it is for example the case for Metamask, see my article [Deep dive into MetaMask Secrets](https://rya-sge.github.io/access-denied/2023/07/20/metamask-secret/)

- **Backup Your Wallet**: Keep multiple backups of your wallet’s recovery phrase or private key in secure locations like a safe or encrypted storage device.
- **Use Cold  Wallet**: For large amounts of crypto or long-term holdings, use cold wallet to minimize exposure to online threats. Prefer using hardware devices instead of Paper wallets which are generally not recommended and also more difficult to install and manage.
- **Be Cautious with Links**: Always access wallets via official channels, and avoid clicking on random links in emails or messages related to your wallet.

### Ambivalent opinion

- **Keep Software Updated (eventually)**:

In general, it is advised to regularly update your wallet software to get the latest security features. 

In practice, the majority of upgrades add new features and blockchains, and therefore potentially new vulnerabilities. For established and already battle-tested hardware wallets, like Ledger or Trezor, it is unlikely that a new feature will really improve the security of the wallet.



### Summary Table of Risks

| Wallet Usage | Major Risks                                                 | Mitigation Strategies                                        |
| ------------ | ----------------------------------------------------------- | ------------------------------------------------------------ |
| **Hot**      | Hacking, phishing, malware, third-party risk                | Use strong passwords, 2FA, and only trusted services         |
| **Warm**     | Malware, human error, physical device theft                 | Regular backups, secure the device, don't install random software and don't click on random link (phishing) |
| **Cold**     | Physical theft, loss, no backups, malicious firmware update | Store securely, backup recovery phrase, use only trusted hardware |

Each type of wallet has its strengths and weaknesses in terms of security and convenience. Users should carefully evaluate their own needs, balancing ease of access with the level of risk they are willing to take.

## Conclusion

Crypto wallets are a fundamental part of participating in the cryptocurrency ecosystem, providing users with the tools to manage, store, and secure their digital assets. Understanding the different types of wallets and the security risks associated with each helps you choose the best option for your needs.

Whether you are a casual user or an investor looking to store large sums of crypto, it's vital to approach wallet management with caution and find the right balance between your own competence, constraints, desires and security. Ideally, always prioritize security. 

Finally, if you want to know if your Bitcoin wallet is truly open-source and secure, you can visit this excellent website [wallet scrutiny](https://walletscrutiny.com)

## Reference

- [Chainstack - Crypto Wallets 101: Hot wallets vs. cold wallets explained](https://chainstack.com/crypto-hot-wallets-vs-cold-wallets-explained/)
- [blockchain-council - What is a Crypto Wallet?](https://www.blockchain-council.org/blockchain/types-of-crypto-wallets-explained/)
- [secuxtech.com - Choosing Your Crypto Wallet: Paper versus Hardware](https://secuxtech.com/blogs/blog/paper-wallet-vs-hardware-wallet?srsltid=AfmBOor65CBdu-6IWQNp46RQXlrEQPR9yr_ed9Wnj34xkBFhSKga3M2g)
- ChatGPT with the inputs
  -  "Write me an article about crypto wallet. What they do, their usage, risk, the different type of wallet, and so on."
  - "For the different type of cold wallet, price their pros and cons"

