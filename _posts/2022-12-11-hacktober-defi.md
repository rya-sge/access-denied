---
layout: post
title: 2022 - Hacktober in DeFi
date: 2022-12-11
last-update: 
locale: en-GB
lang: en
categories: securite blockchain
tags: DeFi crypto hack
image:
description: This article summarizes the main hacks that took place during the month of October 2022 in the DeFi ecosystem. 
---



This article summarizes the main hacks that took place during the month of October 2022. The hacks are classified according to the following five categories: contracts vulnerabilities, private Key (leak, Profanity, stolen key),  Price Market Manipulation, Scam (ponzi, rug pull, phising), bugs & unknown cause. 

The different hacks are monitored with my twitter account [BlockUnderFire](https://twitter.com/BlockUnderFire) by following several security firms as [Beosin](https://twitter.com/BeosinAlert), [PeckShield](https://twitter.com/PeckShieldAlert), [Certik](https://twitter.com/CertiK) and many others. To have a complete overview, the main reference for this list, e.g the amount of loss, come, from the website [hacked.slowmist](https://hacked.slowmist.io/en/) 

## Contract vulnerabilities

**2022-10-27 / Team Finance**

Amount of loss: $ 14,500,000

Vulnerability: [CWE-20: Improper Input Validation](https://cwe.mitre.org/data/definitions/20.html)

The attacker exploited the migration functions V2 to v3. It was possible to mint fake token and add them to the contract so that they are reimbursed when switching from v2 to v3.

Reference : [Official statement by the team](https://twitter.com/TeamFinance_/status/1585770918873542656), [BlockSec - status](https://twitter.com/BlockSecTeam/status/1585587617063895041)

See [my status](https://twitter.com/BlockUnderFire/status/1586849033183715335)

**2022-10-27 / UvToken**

Vulnerability : [CWE-20: Improper Input Validation](https://cwe.mitre.org/data/definitions/20.html)

*Amount of loss:* 5,011 BNB

> hackers exploited the fact that the UVT eco-project (UVT ECO Staking interest-bearing pool contract) did not strictly judge user input, allowing attackers to maliciously pass in illegal contract addresses and use the malicious contracts to eventually Stole 5000 BNB in the liquid pool created by UVT on Pancakeswap.

Remarks : the stolen funds were landuring through tornado cash.

Reference: [UVT Hack Bounty](https://mirror.xyz/0x843FE6C51CF716906720Dcc5c9d3f71A14545FC3/fsaYuWa4GlLJhdGNkbERVXf5cy2aevGAZ8OfSClmOtQ)

[See my status](https://twitter.com/BlockUnderFire/status/1585522254317867008)

**2022-10-26 / n00dleSwap**

Vulnerability: [SWC-107](https://swcregistry.io/docs/SWC-107) / Reentrancy Attack

 DEX platform for NFTs suffers from a re-entrancy attack on their ERC777 contract according to BlockSec,

Reference: [BlockSec - Status](https://twitter.com/BlockSecTeam/status/1584959295829180416)

[See my status](https://twitter.com/BlockUnderFire/status/1585151343576383491)

**2022-10-20/ Ethereum Alarm Clock /  Contract vulnerabilities**

A vulnerability on the contract, old of four years old but only exploited this month. it was possible to trick the gas refund process for cancelled transactions

Vulnerability: gas

*Amount of loss:* $ 260,000

See [my status](https://twitter.com/BlockUnderFire/status/1583505764802768896)

**2022-10-20 / Petra / bug** 

Vulnerability : bug

*Amount of loss:* -

The wallet printed the wrong mnemonic phrase on the page in some occasion

[PetraWallet - official statement](https://twitter.com/PetraWallet/status/1583235962317852672)



**2022-10-19 / Dataverse**

Type : [CWE-284: Improper Access Control](https://cwe.mitre.org/data/definitions/284.html)

This platform offers service to decentralize your data in the Metaverse & the real world. Their GEO contract on the BSC chain was attacking. According to [SlowMist](https://hacked.slowmist.io/en/), the vulnerability may be a leak of control of the minitng function, thus allowing to mount tokens in an unlimited way

[Dataverse - official statement](https://twitter.com/data_verse/status/1582820158699343873)



**2022-10-18 / BitBTC, Optimism**

*Attack method:* Fake mint

A critical vulnerability affects the bridge BitBTC (optimism) and the exploit has been published on twitter because the team did not answer to messages. The vulnerabaility allowed to mint fake tokens on one side of the bridge and then swap them with real rokens with the other side [cointelegraph](https://cointelegraph.com/news/twitter-user-saves-cross-chain-bridge-from-potential-exploit)

The vulnerability was fixed fast enough to avoid losses, the team had 7 days to fix the vulnerabilities.

[See my status](https://twitter.com/BlockUnderFire/status/1582416233240006664)



**2022-10-18 / Bitkeep Swap (BNB Chain)**

*Amount of loss:* $ 1,180,000

Type : [CWE-20: Improper Input Validation](https://cwe.mitre.org/data/definitions/20.html) / external call

According to BlockSec, the address parameter was not checked and attackers  exploit this to perform arbitrary call to steal the user funds by tranferring them to their address.

Reference: [official statement](https://twitter.com/BitKeepOS/status/1582157619032395776), [BlockSec- Status](https://twitter.com/BlockSecTeam/status/1582261040334901249).,

[See my status](https://twitter.com/BlockUnderFire/status/1582474556790276096)

https://twitter.com/BitKeepOS/status/1586264526777114626

[See my status](https://twitter.com/BlockUnderFire/status/1582474556790276096)

**2022-10-11 / TempleDAO**

*Amount of loss:* $ 2,360,000

Vulnerability : [CWE-20: Improper Input Validation](https://cwe.mitre.org/data/definitions/20.html)

One of the functions took a contract as an argument. This contract was not verified and the hacker took the opportunity to give his own contract as an argument, which allowed him to withdraw all the tokens.  According to Peckshield, Tornado Cash was used to move the funds.

Reference: [Accident report](https://docs.google.com/document/d/1-chBi1Yqdmz8h81Arg4PIRbSXYFd2nqOKUXCy2c3kZk/edit), [BlockSec - Status](https://twitter.com/BlockSecTeam/status/1582261040334901249)

[See my status](https://twitter.com/BlockUnderFire/status/1579859304102105093)

**2022-10-11 /  Rabby**

*Amount of loss:* $ 190,000

Vulnerability : [CWE-20: Improper Input Validation](https://cwe.mitre.org/data/definitions/20.html) + arbitrary external call 

The root cause is a vulnerability in the call of the function [CallWithValue]( https://docs.openzeppelin.com/contracts/4.x/api/utils#Address-functionCallWithValue-address-bytes-uint256-) of OpenZeppelin Library.  This function  performs a low leval Call. The address parameter was not checked and attackers  exploit this to perform arbitrary call to steal the user funds by transferring them to their address.

RabbySwap use their Rabby Insurance Fund to reimbursement fund to users [Reference](https://rabby.io/claims)

Reference: [official statement](https://twitter.com/Rabby_io/status/1579819525494960128),  [Supremacy Inc - Status](https://twitter.com/Supremacy_CA/status/1579813933669486592)

[See my status](https://twitter.com/BlockUnderFire/status/1579944589250945025)

**2022-10-02 / Transit Swap (Cross-chain DEX Aggregator)**

*Amount of loss:* $ 28,900,000

CWE: [CWE-20: Improper Input Validation](https://cwe.mitre.org/data/definitions/20.html) + Arbitrary external call.

The root cause seems to be a lack of verification in the data passed by the user according to SlowMist.  The attacker can exploit this to perform an arbitrary external call to steal the authorized tokens by a user. A part of stolen funds have been laundered through Tornado Cash.

Fun Fact : One of the attackers was front-run by a bot whose private key was vulnerable to the Profanity vulnerability. BlockSec, a security firm, used this vulnerability to recover a part of stolen funds .

Reference: [SlowMist](https://slowmist.medium.com/cross-chain-dex-aggregator-transit-swap-hacked-analysis-74ba39c22020), [BlockSec](https://blocksecteam.medium.com/how-we-recover-the-stolen-funds-for-transitswap-and-babyswap-2a68c9f4d66f)

[See my status](https://twitter.com/BlockUnderFire/status/1576654721464832000)

**2022-10-09 / Xave Finance / DAO**

*Amount of loss:* $ 635

Vulnerability: library misconfiguration,**[CWE-453: Insecure Default Variable Initialization](https://cwe.mitre.org/data/definitions/453.html)**

The DAO system has a vulnerability allowing the attacker to issue a proposal to the DAO and then execute it immediately. The attackers profits of it by minting 100,000,000,000,000 tokens and swapping it in the 2 Uniswap RNBW:ETH pool. The  issue concerned the use of the library [zodiac-module-reality](https://github.com/gnosis/zodiac-module-reality/tree/7a5244d0a0a70b023d23af59659e0c055be7cca2)  The default setting had not been changed and one of these parameters was precisely the one that gave the Gnosis module the time to check the proposal before accepting it.

Reference 1: [Ancilia - status](https://mobile.twitter.com/AnciliaInc/status/1578952542926491650), [Xave Finance - post mortem](https://medium.com/xave-finance/post-mortem-safenap-dao-module-bug-505958e9c716)

Reference 2: [DaoModule misconfig exploit on HaloDao contracts](https://gist.github.com/andreiashu/da5909a7230ff67a8c3b4018a9717276), [zodiac-module-reality - DaoModule.sol#L261-L264](https://github.com/gnosis/zodiac-module-reality/blob/7a5244d0a0a70b023d23af59659e0c055be7cca2/contracts/DaoModule.sol#L261-L264)

### External Libraries

**2022-10-21 OlympusDAO /** 

*Amount of loss:* $ 292,000

According to PeckShield, OlympusDAO was hacked for ~$292K due to a lack of input validation in one of their contracts.  The hack is also confirmed by [The Block](https://www.theblock.co/post/178927/hacker-drains-olympus-dao), and according to them, all the stolen funds were returned.

After doing some research, it seems that the vulnerable code comes from a contract created by Bond-Protocol [https://github.com/Bond-Protocol/bond-contracts/blob/master/src/BondFixedExpiryTeller.sol](https://t.co/9lwiYtL6B4)

[See my status](https://twitter.com/BlockUnderFire/status/1583487846488641537)

**2022-10-06 / BNB Chain**

Amount of loss: 2,000,000 BNB

Vulnerability:  IAVL merkle proof verification 

The bridge BNB suffers from a hack of (iniital). The blockchain

The root cause is a vulnerability in IAVL merkle proof verification in Cosmos SDK. Cosmos SDk by itself do not suffer from the vulnerability because the Cosmos-SDK only uses the IAVL tree for merkle storage while BNB uses it for proofs.  The hacker exploited the vulnerability to create extra [BNB](https://www.investopedia.com/terms/b/binance-coin-bnb.asp) tokens out of thin air. The hacker made a profit of 100 millions de dollars before the created tokens were  frozen by validators. 

BNB chain decide to organize a governance vote to choose what to do but i do not knwo what is the result [BNB Chain Ecosystem Update](https://www.bnbchain.org/ru/blog/bnb-chain-ecosystem-update/)

During an auto-burn, On October 13, the chain burnt 2,065,152.42 BNB, worth over $549 (r$549 million )

Reference: [Cosmos - SDK](https://forum.cosmos.network/t/cosmos-sdk-security-advisory-dragonfruit/7614), [decrypt.co](https://decrypt.co/111905/binance-burns-bnb-tokens-hacker-minted), [investopedia.com](https://www.investopedia.com/binance-got-hacked-6748215), 

[See my status](https://twitter.com/BlockUnderFire/status/1579234924707516418?t=7gMUIxtP9U4P6OjhWFv0lw&s=19)

## Private key

This category regroups the hacks which the root cause is a vulnerability linked to the private key. The profanity vulnerability continues to have a big impact with several hacks related.

**2022-10-29 / Eden Network**

According to PANews (and reported by SlowMist), an attacker has taken control of the [@EdenNetwork](https://twitter.com/EdenNetwork) token  contract due to a leak of a private key (perhaps Profanity)

Reference:  [panewslab](https://www.panewslab.com/zh/sqarticledetails/rw58tidv.html)

Remark: I have not seen any other confirmation of the attack, nor post-mortem

**2022-10-28 / FriesDAO**

Amount of loss : $ 2,300,000

Vulnerability : Private Key generated with Profanity

According to the post-mortem statement, one of the private key, with ownership on the contract has been generated with the profanity tool. The transfer  of ownership to a safer wallet was forgotten by the team.

Reference: [Official statement of the team](https://twitter.com/friesdao/status/1585712229067915264), [Post-mortem](https://docs.google.com/document/d/1xKZmj1aeM9iFrdQ7sieUNvh0_UI60worl1lfs5ImXk0/edit)

**2022-10-24 / Melody**

Possible cause : front-end hack or private key

Reference: [Melody - official statement](https://twitter.com/Melody_SGS/status/1584607069251870720), [Beosin](https://twitter.com/BeosinAlert/status/1584902496660893699)

[See my status](https://twitter.com/BlockUnderFire/status/1584790417740271617)

**2022-10-23 / Layer2DAO (Optimism)**

Vulnerability : Get multi-signature permission

*Amount of loss:* 49,950,000 L2DAO

Laundry : Tornado Cash

A hacker managed to access to the multisig wallet of Layer2DAO, a [#DAO](https://twitter.com/hashtag/DAO?src=hashtag_click) investment firm, on Optimism. The number of tokens stolen is 49,950,000

[See my status](https://twitter.com/BlockUnderFire/status/1585518408136884225)

**2022-10-17 / LiveArt**

*Amount of loss:* 197 NFTs

Vulnerability : leak of Private Key

According to [SlowMist](https://hacked.slowmist.io/en/),  an attacker manages to steal the official wallet of NFT Platform LiveArtX

According to [the Block](https://www.theblock.co/post/177630/liveart-burns-stolen-nfts-offers-compensation-to-buyers), LiveArtX choose to destroy All the 197 stolen NFT

[LiveArtX - Official statement](https://twitter.com/LiveArtX/status/1581736201111089152)

[MistTrack - status](https://twitter.com/MistTrack_io/status/1581916015553699840)

**2022-10-11 / QANplatform**

*Amount of loss:* $ 2,000,000

The deployer of the smart contract QANX Bridge was generated by the tool [cenut/vanity-eth-gpu](https://github.com/cenut/vanity-eth-gpu/) which is vulnerable to the Profanity Vulnerability.

> At 08:16:39 AM +UTC the exploiter was able to drain 1,444,169,100.98 QANX from the QANX Bridge on Binance Smart Chain (BSC) and sold it for 3090.5 BNB on PancakeSwap which was later tunnelled into Tornado Cash.

Reference: [QANplatform - post mortem](https://medium.com/qanplatform/qanx-bridge-wallet-disclosure-analysis-continuously-updated-724121bbbf9a)

[See my status](https://twitter.com/BlockUnderFire/status/1579935127832231938)

## Price Market Manipulation

**2022-10-25  / ULME token**

Method: Flash Loan Attack

Vulnerability:  [CWE-284: Improper Access Control](https://cwe.mitre.org/data/definitions/284.html) 

The attacker uses a flashloan to borrow BUSD, SWAP these BUSD for ULME on Pancake, and use a vulnerability on the smart contract (unrestricted access control) to abuse of the smart contract

Reference: [BlockSec](https://twitter.com/BlockSecTeam/status/1584839309781135361)

[See my status](https://twitter.com/BlockUnderFire/status/1584842931135213568)

**2022-10-24 / Market XYZ**

Method: Oracle Price Manipulation

One pool of the Quickswap lending market suffers from an oracle price manipulation, This is also affected QiDaiProtocol.

Reference: [mkartet xsy - official statement](https://twitter.com/market_xyz/status/1585317167335370752/photo/1)

[See my status](https://twitter.com/BlockUnderFire/status/1584435589033914368)

**2022-10-20 / HEALTH token**

 HEALTH token (BSC) suffers from a price manipulation attack.

Reference: [BlockSecTeam](https://twitter.com/BlockSecTeam/status/1583073442433495040)

**2022-10-19 / Moola Market**

*Amount of loss:* $ 9,000,000

Method: Oracle Price Manipulation

Reference: [Moola Market - Status](https://twitter.com/Moola_Market/status/1582588102790434816), [Certik](https://www.certik.com/resources/blog/8ENVqveSYRcppTHOcxG29-moola-market)

Steps :

1) The attacker inflated the value of the MOO tokens, native token of the platform

2) They used the inflating tokens to borrow more valuable assets like CELO, cEUR, cUSD.

Moola Market negotiated a bug bounty with the attacker to recover a part of the profits (~ $500,000)

**2022-10-12 / Mango**

Method: Oracle Price Manipulation

Mango markets suffers from an oracle manipulation attacks. Finally, an agreement was made with the hacker : $67M in various crypto assets have been returned to the DAO and the hacker keeps nevertheless $47 million. This agreement was submitted to the DAO as a proposal and was accepted, see the proposition [here](https://dao.mango.markets/dao/MNGO/proposal/GYhczJdNZAhG24dkkymWE9SUZv8xC4g8s9U8VF5Yprne).

> We are currently investigating an incident where a hacker was able to drain funds from Mango via an oracle price manipulation.  

The different steps of the attack :

1) The attacker Opens large MNGO-PERP position on Mango Markets

2) The Oracle price pumped upon which MNGO-PERP was based

3) With the token pumped, the attacker can borrow from Mango and drained the protocol for $100mn worth.

Reference: [Mango - official statement](https://twitter.com/mangomarkets/status/1579979342423396352), [13.10](https://twitter.com/mangomarkets/status/1580517795149643776), [15.10](https://twitter.com/mangomarkets/status/1581351549644591104), [18.10](https://twitter.com/mangomarkets/status/1582450206645268480)

[Mango Markets and the Benefits and Limitations of Oracles -  Riyad Carey](https://blog.kaiko.com/mango-markets-and-the-benefits-and-limitations-of-oracles-753ce6d2a732)

[see my status](https://twitter.com/BlockUnderFire/status/1580078311585513472)

**2022-10-18 / PLTD**

*Amount of loss:* 24,497 BUSD

Method: Flash Loan Attack

[$PLTD](https://twitter.com/search?q=%24PLTD&src=cashtag_click) suffers from a price manipulation attack according to [Beosin](https://twitter.com/BeosinAlert/status/1582181583343484928).

[See my status](https://twitter.com/BlockUnderFire/status/1582258688110100480)

https://www.cybavo.com/glossary/flash-loan-attack/

**2022-10-17 / MTDAO**

*Amount of loss:* 487,042.615 BUSD

**2022-10-12 / ATK**

Method: Flash loan attack

*Amount of loss:* $ 120,000

Reference: [panewslab](https://www.panewslab.com/zh/sqarticledetails/q1qgvsgc.html)

The attack consisted in two steps :

1) Flashloan attack to obtain a large quantity of ATK from the contract.

2) Convert the tokens in pair BSC-USD 

The result was laundered through tornado cash

 **2022-10-05 - Sovryn**

*Amount of loss:* $ 554,822

Vulnerability: cross-contract reentrancy attack

> The exploit utilized a manipulation of the iToken price.

According to the team, the price manipulation was made by exploiting a cross-contract reentrancy attack

Reference : [offcial statement of sovryn](https://www.sovryn.app/blog/interim-exploit-update)

> This attack was only possible because the exploiter interacted with two different contracts with separate storage, where one contract depended on the other.

Reference : [www.sovryn - October 2022 lending pool exploit postmortem](https://www.sovryn.app/blog/october-2022-lending-pool-exploit-postmortem)

## Scam

**2022-10-25 / Spookie Finance (Avalanche)**

The front-end of the official website was probably hacked. The website printed a malicious transaction to steal the user's assets.

Since then the twitter account and the website are no longer available

Reference: [Mario Paladin - Status](https://twitter.com/MarioAtPaladin/status/1584938712856526850)

**2022-10-20 / Freeway  / Ponzi**

*Amount of loss:* $ 100,000,000

Type : Ponzi

The deposit platform halted all withdrawals, it was a ponzi according to [FatMan](https://twitter.com/FatManTerra/status/1584247387941351424).

See [my status](https://twitter.com/BlockUnderFire/status/1585153090738876417)

**2022-10-20 / Mango INU  / Scam**

*Amount of loss:* $ 48,500

The token, deployed by the Mango Market exploiter is an exist scam

Reference: [CertiKAlert - status]( https://twitter.com/CertiKAlert/status/1582976826653126656)

**2022-10-11 / The Micro Elements (BSC)**

BSC address 0xd631464f596e2ff3b9fe67a0ae10f6b73637f71e.

*Amount of loss:* $ 548,600

Another exit scam

Reference: [Certik - Status](https://twitter.com/CertiKAlert/status/1579707616002908160)

**2022-10-05 / Sex DAO / rug pull**

A classic rug pull

*Amount of loss:* 220,000 USDT

Reference : [www.panewslab.com](https://www.panewslab.com/zh_hk/articledetails/6jry6n1d4iu7.html)

**2022-10-09 / Jumpnfinance  / rug pull**

*Amount of loss:* $ 1,150,000
The scammer call a function in the contract to extract all user's funds.

Reference: [https://bscscan.com/address/0xd3de02b1af100217a4bc9b45d70ff2a5c1816982](https://bscscan.com/address/0xd3de02b1af100217a4bc9b45d70ff2a5c1816982)

### Phishing

**2022-10-28 / OpenSea/ Contract Vulnerability**

Old contract of [#OpenSea](https://twitter.com/hashtag/OpenSea?src=hashtag_click) (before Seaport upgrades) are vulnerable to a scam where the goal is to convince the user to sign a specific transaction  that gives the attacker ownership of the proxy contract's user. This contract can withdraw the user's NFTs, so the attacker can withdraw them too.

Reference: [PocketUniverseZ - status](https://twitter.com/PocketUniverseZ/status/1585793457385140225)

See [my status](https://twitter.com/BlockUnderFire/status/1587576704310157318)

**2022-10-23 / FTX & 3Commas** 

*Amount of loss:* $ 6,000,000

> The theft occurred outside of the 3Commas system, via a phishing attack conducted on inauthentic websites mocked up to resemble the 3Commas interface. 

Reference: [3commas - official statement](https://3commas.io/blog/3commas-security-update-october-20)

**2022-10-22  / Blur / Impersonate**

Amount of loss: no known loss

A twitter account tried to impersonate the official account of Blur and shared phishing links

Reference: [Blur - status](https://mobile.twitter.com/blur_io/status/1583331869839409152)

**2022-10-22 / Vivity / Discord hack**

*Amount of loss:* no known loss

The discord of Vivity was hacked

[Certik - Status](https://twitter.com/CertiKAlert/status/1583617781370851328)

**Gate.io / twitter hack**

The twitter account of [http://Gate.io](https://t.co/1pOaTn54z2) was hacked and spreads phishing / scam links.

See [my status](https://twitter.com/BlockUnderFire/status/1583748244483452929)

**2022-10 / Solana Phantom Fake Update**

A malicious airdrop contains a false security update to convince the user to install a malware(MarsStealer) which targets cryptocurrencies

Reference: [bleepingcomputer](https://www.bleepingcomputer.com/news/security/fake-solana-phantom-security-updates-push-crypto-stealing-malware/)



## Bug

## Others

**2022-10-28 / THORChain / Network interruption**

The THORCHAIn network suffered front an interruption due to a consensus bug. The root cause is an incorrect type, a Uint value (instead of uint64) was pushed into a string, which then took the value of an arbitrary large number.

Reference: [THORChain - Status](https://twitter.com/THORChain/status/1585800482764730369)

**TokenPocket / DoS**

*Amount of loss:* -

A DoS attack target the website TokenPocker

Reference: [official statement](https://twitter.com/TokenPocket_TP/status/1579787917656207361)

**2022-10-13 / FTX gas stealing attack**

An attacker managed to mint XEN tokens without paying the gas. 

The root cause was that FTX does not have a gas limit while the withdrawal fee is free. Here the gas limit was equal to 500'000 whereas the base value is 21'000. Moreover, the recipient could be different from the contract address.

- The attacker deployed a contract and performed an ETH withdrawal to it.

- In the fallback function of the contract, a call to the mint function of the XEN project ($XEN tokens) is made
- Different other steps are necessary, but in summary, since the initiator of the transaction was FTX, the gas was paid by FTX but the receiver address of the mint token was the attacker's address

Reference: [x-explorer](https://mirror.xyz/x-explore.eth/M2BJgQJaj2JK0mAO9OecByja3tU7mKXbHR_Agjs-MjA), [Beosin](https://twitter.com/BeosinAlert/status/1580426718711463937)

[See my status](https://twitter.com/BlockUnderFire/status/1580801689988186112)

## Unknown

**2022-10-14 / EFLeverVault**

EFLeverVault (a mev bot I believe) was exploited for around 750 ETH

Reference: [MevRefund](https://twitter.com/MevRefund/status/1580917351217627136)