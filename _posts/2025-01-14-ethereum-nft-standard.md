---
layout: post
title: NFT Standards on Ethereum - ERC-721 and Beyond
date:   2025-01-14
lang: en
locale: en-GB
categories: blockchain solidity ethereum
tags: ERC-721 NFT ERC-1155 royalty ERC-2981 ERC-4907 ERC-998 ERC-6551
description: Non-Fungible Tokens (NFTs) enable unique, verifiable ownership of digital and real-world items on the blockchain. While ERC-721 remains the main standard to represent NFTs on Ethereum and EVM blockchains, several other standards (ERC-1155, ERC-2981, ERC-4907,...) have emerged to meet various use cases and improve functionality. 
image: 
isMath: false
---

Non-Fungible Tokens (NFTs) enable unique, verifiable ownership of digital and real-world items on the blockchain. The Ethereum network pioneered this movement through its robust and flexible smart contract standards. 

While ERC-721 remains the main standard to represent NFTs, several other standards (ERC-1155, ERC-2981, ERC-4907,...) have emerged to meet various use cases and improve functionality. This article lists the different standards to represent NFT and their extensions on Ethereum.

[TOC]

----

## Summary: Ethereum NFT Standards

The different NFT standards extends the possibility to create NFT and use it:

- either by defining a new and separate token standard different from ERC-721: ERC-1155
- or by extending ERC-721 with new functionalities (ERC-2981, ERC-4907)
- or by proposing a new way to implement it (ERC-721A, ERC-404)

All these standard show that Ethereum is a real sandbox to build innovative applications.


Here a list of use case and their corresponding standards:

