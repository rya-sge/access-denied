---
layout: post
title: How indicates the solidity version of your smart contract
date:   2022-10-29
locale: en-GB
lang: en
last-update: 
categories: blockchain solidity
tags: solidity ethereum smart-contract
description: There are different way to indicate the solidity version of the compiler. This article presents the advantages and disadvantages of each
isMath: false
image: 
---

There are many ways to indicate the solidity version of the compiler.
As stated in the solidity documentation [[docs.soliditylang.org 2022](https://docs.soliditylang.org/en/v0.8.17/layout-of-source-files.html#version-pragma)], the pragma only instructs the compiler to check whether its version matches the one required by the pragma. 
The version pragma has no effect:

- On the version of the compiler installed locally
- On the features provided by the compiler.

### Fixed
With this notation, the compiler version is fixed exactly.
`pragma solidity 0.5.2;`

### Floating point (to avoid)

With the floating notation, the versions accepted during the compilation will be all those from the version indicated until the next major version.

**Example**

`pragma solidity ^0.5.2;`

As indicated by the solidity documentation [[docs.soliditylang.org 2022](https://docs.soliditylang.org/en/v0.8.17/layout-of-source-files.html#version-pragma)], "The code will compile for 0.5.2 version and higher up to version 6.0.0 (not include)"

To sum up:
- '0.5.2' will compile
- '0.5.3' will compile
- '0.6.0' will generate an error.

**Security**

With this notation, minor updates will be accepted. Nevertheless, even if the modifications are minimal, they will not have been tested at the time of the development of the contracts.


The SWC-103 considers the floating notation as a vulnerability.

### Range notation (to avoid)
It is possible to use a more complex way to indicate the version by using the same notation as the versioner of NPM (semver)  [[npm V6.14.17](https://docs.npmjs.com/cli/v6/using-npm/semver)].
For instance, it is possible to indicate precisely a range between two major version, here 0.4.0 and 0.6.0 [6]
`pragma solidity >=0.4.0 < 0.6.0;`

## Conclusion
As indicated in several articles [[Shashank 2022](https://blog.solidityscan.com/understanding-solidity-pragma-and-its-security-practices-3b5458763a34)], [[immunebytes. 2022](https://www.immunebytes.com/blog/floating-pragma/)], it is better to use the fixed version, the one that was used to develop and test the smart contracts.

For libraries, some believe that one can use the floating notation because the code will be used by other smart contracts. This is notably the choice made by OpenZeppelin, see this [[issue](https://github.com/ConsenSys/smart-contract-best-practices/issues/125)] [ConsenSys 2017].


# Reference

CONSENSYS, 2017. Should we lock pragma. *GitHub*. Online. 28 December 2017. [Accessed 29 October 2022]. Retrieved from: [https://github.com/ConsenSys/smart-contract-best-practices/issues/125](https://github.com/ConsenSys/smart-contract-best-practices/issues/125)

DOCS.SOLIDITYLANG.ORG, 2022. Version Pragma. *docs.soliditylang.org*. Online. 30 August 2022. [Accessed 29 October 2022]. Retrieved from: [https://docs.soliditylang.org/en/v0.8.17/layout-of-source-files.html#version-pragma](https://docs.soliditylang.org/en/v0.8.17/layout-of-source-files.html#version-pragma)

IMMUNEBYTES., 2022. Floating Pragma: the Ultimate Guide. *immunebytes.* Online. 7 August 2022. [Accessed 29 October 2022]. Retrieved from: [https://www.immunebytes.com/blog/floating-pragma/](https://www.immunebytes.com/blog/floating-pragma/)

NPM, V6.14.17. semver. *npm Docs*. Online. V6.14.17. [Accessed 29 October 2022]. Retrieved from: [https://docs.npmjs.com/cli/v6/using-npm/semver](https://docs.npmjs.com/cli/v6/using-npm/semver)

SHASHANK, 2022. Understanding Solidity Pragma and its Security Practices. *SolidityScan*. Online. 9 May 2022. [Accessed 29 October 2022]. Retrieved from: [https://blog.solidityscan.com/understanding-solidity-pragma-and-its-security-practices-3b5458763a34](https://blog.solidityscan.com/understanding-solidity-pragma-and-its-security-practices-3b5458763a34)

SMARTCONTRACTSECURITY, no date. semver_floating_pragma.sol. *SWC Registry*. Online. [Accessed 29 October 2022]. Retrieved from: [https://swcregistry.io/docs/SWC-103#semver_floating_pragmasol](https://swcregistry.io/docs/SWC-103#semver_floating_pragmasol)

SMARTCONTRACTSECURITY, 2018. SWC-103. *SWC Registry*. Online. 24 September 2018. [Accessed 29 October 2022]. Retrieved from: [https://swcregistry.io/docs/SWC-103](https://swcregistry.io/docs/SWC-103)

