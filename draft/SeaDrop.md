# SeaDrop

https://docs.opensea.io/docs/seadrop

## Overview

SeaDrop is a smart contract protocol for primary drops on EVM-compatible blockchains. The types of drops supported are:

- Public drops
- Merkle Tree-based allowlists
- server-signed mints
- token-gated drops. 

An implementing token contract should contain the methods to interface with SeaDrop through an authorized user such as an Owner or Administrator.

Our [SeaDrop](https://github.com/ProjectOpenSea/seadrop/blob/main/src/ERC721SeaDrop.sol) protocol contract provides the latest in NFT Primary Drop functionality, including:

- Extending [ERC721A](https://www.erc721a.org/) to make minting multiple tokens in a single transaction gas-efficient
- Support for a public sale and multiple pre sales using [Merkle Tree](https://en.wikipedia.org/wiki/Merkle_tree) -based allowlists and server-signed mints
- All the functionality needed to integrate with OpenSea’s Drops program.

Many creators find that they require some special functionality on their smart contracts for their drops. The SeaDrop repository has an extension for an implementation of a [random offset](https://github.com/ProjectOpenSea/seadrop/blob/main/src/extensions/ERC721SeaDropRandomOffset.sol) contract. If you require functionality not available in our pre-made contracts, feel free to extend ERC721SeaDrop and add additional functionality. To ensure users have a seamless experience minting your drop on OpenSea, please do not modify any minting functionality.



## Diagram



[![SeaDrop Diagram](https://github.com/ProjectOpenSea/seadrop/raw/main/img/seadrop-diagram.png)](https://github.com/ProjectOpenSea/seadrop/blob/main/img/seadrop-diagram.png)

This diagram shows the logic flow in the case that a drop is hosted on OpenSea, with an optional mint hosted elsewhere. Note that a fee recipient is not required to integrate with SeaDrop, and a fee recipient may be any address.

## Bring Your Own Token Contract

Token creators who would like to use their own token contract functionality can inherit `ERC721SeaDrop`. 

There are also several extensions in `src/extensions` such as Burnable and RandomOffset.

SeaDrop tokens use ERC721A for efficient multiple-quantity mint, along with additional tracking metadata like number of tokens minted by address used for enforcing wallet limits. Please do not override or modify any SeaDrop-related functionality on the token like `getMintStats()` to remain compatible and secure with SeaDrop.

## Extensions



|                                                              |                                                              |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [ERC721SeaDropPausable](https://github.com/ProjectOpenSea/seadrop/blob/main/src/extensions/ERC721SeaDropPausable.sol) | A token contract that extends ERC721SeaDrop to be able to :pause token transfers. By default on deployment transfers are paused,<br/>The owner of the token contract can pause or unpause. |
| [ERC721SeaDropSoulbound](https://github.com/ProjectOpenSea/seadrop/blob/main/src/extensions/ERC721SeaDropSoulbound.sol) | A token contract that extends ERC721SeaDrop to be soulbound, meaning it cannot be transferred after minting |
| [ERC721SeaDropRandomOffset](https://github.com/ProjectOpenSea/seadrop/blob/main/src/extensions/ERC721SeaDropRandomOffset.sol) | ERC721SeaDropRandomOffset is a token contract that extends ERC721SeaDrop to apply a randomOffset to the tokenURI, to enable fair metadata reveals. |



## Provenance Hash

The provenance hash is an optional way for token creators to show that they have not altered their random token metadata since minting started. It can only be set before the first item is minted, and afterwards is expected to match the hash of the metadata.

We recommend token creators to set their provenance hash to the keccak256 hash of the ipfs hash of the folder with the metadata inside as expected to be returned by `tokenURI()`.

To generate consistent ipfs hashes, we recommend to use CID version 1 and sha2-256, as shown below:

https://github.com/ProjectOpenSea/seadrop/blob/main/docs/ProvenanceHash.md

##  Notable Links

- [SeaDrop Repo](https://github.com/ProjectOpenSea/seadrop)
- [Metrics](https://dune.com/opensea_team/seadrop)

## 