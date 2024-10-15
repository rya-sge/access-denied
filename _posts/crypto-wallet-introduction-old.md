

> layout: post
> title:  Understanding Crypto Wallets: What They Do, Usage, Risks, and Types
> date:   2024-09-19
> lang: en
> locale: en-GB
> categories: blockchain cryptography
> tags: blockchain wallet
> description: This article is an introduction to crypto Wallets
> image:  /assets/article/blockchain/solana/solanaLogoMark.png
> isMath: false



Cryptocurrencies such as Bitcoin or Ethereum require a private key to prove ownership of the asset. Most often, this key is generated and stored by software called a crypto wallet. 

[TOC]

A crypto wallet is generally responsible to: 

- Generate seed phrase and associated private keys 

- Store the private keys securely 

- Provide a way to sign transactions, interact with applications (dApps), move the funds, ... 

From a cryptography perspective, these blockchains use most often public key cryptography (asymmetric) with two main keys involved:

1. **Public Key**: This is similar to an account number. You can share your public key with others to receive payments.
2. **Private Key**: The private key functions as a password, granting access to your crypto holdings. You must keep this key secure, as anyone with access to it can control your funds.





## Types of Crypto Wallets

Crypto wallets come in various forms, each catering to different user needs based on convenience, security, and usage scenarios. The two broad categories are **hot wallets** and **cold wallets**.



### 1. **Hot Wallets**

Hot wallets are connected to the internet and allow for quick and easy access to your crypto assets. These wallets are typically more user-friendly, making them ideal for beginners or frequent traders. However, their constant internet connection makes them vulnerable to hacking attempts.

There are two main types of hot wallets: web wallets and smart contract based wallet

- **Web Wallets:  They are hosted on cloud servers and can be accessed from any device with an internet connection. Web wallets are easy to set up but often require you to trust a third party with your private keys.
-  smart contract based wallet: these wallets are managed by smart contracts. They are mainly used for Ethereum and EVM blockchains. One of the most known wallet is the one from Safe which allows multi-signature access and is self-custodial. Since smart contracts are always accessible through blockchain, they are therefore considered as hot wallets.

