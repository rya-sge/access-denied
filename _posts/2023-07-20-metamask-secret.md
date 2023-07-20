---
layout: post
title:  "Deep dive into MetaMask Secrets"
date:   2023-07-20
categories: blockchain cryptographie
tags: crypto wallet blockchain cryptography
description: This article focuses on the different secrets available on Metamask, one of the most used crypto wallets.
image: /assets/article/blockchain/wallet/metamask/MetaMask.svg
---

# Introduction

Trusted by millions of users, **MetaMask** is a self-custodial wallet, providing access to blockchain applications and web3. 

This article focuses on the different secrets available on Metamask.

Metamask has three different **secrets** that are used in different ways :

- The Secret Recovery Phrase
- The password
- The private key

They implement and use several standard and cryptography algorithms to generate these three secrets used inside the application (SRP/seed phrase, private key and password) and keep them safe.

- To generate the recovery Phrase, Metamask implements the standard BIP_0039 from Bitcoin
- To encrypt the SRP and private keys inside the application, Metamask used a password defined by the user. From this password, a key is derived with the algorithm [PBKDF2](https://cryptobook.nakov.com/mac-and-key-derivation/pbkdf2), a derivation key algorithm. The behavior is similar to a password manager.
- With this key, the data are encrypted using the algorithm [AES-GCM](https://www.cryptosys.net/pki/manpki/pki_aesgcmauthencryption.html#:~:text=AES%20with%20Galois%2FCounter%20Mode,38D%20%5BSP800-38D%5D.), a well known algorithm to perform authenticated encryption (confidentiality and authentication).

Reference: [17. User Guide: Secret Recovery Phrase, password, and private keys](https://support.metamask.io/hc/en-us/articles/4404722782107)



## Secret Recovery Phrase ( SRP / Seed Phrase)

The secret Recovery phrase, or sometimes called a seed phrase,

-  It is inspired by the [BIP_0039](https://en.bitcoin.it/wiki/BIP_0039) from Bitcoin [[1.BIP_0039](https://en.bitcoin.it/wiki/BIP_0039)]
   -  This BIP describes the implementation of a mnemonic code / seed phrase -- a group of easy to remember words -- for the generation of deterministic wallets.
   -  It consists of two parts: generating the mnemonic and converting it into a binary seed.
   -  This seed can be later used to generate deterministic wallets using BIP-0032 or similar methods. Unfortunately, I do not know which standard is used by Metamask to generate Deterministic wallet. 
-  This phrase is made of 12 words taken from a list in a random way
-  it will be used to generate the first private key of the wallet. 
   -  The result of the computation will be the same all the time. It is what we call this type of wallet a "deterministic wallet".

Reference: [4. What is a ‘Secret Recovery Phrase’ and how to keep your crypto wallet secure            ](https://support.metamask.io/hc/en-us/articles/360060826432-What-is-a-Secret-Recovery-Phrase-and-how-to-keep-your-crypto-wallet-secure)


### Conservation & Access 

- MetaMask does not keep your SRP in their server, but locally in the application.
- It is why MetaMask is a self-custodial wallet 

In summary, Metamask 

- Does not store any data about the wallet
- No email associated with accounts
- Metamask can not access your wallet from their side => you are responsible to store the SRP in a safe place.

Reference: [[2.MetaMask is a self-custodial wallet](https://support.metamask.io/hc/en-us/articles/360059952212    )], [[3. Why do I have the same seed phrase for all of my MetaMask addresses/accounts?](https://community.metamask.io/t/why-do-i-have-the-same-seed-phrase-for-all-of-my-metamask-addresses-accounts/454)]     

### SRP recovery

It is very important to have backup of your SRP.

But if you are in a situation where you can not unlock your metamask extensions but you :

- Have access to your system data and the Metamask vault files
- You know your password

Typically, it is the case if your computer is broken

Then, there may still be a *possibility* of recovering your Secret Recovery Phrase by using the vault decryptor tool provided by Metamask, see [8. github.com/MetaMask/vault-decryptor](https://github.com/MetaMask/vault-decryptor/tree/master) / [9. support.metamask.io](https://support.metamask.io/hc/en-us/articles/360018766351-How-to-recover-your-Secret-Recovery-Phrase).

Others tools: [https://github.com/JesseBusman/FirefoxMetamaskWalletSeedRecovery](https://github.com/JesseBusman/FirefoxMetamaskWalletSeedRecovery)

### Deterministic wallets / Multiples accounts

It is the reason why it is called "Recovery Phrase" by Metamask because all the private keys will be generated from this phrase, as indicated in the previous point see [13. https://support.metamask.io](https://support.metamask.io/hc/en-us/articles/360015289612-How-to-restore-your-MetaMask-wallet-from-Secret-Recovery-Phrase).

As the wallet is deterministic, it will always re-create the same accounts, in the same order.

When you import a recovery phrase, accounts are automatically re-added if they have a non-zero ETH balance on Ethereum mainet, see  [4. support.metamask.io](https://support.metamask.io/hc/en-us/articles/360015489271).

To have a better understanding, I invite you to read this excellent article [14. What are MetaMask "Accounts" or "Sub-Accounts"? And why are they not as private as they are supposed to be?](https://dev.to/luislucena16/what-are-metamask-accounts-or-sub-accounts-and-why-are-they-not-as-private-as-they-are-supposed-to-be-2c58)

### Complementary information

Here a list of questions related to the secret Recovery Phrase

- [How to reveal your Secret Recovery Phrase](https://support.metamask.io/hc/en-us/articles/360015290032)
- [How do I access my accounts without my Secret Recovery Phrase?](https://support.metamask.io/hc/en-us/articles/13112366068251)

- [Importing a seed phrase from another wallet software: derivation path](https://support.metamask.io/hc/en-us/articles/360060331752)
- [Wallet Migration Guide](https://support.metamask.io/hc/en-us/articles/4867408571803)

- [How to import an account](https://support.metamask.io/hc/en-us/articles/360015489331)

- [How to check my wallet activity on the blockchain explorer](https://support.metamask.io/hc/en-us/articles/360057536611)

- [What is a Secret Recovery Phrase and how do I keep my wallet safe?](https://support.metamask.io/hc/en-us/articles/360060826432)



## Password

The password is used to secure the application itself. If you have the mobile app, you can use a biometric authentication such as facial recognition or your fingerprint.

The password is local to the application.

The browser extension is made as following:

- The password is used to derive a private key by using the algorithm [PBKDF2 [11]](https://cryptobook.nakov.com/mac-and-key-derivation/pbkdf2)
- The data are encrypted with the algorithm AES-GCM

Reference: [5. https://support.metamask.io](https://support.metamask.io/hc/en-us/articles/4405451730331)

To know how the private key is encrypted, MetaMask have published on GitHub a module called [Browser Passworder](https://github.com/MetaMask/browser-passworder). It is a module for encrypting & decrypting JavaScript objects with a password in the browser.

In the README, they indicate

> A key is derived from the password using `PBKDF2` with a salt sampled from `crypto.getRandomValues()`. The data is encrypted using the `AES-GCM` algorithm with an initialization vector sampled from `crypto.getRandomValues()`.

Here the most interesting files:

a. [https://github.com/MetaMask/browser-passworder/blob/main/src/index.ts#L87](https://github.com/MetaMask/browser-passworder/blob/main/src/index.ts#L87)

b. [https://github.com/MetaMask/browser-passworder/blob/main/src/index.ts#L230](https://github.com/MetaMask/browser-passworder/blob/main/src/index.ts#L230)

c. [https://github.com/MetaMask/browser-passworder/blob/main/src/index.ts#L19](https://github.com/MetaMask/browser-passworder/blob/main/src/index.ts#L19)

d. [https://developer.mozilla.org/en-US/docs/Web/API/Crypto/getRandomValues](https://developer.mozilla.org/en-US/docs/Web/API/Crypto/getRandomValues)

For example, link b, you can see that the key is generated with the algorithm `PBKDF2`.

```javascript
const key = await global.crypto.subtle.importKey(
    'raw',
    passBuffer,
    { name: 'PBKDF2' },
    false,
    ['deriveBits', 'deriveKey'],
);
```

With the link c, you can see that the algorithm used is `AES-GCM`

```javascript
const DERIVED_KEY_FORMAT = 'AES-GCM';
```



## Security consideration

### Bug bounties

Metamask has a bug bounties proogram  through the platform **HackerOne** [7. https://support.metamask.io](https://support.metamask.io/hc/en-us/articles/6000270235291-Does-MetaMask-have-a-bug-bounty-program-for-vulnerabilities-) /[8. hackerone.com/metamask](https://hackerone.com/metamask)

### Basic safety and Security tips

- **Never share your Secret Recovery Phrase or private keys with anyone**
- *If you have a large value of tokens in your account(s), consider getting a hardware wallet.**

You can also read [consensys.net/blog/metamask/metamask-secret-seed-phrase-and-password-management/](https://consensys.net/blog/metamask/metamask-secret-seed-phrase-and-password-management/) to get more information.

Reference: 

[10. support.metamask.io](https://support.metamask.io/hc/en-us/articles/360015489591-Basic-Safety-and-Security-Tips-for-MetaMask)

### Files directory

If you are using Opera, you will probably find the different files of the application in the directory `.config/opera/Extensions/nkbihfbeogaeaoehlefnkodbefgpgknn`

and 
`/.config/opera/'Local Extension Settings'/nkbihfbeogaeaoehlefnkodbefgpgknn`



See also [11. ethereum.stackexchange.com/questions/52658/where-does-metamask-store-the-wallet-seed-file-path](https://ethereum.stackexchange.com/questions/52658/where-does-metamask-store-the-wallet-seed-file-path/107765#107765) & [16. community.metamask.io/t/access-metamask-seed-via-pc-files/1027/5](https://community.metamask.io/t/access-metamask-seed-via-pc-files/1027/5)

### Bonus

The application was also analyzed by a security engineer at CertiK in his blog.

[18. How MetaMask stores your wallet secret?](https://www.wispwisp.com/index.php/2020/12/25/how-metamask-stores-your-wallet-secret/)

## Reference

1. [https://en.bitcoin.it/wiki/BIP_0039](https://en.bitcoin.it/wiki/BIP_0039)
2. [https://support.metamask.io/hc/en-us/articles/360059952212](https://support.metamask.io/hc/en-us/articles/360059952212)
3. [https://community.metamask.io/t/why-do-i-have-the-same-seed-phrase-for-all-of-my-metamask-addresses-accounts/454](https://community.metamask.io/t/why-do-i-have-the-same-seed-phrase-for-all-of-my-metamask-addresses-accounts/454)
4. [https://support.metamask.io/hc/en-us/articles/360015489271](https://support.metamask.io/hc/en-us/articles/360015489271)
5. [https://support.metamask.io/hc/en-us/articles/4405451730331](https://support.metamask.io/hc/en-us/articles/4405451730331)
6. [https://support.metamask.io/hc/en-us/articles/6000270235291-Does-MetaMask-have-a-bug-bounty-program-for-vulnerabilities-](https://support.metamask.io/hc/en-us/articles/6000270235291-Does-MetaMask-have-a-bug-bounty-program-for-vulnerabilities-)
7. [https://hackerone.com/metamask](https://hackerone.com/metamask)
8. [https://github.com/MetaMask/vault-decryptor/tree/master](https://github.com/MetaMask/vault-decryptor/tree/master)
9. [https://support.metamask.io/hc/en-us/articles/360018766351-How-to-recover-your-Secret-Recovery-Phrase](https://support.metamask.io/hc/en-us/articles/360018766351-How-to-recover-your-Secret-Recovery-Phrase)
10. [https://support.metamask.io/hc/en-us/articles/360015489591-Basic-Safety-and-Security-Tips-for-MetaMask](https://support.metamask.io/hc/en-us/articles/360015489591-Basic-Safety-and-Security-Tips-for-MetaMask)
11. [https://cryptobook.nakov.com/mac-and-key-derivation/pbkdf2](https://cryptobook.nakov.com/mac-and-key-derivation/pbkdf2)
12. [https://ethereum.stackexchange.com/questions/52658/where-does-metamask-store-the-wallet-seed-file-path/107765#107765](https://ethereum.stackexchange.com/questions/52658/where-does-metamask-store-the-wallet-seed-file-path/107765#107765)
13. [https://support.metamask.io/hc/en-us/articles/360015289612-How-to-restore-your-MetaMask-wallet-from-Secret-Recovery-Phrase](https://support.metamask.io/hc/en-us/articles/360015289612-How-to-restore-your-MetaMask-wallet-from-Secret-Recovery-Phrase)
14. [https://dev.to/luislucena16/what-are-metamask-accounts-or-sub-accounts-and-why-are-they-not-as-private-as-they-are-supposed-to-be-2c58](https://dev.to/luislucena16/what-are-metamask-accounts-or-sub-accounts-and-why-are-they-not-as-private-as-they-are-supposed-to-be-2c58)
15. [https://support.metamask.io/hc/en-us/articles/360060826432-What-is-a-Secret-Recovery-Phrase-and-how-to-keep-your-crypto-wallet-secure](https://support.metamask.io/hc/en-us/articles/360060826432-What-is-a-Secret-Recovery-Phrase-and-how-to-keep-your-crypto-wallet-secure)
16. [https://community.metamask.io/t/access-metamask-seed-via-pc-files/1027](https://community.metamask.io/t/access-metamask-seed-via-pc-files/1027)
17. [https://support.metamask.io/hc/en-us/articles/4404722782107](https://support.metamask.io/hc/en-us/articles/4404722782107)
18. [https://www.wispwisp.com/index.php/2020/12/25/how-metamask-stores-your-wallet-secret/](https://www.wispwisp.com/index.php/2020/12/25/how-metamask-stores-your-wallet-secret/)

