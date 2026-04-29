# Lonbard

Lombard is dedicated to expanding the digital economy by transforming Bitcoin’s utility from a mere store of value into a productive financial tool. While Bitcoin remains the world’s largest crypto asset, with over $1 trillion worth of Bitcoin often sitting idle, its utility is limited compared to other digital assets. Lombard sees a significant opportunity to change this by connecting Bitcoin to decentralized finance (DeFi).

Lombard is driven by the fact that if just 10% of Bitcoin's $1.5 trillion market cap flows into DeFi, the total value locked (TVL) in the ecosystem could more than double, catalyzing unprecedented growth and enabling sustainable market dynamics over time. Lombard believes this potential can be unlocked through a security-first liquid Bitcoin primitive—LBTC. Our flagship product, LBTC, is a secure Bitcoin liquid staked token (LST), designed to empower anyone—from individual holders to large institutions—to amplify the utility of their Bitcoin. It allows users to earn a native yield from providing economic security to networks via Babylon and participate in DeFi, all while maintaining the value of the original asset.  By building LBTC on top of Babylon, Lombard’s LBTC bridges the gap between Bitcoin’s immense economic value, security capabilities, and the dynamic opportunities within PoS and DeFi ecosystems, marking a transformative phase for Bitcoin in the decentralized economy.

## About Lombard

Lombard’s founding team is composed of DeFi experts from Polychain, Babylon, Argent, Coinbase, and Maple. Each team member brings extensive experience in starting, scaling, and operating companies in the DeFi space.

Lombard is incubated by Polychain Capital. Polychain Capital’s incubation of Lombard provides financial backing and access to its expert teams and resources. Polychain Capital led Lombard's $16 million seed round in July 2024. The round welcomed participation from Babylon, dao5, Franklin Templeton, Foresight Ventures, HTX Ventures, Mirana Ventures, Mantle EcoFund, Nomad Capital, OKX Ventures, and Robot Ventures and more. [Read more](https://www.lombard.finance/blog/lombard-16m-seed-round-polychain/). 

Named after the historic Lombard Street in London—a hub of financial activity since the Middle Ages—Lombard symbolizes a place where all participants are connected to opportunity. By adopting the Lombard name, we rebuild its legacy on digital blocks, transforming it into a modern nexus of innovation and connectivity.

## LBTC: Liquid Bitcoin Standard

LBTC is liquid Bitcoin; it's yield-bearing, cross-chain, and 1:1 backed by BTC. LBTC enables yield-bearing BTC to move cross-chain without fragmenting liquidity, and is designed to seamlessly integrate Bitcoin into the decentralized finance (DeFi) ecosystem while maintaining the security and integrity of the underlying asset.

### Attributes of LBTC:

- **Earns native yield + rewards:** LBTC earns native yield from Babylon staking and Lombard Lux, and can be used across DeFi to maximize returns.
- **Cross-chain compatible:** LBTC is natively minted across major blockchain ecosystems, enabling seamless cross-chain movement.
- **Liquid & DeFi compatible:**  LBTC, backed 1:1 with BTC, can be used as collateral in lending and borrowing protocols, perp DEXs, and more.
- **Secure:** LBTC is secured by a network of consortium ecosystems, providing better security than centralized wrapped tokens and unsecured bridges.

### Benefits to LBTC holders:

- **LBTC holders retain the liquid value of their BTC**
- **LBTC holders passively accrue multiple layers of yields:**
  - Babylon Staking Yield
  - Babylon Points
  - Lombard Lux
  - Yields and Incentives from LBTC destination chains and protocols
- **LBTC holders can earn even more by deploying their LBTC into DeFi**
  - Providing liquidity on Decentralized Exchanges
  - Lending LBTC or borrowing against it
  - Executing yield trading strategies
  - Committing LBTC to automated yield-generating vaults

## DeFi Vaults

Lombard partners with several  vault infrastructure providers to offer automated DeFi yields.

Lombard DeFi Vault is an automated yield management solution designed to maximize BTC-denominated returns by strategically allocating deposits across various opportunities within the DeFi ecosystem. 

The vault designed to bridge the gap between bitcoin and DeFi, offering enhanced yields through a seamless experience and eliminating the need for manual management of positions. 

Participating in DeFi can be complex, often requiring technical knowledge to select strategies and manage positions. The DeFi Vault simplifies this process by leveraging Veda’s expertise in tokenizing DeFi yields. The vault accepts both LBTC, wBTC and cbBTC, offering users access to a variety of DeFi strategies including Aave, Pendle, Uniswap, and others.