Example: [bitget](https://web3.bitget.com/en), [cropty.io - web-wallet](https://www.cropty.io/web-wallet)

### 2. **Warm Wallets**

This type of wallets is installed and stored the private keys on devices used in everyday life

They are not permanently connected to internet, for example because the device can be turned off, but are subject to threats posed by internet, such as downloading malware.

It is possible to turn a warm wallet in a cold wallet by using a dedicated laptop with only the walle

the use of [Metamask as a cold wallet](https://www.reddit.com/r/ethereum/comments/101tfe2/using_metamask_as_a_cold_wallet/)

There are three way to have these wallets:

- **Browser extension**: These wallets are installed as extensions inside your browser. These type of wallet is very common and used to interact with decentralized application. Metamask is one of the most known wallet installed as a browser extension.

- **Mobile Wallets**: Mobile wallets are apps installed on smartphones. They are convenient for everyday use, allowing you to quickly transfer and receive crypto on the go. Examples include Trust Wallet or MetaMask.
- **Desktop Wallets**: These are software programs downloaded and installed on your computer. Desktop wallets are more secure than web wallets, but they are still susceptible to malware and hacks if your computer is compromised.

Reference:

[Ceffu - Cold vs. Warm vs. Hot Wallets: Which Crypto Wallet Solution Should You Choose?](https://www.ceffu.com/blog/cold-warm-hot-wallet-which-crypto-wallet-solution-should-you-choose), [Fireblocks - Hot vs. cold vs. warm wallets: Which crypto wallet is right for me?](https://www.fireblocks.com/blog/hot-vs-warm-vs-cold-which-crypto-wallet-is-right-for-me/)

### 3. **Cold Wallets**

Cold wallets are not connected to the internet, making them much safer from online threats like hacking. These are preferred for long-term storage of significant amounts of cryptocurrency. 

- Advantage: Cold wallets are ideal to hold cryptos for extended periods without frequent transactions.
- Cold wallets are considered more secure than hot and warm wallet because the private keys are isolated from internet and, they require human intervention to approve transactions.
- Disadvantage: this human intervention reduces transaction speed based on the authorized personnel’s availability and readiness. This is the reason why companies also use hot and warm wallets. Moreover, due to constraint hardware, they generally support fewer cryptos and blockchain than hot or warm wallets.

Example: [Ledger](https://www.ledger.com/), [Trezor](https://trezor.io/), and [KeepKey](https://www.keepkey.com/).

#### Types of Cold Wallets

##### Hardware wallet

Hardware wallets are physical devices that store private keys offline. These are considered one of the safest methods to store crypto. Examples include devices from brands like Ledger or Trezor.

It looks like a USB with an OLED screen and side buttons to perform actions with the private keys

The Most popular hardware wallets are from Ledger and Trezor.

###### **Pros**

- **Highly Secure**: Since they store private keys offline, hardware wallets are immune to online hacking.
- **User-friendly**: Now, many hardware wallets have intuitive interfaces and are designed for easy use even by beginners.

**Cons**

- **Cost**: They are not free and can range in price depending on the model and features.
- **Physical Theft**: If someone steals your hardware wallet and knows your PIN or recovery phrase, they can access your funds.
- **Limited Access**: You need physical access to your hardware wallet to make transactions, which can be inconvenient if you need to make frequent transactions.
- **Firmware Updates**: Requires periodic updates to support new features and eventually remain secure if a vulnerability is discovered, which can be a hassle for less tech-savvy users.

###### Ambivalent opinion

- **Backup and Recovery**: 
  - The recovery/seed phrase can be generally obtained to perform a backup.
  - ...But it is your responsability to perform the backup proprely. Some solutions are in early stage like [Ledger Recover](https://www.ledger.com/academy/what-is-ledger-recover)
- **Multi-currency Support**: 
  - Most hardware wallets support a wide variety of cryptocurrencies, allowing users to store their assets in one place.
  - ..But in general, they only support Bitcoin and derived (e.g Litecoin), Ethereum and EVM blockchain. They are slow to support new blockchain due to Hardware constraint.

##### Paper wallet

A paper wallet consists of a piece of paper with your public and private keys printed on it as plain text or QR code. If it is under the form of a QR code, several wallets support the import of public or private key through a scan.

Advantage: This is completely offline and immune to cyberattacks

Disadvantage:  

- They can be easily lost, destroyed, or stolen if not carefully protected. 
- Additionally, they can not be updated to support multi-blockchain. 

##### AirGap wallet

- **Air-gapped Computers**: These are computers or devices completely isolated from the internet, often used by highly security-conscious users for cold storage.

The company AirGap offers one of these wallets with this approach:

- you can **sign transactions completely offline** on a device without any network connectivity with the **AirGap Vault** application 
- Then broadcast them with your every-day smartphone with the **AirGap Wallet** app.

See [airgap.it/offline-device/](https://airgap.it/offline-device/)

Reference: [coinbase.com - What is an air-gapped wallet?](https://www.coinbase.com/learn/wallet/what-is-an-air-gapped-wallet)

## How to Use a Crypto Wallet

Using a crypto wallet involves a few straightforward steps:

1. **Setting up the wallet**: Download the appropriate software for your wallet type or purchase a hardware wallet. Follow the instructions to generate your public and private keys. Make sure to write down your private key or recovery phrase and store it securely.
2. **Receiving crypto**: Share your public key (wallet address) with the sender. Once the transaction is initiated, the cryptocurrency will appear in your wallet after the network verifies it.
3. **Sending crypto**: Enter the recipient’s public key, specify the amount, and confirm the transaction. The process takes a few minutes to hours, depending on the network's congestion and the blockchain you are using.
4. **Monitoring your balance**: Use your wallet interface to check your balance and track incoming and outgoing transactions. You can also interact with decentralized applications (dApps) or stake your assets (depending on the blockchain) using your wallet.

## Risks and Security Concerns

While crypto wallets offer secure management of digital assets, they are not without risks. It’s crucial to be aware of potential pitfalls:

### 1. **Hacking and Phishing Attacks**

Hot wallets, due to their internet connectivity, are susceptible to hacks. Attackers can steal private keys or use phishing attacks to trick users into giving up their credentials. Always double-check URLs when accessing web wallets and be cautious of unsolicited communication from exchanges or wallet providers.

### 2. **Lost Private Keys**

Unlike bank accounts, crypto wallets do not have a customer support number to recover lost credentials. If you lose access to your private key or seed phrase, you lose access to your funds permanently. Keeping a backup of your private key in a secure place is essential.

### 3. **Malware and Scams**

Malware can infect your device and steal your private keys or reroute transactions to a scammer’s address. Scams in the crypto world are also common, with fraudsters luring victims through fake wallet apps, fraudulent exchanges, or Ponzi schemes. Use well-vetted wallets and platforms to avoid these risks.

### 4. **Human Error**

Sending crypto to the wrong address or making mistakes in transactions is irreversible. Unlike traditional banking systems, there’s no centralized authority to reverse errors. Double-check all details before initiating transfers.

## Best Practices for Wallet Security

- **Use Strong Passwords**: For wallets that require passwords, use strong, unique passwords and enable two-factor authentication (2FA) when available. The password is often used to encrypt your seed phrase and private keys, it is for example the case for Metamask, see my article [Deep dive into MetaMask Secrets](https://rya-sge.github.io/access-denied/2023/07/20/metamask-secret/)
- **Backup Your Wallet**: Keep multiple backups of your wallet’s recovery phrase or private key in secure locations like a safe or encrypted storage device.
- **Use Cold Storage**: For large amounts of crypto or long-term holdings, use cold wallet to minimize exposure to online threats. Prefer using hardware devices instead of Paper wallets which are generally not recommended.
- **Be Cautious with Links**: Always access wallets via official channels, and avoid clicking on random links in emails or messages related to your wallet.

### Ambivalent opinion

- **Keep Software Updated (eventually)**:

In general, it is advised to regularly update your wallet software to get the latest security features. 

In practice, the majority of upgrades add new features and blockchains, and therefore potentially new vulnerabilities. For established and already battle-tested hardware wallets, like Ledger or Trezor, it is unlikely that a new feature will really improve the security of the wallet.

## Conclusion

Crypto wallets are a fundamental part of participating in the cryptocurrency ecosystem, providing users with the tools to manage, store, and secure their digital assets. Understanding the different types of wallets and the security risks associated with each helps you choose the best option for your needs.

Whether you are a casual user or an investor looking to store large sums of crypto, it's vital to approach wallet management with caution and always prioritize security. The decentralized nature of crypto means that the responsibility for safeguarding your funds rests solely with you.

If you want to know if your Bitcoin wallet is truly open-source and secure, you can visit this excellent website [wallet scrutiny](https://walletscrutiny.com) which studies the different wallet availables.



## Reference

- [Chainstack - Crypto Wallets 101: Hot wallets vs. cold wallets explained](https://chainstack.com/crypto-hot-wallets-vs-cold-wallets-explained/)
- [blockchain-council - What is a Crypto Wallet?](https://www.blockchain-council.org/blockchain/types-of-crypto-wallets-explained/)
- [secuxtech.com - Choosing Your Crypto Wallet: Paper versus Hardware](https://secuxtech.com/blogs/blog/paper-wallet-vs-hardware-wallet?srsltid=AfmBOor65CBdu-6IWQNp46RQXlrEQPR9yr_ed9Wnj34xkBFhSKga3M2g)
- ChatGPT with the inputs
  -  "Write me an article about crypto wallet. What they do, their usage, risk, the different type of wallet, and so on."
  - "For the different type of cold wallet, price their pros and cons"

