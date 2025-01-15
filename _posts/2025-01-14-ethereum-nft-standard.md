---
layout: post
title: NFT Standards on Ethereum - ERC-721 and Beyond
date:   2025-01-14
lang: en
locale: en-GB
categories: cryptography blockchain zkp
tags: ERC-721 NFT ERC-1155 royalty ERC-2981 ERC-4907 ERC-998 ERC-6551
description: Non-Fungible Tokens (NFTs) enable unique, verifiable ownership of digital and real-world items on the blockchain. While ERC-721 remains the main standard to represent NFTs on Ethereum and EVM blockchains, several other standards (ERC-1155, ERC-2981, ERC-4907,...) have emerged to meet various use cases and improve functionality. 
image: 
isMath: false
---

Non-Fungible Tokens (NFTs) enable unique, verifiable ownership of digital and real-world items on the blockchain. The Ethereum network pioneered this movement through its robust and flexible smart contract standards. While ERC-721 remains the main standard to represent NFTs, several other standards (ERC-1155, ERC-2981, ERC-4907,...) have emerged to meet various use cases and improve functionality. 

This article explores ERC-721, its compatible extensions, and other NFT standards on Ethereum.

[TOC]

## Final Standard

### ERC-721: The Foundation of NFTs

[EIP Reference](https://eips.ethereum.org/EIPS/eip-721)

The **ERC-721** standard was the first to introduce a blueprint for non-fungible tokens on Ethereum. Published in January 2018, ERC-721 defines NFTs as unique, indivisible assets that can be transferred and tracked on the Ethereum blockchain. Each token under this standard has a distinct ID, making it different from any other token.

#### Key Features of ERC-721:

- **Uniqueness:** Each token is unique and distinguishable by its ID.
- **Transferability:** Tokens can be transferred between accounts.
- **Ownership Tracking:** Ownership history is immutably recorded on-chain.
- **Interoperability:** Compatible with wallets, marketplaces, and exchanges that support ERC-721.

#### Main functions

```solidity
/// @notice Count all NFTs assigned to an owner
function balanceOf(address _owner) external view returns (uint256);

/// @notice Find the owner of an NFT
 function ownerOf(uint256 _tokenId) external view returns (address);

 /// @notice Transfers the ownership of an NFT from one address to another address
 function safeTransferFrom(address _from, address _to, uint256 _tokenId, bytes data) external payable;

 /// @notice Transfers the ownership of an NFT from one address to another address
 function safeTransferFrom(address _from, address _to, uint256 _tokenId) external payable;

 /// @notice Transfer ownership of an NFT
 function transferFrom(address _from, address _to, uint256 _tokenId) external payable;

 /// @notice Change or reaffirm the approved address for an NFT
 function approve(address _approved, uint256 _tokenId) external payable;

 /// @notice Enable or disable approval for a third party ("operator") to manage
 ///  all of `msg.sender`'s assets
 function setApprovalForAll(address _operator, bool _approved) external;

 /// @notice Get the approved address for a single NFT
  function getApproved(uint256 _tokenId) external view returns (address);

 /// @notice Query if an address is an authorized operator for another address
 function isApprovedForAll(address _owner, address _operator) external view returns (bool);
}
```

#### Examples of ERC-721 Use Cases:

- **Digital Art:** Platforms like OpenSea and Rarible use ERC-721 for trading unique art pieces.
- **Collectibles:** CryptoKitties, the first major NFT project, uses this standard to create unique digital cats.
- **Gaming:** In-game items like skins, weapons, or avatars can be represented as ERC-721 NFTs.



### ERC-1155: Multi-Token Standard

[EIP Reference](https://eips.ethereum.org/EIPS/eip-1155)

ERC-1155, also known as the "multi-token standard," was introduced by Enjin. It enables the creation of **fungible, semi-fungible, and non-fungible tokens** within a single contract. This significantly reduces gas fees and enhances efficiency.

**Key Features:**

- **Batch Transfers:** Multiple tokens can be transferred in a single transaction.
- **Lower Costs:** Reduced gas fees by optimizing token operations.
- **Flexibility:** Supports fungible (e.g., in-game currency) and non-fungible (e.g., unique items) assets.

#### Main functions

```solidity
///@notice Transfers `_value` amount of an `_id` from the `_from` address to the `_to` address specified (with safety call).
 function safeTransferFrom(address _from, address _to, uint256 _id, uint256 _value, bytes calldata _data) external;
 
/// @notice Transfers `_values` amount(s) of `_ids` from the `_from` address to the `_to` address specified (with safety call).      
 function safeBatchTransferFrom(address _from, address _to, uint256[] calldata _ids, uint256[] calldata _values, bytes calldata _data) external;

 /// @notice Get the balance of an account's tokens.
 function balanceOf(address _owner, uint256 _id) external view returns (uint256);

/// @notice Get the balance of multiple account/token pairs
function balanceOfBatch(address[] calldata _owners, uint256[] calldata _ids) external view returns (uint256[] memory);

/// @notice Enable or disable approval for a third party ("operator") to manage all of the caller's tokens.
function setApprovalForAll(address _operator, bool _approved) external;

/// @notice Queries the approval status of an operator for a given owner.
function isApprovedForAll(address _owner, address _operator) external view returns (bool);
```

**Popular Use Cases:**

- Gaming assets like weapons and currencies (e.g., Enjin-powered games).
- Collectibles where multiple items share a similar design but with variations.

### ERC-2981: Royalty Standard

[EIP Reference](https://eips.ethereum.org/EIPS/eip-2981)

ERC-2981 standardizes royalty payments for NFTs, allowing creators to automatically receive a percentage of sales whenever their NFT is resold on a secondary marketplace.

This standard allows contracts, such as NFTs that support [ERC-721](https://eips.ethereum.org/EIPS/eip-721) and [ERC-1155](https://eips.ethereum.org/EIPS/eip-1155) interfaces, to signal a royalty amount to be paid to the NFT creator or rights holder every time the NFT is sold or re-sold. This is intended for NFT marketplaces that want to support the ongoing funding of artists and other NFT creators. The royalty payment must be voluntary, as transfer mechanisms such as `transferFrom()` include NFT transfers between wallets, and executing them does not always imply a sale occurred. Marketplaces and individuals implement this standard by retrieving the royalty payment information with `royaltyInfo()`, which specifies how much to pay to which address for a given sale price. The exact mechanism for paying and notifying the recipient will be defined in future EIPs. This ERC should be considered a minimal, gas-efficient building block for further innovation in NFT royalty payments.

**Key Features:**

- **Creator Royalties:** Ensures creators earn passive income from secondary sales.
- **Interoperability:** Works seamlessly across marketplaces that implement the standard.



**Popular Use Cases:**

- Artists earning royalties on every resale of their digital artwork.
- Content creators ensuring perpetual revenue from their creations.

#### Main functions

```solidity
/// @notice Called with the sale price to determine how much royalty is owed and to whom.
function royaltyInfo(
        uint256 _tokenId,
        uint256 _salePrice
    ) external view returns (
        address receiver,
        uint256 royaltyAmount
    );
```



### ERC-4907: Rentable NFTs (ERC-721 ext)

[EIP Reference](https://eips.ethereum.org/EIPS/eip-4907)

ERC-4907 introduces the concept of "rentable NFTs." This standard allows NFTs to be rented for a specified time period without transferring full ownership.

This standard is an extension of [EIP-721](https://eips.ethereum.org/EIPS/eip-721). It proposes an additional role (`user`) which can be granted to addresses, and a time where the role is automatically revoked (`expires`). The `user` role represents permission to “use” the NFT, but not the ability to transfer it or set users.

**Key Features:**

- **Dual Roles:** Separates ownership (owner) and usage rights (user).
- **Automated Expiration:** Usage rights automatically expire after the rental period.
- **Use Case Focus:** Perfect for gaming, metaverse items, and digital real estate rentals.

**Popular Use Cases:**

- Renting in-game assets (e.g., rare weapons or avatars).
- Leasing virtual land in the metaverse for a specific time frame.

#### Main functions

```solidity
/// @notice set the user and expires of an NFT
function setUser(uint256 tokenId, address user, uint64 expires) external;

/// @notice Get the user address of an NFT
function userOf(uint256 tokenId) external view returns(address);

/// @notice Get the user expires of an NFT
function userExpires(uint256 tokenId) external view returns(uint256);
```



## Draft ERCs

While ERC-721 paved the way, other standards have emerged to address additional functionality, scalability, and versatility in NFTs. Here are the most prominent ones:

### ERC-998: Composable NFTs

[EIP reference](https://eips.ethereum.org/EIPS/eip-998)

ERC-998 allows NFTs to own other ERC-721 or ERC-20 tokens. This "composability" enables hierarchical ownership structures.

**Key Features:**

- **Nested Ownership:** An ERC-721 NFT can hold other NFTs or fungible tokens.
- **Asset Bundling:** Useful for grouping assets as a single entity (e.g., an NFT representing a house can include furniture NFTs).

**Popular Use Cases:**

- Bundling gaming assets (e.g., a character NFT that owns weapons, armor, and currency).
- Tokenizing complex assets like virtual real estate and properties.

Example: [A Technical Overview of zkPass — zkTLS Oracle Protocol](https://medium.com/zkpass/a-technical-overview-of-zkpass-protocol-e28303e472e9)

See also http://erc998.org

#### Main functions

```solidity
 /// @notice Get the root owner of tokenId.
  function rootOwnerOf(uint256 _tokenId) public view returns (bytes32 rootOwner);
  
 /// @notice Get the root owner of a child token.
 function rootOwnerOfChild(
    address _childContract, 
    uint256 _childTokenId
  ) 
    public 
    view
    returns (bytes32 rootOwner);
  
 /// @notice Get the parent tokenId of a child token.
  function ownerOfChild(
    address _childContract, 
    uint256 _childTokenId
  ) 
    external 
    view 
    returns (
      bytes32 parentTokenOwner, 
      uint256 parentTokenId
    );
  
 /// @notice A token receives a child token receiving parent tokenId.  
  function onERC721Received(
    address _operator, 
    address _from, 
    uint256 _childTokenId, 
    bytes _data
  ) 
    external 
    returns(bytes4);
    
 /// @notice Transfer child token from top-down composable to address.
function transferChild(
    uint256 _fromTokenId,
    address _to, 
    address _childContract, 
    uint256 _childTokenId
  ) 
    external;
  
 /// @notice Transfer child token from top-down composable to address.
  function safeTransferChild(
    uint256 _fromTokenId,
    address _to, 
    address _childContract, 
    uint256 _childTokenId
  ) 
    external;
  
/// @notice Transfer child token from top-down composable to address.
function safeTransferChild(
    uint256 _fromTokenId,
    address _to, 
    address _childContract, 
    uint256 _childTokenId, 
    bytes _data
  ) 
    external;
  
/// @notice Transfer bottom-up composable child token from top-down composable to other ERC-721 token.
  function transferChildToParent(
    uint256 _fromTokenId, 
    address _toContract, 
    uint256 _toTokenId, 
    address _childContract, 
    uint256 _childTokenId, 
    bytes _data
  ) 
    external;
  
/// @notice Get a child token from an ERC-721 contract.
function getChild(
    address _from, 
    uint256 _tokenId, 
    address _childContract, 
    uint256 _childTokenId
  ) 
    external;
}
```



### ERC-721A: Gas-Optimized ERC-721 (ERC-721 ext)

ERC-721A is an extension of the ERC-721 standard designed for gas efficiency when minting multiple NFTs in a single transaction. It was introduced by the Azuki NFT team to solve the cost challenge for large NFT drops.

The code is available on the [Chiru Labs GitHub](https://github.com/chiru-labs/ERC721A)**Key Features:**

- **Gas Optimization:** Minting multiple NFTs incurs almost the same gas fee as minting a single NFT.
- **Backward Compatibility:** Fully compatible with ERC-721.

**Popular Use Cases:**

- NFT projects with mass minting events (e.g., profile picture (PFP) collections like Azuki).

See also [ERC-721a](https://www.erc721a.org)

### ERC-6551: Non-fungible Token Bound Accounts

[EIP reference](https://eips.ethereum.org/EIPS/eip-6551)

NFTs represented as [ERC-721](https://eips.ethereum.org/EIPS/eip-721) cannot act as agents or associate with other on-chain assets. This limitation makes it difficult to represent many real-world non-fungible assets as NFTs. For example:

- A character in a role-playing game that accumulates assets and abilities over time based on actions they have taken
- An automobile composed of many fungible and non-fungible components
- An investment portfolio composed of multiple fungible assets

This standard aims to give every NFT the same rights as an Ethereum user. This includes the ability to self-custody assets, execute arbitrary operations, control multiple independent accounts, and use accounts across multiple chains. By doing so, this proposal allows complex real-world assets to be represented as NFTs using a common pattern that mirrors Etherem’s existing ownership model.

This is accomplished by defining a singleton registry which assigns unique, deterministic smart contract account addresses to all existing and future NFTs. Each account is permanently bound to a single NFT, with control of the account granted to the holder of that NFT.

#### Use

The Virtual Protocol uses this ERC to represent each VIRTUAL agent as a unique wallet address. 

See [Virtual Protocol Whitepaper](https://whitepaper.virtuals.io/the-protocol/co-contribution-and-provenance/immutable-contribution-vault)

#### Main functions

##### Registry

The registry MUST implement the following interface:

```solidity
// @notice Creates a token bound account for a non-fungible token.
  function createAccount(
        address implementation,
        bytes32 salt,
        uint256 chainId,
        address tokenContract,
        uint256 tokenId
    ) external returns (address account);

// @dev Returns the computed token bound account address for a non-fungible token.
    function account(
        address implementation,
        bytes32 salt,
        uint256 chainId,
        address tokenContract,
        uint256 tokenId
    ) external view returns (address account);
}
```

#####  Account Interface

All token bound account implementations MUST implement the interface:

```solidity
/// @dev the ERC-165 identifier for this interface is `0x6faff5f1`
interface IERC6551Account {

// @dev Allows the account to receive Ether.
receive() external payable;

// @dev Returns the identifier of the non-fungible token which owns the account.
function token()
        external
        view
        returns (uint256 chainId, address tokenContract, uint256 tokenId);

// @dev Returns a value that SHOULD be modified each time the account changes
function state() external view returns (uint256);

/**
* @dev Returns a magic value indicating whether a given signer is authorized to act on behalf
* of the account.
*
* MUST return the bytes4 magic value 0x523e3260 if the given signer is valid.
*/
 function isValidSigner(address signer, bytes calldata context)
        external
        view
        returns (bytes4 magicValue);
}
```

##### Execution interface

All token bound accounts MUST implement an execution interface which allows valid signers to execute arbitrary operations on behalf of the account. Support for an execution interface MUST be signaled by the account using ERC-165 interface detection.

Accounts implementing this interface MUST accept the following operation parameter values:

- 0 = CALL
- 1 = DELEGATECALL
- 2 = CREATE
- 3 = CREAT2

```solidity
// @dev Executes a low-level operation if the caller is a valid signer on the account.
function execute(address to, uint256 value, bytes calldata data, uint8 operation)
        external
        payable
        returns (bytes memory);
```



## Summary Table: Ethereum NFT Standards

| **Standard**                                            | **Description**                         | **Primary Use Cases**                         | **Key Feature**                       | Protocol Use                                                 |
| ------------------------------------------------------- | --------------------------------------- | --------------------------------------------- | ------------------------------------- | ------------------------------------------------------------ |
| [**ERC-721**](https://eips.ethereum.org/EIPS/eip-721)   | The original NFT standard.              | Digital art, gaming, collectibles.            | Uniqueness and ownership tracking.    | [OpenSea](https://docs.opensea.io/docs/metadata-standards), [LooksRare](https://docs.looksrare.org/about/welcome-to-looksrare), Rarible |
| [**ERC-721A**](https://www.erc721a.org)                 | Gas-optimized ERC-721 extension.        | High-volume NFT minting (PFP collections).    | Efficient batch minting.              | [Azuki](https://www.azuki.com/en/erc721a)                    |
| [**ERC-1155**](https://eips.ethereum.org/EIPS/eip-1155) | Multi-token standard (fungible + NFTs). | Gaming assets, batch transfers.               | Batch operations and lower gas costs. | [OpenSea](https://docs.opensea.io/docs/metadata-standards)   |
| [**ERC-998**](https://eips.ethereum.org/EIPS/eip-998)   | Composable NFTs with nested ownership.  | Asset bundling, complex ownership structures. | NFTs owning other tokens.             | [ZKPass](https://medium.com/zkpass/a-technical-overview-of-zkpass-protocol-e28303e472e9) |
| [**ERC-4907**](https://eips.ethereum.org/EIPS/eip-4907) | Rentable NFTs with usage rights.        | Renting digital real estate, gaming assets.   | Temporary usage with expiration.      | [Double Protocol](https://double.one)                        |
| [**ERC-2981**](https://eips.ethereum.org/EIPS/eip-2981) | Standardized royalty payments for NFTs. | Secondary sales royalties for creators.       | Automatic royalty payouts.            | [LooksRare](https://docs.looksrare.org/developers/protocol/looksrare-v2-protocol-overview) |
| [ERC-6551](https://eips.ethereum.org/EIPS/eip-6551)     | Token-bound accounts for NFTs.          | Gaming assets, metaverse, identity solutions. | NFTs acting as wallets.               | [Virtual Protocol](https://whitepaper.virtuals.io/the-protocol/co-contribution-and-provenance/immutable-contribution-vault) |

## Final Thoughts

Ethereum's ecosystem continues to evolve with NFT standards that address diverse needs,

 from reducing gas fees and supporting composability to enabling rentals and ensuring royalties for creators. 

While ERC-721 remains the bedrock of NFTs, standards like ERC-1155, ERC-4907, and ERC-2981 showcase Ethereum's adaptability to emerging use cases. 

By leveraging these standards, developers and creators can build more efficient, versatile, and user-friendly NFT applications.

