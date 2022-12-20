---
layout: post
title: Creating an NFT with Foundry & Solmate
date:   2022-12-20
locale: en-GB
lang: en
last-update: 
categories: blockchain
tags: solidity ethereum foundry
description: This article is a summary of all commands of the tutorial "Creating an NFT with Solmate" offered by Foundry
isMath: false
image: 
---

This article is a summary of all commands of the tutorial "Creating an NFT with Solmate" offered by Foundry

- Link : [https://book.getfoundry.sh/tutorials/solmate-nft](https://book.getfoundry.sh/tutorials/solmate-nft)

- Full implementation  : [https://github.com/FredCoen/nft-tutorial](https://github.com/FredCoen/nft-tutorial)

## Create project and install dependencies
**Initialize the project**

```bash
forge init hello_foundry
```

**Install dependencies**

```bash
forge install transmissions11/solmate Openzeppelin/openzeppelin-contracts
```

**Print tree**
`tree -L 2`
This commands is used to check the installation

> .
> ├── foundry.toml
> ├── lib
> │   ├── forge-std
> │   ├── openzeppelin-contracts
> │   └── solmate
> ├── script
> │   └── Counter.s.sol
> ├── src
> │   └── Counter.sol
> └── test
>     └── Counter.t.sol

## Configure your environment
**Run local node**	
`anvil`
**Set environnement variable**

- Url of the local node
  `export RPC_URL=http://127.0.0.1:8545`
- Private key of the ethereum account
  `export PRIVATE_KEY=<PRIVATE_KEY_TEST>`
  This private key will be use to deploy the contract	


## Implement a basic NFT

### Deployment

**Deploy your NFT contract**

- Template

```bash
forge create NFT --rpc-url=$RPC_URL --private-key=$PRIVATE_KEY --constructor-args <name> <symbol>
```

- Full command

```bash
forge create NFT --rpc-url=$RPC_URL --private-key=$PRIVATE_KEY --constructor-args Bitcoin BTC
```

Result
![alt text]({{site.url_complet}}/assets/article/blockchain/ethereum/foundry-nft-tutorial/deploy-contract.png)

![alt text]({{site.url_complet}}/assets/article/blockchain/ethereum/foundry-nft-tutorial/deploy-contract-anvil.png)

### Minting

```bash
export CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
export RECIPIENT_ADDRESS=0x70997970c51812dc3a010c7d01b50e0d17dc79c8
```

- Minting from your contract

```bash
cast send --rpc-url=$RPC_URL $CONTRACT_ADDRESS  "mintTo(address)" $RECIPIENT_ADDRESS --private-key=$PRIVATE_KEY
```

![alt text]({{site.url_complet}}/assets/article/blockchain/ethereum/foundry-nft-tutorial/mintNFT.png)

![alt text]({{site.url_complet}}/assets/article/blockchain/ethereum/foundry-nft-tutorial/mintNFT-anvil.png)	

- Check the owner of the created NFT

```bash
cast call --rpc-url=$RPC_URL --private-key=$PRIVATE_KEY $CONTRACT_ADDRESS "ownerOf(uint256)" 1
```

Result![alt text]({{site.url_complet}}/assets/article/blockchain/ethereum/foundry-nft-tutorial/check-owner.png)
	
![alt text]({{site.url_complet}}/assets/article/blockchain/ethereum/foundry-nft-tutorial/check-owner-anvil.png)
	

### Test

Warning : this part is performed on an extended version of the basic NFT contract

```bash
forge test
```

​	Warning : you may have some warnings when you are running the test
​	
![alt text]({{site.url_complet}}/assets/article/blockchain/ethereum/foundry-nft-tutorial/test-result.png)

```bash
forge test --gas-report
```

![alt text]({{site.url_complet}}/assets/article/blockchain/ethereum/foundry-nft-tutorial/gas-result1.png)
	
![alt text]({{site.url_complet}}/assets/article/blockchain/ethereum/foundry-nft-tutorial/gas-result2.png)
	

## Reference

[Foundry Book - Creating an NFT with Solmate](https://book.getfoundry.sh/tutorials/solmate-nft#creating-an-nft-with-solmate)