The vault is developed in collaboration between Lombard and [Veda](https://veda.tech/). Veda is a native yield protocol that tokenizes yields, making them more accessible to users. With over $1 billion in TVL, Veda serves as a core infrastructure partner for [ether.fi](https://www.ether.fi/products#liquid).

------

### How It Works

After depositing LBTC, wBTC, eBTC or cbBTC into the Lombard DeFi Vault, users receive a liquidity provisioning (LP) token called LBTCv. 

LBTCv represents the user’s share of the vault’s balance, including both the principal value and accumulated yield after fees, and any Lombard Lux, Babylon or Veda points that are earned — updated hourly in the dApp.  [Read more about how LBTCv is calculated](https://docs.lombard.finance/lbtc-liquid-bitcoin/defi-vaults/lombard-defi-vault/lbtc-lbtcv).

The vault engages into DeFi strategies and optimizes yields through active rebalancing. These strategies include:

- providing liquidity on DEX platforms like Uniswap (tight price ranges) and Curve, 
- lending through platforms such as Gearbox and Morpho, 
- and engaging in yield trading on protocols like Pendle. 

New positions are taking on a case-by-case basis. Volumes in pools are updated hourly on the dashboard.

Additionally, the Lombard DeFi Vault automates compounding by efficiently converting all accrued DeFi rewards back into additional liquidity for the vault. These rewards get distributed proportionally amongst LBTCv holders; when a user withdraws from the vault, any accrued value in the vault's total liquidity will be returned proportionally to their respective stake in vault's total pooled liquidity.

By leveraging multiple DeFi strategies, the vault ensures that yields are diversified across various sources, reducing reliance on any single strategy. This diversification helps mitigate risks while enhancing potential returns.

The Lombard DeFi Vault can be accessed via the [Lombard WebApp](https://www.lombard.finance/app/). For detailed instructions on how to deposit funds, you can also follow the step-by-step guide provided in the[ Depositing in the Lombard DeFi Vault](https://docs.lombard.finance/lbtc-liquid-bitcoin/user-guides/lombard-defi-vault-depositing-and-withdrawing) doc.

### Details:

- **Yield:** DeFi yields are automatically converted into LBTC and accumulate directly within the Lombard DeFi Vault, allowing users to benefit from continuous growth.
- **Fees:** 
  - A competitive 1.5% annual management fee is applied. The pro rata fee is deducted periodically (typically once per day) when Lombard’s DeFi Vault rebalances its position. This fee is reflected in your balance, ensuring transparency and clarity in your returns.
  - WBTC has a 40pbs deposit fee, and FBTC has a 30bps fee.
  - LBTC, cbBTC, and eBTC deposits have no fees. 
  - When you withdraw, you will enter a withdrawal queue, which requires a small discount ranging from 1 basis point of your LP to compensate the Solver's gas costs for fulfilling your withdrawal.
- **Withdrawals:** Withdrawals can be initiated anytime, with LBTC redeemable within 3 days. A new withdrawal cannot be issued whilst a previous withdrawal is still processing.
- **Additional Rewards:** Depositors earn 4x Lombard Lux, 3x Veda Points, and 1x Babylon Points.
- **Access:** Users can deposit into the vault from the Ethereum and Base networks. Staking directly through Babylon, and selecting Lombard's FP does not make users elligible for Lombard Lux.

### Risks Disclaimer

Lombard DeFi Vault is composed of a diverse range of DeFi products, each carrying inherent smart contract risks and varying levels of economic risk. Users should be aware that these risks can impact both the principal and yield. It is essential to carefully assess the risk tolerance before participating in the vault.

### Audits & Code:

- **Audit:** https://github.com/Se7en-Seas/boring-vault/tree/main/audit
- **Vault Contract:** 0x5401b8620E5FB570064CA9114fd1e135fd77D57c
- **Teller Contract:** 0x4E8f5128F473C6948127f9Cbca474a6700F99bab
- **Accountant Contract:** 0xcB762D7bedfA78c725f2F347220d41062b6B0A4A
- **Manager:** 0xeBC7d8B1796eE587c2E91473c0b07A34a1a61E70
- **Withdrawal Queue:** 0x3b4aCd8879fb60586cCd74bC2F831A4C5E7DbBf8

### **Legal Note**

The Lombard Protocol restricts access to users in certain jurisdictions, including the United States. For a full list of restricted parties, please visit our [Terms of Service](https://docs.lombard.finance/legals/terms-of-service). 

------

### Note on Veda:

Lombard’s DeFi Vault is built using the Veda infrastructure. Veda is a native yield protocol that partners with projects like Lombard to tokenize yields in their DeFi ecosystem and make those yields more accessible to users. Veda already boasts $1 billion in TVL and serves as infrastructure for [ether.fi Liquid](https://www.ether.fi/products#liquid).

You can learn more about Veda on X https://x.com/veda_labs.  Veda points track your participation within the Veda ecosystem. Learn more about [Veda points](https://veda.tech/blog/launching-season-1-of-the-veda-points-campaign) in this blog.

## Bitcoin Beta Vaults

Lombard has teamed up with Concrete to launch a BTC DeFi vault (similar to our Veda vault on ETH Mainnet) that allocates LBTC and WBTC into conservative DeFi strategies (DEX liquidity provision and passive lending) on Berachain in a curated and automated fashion.

Lombard and Concrete have built with Berachain, Royco, and the top projects in the Bera ecosystem to provide early access to Berachain with LBTC & wBTC. 

Upon Berachain Mainnet, the Bitcoin Bera Vault operated by Concrete will deploy deposits across various strategies utilizing Dolomite and Kodiak and other partner protocols participating in Boyco.

## Note on Bridging:

Bridging through Boyco contracts via Layerzero bridge. *This is not the Boyco program itself. That will start in the near future, and Berachain mainnet will follow within a couple weeks of Boyco launch.*

### Risks Disclaimer

Lombard DeFi Vault is composed of a diverse range of DeFi products, each carrying inherent smart contract risks and varying levels of economic risk. Users should be aware that these risks can impact both the principal and yield. It is essential to carefully assess the risk tolerance before participating in the vault.

## Audits & Code:

- **Audit:** https://www.halborn.com/audits/concrete/earn-v1
- **ctWBTC:** [0x52c2bc859f5082c4f8c17266a3cd640b5047370e](https://etherscan.io/token/0x52c2bc859f5082c4f8c17266a3cd640b5047370e)
- **ctLBTC:** [0x34bdba9b3d8e3073eb4470cd4c031c2e39c32da8](https://etherscan.io/token/0x34bdba9b3d8e3073eb4470cd4c031c2e39c32da8)

### **Legal Note**

The Lombard Protocol restricts access to users in certain jurisdictions, including the United States. For a full list of restricted parties, please visit our [Terms of Service](https://docs.lombard.finance/legals/terms-of-service). 

------

## Note on Concrete:

The Bitcoin Bera Vault is built using Concrete Infrastructure. [Read more about Concrete.](https://docs.concrete.xyz/Overview/welcome)

### Smart Contracts

There are three types of contracts deployed on networks where LBTC is supported:

- **The LBTC ERC-20 token smart contract**: Mints and burns LBTC tokens.
- **Consortium’s governance smart contract**: Reads and commits state changes related to LBTC, ensuring that all actions are transparent and verifiable on the blockchain.
- **Proxy upgrade timelock smart contract**: Delays the proxy upgrades of our smart contracts by one hour. This provides an additional layer of security which enables us to take actions or cancel the upgrade if a malicious actor's activity is detected.

Smart contract audit reports are [available on GitHub](https://github.com/lombard-finance/evm-smart-contracts/tree/main/docs/audit).

EthereumBinance Smart Chain (BSC)BaseCornSwell

Component

Address

LBTC ERC-20

[0x8236a87084f8B84306f72007F36F2618A5634494](https://etherscan.io/token/0x8236a87084f8B84306f72007F36F2618A5634494)

LBTCv ERC-20

[0x5401b8620E5FB570064CA9114fd1e135fd77D57c](https://etherscan.io/address/0x5401b8620E5FB570064CA9114fd1e135fd77D57c)

Consortium's Governance

[0xed6D647E2F81E5262101aFf72c4A7bcDcfd780e0](https://etherscan.io/address/0xed6D647E2F81E5262101aFf72c4A7bcDcfd780e0/)

Proxy Upgrade Timelock

[0x055E84e7FE8955E2781010B866f10Ef6E1E77e59](https://etherscan.io/address/0x055E84e7FE8955E2781010B866f10Ef6E1E77e59)

Bascule Drawbridge

[0xc750eCAC7250E0D18ecE2C7a5F130E3A765dc260](https://etherscan.io/address/0xc750eCAC7250E0D18ecE2C7a5F130E3A765dc260)

# Protocol Fees

This section outlines all the fees associated with utilizing the Lombard protocol. Understanding these fees is crucial for users to manage their interactions with the platform.

### Staking Fees

- On chains where network fess are higher, such as Ethereum, users authorize a small network fee in LBTC. This fee is deducted when Lombard Protocol relays a transaction to mint LBTC, and is a contribution towards the network gas fee paid by Lombard Protocol.
  - In the unlikely event where Lombard Protocol does not mint LBTC, the user may do this themselves, paying the associated network gas fee. In this scenario, there are no fees deducted by Lombard Protocol.

### Performance Fees

- Lombard delegates BTC stakes to Finality Providers (validators) who take a 3–5% commission on all rewards. 

### Unstaking Fees

A fixed 0.0001 LBTC unstaking fee applies, called the *Network Security Fee*. This fee is the minimum amount:

- to contribute to Bitcoin network fees paid by Lombard; and,
- to secure Lombard by setting the economic cost of denial-of-service attacks to be prohibitive.

### DeFi Vault Management Fees

- A management fee of 1.5% per annum will be charged on holdings in the Lombard DeFi Vault.

# Protocol Architecture

Lombard Technical Architecture

## Current Architecture

![img](https://docs.lombard.finance/~gitbook/image?url=https%3A%2F%2F2727780006-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FshysQ5d1rHU8C0eDQoLF%252Fuploads%252FKrzzMopVOSgfe2pIoMVx%252Fimage.png%3Falt%3Dmedia%26token%3D824eb4bd-b70c-4610-b5d7-60c0adb38363&width=768&dpr=4&quality=100&sign=1efa8625&sv=2)

### Components

- [Lombard Ledger (Consortium)](https://docs.lombard.finance/technical-documentation/protocol-architecture/lombard-ledger-consortium): The Cosmos app-chain at the heart of Lombard Protocol.
- [CubeSigner (Cubist)](https://docs.lombard.finance/technical-documentation/protocol-architecture/cubesigner-key-management): Non-custodial key management with multiple layers of control.
- [LBTC Smart Contracts](https://docs.lombard.finance/technical-documentation/protocol-architecture/lbtc-design): Deployed on all [Supported Blockchains](https://docs.lombard.finance/lbtc-liquid-bitcoin/supported-blockchains).
- [Babylon](https://docs.lombard.finance/technical-documentation/protocol-architecture/babylon-staking): The market place for Bitcoin economic security, where Lombard Protocol delegates Bitcoin staking to secure Bitcoin Secured Networks, earning yield for LBTC holders.
- [Bascule Drawbridge](https://docs.lombard.finance/technical-documentation/protocol-architecture/bascule-drawbridge): A state oracle operated by Cubist, serving as an additional layer of security for every LBTC mint and every BTC withdrawal.
- [Trustless Relayer](https://docs.lombard.finance/technical-documentation/protocol-architecture/trustless-relayer): Lombard operates several non-critical APIs and services to aid in communication between networks and user experience.

## Overview of Key Processes

### Minting LBTC from Bitcoin

1. The staker initiates a staking request and receives a unique BTC address generated by the Security Consortium. The BTC address is verified client-side before display.  Each BTC address corresponds to where LBTC can be minted (the destination blockchain), who LBTC will be minted to (an address on the destination blockchain), and a partner code used for tracking purposes.
2. After the staker has deposited BTC, the Trustless Relayer watches the transfer and, once the transfer is confirmed, requests the Consortium to verify it.
3. After the Consortium has verified the request on Ledger, the Trustless Relayer uses the authorized signatures to mint the LBTC on the destination blockchian.
   1. If the Trustless Relayer fails to mint LBTC, the signatures can always be used directly by the staker to mint LBTC.

### Redeeming LBTC for Bitcoin

1. The staker burns the LBTC tokens on the designated blockchain by calling the `redeem` function on the LBTC contract, specifying the BTC address to withdraw to.
2. The Trustless Relayer observes the burn transaction (finding it on the designated blockchain and awaiting for the transaction to be confirmed), and then requests the Consortium to verify it.
3. After verification, on Ledger, Lombard Protocol will queue the withdrawal request. The daily process in [Staking Bitcoin](https://docs.lombard.finance/technical-documentation/protocol-architecture#staking-bitcoin) will ensure sufficient liquidity exists for the withdrawal to be processed.
4. When the time comes for the withdrawal to be honoured, the Consortium builds a Bitcoin transaction with CubeSigner. 
   1. CubeSigner ensures the transaction is not suspicious and enforces security policies before signing the transaction, including requiring: multiple Consortium members to approve the transaction; the timelock to expire; and, the withdrawal amount to be within the daily/weekly limit.

### Bridging LBTC

Lombard Protocol's core bridging solution is powered by [Chainlink CCIP](https://ccip.chain.link/), with additional verification by the Security Consortium:

1. The user initiates the bridge transaction on the source chain, paying all network fees upfront.
2. The Trustless Relayer observes the bridge transaction and requests the Consortium to verify it.
3. After verification, Chainlink retrieves the authorization signatures from the Consortium, and can then complete the bridge transaction on the destination chain (where the signatures are validated on the LBTC contract). 

### Staking Bitcoin

Every day, Lombard Protocol runs an asynchronous routine based on the amount of newly minted LBTC and LBTC redemptions, and then stakes and/or unstakes into Babylon accordingly:

1. If there is an increase in LBTC supply, additional Bitcoin will be staked into Babylon.
2. If there is a decrease in LBTC supply, Bitcoin will be unstaked from Babylon to fulfil redemptions within the target timeframe (7-9 days).

For more information, see [Babylon Staking](https://docs.lombard.finance/technical-documentation/protocol-architecture/babylon-staking).

### Details

# Lombard Ledger (Consortium)

Lombard Protocol is anchored by its Security Consortium, comprised of members who validate and sign critical operations. The Security Consortium’s primary activity is to validate Lombard Ledger, a Cosmos app-chain operating via Proof-of-Authority. The Security Consortium is unique in the blockchain space, and ensures every transaction on the Lombard Protocol is validated transparently by multiple independent parties.

Lombard Ledger provides a robust governance for the Lombard Protocol, enabling clear on-chain verifiable records of all operations and Security Consortium member activity. Lombard Ledger also acts as a platform for the collection & distribution of BSN rewards.

### Security Consortium in Lombard's Architecture

The Security Consortium is a decentralized state machine deployed on a trusted network of nodes that uses CometBFT to reach consensus. The Consortium performs the following actions to handle these processes:

1. **Create a New Deposit Address**:
   - **CubeSigner-Managed BTC Address**: When a staker requests to make a deposit, the Consortium creates a new BTC key—and address—managed by CubeSigner in secure hardware.
2. **Verify Deposits and Produce Signed Data**:
   1. **Check Deposit Transaction Existence**: Confirm that the deposit transaction exists on the Bitcoin blockchain.
   2. **Confirm Transaction**: Ensure that the transaction has been confirmed with the required number of confirmations.
   3. **Validate BTC Amount**: Verify that the transaction includes the BTC amount.
   4. **Point to Deposit Address**: Ensure that the transaction points to the correct deposit address.
   5. **Produce Signed Data**: Once the deposit is verified, generate the signed data that points to the selected blockchain where the user will claim the LBTC.
3. **Stake and Unstake BTC**:
   - **Select Providers**: The Consortium selects appropriate finality providers for staking.
   - **Stake BTC**: Stake BTC to the finality providers.
   - **Unstake BTC**: Unstake BTC from the finality providers.
4. **Mint and Burn LBTC:**
   - **Select Deposit Address:** User provides address to mint LBTC on for corresponding amount of staked BTC.
   - **Mint LBTC:** Consortium's BTC nodes verify that the staking transaction exists, and has received 6 confirmations, after which, provides a signature enabling the minting of LBTC.
   - **Burn LBTC:**  User calls `redeem` on the LBTC smart contract, specifying the BTC redemption address & the amount of LBTC to redeem. The corresponding LBTC is burned, and the Consortium provides signatures for pay out from CubeSigner.
5. **Pay Out Unstaked BTC**:
   - **Pay out Process**: Once BTC is unstaked from Babylon, the Consortium handles the payout of the unstaked BTC back to the user.

### Requirements to be a Consortium Member

 Currently, becoming a Consortium member entails the following steps:

1. **Infrastructure Rollout:** The new Consortium member deploys their required infrastructure (Lombard Ledger node, CubeSigner, Bitcoin and destination chain nodes).
2. **New Member Review Process:** The new member exchanges their public keys and organizational details with existing Consortium members. The existing Consortium members review the request to add a new Consortium member (including independent KYB checks).
3. **New Member Joins Network:** The existing Consortium members vote to add the new Consortium member to the Proof-of-Authority network.
4. **Smart Contracts Update:** The Lombard Protocol multisig wallet updates the Consortium Smart Contracts to include the new members' public address for signature verification.

# CubeSigner: Key Management

## Hardware-Backed, Non-Custodial Key Management

CubeSigner is a hardware-backed, non-custodial key management platform built by [Cubist](https://cubist.dev/) for programmatically managing cryptographic keys. CubeSigner addresses the security vs availability, tradeoff LSTs have traditionally struggled with by safeguarding keys in secure hardware and restricting how these keys can be used with policies. CubeSigner is designed to:

- **Protect against key theft**. Keys stay in secure hardware from generation to signing. Since this hardware—in particular, [HSM](https://aws.amazon.com/kms/)-sealed [Nitro enclaves](https://aws.amazon.com/ec2/nitro/nitro-enclaves/)—is *designed* to prevent key extraction, this means that no one—not even Cubist nor Lombard!—can see user keys, let alone steal them.
- **Mitigate breaches, hacks, and insider threats**. To sign transactions, Lombard uses CubeSigner signing *sessions*. These sessions have fine-grained scopes (i.e., they restrict who can sign, which messages, and with which keys), short-lived, and instantly revocable—this lets us ensure each session is least privileged and, even in the case of a breach, useless to an attacker.
- **Protect against key misuse**. Keys are further protected with custom per-key policies (e.g., "require approval from ⅔ of Consortium members before signing large transactions"). CubeSigner has first-class support for Lombard- and Babylon-specific policies and workflows—even [anti-slashers for Babylon](https://cubist.dev/blog/cubist-babylon-partner-on-anti-slashing-for-bitcoin-stakers) that ensure that validators using CubeSigner can't sign slashable messages (e.g., because of [operational mistakes or validator client bugs](https://cubist.dev/blog/your-validator-can-get-slashed-even-if-you-do-everything-by-the-book)).

## CubeSigner in Lombard's Architecture

Lombard uses CubeSigner to generate Bitcoin keys (and their addresses) and restrict how (and when) these keys can be used with policies. This coupling of Bitcoin keys with policies is what Cubist calls *hardware-enshrined, off-chain smart contracts.* Much like a smart contract on a chain like Ethereum, the hardware-enshrined contract consists of a signing key (which can receive funds) and custom logic—the policy—which controls how those funds are used (beyond what we can enforce with Bitcoin scripts). Lombard implements different kinds of policies, including:

- **Access Control**: Who can create and use keys, and under what conditions.

- **Usage Limits**: How many transactions and what types of transactions (including their value, recipient, and kind of transactions) can be signed. For example, user keys can only sign Babylon transactions—*not* arbitrary Bitcoin transactions. And, even then, the kind of Babylon transactions are restricted. Similar to LST smart contracts, for example, we ensure that deposit transactions use trusted stakers and finality providers, and that the withdrawal address is the Lombard pool address.

- **Multi-party Authorization (MPA)**: MPA policies require multiple users and, typically, multiple factors (e.g., YubiKeys) to sign-off on different operations (e.g., signing transactions or updating policies). This enhances security by, for example, ensuring that no single party can unilaterally authorize a transaction, making the entire process more robust, reliable, and decentralized.

- **Timelocks**: Keys and policies have timers that prevent even authorized parties from using them. This enhances security by ensuring that a key is timelocked and cannot be used (e.g., for a day) even by authorized (but potentially compromised) parties. We similarly use timelocks to safeguard policy modifications.

- # Bascule Drawbridge

  The Bascule Drawbridge provides an extra layer of security by cross-checking all actions by the Security Consortium before they can be executed. This third-party view of the world is built and controlled by Cubist, to prevent cross-chain bridge hacks in real-time.

  The Bascule Drawbridge is a state oracle running its own smart contract. It is unique to Lombard's multi-layered security approach. The drawbridge, operated by Cubist, attests the truth from the Bitcoin network on destination chains independently of the Consortium. This adds additional security to LBTC by providing a secondary and independent attestation on the state of the Bitcoin network. Minting of LBTC, in normal operating conditions, requires a valid signature from both the Consortium and the Bascule Drawbridge. The Reverse Bascule Drawbridge is an off-chain Bascule contract, used for verifying BTC withdrawals, where the on-chain state of LBTC is checked before authorization within CubeSigner. 

  ### Overview of Bascule Drawbridge

  ![img](https://docs.lombard.finance/~gitbook/image?url=https%3A%2F%2F2727780006-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FshysQ5d1rHU8C0eDQoLF%252Fuploads%252FYclhVfRyeifEXHZExGiQ%252Fimage.png%3Falt%3Dmedia%26token%3D6b83a44b-9302-466e-9d8e-6df207e75df5&width=768&dpr=4&quality=100&sign=20cb68c4&sv=2)

  1. A Bitcoin deposit is detected on the Bitcoin network, to a deterministic user deposit address owned and controlled by Lombard Protocol.
  2. Cubist wait for 6 block confirmations for security, before writing this information to the Bascule smart contract on a supported blockchain.
  3. When attempting to mint on the LBTC contract, both the Bascule attestation and the Security Consortium majority signatures must be provided.

  ### Overview of Reverse Bascule Drawbridge

  ![img](https://docs.lombard.finance/~gitbook/image?url=https%3A%2F%2F2727780006-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FshysQ5d1rHU8C0eDQoLF%252Fuploads%252Fz5Zlx6Bksu8786Kvk9w9%252Fimage.png%3Falt%3Dmedia%26token%3D9d3a081f-b9a3-4774-820e-26d76c1f4863&width=768&dpr=4&quality=100&sign=c7db73f4&sv=2)

  1. User calls redeem function on the LBTC smart contract on any supported blockchain. The corresponding LBTC is burned.
  2. Cubist listen to the redeem events emitted from the LBTC smart contract, and after a set number of block confirmations for security, will write this state into CubeSigner.
  3. CubeSigner checks for receipt of redeem attestation after the Security Consortium have initiated a Bitcoin withdrawal process.

  For more information on the Bascule Drawbridge, check out [this blog](https://cubist.dev/blog/introducing-the-bascule-drawbridge-for-bitcoin-bridge-security).

# LBTC Design

LBTC is deployed as a standard token on supported blockchains (i.e. ERC-20 on Ethereum, BEP-20 on BSC, etc.) with a minimal level of customization.

## On EVM chains

### Interfaces

LBTC uses standard OpenZeppelin implementations for:

- **ERC-20:** token standard widely adopted across EVM networks.
- **ERC-20 Permit:** enables off-chain signed messages to authorize spending (gasless transactions). Necessary for many DeFi protocols, e.g. DeXs
- **Two-step Upgradable:** allows LBTC to be upgraded following best-practices (two-step transactions with timelock), following a standard proxy and implementation pattern.
- **ERC-20 Pausable:** used for automated incident response to pause all critical functions.

### Functionality

- **Minting:** Mints new LBTC into circulation after authorization from both the Security Consortium and Bascule.
  - Transactions can be minted individually or in batches.
  - Minting can be performed with an optional fee charged in LBTC (used to cover network gas costs, e.g. for auto-mint).
- **Redemptions:** Burns LBTC with a request to withdraw Bitcoin to a provided bitcoin address.
- **Chainlink CCIP:** Used for bridging between [Supported Blockchains](https://docs.lombard.finance/lbtc-liquid-bitcoin/supported-blockchains). Minting allowed after authorization from both the Security Consortium and Chainlink. to mint.
- **Consortium**: Multi-sig contract to check all authorizations, must be signed by ⅔ of members

### Roles

- **Minters**: used for adapters with delegated minting rights (i.e. CCIP).
- **Claimers**: restricted set to call the minting with fee functions, to prevent frontrunning attacks (inconvenience).
- **Operator**: change the maximum authorized mint fee, based on network conditions and exchange rate.
- **Pauser**: to (un)pause critical security operations.
- **Owner:** change role membership and contract configuration**.**

# Babylon Staking

An outline of the Babylon Bitcoin Staking Protocol

Babylon is the first to build a permissionless non-custodial Bitcoin staking protocol. The Babylon Bitcoin staking protocol is a cross-chain staking protocol that uses BTC to secure PoS networks. Networks secured by Bitcoin are called BSNs, or Bitcoin Secured Networks. The Lombard Protocol is a liquid staking protocol built on top of Babylon. Lombard stakes users BTC into Babylon, and issues a derivative token called LBTC (Liquid Bitcoin). Staking BTC directly through Babylon leaves funds illiquid. Staking BTC through Lombard leaves funds liquid, enabling LBTC to be freely moved and entered into further DeFi positions to accrue additional yields, while still maintaining all the benefits of BTC staked directly into Babylon. For more information on the different types of BTC derivatives, check out [this blog](https://x.com/Lombard_Finance/status/1852313319442452895). When staking BTC through Babylon or Lombard, the staked BTC is delegated to a Finality Provider. A finality provider is a type of finality gadget used in Nakamoto inspired blockchains: providing finality to transactions on the blockchain after they have been decidedly verified, and thus ensures robust security for the blockchain network.  This Finality Provider acts as the validation layer for any Bitcoin Secured Network (BSN). Presently, the Babylon Chain is the only BSN, but more BSNs will be available soon. Rewards are paid to users for securing a BSN, and a commission on the reward is charged by the Finality Provider. 

In the Babylon Bitcoin Staking protocol, only the Babylon Chain posts data to the Bitcoin network. All other BSNs will post their data to the Babylon Chain — acting as an aggregation layer — which will be, in turn, batched and posted to the Bitcoin network. This timestamping of BSN data to the secure Bitcoin network is, in part, what makes Babylon's staking protocol so safe.

## Overview of how Lombard stakes BTC into Babylon

1. **Babylon's Mechanism for Finality Providers**:
   - **Registration**: Finality Providers register themselves on Babylon's platform. Get KYB approved.
   - **Selection of Finality Gadgets**: Finality Providers select which Finality Gadgets (IBC connected CosmWasm contracts and CosmosSDK modules) they want to maintain. By doing so, they earn rewards for their maintenance efforts. The rewards are shared with BTC stakers.
2. **Staking BTC to Lombard's Finality Providers**:
   - **Consortium Initiation**: The Security Consortium initiates the process by staking BTC to Lombard's Finality Providers.
   - **Creation of Staking UTXO**:
     - **Self-Custodian Vault**: The sent BTC amount is locked in a self-custodian vault, creating a special staking UTXO (Unspent Transaction Output) with two spending conditions:
       - **Timelock**: Specifies a period after which the Consortium can use their secret key to withdraw the staked BTC.
       - **EOTS (Extractable One-Time Signature)**: Allows the slashable portion (pre-defined) of the UTXO to be burned through a special EOTS. 
3. **Signing with CubeSigner**: The UTXO is then signed using CubeSigner. This ensures that the UTXO is securely locked and can only be spent under the specified conditions (Timelock and EOTS).
4. **Broadcasting to Bitcoin node**: After signing, the transaction is broadcasted to a Bitcoin node, eventually making it part of the Bitcoin blockchain. This step finalizes the staking process.
5. **Finality Round**: An additional signing round takes place after the base consensus protocol:
   - **Finalization Condition**: A block is considered finalized only if it receives EOTS signatures from over 2/3 of the Bitcoin stake.
   - **Consensus and Safety**:
     - All safety violations of the consensus are reduced to double signing in this round.
     - If there is a safety violation (i.e., more than 1/3 of the Bitcoin stake signs two blocks at the same height using EOTS), the secret keys of those stakers can be extracted.
   - **Slashing Mechanism**: The EOTS signature scheme (implemented by Schnorr signatures) is natively supported by Bitcoin, and therefore the extracted secret keys can be used to slash the staked bitcoin of those who double-signed, ensuring network integrity.

For more information a more comprehensive overview of the Babylon Staking Protocol, check out [this blog](https://x.com/Lombard_Finance/status/1864829856069959946).

# PMM Module

On specific blockchains, Lombard Protocol deploys a Private Market Maker (PMM) module smart contract to improve the user experience for acquiring LBTC holders from other popular BTC derived assets.

The PMM smart contract has defined risk parameters to allow for temporary & limited exposure to other BTC-assets, as the super-majority of LBTC is backed by only native BTC. 

All deployed PMM smart contracts are [listed here.](https://docs.lombard.finance/technical-documentation/smart-contracts) 

The smart contract has an optional fee, set based depending on the asset being swapped to LBTC.

Note: The PMM smart contract is operated as a convenience function aimed at onboarding retail users. Any financial market operations (i.e. arbitrage) utilising these contracts is discouraged. Additional security measures will be introduced to restrict access if needed. 

### Example:

The PMM smart contract deployed on BNB Smart Chain to serve BTCB to LBTC onboarding has the following notable functions:

- `remainingStake` is the amount of LBTC available to be minted before the PMM is at capacity and no more BTCB can be swapped to LBTC.
- `relativeFee` is the percentage of LBTC to be deducted per swap, to cover treasury operational costs to provide this service.
- `swapBTCBToLBTC(uint256 amount)` will execute an atomic swap for the amount of BTCB specified. Note: the PMM smart contract must be authorized to debit the BTCB amount from the user.

Lombard Protocol has defined risk parameters to limit maximum exposure to BTCB, as the majority of Lombard's reserves are held in native Bitcoin. This temporary exposure to non-native Bitcoin (i.e. BTCB), ensures the stability of LBTC.

A Private Market Maker module (PMM) is used to control the exchange of LBTC for BTCB, ensuring the corresponding underlying BTC is staked safely into Babylon.

Further info can be found on the PMM and LBTC smart contracts [here](https://docs.lombard.finance/technical-documentation/smart-contracts#base).



# Trustless Relayer

Lombard operates several non-critical APIs and services to aid in communication between blockchain networks and enhance the user experience.

These APIs have limited elevated privileges (Operator and Claimer roles, see [LBTC Design](https://docs.lombard.finance/technical-documentation/protocol-architecture/lbtc-design)), as well as permission to submit transactions on the Lombard Ledger.

1. Monitor the Bitcoin network, and report any suspected Lombard Protocol related deposits to Lombard Ledger.
2. Monitor [Supported Blockchains](https://docs.lombard.finance/lbtc-liquid-bitcoin/supported-blockchains) and report any CCIP bridge events to Lombard Ledger.
3. Monitor Lombard Ledger, and automatically mint LBTC for depositors, after authorization from Security Consortium.
   1. *Note: After Consortium authorization, a user can always mint their own LBTC, e.g. in the instance when auto-mint is disabled due to a period with high transaction costs.*
4. Record all Lombard Protocol related Bitcoin deposit addresses on an on-chain registry (on Base), used for Proof-of-Reserve attestation validation.
5. Request on Lombard Ledger to (un)stake into Babylon. *This is temporary, until automation on Lombard Ledger in a future upgrade.*
6. Monitor the performance of Lombard Ledger and the LBTC ecosystem.

# Sanctions & Risk Monitoring

Lombard utilizes TRM to fulfil our legal obligations, and also to develop our own enhanced risk framework beyond this baseline.

All wallet addresses (for BTC deposits, LBTC minting, and bridging LBTC between networks) are scanned against TRM for every request.

Overview of our risk framework:

- An address cannot be sanctioned by OFAC (Office of Foreign Assets Control).
- An address cannot be a close counterparty to a sanction address.
- An address cannot hold a share of funds obtained by illicit means.

In the event of interaction with Lombard via a sanctioned address, the following will occur:

- Lombard's Security Consortium will not sign for the minting of LBTC or the redemption of LBTC
- Lombard's Security Consortium will not stake relevant BTC into Babylon
- Depending on the severity of the risk event; Lombard Protocol is required to hold these funds and may only return with relevant authorization.