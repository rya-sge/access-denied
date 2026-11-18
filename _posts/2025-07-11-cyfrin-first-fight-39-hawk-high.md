---
layout: post
title: "Cyfrin First Fight 39 - Hawk High"
date: 2025-07-11
last_modified_at: 2026-11-17
lang: en
locale: en-GB
categories: solidity blockchain
tags: ctf cyfrin first-fight
series: cyfrin-first-fight
description: First Fight 39 - Hawk High.
image: /assets/article/blockchain/audit/2025-07-11-cyfrin-first-fight-39-hawk-high-mindmap.png
isMath: false
---

Welcome to **Hawk High**, enroll, avoid bad reviews, and graduate!!!

You have been contracted to review the upgradeable contracts for the Hawk High School which will be launched very soon.

These contracts utilize the UUPSUpgradeable library from OpenZeppelin.

At the end of the school session (4 weeks), the system is upgraded to a new one.



This article describes the [First Fight 39](https://codehawks.cyfrin.io/c/2025-05-hawk-high) from Cyfrin.

The code is available on [GitHub](https://github.com/CodeHawks-Contests/2025-05-hawk-high).

[TOC]

## What you need to know first

The findings below rely on a few Solidity mechanisms of upgradeable contracts that the article uses without explaining them.

- **Proxy pattern**: an upgradeable contract is split into a proxy, which holds the storage and the funds, and an implementation contract, which holds the code; the proxy forwards every call to the implementation with `delegatecall`, so the code runs against the proxy's storage. Upgrading means changing the implementation address stored in the proxy. The site's [proxy contracts summary]({{site.url_complet}}/2022/10/31/proxy-contract-summary/) describes the OpenZeppelin variants.
- **UUPS (ERC-1822)**: in the Universal Upgradeable Proxy Standard, the upgrade function lives in the implementation rather than in the proxy. OpenZeppelin's `UUPSUpgradeable` exposes `upgradeToAndCall` and requires the contract to override the internal `_authorizeUpgrade` hook to restrict who can upgrade; H-02 is about a contract whose own upgrade function never calls `upgradeToAndCall`, so the implementation address is never changed.
- **Storage layout and slot ordering**: Solidity assigns state variables to storage slots in declaration order, and a mapping or a dynamic array takes one slot of its own. A new implementation must keep the previous variables in the same order, otherwise its variables read and write the slots of different old ones, which is the storage collision of M-03. [ERC-7201](https://eips.ethereum.org/EIPS/eip-7201) namespaced storage is one way to avoid it.
- **Fixed-point percentages**: Solidity has no decimals, so a percentage is stored as an integer scaled by a `PRECISION` constant and applied as `amount * RATE / PRECISION`. The wage split (5% for the principal, 35% for the teachers) is computed this way, and H-01 is an error in that formula.
- **Specification invariants**: the contest lists invariants, properties the code must always respect, such as "remaining 60% should reflect in the bursary after upgrade". M-04 and M-02 are findings where the code breaks one of these stated invariants rather than a generic vulnerability class.
- **Foundry cheatcodes**: the proof of concept uses Foundry's `vm.startPrank` and `vm.stopPrank` to send the enclosed calls from a chosen address, here the principal adding teachers.



## Description

- Actors

  - `Principal`: In charge of hiring/firing teachers, starting the school session, and upgrading the system at the end of the school session. Will receive 5% of all school fees paid as his wages. can also expel students who break rules.
  - `Teachers`: In charge of giving reviews to students at the end of each week. Will share in 35% of all school fees paid as their wages.
  - `Student`: Will pay a school fee when enrolling in Hawk High School. Will get a review each week. If they fail to meet the cutoff score at the end of a school session, they will be not graduated to the next level when the `Principal` upgrades the system.

  ### Invariants

  - A school session lasts 4 weeks
  - For the sake of this project, assume USDC has 18 decimals
  - Wages are to be paid only when the `graduateAndUpgrade()` function is called by the `principal`
  - Payment structure is as follows:
    - `principal` gets 5% of `bursary`
    - `teachers` share of 35% of bursary
    - remaining 60% should reflect in the bursary after upgrade
  - Students can only be reviewed once per week
  - Students must have gotten all reviews before system upgrade. System upgrade should not occur if any student has not gotten 4 reviews (one for each week)
  - Any student who doesn't meet the `cutOffScore` should not be upgraded
  - System upgrade cannot take place unless school's `sessionEnd` has reached

## Valid submissions



### M-04. bursary is not updated in graduateAndUpgrade (Heigt

My severity: Medium

#### Summary

The bursary is not updated in graduateAndUpgrade.

As the result, the following specification is not respected
"remaining 60% should reflect in the bursary after upgrade"

#### Vulnerability Details

Forget to update a storage variable

#### Impact

bursary will store an incorrect amount

#### Recommendations

Update bursary at the end of the function by soustracting the amount transferred to the teaacher and the principal



### H-02. LevelOne UUPS upgrade logic is broken

#### Summary

The function`graduateAndUpgrade `does not allow updating the address of a UUPS proxy implementation

#### Vulnerability Details

The function to upgrade a proxy with the Openzeppelin library UUPS is `upgradeToAndCall`. This function calls `_authorizeUpgrade`to check the access control.

If the principal upgrade the contract LevelOne by calling this function, the contract UUPS will be upgrade to LevelTwo without calling the function `graduateAndUpgrade`

If the principal calls instead `graduateAndUpgrade`

This will not change the implementation that the UUPS proxy points to, since `_authorizeUpgrade` does not change the implementation address stored in the proxy.

Reference: https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/proxy/utils/UUPSUpgradeable.sol#L86

#### Impact

It is not possible to upgrade the proxy while calling the `graduateAndCall` function

#### Tools Used

Manual analysis

#### Recommendations

- Set the function `graduateAndUpgrade`internal instead of public
- Call the function `graduateAndUpgrade`inside the function `_authorizeUpgrade`

### H-01. Incorrect pay per Teacher calculation in graduateAndUpgrade

#### Summary

The function graduateAndUpgrade`don't compute correctly the pay for each teacher.

As a result:

- The function will revert if there are more teachers that what the contract can pay with the wrong calculation
- Teacher will not receive the correct amount if the function does not revert

#### Vulnerability Details

The amount for each teacher is computer as following:

uint256 payPerTeacher = (bursary * TEACHER_WAGE) / PRECISION;

But this does not account the number of teachers in the calcul.

POC

Update the test as following to add more teachers

```solidity
function _teachersAdded() internal {
        vm.startPrank(principal);
        levelOneProxy.addTeacher(alice);
        levelOneProxy.addTeacher(bob);
        levelOneProxy.addTeacher(address(0x5));
        levelOneProxy.addTeacher(address(0x6));
        vm.stopPrank();
    }
```



#### Impact

High since this impact the fund distributed.

#### Tools Used

Manual analysis + Foundry + ChatGPT (for the recommandation)

#### Recommendations

Include the number of teacher in the calculation, here a simplist example:

```solidity
uint256 payPerTeacher = (bursary * TEACHER_WAGE) / (PRECISION * numberOfTeachers);
```

### M-03. LevelTwo has storage collisions with levelOne

#### Summary

In level two, it misses two storage variable `reviewCount`and `lastReviewTime`

As a result, the two following variables `listOfStudents` and `listOfTeachers` will use their variable slots.

```solidity
 mapping(address => bool) public isTeacher;
    mapping(address => bool) public isStudent;
    mapping(address => uint256) public studentScore;
    /**
    @audit miss: reviewCount & lastReviewTime
     */
    address[] listOfStudents;
    address[] listOfTeachers;
```



#### Vulnerability Details

`listOfStudents` and `listOfTeachers` will take the slots used by `reviewCount` and `lastReviewTime` in LevelOne. The base slot of a mapping stays empty (its entries live at `keccak256(key . slot)`), while the base slot of a dynamic array holds its length. In LevelTwo, the two arrays therefore read their length from the empty mapping slots and appear empty, and the student and teacher lists written by LevelOne, whose lengths sit two slots further, are no longer reachable. See [Solidity docs - Layout of State Variables in Storage](https://docs.soliditylang.org/en/latest/internals/layout_in_storage.html).

#### Impact

It is not possible to use`reviewCount`and `lastReviewTime`inside LevelTwo.
The impact is low since the logic inside levelTwo is minimalst

#### Tools Used

Manual analysis

#### Recommendations

Add the missing variables or implement ERC-7201 to manage storage variable: https://eips.ethereum.org/EIPS/eip-7201

### M-02. System can be upgraded even if the session is not finished (Low)

#### Summary

The function to upgrade the system `graduateAndUpgrade `does not check if the session (`sessionEnd`) is terminated.

As a result, the principal can perform an upgrade even if the session is not finished

#### Vulnerability Details

As a result, the following specification is not respected
*System upgrade cannot take place unless school's* *`sessionEnd`* *has reached*

#### Impact

#### Tools Used

Foundry / static analysis

#### Recommendations

Revert in the function ``graduateAndUpgrade` if block.timestamp is < sessionEnd

### L-02.The principal can add himself as a teacher

#### Summary

The principal can add himself as a teacher by calling 'addTeacher`

#### Vulnerability Details

Contrary to `enroll`, the function does not revert if the argument `_teacher`is the principal address.

#### Impact

The princiapl will receive a part of the fees distributed to teacher in `graduateAndUpgrade`

The impact is low because even if the function revert, the principal can still bypass the check by providing another address managed by him.

#### Tools Used

Manual analysis

#### Recommendations

Add the same check as for `enroll`

> if (msg.sender == principal) {
> revert HH__NotAllowed();
> }

## Missed submissions

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Proxy** | The contract that holds storage and funds and forwards calls with `delegatecall` to an implementation contract whose address it stores. |
| **Implementation** | The contract that holds the logic executed by the proxy; here `LevelOne` is the first implementation and `LevelTwo` its upgrade. |
| **UUPS** | The Universal Upgradeable Proxy Standard, in which the upgrade function lives in the implementation; the contest uses OpenZeppelin's `UUPSUpgradeable`. |
| **`upgradeToAndCall`** | The OpenZeppelin UUPS function that changes the implementation address stored in the proxy, after checking `_authorizeUpgrade`. |
| **`_authorizeUpgrade`** | The internal hook that a UUPS contract overrides to apply access control on upgrades; it does not change the implementation address itself. |
| **Storage slot** | A 32-byte location in contract storage; state variables are assigned to slots in declaration order. |
| **Storage collision** | Two versions of a contract using the same slot for different variables, as when `LevelTwo` omits `reviewCount` and `lastReviewTime`. |
| **ERC-7201** | A standard for namespaced storage layouts, proposed in M-03 to manage the storage variables of upgradeable contracts. |
| **Bursary** | The `bursary` variable that accumulates the school fees paid by students and funds the principal's and teachers' wages. |
| **`graduateAndUpgrade`** | The principal's function meant to pay wages and move the system to the next level at the end of the session. |
| **Cut-off score** | The `cutOffScore` a student must reach to be upgraded to the next level. |
| **Invariant** | A property stated in the contest specification that the code must always respect, such as the 5% / 35% / 60% split of the bursary. |

## Mindmap

The mindmap below summarizes the article.

![First Fight 39 Hawk High mindmap]({{site.url_complet}}/assets/article/blockchain/audit/2025-07-11-cyfrin-first-fight-39-hawk-high-mindmap.png)
