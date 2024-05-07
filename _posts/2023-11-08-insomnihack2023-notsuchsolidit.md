---
layout: post
title:  "Insomni Hack 2023 - NotSuchSolidIT challenge"
date:   2023-11-08
lang: en
locale: en-GB
categories: blockchain ethereum solidity
tags: solidity blockchain ethereum ctf
description: This article describes the challenge NotSuchSolidIT of Insomni'hack 2023
image: /assets/article/blockchain/ethereum/ethereum-logo-portrait-purple-purple.png
---

This article presents the challenge [NotSuchSolidIT](https://ctftime.org/task/24679) from [Insomni'hack ](https://www.insomnihack.ch/insomnihack-2023/)

## Contracts

The challenge was formed of two different files :

- setup.sol
- Challenge.sol

Two smartcontracts have been deployed, try to withdrawal the `Challenge.sol` to get the flag.

### Setup.sol

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.1;
import "./Challenge.sol";

contract Setup {
	Challenge public chall;

	constructor() payable {
		require(msg.value >= 100, "Not enough ETH to create the challenge..");
		chall = (new Challenge){ value: 50 ether }();
	}

	function isSolved() public view returns (bool) {
		return address(chall).balance == 0;
	}
	
	function isAlive(string calldata signature, bytes calldata parameters, address addr) external returns(bytes memory) {
		(bool success, bytes memory data) = address(addr).call(
			abi.encodeWithSelector(
				bytes4(keccak256(bytes(signature))),
				parameters
			)
		);
		require(success, 'Call failed');
		return data;
	}
}
```

### Challenge

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.1;
contract Challenge {

	address payable owner;
	constructor() payable {
		owner = payable(msg.sender); 
	}

	modifier onlyOwner {
		require(msg.sender == owner);
		_;
	}
	
	function getBalance() public view returns (uint){
		return address(this).balance;
	}
	
	function withdrawAll(address payable _to) public onlyOwner {
		_to.transfer(address(this).balance);
	}
	
	function destroy() public onlyOwner {
		selfdestruct(owner);
	}
}
```

## Solution

1.Compile the contracts with Remix: [https://remix.ethereum.org](https://remix.ethereum.org) 

2.Connect with a custom external provider

![insomniak2023]({{site.url_complet}}/assets/article/blockchain/ctf/insomniak2023/remix-HttpProvider.png)

3.Call withdrawAll with the parameters

![insomniak2023]({{site.url_complet}}/assets/article/blockchain/ctf/insomniak2023/remix-withdraw.png)

4.Check if the challenge **isSolved**

![insomniak2023]({{site.url_complet}}/assets/article/blockchain/ctf/insomniak2023/remix-solved.png)