- Multi-token standard (fungible + NFTs): [ERC-1155](https://eips.ethereum.org/EIPS/eip-1155)
- Royalty payment: [ERC-2771](https://eips.ethereum.org/EIPS/eip-2771)
- Gas optimized NFTs: [ERC-721A](https://www.erc721a.org)
- Rentable NFTs: [ERC-4907](https://eips.ethereum.org/EIPS/eip-4907)
- Non-transferable NFT: [ERC-5192](https://eips.ethereum.org/EIPS/eip-5192)
- Multi-privilege Management NFT Extension: [ERC-5496](https://eips.ethereum.org/EIPS/eip-5496)
- Token-bound accounts for NFTs: [ERC-6551](https://eips.ethereum.org/EIPS/eip-6551)
- Extendable NFT metadata protocol: [ERC-3664](https://github.com/DRepublic-io/EIPs/blob/master/EIPS/eip-3664.md)
- Custom errors for commonly-used tokens: [ERC-6093](https://eips.ethereum.org/EIPS/eip-6093)

### Table

| **Standard**                                                 | Status    | ERC-721 extension (or compatible) | OpenZeppelinV5 impl                                          | [ERC-165 ID](https://eips.ethereum.org/EIPS/eip-165) | **Description**                                              | **Primary Use Cases**                                        | **Key Feature**                                              | Protocol Use                                                 |
| ------------------------------------------------------------ | --------- | --------------------------------- | ------------------------------------------------------------ | ---------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| [**ERC-721**](https://eips.ethereum.org/EIPS/eip-721)<br />(2018) | Final     | -                                 | ☑<br />[doc](https://docs.openzeppelin.com/contracts/5.x/erc721) | 0x80ac58cd                                           | The original NFT standard.                                   | Digital art, gaming, collectibles, Liquidity position (see Uniswap) | Uniqueness and ownership tracking.                           | [OpenSea](https://docs.opensea.io/docs/metadata-standards), [LooksRare](https://docs.looksrare.org/about/welcome-to-looksrare), Rarible,<br />[Uniswap v3/v4](https://docs.uniswap.org/contracts/v4/quickstart/manage-liquidity/mint-position) |
| [**ERC-721A**](https://www.erc721a.org)                      | ☒         | ☑                                 | ☒                                                            | Same as ERC-721                                      | Gas-optimized ERC-721 implementation.                        | High-volume NFT minting (PFP collections).                   | Efficient batch minting.                                     | [Azuki](https://www.azuki.com/en/erc721a)                    |
| [**ERC-1155**](https://eips.ethereum.org/EIPS/eip-1155)<br />(2018) | Final     | ☒                                 | ☑<br />[doc](https://docs.openzeppelin.com/contracts/5.x/erc1155) | 0xd9b67a26                                           | Multi-token standard (fungible + NFTs).                      | Gaming assets, batch transfers.                              | Batch operations and lower gas costs.                        | [OpenSea](https://docs.opensea.io/docs/metadata-standards)   |
| [**ERC-998**](https://eips.ethereum.org/EIPS/eip-998)<br />(2018) | Draft     | ☑                                 | ☒                                                            | 0xcde244d9                                           | Composable NFTs with nested ownership.                       | Asset bundling, complex ownership structures.                | NFTs owning other tokens.                                    | [ZKPass](https://medium.com/zkpass/a-technical-overview-of-zkpass-protocol-e28303e472e9) |
| [**ERC-4907**](https://eips.ethereum.org/EIPS/eip-4907)<br />(2022) | Final     | ☑                                 | ☒                                                            | 0xad092b5c                                           | Rentable NFTs with usage rights.                             | Renting digital real estate, gaming assets.                  | Temporary usage with expiration.                             | [Double Protocol](https://double.one)<br />(nft rental protocol) |
| [**ERC-2981**](https://eips.ethereum.org/EIPS/eip-2981)<br />(2020) | Final     | ☑<br />(also ERC-1155)            | [doc](https://docs.openzeppelin.com/contracts/5.x/api/token/erc721#ERC721Royalty) | 0x2a55205a                                           | Standardized royalty payments information for NFTs.<br />(don't force/guarantee payment for NFt creators) | Secondary sales royalties for creators.                      | Allow NFT marketplace to provide automatic royalty payouts.  | NFT markplac-Eg:[LooksRare](https://docs.looksrare.org/developers/protocol/looksrare-v2-protocol-overview) |
| [**ERC-6551**](https://eips.ethereum.org/EIPS/eip-6551)<br />(2023) | Review    | ☑                                 | ☒                                                            | 0x6faff5f1<br />(IERC6551Account)                    | Token-bound accounts for NFTs.                               | Gaming assets, metaverse, identity solutions,<br /> [automated investment portfolio](https://mundus.dev/blog/tpost/1t1euygmi1-eip-6551-overview-token-bounds-accounts) | NFTs acting as wallets.                                      | [Virtual Protocol](https://whitepaper.virtuals.io/the-protocol/co-contribution-and-provenance/immutable-contribution-vault) |
| [**ERC-5496**](https://eips.ethereum.org/EIPS/eip-5496)<br />(2022) | Last Call | ☑                                 | ☒                                                            | 0x076e1bbb                                           | Multi-privilege Management NFT Extension                     | Privileges use-case (voting rights, permission to claim airdrop, coupon discount) | Linked privilege rights to an ERC-721 token                  |                                                              |
| [**ERC-3664**](https://github.com/DRepublic-io/EIPs/blob/master/EIPS/eip-3664.md)<br />(2022) | Draft     | ☑<br />(also ERC-1155)            | ☒                                                            | yes <br />but value unknown                          | Extendable NFT metadata protocol                             | Game, metaverse                                              | Better descriptive power for attributes metadata with ERC-721 and ERC-1155 | [DRepublic Labs](https://github.com/DRepublic-io) (project abandoned) |
| [**ERC-3525**](https://eips.ethereum.org/EIPS/eip-3525)<br />(2020) | Final     | ☑                                 | ☒                                                            | 0xd5358140                                           | Define Semi-Fungible tokens                                  | Monetary gifts, Certificates of deposit (CDs) and annuity, Debt instruments, Structured products | Semi-Fungible tokens                                         | [Solv finance](https://github.com/solv-finance)              |
| [ERC-5192](https://eips.ethereum.org/EIPS/eip-5192)<br />(2022) | Final     | ☑                                 | ☒                                                            | 0xb45a3c0e                                           | Define non-transferrable, non-fungible tokens                | award, certificate of achievement                            | Non-transferable NFT                                         |                                                              |
| [ERC-4906](https://eips.ethereum.org/EIPS/eip-4906)<br />(2022) | Final     | ☑                                 | ☑<br /> [code]( https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.2.0/contracts/token/ERC721/extensions/ERC721URIStorage.sol)<br />[doc](https://docs.openzeppelin.com/contracts/5.x/api/token/erc721#ERC721URIStorage) | 0x49064906                                           | EIP-721 Metadata Update Extension                            | Allow third-party platforms  (e.g NFT marketplace) to track metadata change | Metadata tracking change                                     | -                                                            |
| [ERC-6093](https://eips.ethereum.org/EIPS/eip-6093)<br />(2023) | Last Call | ☑<br />(also ERC-1155 and ERC-20) | ☑                                                            | ☒                                                    | Custom errors for commonly-used tokens                       | Standardized errors allow users to expect more consistent error messages across applications or testing environments, | Standardized errors                                          | OpenZeppelin                                                 |


## Final Standard

### ERC-721: The Foundation of NFTs

> [EIP Reference](https://eips.ethereum.org/EIPS/eip-721)
>
> Status: final
>
> OpenZeppelin implementation: yes

The **ERC-721** standard was the first to introduce a blueprint for non-fungible tokens on Ethereum. Published in January 2018, ERC-721 defines NFTs as unique, indivisible assets that can be transferred and tracked on the Ethereum blockchain. Each token under this standard has a distinct ID, making it different from any other token.

For more details, you can read my article [ERC-721 (NFT) Overview: Implementation, Security, and Best Practices](https://rya-sge.github.io/access-denied/2025/03/03/erc721-overview/)

#### Key Features of ERC-721:

- **Uniqueness:** Each token is unique and distinguishable by its ID.
- **Transferability:** Tokens can be transferred between accounts.
- **Ownership Tracking:** Ownership history is immutably recorded on-chain.
- **Interoperability:** main interface to represent NFT, supported by many wallets, NFT marketplaces, and exchanges.
- Additional information (symbol, name, URI) can be linkted to the NFT through the optional metadata extension

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

##### Metadata extension

The **metadata extension** is OPTIONAL for ERC-721 smart contracts. This allows your smart contract to be interrogated for its name and for details about the assets which your NFTs represent.

```json
/// @title ERC-721 Non-Fungible Token Standard, optional metadata extension
/// @dev See https://eips.ethereum.org/EIPS/eip-721
///  Note: the ERC-165 identifier for this interface is 0x5b5e139f.
interface ERC721Metadata /* is ERC721 */ {
    /// @notice A descriptive name for a collection of NFTs in this contract
    function name() external view returns (string _name);

    /// @notice An abbreviated name for NFTs in this contract
    function symbol() external view returns (string _symbol);

    /// @notice A distinct Uniform Resource Identifier (URI) for a given asset.
    /// @dev Throws if `_tokenId` is not a valid NFT. URIs are defined in RFC
    ///  3986. The URI may point to a JSON file that conforms to the "ERC721
    ///  Metadata JSON Schema".
    function tokenURI(uint256 _tokenId) external view returns (string);
}
```



#### Examples of ERC-721 Use Cases:

- **Digital Art and collectibles:** 
  - Platforms like OpenSea and Rarible use ERC-721 for trading unique art piece
  - Ex: [CryptoKitties](https://www.cryptokitties.co), the first major NFT project, uses this standard to create unique digital cats.

- **Gaming:** In-game items like skins, weapons, or avatars can be represented as ERC-721 NFTs.
- **LP position**: Uniswap v3 and v4 uses ERC-721 to represent LP positions. These NFTs store all of the data for the liquidity position. See [Uniswap support - Why is liquidity position ownership represented by tokens or NFTs?](https://support.uniswap.org/hc/en-us/articles/20980786685069-Why-is-liquidity-position-ownership-represented-by-tokens-or-NFTs), [Uniswap v3 book - Overview of ERC-721](https://uniswapv3book.com/milestone_6/erc721-overview.html), [Uniswap v3 - NFT manager contract]( https://uniswapv3book.com/milestone_6/nft-manager.html)

#### Extension

These extensions add several functionalities to the standard ERC-721

##### ERC-4906: EIP-721 Metadata Update Extension

> [EIP reference](https://eips.ethereum.org/EIPS/eip-4906)
>
> Status: final
>
> OpenZeppelin implementation: yes

This standard is an extension of [EIP-721](https://eips.ethereum.org/EIPS/eip-721). It adds a `MetadataUpdate` event to EIP-721 tokens.

```solidity
/// @title EIP-721 Metadata Update Extension
interface IERC4906 is IERC165, IERC721 {
    /// @dev This event emits when the metadata of a token is changed.
    /// So that the third-party platforms such as NFT market could
    /// timely update the images and related attributes of the NFT.
    event MetadataUpdate(uint256 _tokenId);

    /// @dev This event emits when the metadata of a range of tokens is changed.
    /// So that the third-party platforms such as NFT market could
    /// timely update the images and related attributes of the NFTs.    
    event BatchMetadataUpdate(uint256 _fromTokenId, uint256 _toTokenId);
}
```

##### ERC-6093: Custom errors for commonly-used tokens

> [EIP reference](https://eips.ethereum.org/EIPS/eip-4906)
>
> Status: last call
>
> OpenZeppelin implementation: yes

This EIP defines a standard set of custom errors for commonly-used tokens, which are defined as [ERC-20](https://eips.ethereum.org/EIPS/eip-20), [ERC-721](https://eips.ethereum.org/EIPS/eip-721), and [ERC-1155](https://eips.ethereum.org/EIPS/eip-1155) tokens.

See also [OpenZeppelin - interfaces/draft-IERC6093.sol](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.1.0/contracts/interfaces/draft-IERC6093.sol)

```solidity
/**
* @dev Indicates that an address can't be an owner. For example, `address(0)` is a forbidden owner in ERC-20.
* Used in balance queries.
*/
error ERC721InvalidOwner(address owner);

/**
* @dev Indicates a `tokenId` whose `owner` is the zero address.
*/
error ERC721NonexistentToken(uint256 tokenId);

/**
* @dev Indicates an error related to the ownership over a particular token. Used in transfers.
*/
error ERC721IncorrectOwner(address sender, uint256 tokenId, address owner);

/**
* @dev Indicates a failure with the token `sender`. Used in transfers.
*/
error ERC721InvalidSender(address sender);

/**
* @dev Indicates a failure with the token `receiver`. Used in transfers.
*/
error ERC721InvalidReceiver(address receiver);

/**
* @dev Indicates a failure with the `operator`’s approval. Used in transfers.
*/
error ERC721InsufficientApproval(address operator, uint256 tokenId);

/**
* @dev Indicates a failure with the `approver` of a token to be approved. Used in approvals.
*/
error ERC721InvalidApprover(address approver);

/**
* @dev Indicates a failure with the `operator` to be approved. Used in approvals.
*/
error ERC721InvalidOperator(address operator);

```

------

### ERC-1155: Multi-Token Standard

> [EIP Reference](https://eips.ethereum.org/EIPS/eip-1155)
>
> Status: final
>
> OpenZeppelin implementation: yes

ERC-1155, also known as the "multi-token standard," was introduced by Enjin. It enables the creation of **fungible, semi-fungible, and non-fungible tokens** within a single contract. This significantly reduces gas fees and enhances efficiency.

**Key Features:**

- **Batch Transfers:** Multiple tokens can be transferred in a single transaction.
- **Lower Costs:** Reduced gas fees by optimizing token operations.
- **Flexibility:** Supports fungible (e.g., in-game currency) and non-fungible (e.g., unique items) assets.
- Note that contrary to [ERC-1400](https://github.com/ethereum/EIPs/issues/1411) and [ERC-3525](https://eips.ethereum.org/EIPS/eip-3525), you don't have a decimal field attached to a specific token. Therefore you can several amount of a specific token, represented by its tokenId, but from the outside, it will be a whole number.

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

------

### ERC-2981: Royalty Standard

> [EIP Reference](https://eips.ethereum.org/EIPS/eip-2981)
>
> Status: final
>
> OpenZeppelin implementation: yes

ERC-2981 standardizes royalty payments for NFTs, allowing creators to automatically receive a percentage of sales whenever their NFT is resold on a secondary marketplace.

This standard allows contracts, such as NFTs that support [ERC-721](https://eips.ethereum.org/EIPS/eip-721) and [ERC-1155](https://eips.ethereum.org/EIPS/eip-1155) interfaces, to signal a royalty amount to be paid to the NFT creator or rights holder every time the NFT is sold or re-sold. This is intended for NFT marketplaces that want to support the ongoing funding of artists and other NFT creators. The royalty payment must be voluntary, as transfer mechanisms such as `transferFrom()` include NFT transfers between wallets, and executing them does not always imply a sale occurred. Marketplaces and individuals implement this standard by retrieving the royalty payment information with `royaltyInfo()`, which specifies how much to pay to which address for a given sale price. The exact mechanism for paying and notifying the recipient will be defined in future EIPs. This ERC should be considered a minimal, gas-efficient building block for further innovation in NFT royalty payments.

**Key Features:**

- **Creator Royalties:** Allows creators earn passive income from secondary sales.
- **Interoperability:** Works seamlessly across marketplaces that implement the standard.

**Popular Use Cases:**

- Artists earning royalties on every resale of their digital artwork.
- Content creators ensuring revenue from their creations.

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

------

### ERC-4907: Rentable NFTs (ERC-721 ext)

> [EIP Reference](https://eips.ethereum.org/EIPS/eip-4907)
>
> Status: final
>
> OpenZeppelin implementation: no
>
> Video details: [What is Double Protocol and how does it work? - Unlock the Liquidity of NFTs with ERC-490](https://www.youtube.com/watch?v=sZZ1JgtpcL4&t=183s)

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

### ERC-5496 (ERC-721 extension)

> Status: last call
>
> OpenZeppelin implementation: no
>
> [ERC specification](https://eips.ethereum.org/EIPS/eip-5496),[Example](https://github.com/wnft/wnft-contracts/blob/main/contracts/ERC5496/ERC5496.sol), [ethereum-magicians.org](https://ethereum-magicians.org/t/eip-5496-multi-privilege-management-extension-for-erc-721/10427)

This EIP defines an interface extending [EIP-721](https://eips.ethereum.org/EIPS/eip-721) to provide shareable multi-privileges for NFTs.

Privileges may be:

- on-chain: voting rights, permission to claim an airdrop
-  Off-chain: a coupon for an online store, a discount at a local restaurant, access to VIP lounges in airports.

Each NFT may contain many privileges, and the holder of a privilege can verifiably transfer that privilege to others. 

Privileges may be non-shareable or shareable. Shareable privileges can be cloned, with the provider able to adjust the details according to the spreading path. Expiration periods can also be set for each privilege.

#### Motivation

**ERC-721 limitation**

[EIP-721](https://eips.ethereum.org/EIPS/eip-721) only records the ownership and its transfer, the privileges of an NFT are not recorded on-chain. This extension would allow merchants/projects to give out a certain privilege to a specified group of people, and owners of the privileges can manage each one of the privileges independently. This facilitates a great possibility for NFTs to have real usefulness.

**Example**

For example, an airline company issues a series of [EIP-721](https://eips.ethereum.org/EIPS/eip-721)/[EIP-1155](https://eips.ethereum.org/EIPS/eip-1155) tokens to Crypto Punk holders to give them privileges, in order to attract them to join their club. However, since these tokens are not bound to the original NFT, if the original NFT is transferred, these privileges remain in the hands of the original holders, and the new holders cannot enjoy the privileges automatically. So, we propose a set of interfaces that can bind the privileges to the underlying NFT, while allowing users to manage the privileges independently.



#### Shareable priviliges

The number of privilege holders is limited by the number of NFTs if privileges are non-shareable. A shareable privilege means the original privilege holder can copy the privilege and give it to others, not transferring his/her own privilege to them. 

This mechanism greatly enhances the spread of privileges as well as the adoption of NFTs.

Example:

For example, a local pizza shop offers a 30% off Coupon and the owner of the shop encourages their consumers to share the coupon with friends, then the friends can get the coupon. Let’s say Tom gets 30% off Coupon from the shop and he shares the coupon with Alice. Alice gets the coupon too and Alice’s referrer is Tom. For some certain cases, Tom may get more rewards from the shop. This will help the merchants in spreading the promotion among consumers.

If the owner of the NFT transfers ownership to another user, there is no impact on “privileges”. But errors may occur if the owner tries to withdraw the original [EIP-721](https://eips.ethereum.org/EIPS/eip-721) token from the wrapped NFT through `unwrap()` if any available privileges are still ongoing. 

We protect the rights of holders of the privileges to check the last expiration date of the privilege.

```solidity
function unwrap(uint256 tokenId, address to) external {
    require(getBlockTimestamp() >= privilegeBook[tokenId].lastExpiresAt, "privilege not yet expired");

    require(ownerOf(tokenId) == msg.sender, "not owner");

    _burn(tokenId);

    IERC721(nft).transferFrom(address(this), to, tokenId);

    emit Unwrap(nft, tokenId, msg.sender, to);
}
```



#### Main functions

```solidity
/// @title multi-privilege extension for EIP-721
///  Note: the EIP-165 identifier for this interface is 0x076e1bbb
interface IERC5496{
    /// @notice set the privilege holder of a NFT.
    function setPrivilege(uint256 tokenId, uint256 privilegeId, address user, uint256 expires) external;

    /// @notice Return the expiry timestamp of a privilege
    function privilegeExpires(uint256 tokenId, uint256 privilegeId) external view returns(uint256);

    /// @notice Check if a user has a certain privilege
    function hasPrivilege(uint256 tokenId, uint256 privilegeId, address user) external view returns(bool);
}
```

### ERC-3525: Semi-Fungible tokens

> Status: final
>
> OpenZeppelin implementation: no, see [https://forum.openzeppelin.com/t/plans-to-adopt-erc3525-semi-fungible-tokens-sfts/33522](https://forum.openzeppelin.com/t/plans-to-adopt-erc3525-semi-fungible-tokens-sfts/33522)
>
> [ERC specification](https://eips.ethereum.org/EIPS/eip-3525), [implementation example](https://github.com/solv-finance/erc-3525), [ethereum magicians](https://ethereum-magicians.org/t/eip-3525-the-semi-fungible-token/9770)

This standard defines semi-fungible tokens, compatible with [ERC-721](https://eips.ethereum.org/EIPS/eip-721) standard. 

This standard introduces an `<ID, SLOT, VALUE>` triple scalar model that represents the semi-fungible structure of a token. It also introduces new transfer models as well as approval models that reflect the semi-fungible nature of the tokens.

- Token contains an ERC-721 equivalent **ID property** to identify itself as a universally unique entity, so that the tokens can be transferred between addresses and approved to be operated in ERC-721 compatible way.
- Token also contains a `value` property, representing the quantitative nature of the token. The meaning of the ‘value’ property is quite like that of the ‘balance’ property of an [ERC-20](https://eips.ethereum.org/EIPS/eip-20) token. Each token has a ‘slot’ attribute, ensuring that the value of two tokens with the same slot be treated as fungible, adding fungibility to the value property of the tokens.
- This EIP introduces new token transfer models for semi-fungibility, including value transfer between two tokens of the same slot and value transfer from a token to an address.
- Difference with ERC-1155: 
  - If you have a ERC1155 token with a balance of 10, you have 10 identical items; 
  - while it is a ERC3525 token with a value of 10, you have one item with face value of 10.
  - With ERC-3525, TokenID is universally unique, as which in ERC721.



#### Main functions

```solidity
    /**
     * @notice Get the number of decimals the token uses for value - e.g. 6, means the user
     *  representation of the value of a token can be calculated by dividing it by 1,000,000.
     *  Considering the compatibility with third-party wallets, this function is defined as
     *  `valueDecimals()` instead of `decimals()` to avoid conflict with ERC-20 tokens.
     * @return The number of decimals for value
     */
    function valueDecimals() external view returns (uint8);

    /**
     * @notice Get the value of a token.
     * @param _tokenId The token for which to query the balance
     * @return The value of `_tokenId`
     */
    function balanceOf(uint256 _tokenId) external view returns (uint256);

    /**
     * @notice Get the slot of a token.
     * @param _tokenId The identifier for a token
     * @return The slot of the token
     */
    function slotOf(uint256 _tokenId) external view returns (uint256);

    /**
     * @notice Allow an operator to manage the value of a token, up to the `_value`.
     */
    function approve(
        uint256 _tokenId,
        address _operator,
        uint256 _value
    ) external payable;

    /**
     * @notice Get the maximum value of a token that an operator is allowed to manage.
     */
    function allowance(uint256 _tokenId, address _operator) external view returns (uint256);

    /**
     * @notice Transfer value from a specified token to another specified token with the same slot.
     */
    function transferFrom(
        uint256 _fromTokenId,
        uint256 _toTokenId,
        uint256 _value
    ) external payable;


    /**
     * @notice Transfer value from a specified token to an address. The caller should confirm that
     *  `_to` is capable of receiving ERC-3525 tokens.
     * @return ID of the token which receives the transferred value
     */
    function transferFrom(
        uint256 _fromTokenId,
        address _to,
        uint256 _value
    ) external payable returns (uint256);
}
```

### Soulbound NFT

#### ERC-5192 - Minimal Soulbound NFTs (ERC-721 ext)

> Status: final
>
> OpenZeppelin implementation: no
>
> [EIP specification](https://eips.ethereum.org/EIPS/eip-5192), [implementation example](https://github.com/public-assembly/curation-protocol/blob/main/src/CuratorSkeletonNFT.sol)

This standard is an extension of [EIP-721](https://eips.ethereum.org/EIPS/eip-721). It proposes a minimal interface to make tokens soulbound using the feature detection functionality of [EIP-165](https://eips.ethereum.org/EIPS/eip-165). A soulbound token is a non-fungible token bound to a single account.

##### Motivation

The Ethereum community has expressed a need for non-transferrable, non-fungible, and socially-priced tokens similar to World of Warcraft’s soulbound items. But the lack of a token standard leads many developers to simply throw errors upon a user’s invocation of transfer functionalities. Over the long term, this will lead to fragmentation and less composability.

##### Interface

```solidity
// SPDX-License-Identifier: CC0-1.0
pragma solidity ^0.8.0;

interface IERC5192 {
  /// @notice Emitted when the locking status is changed to locked.
  /// @dev If a token is minted and the status is locked, this event should be emitted.
  /// @param tokenId The identifier for a token.
  event Locked(uint256 tokenId);

  /// @notice Emitted when the locking status is changed to unlocked.
  /// @dev If a token is minted and the status is unlocked, this event should be emitted.
  /// @param tokenId The identifier for a token.
  event Unlocked(uint256 tokenId);

  /// @notice Returns the locking status of an Soulbound Token
  /// @dev SBTs assigned to zero address are considered invalid, and queries
  /// about them do throw.
  /// @param tokenId The identifier for an SBT.
  function locked(uint256 tokenId) external view returns (bool);
}
```



#### ERC-5484: Consensual Soulbound Tokens

> Status: 
>
> OpenZeppelin implementation: no
>
> [EIP specification](https://eips.ethereum.org/EIPS/eip-5484), [ethereum magiciens](https://ethereum-magicians.org/t/eip-5484-consensual-soulbound-tokens/10424)
>
> See also [Cyfrin - What is a Soulbound Token? - ERC-5114 & ERC-5484](https://www.cyfrin.io/blog/what-is-a-soulbound-token)

Interface for special NFTs with immutable ownership and pre-determined immutable burn authorization

This EIP defines an interface extending [EIP-721](https://eips.ethereum.org/EIPS/eip-721) to create soulbound tokens. Before issuance, both parties (the issuer and the receiver), have to agree on who has the authorization to burn this token. Burn authorization is immutable after declaration. 

After its issuance, a soulbound token can’t be transferred, but can be burned based on a predetermined immutable burn authorization.

##### Interface

```solidity
// SPDX-License-Identifier: CC0-1.0
pragma solidity ^0.8.0;

interface IERC5484 {
    /// A guideline to standardlize burn-authorization's number coding
    enum BurnAuth {
        IssuerOnly,
        OwnerOnly,
        Both,
        Neither
    }

    /// @notice Emitted when a soulbound token is issued.
    /// @dev This emit is an add-on to nft's transfer emit in order to distinguish sbt 
    /// from vanilla nft while providing backward compatibility.
    /// @param from The issuer
    /// @param to The receiver
    /// @param tokenId The id of the issued token
    event Issued (
        address indexed from,
        address indexed to,
        uint256 indexed tokenId,
        BurnAuth burnAuth
    );

    /// @notice provides burn authorization of the token id.
    /// @dev unassigned tokenIds are invalid, and queries do throw
    /// @param tokenId The identifier for a token.
    function burnAuth(uint256 tokenId) external view returns (BurnAuth);
}
```

----

#### ERC-5114 - Soulbound badge

>  Status: Last Call
>
> OpenZeppelin implementation: no
>
> [EIP specification](https://eips.ethereum.org/EIPS/eip-5114), [ethereum magicians](https://ethereum-magicians.org/t/eip-5114-soulbound-badges/9417)
>
> See also [Cyfrin - What is a Soulbound Token? - ERC-5114 & ERC-5484](https://www.cyfrin.io/blog/what-is-a-soulbound-token)

A soulbound badge is a token that, when minted, is bound to another Non-Fungible Token (NFT), and cannot be transferred/moved after that.

Warning: contrary

By requiring that badges can never move, we both guarantee non-separability and non-mergeability among collections of soulbound badges that are bound to a single NFT while simultaneously allowing users to aggressively cache results.

##### Interface

```solidity
interface IERC5114 {
	// fired anytime a new instance of this badge is minted
	// this event **MUST NOT** be fired twice for the same `badgeId`
	event Mint(uint256 indexed badgeId, address indexed nftAddress, uint256 indexed nftTokenId);

	// returns the NFT that this badge is bound to.
	// this function **MUST** throw if the badge hasn't been minted yet
	// this function **MUST** always return the same result every time it is called after it has been minted
	// this function **MUST** return the same value as found in the original `Mint` event for the badge
	function ownerOf(uint256 badgeId) external view returns (address nftAddress, uint256 nftTokenId);

	// returns a URI with details about this badge collection
	// the metadata returned by this is merged with the metadata return by `badgeUri(uint256)`
	// the collectionUri **MUST** be immutable (e.g., ipfs:// and not http://)
	// the collectionUri **MUST** be content addressable (e.g., ipfs:// and not http://)
	// data from `badgeUri` takes precedence over data returned by this method
	// any external links referenced by the content at `collectionUri` also **MUST** follow all of the above rules
	function collectionUri() external pure returns (string collectionUri);

	// returns a censorship resistant URI with details about this badge instance
	// the collectionUri **MUST** be immutable (e.g., ipfs:// and not http://)
	// the collectionUri **MUST** be content addressable (e.g., ipfs:// and not http://)
	// data from this takes precedence over data returned by `collectionUri`
	// any external links referenced by the content at `badgeUri` also **MUST** follow all of the above rules
	function badgeUri(uint256 badgeId) external view returns (string badgeUri);

	// returns a string that indicates the format of the `badgeUri` and `collectionUri` results (e.g., 'EIP-ABCD' or 'soulbound-schema-version-4')
	function metadataFormat() external pure returns (string format);
}
```



## Draft ERCs

While ERC-721 paved the way, other standards have emerged to address additional functionality, scalability, and versatility in NFTs. Here are the most prominent ones:

### ERC-998: Composable NFTs

> [ERC reference](https://eips.ethereum.org/EIPS/eip-998)
>
> Status: draft
>
> OpenZeppelin implementation: no

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



-----

### ERC-6551: Non-fungible Token Bound Accounts

> [ERC reference](https://eips.ethereum.org/EIPS/eip-6551)
>
> Status: Review
>
> OpenZeppelin implementation: no

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



### ERC-3664: Metaverse NFTs (ERC-721/1155 extension). 

> Status: draft
>
> OpenZeppelin implementation: no
>
> [ERC specification](https://github.com/DRepublic-io/EIPs/blob/master/EIPS/eip-3664.md), [ethereum magicians](https://ethereum-magicians.org/t/eip-3664-next-generation-game-nft-standard/6738), [Implementation example](https://github.com/DRepublic-io/EIP-3664)

This proposal suggest a new type of extendable NFT metadata protocol, which is compatible with existing ERC721 and ERC1155, and can build on their basis to provide better descriptive power for attributes metadata.

Currently the EIP provide the following options for attribute extendability:

1. General attributes: for describing immutable attributes such as avatar birth dates.
2. Variable attributes: for describing attributes whose value will change, such as an avatar’s combat power.
3. Transferable attributes: for describing attributes that can be transferred to other NFTs.
4. Upgradable attributes: for describing NFT levels and can trigger upgrades.
5. Evolvable attributes: for describing the fact that NFT can evolve, and evolutions can fail, and if the case of failure, the NFT can no longer be used until properly repaired.
6. Text attributes: for realizing functionality similar to Loot since the above attributes are numerical in nature.

See also [Cyfrin - EIP 3664 - The full guide to advanced NFT propertie](https://www.cyfrin.io/blog/eip-3664-full-guide-to-nft-properties)

#### Motivation

NFT standards such as ERC721 and ERC1155 are now widely recognized and utilized, but these two protocols lack descriptive power, particularly regarding metadata. ERC721 and ERC1155 express these attributes via tokenURI, which are typically fixed URL addresses or descriptive texts, which limits the possibility to define mutable attributes.

#### Main functions

```solidity
    /**
     * @dev Returns primary attribute type of owned by `tokenId`.
     */
    function primaryAttributeOf(uint256 tokenId)
        external
        view
        returns (uint256);

    /**
     * @dev Returns all attribute types of owned by `tokenId`.
     */
    function attributesOf(uint256 tokenId)
        external
        view
        returns (uint256[] memory);

    /**
     * @dev Returns the attribute type `attrId` value owned by `tokenId`.
     */
    function balanceOf(uint256 tokenId, uint256 attrId)
        external
        view
        returns (uint256);

    /**
     * @dev Returns the batch of attribute type `attrIds` values owned by `tokenId`.
     */
    function balanceOfBatch(uint256 tokenId, uint256[] calldata attrIds)
        external
        view
        returns (uint256[] memory);

    /**
     * @dev Set primary attribute type of owned by `tokenId`.
     */
    function setPrimaryAttribute(uint256 tokenId, uint256 attrId) external;

    /**
     * @dev Attaches `amount` value of attribute type `attrId` to `tokenId`.
     */
    function attach(
        uint256 tokenId,
        uint256 attrId,
        uint256 amount
    ) external;

    /**
     * @dev [Batched] version of {attach}.
     */
    function batchAttach(
        uint256 tokenId,
        uint256[] calldata attrIds,
        uint256[] calldata amounts
    ) external;
}
```

### ERC-7771:  Fractionally Represented Non-Fungible Token

> Status: draft
>
> OpenZeppelin implementation: no
>
> [ERC specification](https://eips.ethereum.org/EIPS/eip-7651), [ethereum magicians](https://ethereum-magicians.org/t/erc-7651-fractionally-represented-non-fungible-token/19176)

This proposal introduces a standard for fractionally represented non-fungible tokens, allowing NFTs to be managed and owned fractionally within a single contract. 

This approach enables NFTs to coexist with an underlying fungible representation seamlessly, enhancing liquidity and access without dividing the NFT itself, or requiring an explicit conversion step. 

The standard includes mechanisms for both fractional and whole token transfers, approvals, and event emissions. This specification draws from design in both [ERC-721](https://eips.ethereum.org/EIPS/eip-721) and [ERC-20](https://eips.ethereum.org/EIPS/eip-20), but is not fully compatible with either standard.

```solidity
interface IERC7651 is IERC165 {
  /// @dev This emits when fractional representation approval for a given spender
  ///      is changed or reaffirmed.
  event FractionalApproval(address indexed owner, address indexed spender, uint256 value);

  /// @dev This emits when ownership of fractionally represented tokens changes
  ///      by any mechanism. This event emits when tokens are both created and destroyed,
  ///      ie. when from and to are assigned to the zero address respectively.
  event FractionalTransfer(address indexed from, address indexed to, uint256 amount);

  /// @dev This emits when an operator is enabled or disabled for an owner.
  ///      The operator can manage all NFTs of the owner.
  event ApprovalForAll(
    address indexed owner,
    address indexed operator,
    bool approved
  );

  /// @dev This emits when the approved spender is changed or reaffirmed for a given NFT.
  ///      A zero address emitted as spender implies that no addresses are approved for
  ///      this token.
  event NonFungibleApproval(
    address indexed owner,
    address indexed spender,
    uint256 indexed id
  );

  /// @dev This emits when ownership of any NFT changes by any mechanism.
  ///      This event emits when NFTs are both created and destroyed, ie. when
  ///      from and to are assigned to the zero address respectively.
  event NonFungibleTransfer(address indexed from, address indexed to, uint256 indexed id);

  /// @notice Decimal places in fractional representation
  /// @dev Decimals are used as a means of determining when balances or amounts
  ///      contain whole or purely fractional components
  /// @return Number of decimal places used in fractional representation
  function decimals() external view returns (uint8 decimals);

  /// @notice The total supply of a token in fractional representation
  /// @dev The total supply of NFTs may be recovered by computing
  ///      `totalSupply() / 10 ** decimals()`
  /// @return Total supply of the token in fractional representation
  function totalSupply() external view returns (uint256 totalSupply);

  /// @notice Balance of a given address in fractional representation
  /// @dev The total supply of NFTs may be recovered by computing
  ///      `totalSupply() / 10 ** decimals()`
  /// @param owner_ The address that owns the tokens
  /// @return Balance of a given address in fractional representation
  function balanceOf(address owner_) external view returns (uint256 balance);

  /// @notice Query if an address is an authorized operator for another address
  /// @param owner_ The address that owns the NFTs
  /// @param operator_ The address being checked for approval to act on behalf of the owner
  /// @return True if `operator_` is an approved operator for `owner_`, false otherwise
  function isApprovedForAll(
    address owner_,
    address operator_
  ) external view returns (bool isApproved);

  /// @notice Query the allowed amount an address can spend for another address
  /// @param owner_ The address that owns tokens in fractional representation
  /// @param spender_ The address being checked for allowance to spend on behalf of the owner
  /// @return The amount of tokens `spender_` is approved to spend on behalf of `owner_`
  function allowance(
    address owner_,
    address spender_
  ) external view returns (uint256 allowance);

  /// @notice Query the owner of a specific NFT.
  /// @dev Tokens owned by the zero address are considered invalid and should revert on
  ///      ownership query.
  /// @param id_ The unique identifier for an NFT.
  /// @return The address of the token's owner.
  function ownerOf(uint256 id_) external view returns (address owner);

  /// @notice Set approval for an address to spend a fractional amount,
  ///         or to spend a specific NFT.
  /// @dev There must be no overlap between valid ids and fractional values.
  /// @dev Throws unless `msg.sender` is the current NFT owner, or an authorized
  ///      operator of the current owner if an id is provided.
  /// @dev Throws if the id is not a valid NFT
  /// @param spender_ The spender of a given token or value.
  /// @param amountOrId_ A fractional value or id to approve.
  /// @return Whether the approval operation was successful or not.
  function approve(
    address spender_,
    uint256 amountOrId_
  ) external returns (bool success);

  /// @notice Set approval for a third party to manage all of the callers
  ///         non-fungible assets
  /// @param operator_ Address to add to the callers authorized operator set
  /// @param approved_ True if the operator is approved, false if not approved
  function setApprovalForAll(address operator_, bool approved_) external;

  /// @notice Transfer fractional tokens or an NFT from one address to another
  /// @dev There must be no overlap between valid ids and fractional values
  /// @dev The operation should revert if the caller is not `from_` or is not approved
  ///      to spent the tokens or NFT owned by `from_`
  /// @dev The operation should revert if value is less than the balance of `from_` or
  ///      if the NFT is not owned by `from_`
  /// @dev Throws if the id is not a valid NFT
  /// @param from_ The address to transfer fractional tokens or an NFT from
  /// @param to_ The address to transfer fractional tokens or an NFT to
  /// @param amountOrId_ The fractional value or a distinct NFT id to transfer
  /// @return True if the operation was successful
  function transferFrom(
    address from_,
    address to_,
    uint256 amountOrId_
  ) external returns (bool success);

  /// @notice Transfer fractional tokens from one address to another
  /// @dev The operation should revert if amount is less than the balance of `from_`
  /// @param to_ The address to transfer fractional tokens to
  /// @param amount_ The fractional value to transfer
  /// @return True if the operation was successful
  function transfer(address to_, uint256 amount_) external returns (bool success);

  /// @notice Transfers the ownership of an NFT from one address to another address
  /// @dev Throws unless `msg.sender` is the current owner, an authorized
  ///      operator, or the approved address for this NFT
  /// @dev Throws if `from_` is not the current owner
  /// @dev Throws if `to_` is the zero address
  /// @dev Throws if `tokenId_` is not a valid NFT
  /// @dev When transfer is complete, this function checks if `to_` is a
  ///      smart contract (code size > 0). If so, it calls `onERC721Received`
  ///      on `to_` and throws if the return value is not
  ///      `bytes4(keccak256("onERC721Received(address,uint256,bytes)"))`.
  /// @param from_ The address to transfer the NFT from
  /// @param to_ The address to transfer the NFT to
  /// @param tokenId_ The NFT to transfer
  /// @param data_ Additional data with no specified format, sent in call to `to_`
  function safeTransferFrom(
    address from_,
    address to_,
    uint256 id_,
    bytes calldata data_
  ) external;

  /// @notice Transfers the ownership of an NFT from one address to another address
  /// @dev This is identical to the above function safeTransferFrom interface
  ///      though must pass empty bytes as data to `to_`
  /// @param from_ The address to transfer the NFT from
  /// @param to_ The address to transfer the NFT to
  /// @param tokenId_ The NFT to transfer
  function safeTransferFrom(address from_, address to_, uint256 id_) external;
}

interface IERC165 {
    /// @notice Query if a contract implements an interface
    /// @param interfaceID_ The interface identifier, as specified in ERC-165
    /// @dev Interface identification is specified in ERC-165. This function
    ///      uses less than 30,000 gas.
    /// @return `true` if the contract implements `interfaceID` and
    ///         `interfaceID` is not 0xffffffff, `false` otherwise
    function supportsInterface(bytes4 interfaceID_) external view returns (bool);
}
```

https://eips.ethereum.org/EIPS/eip-7651

### ERC-7631: Dual Nature Token pair

> Status: review
>
> OpenZeppelin implementation: no
>
> [ERC specification](https://eips.ethereum.org/EIPS/eip-7631), [ethereum magicians](https://ethereum-magicians.org/t/erc-7631-dual-nature-token-pair/18796)

A fungible [ERC-20](https://eips.ethereum.org/EIPS/eip-20) token contract and non-fungible [ERC-721](https://eips.ethereum.org/EIPS/eip-721) token contract can be interlinked, allowing actions performed on one contract to be reflected on the other. 

- This proposal defines how the relationship between the two token contracts can be queried. 
- It also enables accounts to configure whether ERC-721 mints and transfers should be skipped during ERC-20 to ERC-721 synchronization.

The ERC-20 fungible and ERC-721 non-fungible token standards offer sufficient flexibility for a co-joined, dual nature token pair. 

Transfers on the ERC-20 token can automatically trigger transfers on the ERC-721 token, and vice-versa. This enables applications such as native ERC-721 fractionalization, wherein acquiring ERC-20 tokens leads to the automatic issuance of ERC-721 tokens, proportional to the ERC-20 balance.

#### Compatibility with ERC-20 and ERC-721

Dual nature token pairs maintain full compliance with both ERC-20 and ERC-721 token standards. This proposal aims to enhance the functionality of dual nature token pairs.

To facilitate querying the relationship between the tokens, extension interfaces are proposed for the ERC-20 and ERC-721 tokens respectively. This enables various quality of life improvements such as allowing decentralized exchanges and NFT marketplaces to display the relationship between the tokens.

Additionally, users can configure whether they want to skip ERC-721 mints and transfers during ERC-20 to ERC-721 synchronization.

#### Interface

##### ERC-20 Extension Interface

```solidity
interface IERC7631Base {
    /// @dev Returns the address of the mirror ERC-721 contract.
    function mirrorERC721() external view returns (address);
}
```

##### ERC-721 Extension Interface

```solidity
interface IERC7631Mirror {
    /// @dev Returns the address of the base ERC-20 contract.
    function baseERC20() external view returns (address);
}
```



## Custom implementation

### ERC-721A: Gas-Optimized ERC-721 (ERC-721 ext)

> [ERC-721a](https://www.erc721a.org)
>
> Status: draft
>
> OpenZeppelin implementation: no

ERC-721A is an extension of the ERC-721 standard designed for gas efficiency when minting multiple NFTs in a single transaction. It was introduced by the Azuki NFT team to solve the cost challenge for large NFT drops.

The code is available on the [Chiru Labs GitHub](https://github.com/chiru-labs/ERC721A)

**Key Features:**

- **Gas Optimization:** Minting multiple NFTs incurs almost the same gas fee as minting a single NFT.
- **Backward Compatibility:** Fully compatible with ERC-721.

**Popular Use Cases:**

- NFT projects with mass minting events (e.g., profile picture (PFP) collections like Azuki).

See also [ERC-721a](https://www.erc721a.org)

-----

### ERC-404

> Status: not an ERC
>
> OpenZeppelin implementation: no
>
> [reference implementation](https://github.com/0xacme/ERC404)

ERC404 is an experimental, mixed ERC20 / ERC721 implementation with native liquidity and fractionalization. While these two standards are not designed to be mixed, this implementation strives to do so in as robust a manner as possible while minimizing tradeoffs.https://hacken.io/discover/erc-404/

### DN-404

> Status: not an ERC
>
> OpenZeppelin implementation: no
>
> [Reference implementation](https://github.com/Vectorized/dn404)

DN404 is an implementation of a co-joined ERC20 and ERC721 pair.

To learn more about these dual nature token pairs, you can read the full [ERC-7631 spec](https://eips.ethereum.org/EIPS/eip-7631).

- Full compliance with the ERC20 and ERC721 specifications.
- Transfers on one side will be reflected on the other side.
- Pretty optimized.
