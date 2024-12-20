# NFT Standards on Ethereum: ERC-721 and Beyond

Non-Fungible Tokens (NFTs) have revolutionized the digital asset space by enabling unique, verifiable ownership of digital and real-world items on the blockchain. The Ethereum network pioneered this movement through its robust and flexible smart contract standards. While ERC-721 remains the cornerstone of NFTs, several other standards have emerged to meet various use cases and improve functionality. This article explores ERC-721, its compatible extensions, and other NFT standards on Ethereum.

[TOC]



## Final Standard

### ERC-721: The Foundation of NFTs

[https://eips.ethereum.org/EIPS/eip-721](https://eips.ethereum.org/EIPS/eip-721)

The **ERC-721** standard was the first to introduce a blueprint for non-fungible tokens on Ethereum. Published in January 2018, ERC-721 defines NFTs as unique, indivisible assets that can be transferred and tracked on the Ethereum blockchain. Each token under this standard has a distinct ID, making it different from any other token.

#### Key Features of ERC-721:

- **Uniqueness:** Each token is unique and distinguishable by its ID.
- **Transferability:** Tokens can be transferred between accounts.
- **Ownership Tracking:** Ownership history is immutably recorded on-chain.
- **Interoperability:** Compatible with wallets, marketplaces, and exchanges that support ERC-721.

#### Examples of ERC-721 Use Cases:

- **Digital Art:** Platforms like OpenSea and Rarible use ERC-721 for trading unique art pieces.
- **Collectibles:** CryptoKitties, the first major NFT project, uses this standard to create unique digital cats.
- **Gaming:** In-game items like skins, weapons, or avatars are represented as ERC-721 NFTs.

### ERC-1155: Multi-Token Standard

https://eips.ethereum.org/EIPS/eip-1155

ERC-1155, also known as the "multi-token standard," was introduced by Enjin. It enables the creation of **fungible, semi-fungible, and non-fungible tokens** within a single contract. This significantly reduces gas fees and enhances efficiency.

**Key Features:**

- **Batch Transfers:** Multiple tokens can be transferred in a single transaction.
- **Lower Costs:** Reduced gas fees by optimizing token operations.
- **Flexibility:** Supports fungible (e.g., in-game currency) and non-fungible (e.g., unique items) assets.

**Popular Use Cases:**

- Gaming assets like weapons and currencies (e.g., Enjin-powered games).
- Collectibles where multiple items share a similar design but with variations.

### ERC-2981: Royalty Standard

https://eips.ethereum.org/EIPS/eip-2981

ERC-2981 standardizes royalty payments for NFTs, allowing creators to automatically receive a percentage of sales whenever their NFT is resold on a secondary marketplace.

This standard allows contracts, such as NFTs that support [ERC-721](https://eips.ethereum.org/EIPS/eip-721) and [ERC-1155](https://eips.ethereum.org/EIPS/eip-1155) interfaces, to signal a royalty amount to be paid to the NFT creator or rights holder every time the NFT is sold or re-sold. This is intended for NFT marketplaces that want to support the ongoing funding of artists and other NFT creators. The royalty payment must be voluntary, as transfer mechanisms such as `transferFrom()` include NFT transfers between wallets, and executing them does not always imply a sale occurred. Marketplaces and individuals implement this standard by retrieving the royalty payment information with `royaltyInfo()`, which specifies how much to pay to which address for a given sale price. The exact mechanism for paying and notifying the recipient will be defined in future EIPs. This ERC should be considered a minimal, gas-efficient building block for further innovation in NFT royalty payments.

**Key Features:**

- **Creator Royalties:** Ensures creators earn passive income from secondary sales.
- **Interoperability:** Works seamlessly across marketplaces that implement the standard.

**Popular Use Cases:**

- Artists earning royalties on every resale of their digital artwork.
- Content creators ensuring perpetual revenue from their creations.

### ERC-4907: Rentable NFTs (ERC-721 ext)

https://eips.ethereum.org/EIPS/eip-4907

ERC-4907 introduces the concept of "rentable NFTs." This standard allows NFTs to be rented for a specified time period without transferring full ownership.

This standard is an extension of [EIP-721](https://eips.ethereum.org/EIPS/eip-721). It proposes an additional role (`user`) which can be granted to addresses, and a time where the role is automatically revoked (`expires`). The `user` role represents permission to “use” the NFT, but not the ability to transfer it or set users.

**Key Features:**

- **Dual Roles:** Separates ownership (owner) and usage rights (user).
- **Automated Expiration:** Usage rights automatically expire after the rental period.
- **Use Case Focus:** Perfect for gaming, metaverse items, and digital real estate rentals.

**Popular Use Cases:**

- Renting in-game assets (e.g., rare weapons or avatars).
- Leasing virtual land in the metaverse for a specific time frame.



## Draft ERCs

While ERC-721 paved the way, other standards have emerged to address additional functionality, scalability, and versatility in NFTs. Here are the most prominent ones:

### ERC-998: Composable NFTs

ERC-998 allows NFTs to own other ERC-721 or ERC-20 tokens. This "composability" enables hierarchical ownership structures.

**Key Features:**

- **Nested Ownership:** An ERC-721 NFT can hold other NFTs or fungible tokens.
- **Asset Bundling:** Useful for grouping assets as a single entity (e.g., an NFT representing a house can include furniture NFTs).

**Popular Use Cases:**

- Bundling gaming assets (e.g., a character NFT that owns weapons, armor, and currency).
- Tokenizing complex assets like virtual real estate and properties.

Example: [A Technical Overview of zkPass — zkTLS Oracle Protocol](https://medium.com/zkpass/a-technical-overview-of-zkpass-protocol-e28303e472e9)

See also http://erc998.org

### ERC-721A: Gas-Optimized ERC-721 (ERC-721 ext)

ERC-721A is an extension of the ERC-721 standard designed for gas efficiency when minting multiple NFTs in a single transaction. It was introduced by the Azuki NFT team to solve the cost challenge for large NFT drops.

The code is available on the [Chiru Labs GitHub](https://github.com/chiru-labs/ERC721A)**Key Features:**

- **Gas Optimization:** Minting multiple NFTs incurs almost the same gas fee as minting a single NFT.
- **Backward Compatibility:** Fully compatible with ERC-721.

**Popular Use Cases:**

- NFT projects with mass minting events (e.g., profile picture (PFP) collections like Azuki).

See also [ERC-721a](https://www.erc721a.org)

### ERC-6551: Non-fungible Token Bound Accounts

NFTs represented as  [ERC-721](https://eips.ethereum.org/EIPS/eip-721) cannot act as agents or associate with other on-chain assets. This limitation makes it difficult to represent many real-world non-fungible assets as NFTs. For example:

- A character in a role-playing game that accumulates assets and abilities over time based on actions they have taken
- An automobile composed of many fungible and non-fungible components
- An investment portfolio composed of multiple fungible assets

This standard aims to give every NFT the same rights as an Ethereum user. This includes the ability to self-custody assets, execute arbitrary operations, control multiple independent accounts, and use accounts across multiple chains. By doing so, this proposal allows complex real-world assets to be represented as NFTs using a common pattern that mirrors Etherem’s existing ownership model.

This is accomplished by defining a singleton registry which assigns unique, deterministic smart contract account addresses to all existing and future NFTs. Each account is permanently bound to a single NFT, with control of the account granted to the holder of that NFT.

#### Use

The Virtual Protocol uses this ERC to represent each VIRTUAL agent as a unique wallet address. This dual functionality underscores the fusion of identity and transactional capability in the Virtual ecosystem.

Reference: [eips.ethereum.org/EIPS/eip-6551](https://eips.ethereum.org/EIPS/eip-6551)

## Summary Table: Ethereum NFT Standards

| **Standard** | **Description**                         | **Primary Use Cases**                         | **Key Feature**                       | Use                                                          |
| ------------ | --------------------------------------- | --------------------------------------------- | ------------------------------------- | ------------------------------------------------------------ |
| **ERC-721**  | The original NFT standard.              | Digital art, gaming, collectibles.            | Uniqueness and ownership tracking.    |                                                              |
| **ERC-1155** | Multi-token standard (fungible + NFTs). | Gaming assets, batch transfers.               | Batch operations and lower gas costs. |                                                              |
| **ERC-998**  | Composable NFTs with nested ownership.  | Asset bundling, complex ownership structures. | NFTs owning other tokens.             | [ZKPass](https://medium.com/zkpass/a-technical-overview-of-zkpass-protocol-e28303e472e9) |
| **ERC-721A** | Gas-optimized ERC-721 extension.        | High-volume NFT minting (PFP collections).    | Efficient batch minting.              | Azuki                                                        |
| **ERC-4907** | Rentable NFTs with usage rights.        | Renting digital real estate, gaming assets.   | Temporary usage with expiration.      |                                                              |
| **ERC-2981** | Standardized royalty payments for NFTs. | Secondary sales royalties for creators.       | Automatic royalty payouts.            |                                                              |
| ERC-6551     | Token-bound accounts for NFTs.          | Gaming assets, metaverse, identity solutions. | NFTs acting as wallets.               | Virtual Protocol                                             |

## Final Thoughts

Ethereum's ecosystem continues to evolve with NFT standards that address diverse needs,



 from reducing gas fees and supporting composability to enabling rentals and ensuring royalties for creators. 

While ERC-721 remains the bedrock of NFTs, standards like ERC-1155, ERC-4907, and ERC-2981 showcase Ethereum's adaptability to emerging use cases. 

By leveraging these standards, developers and creators can build more efficient, versatile, and user-friendly NFT applications.

