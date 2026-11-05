// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

/// Article example: transient variables pack like storage and have their own slot 0.
contract C layout at 0x10 {
    uint256 stored;
    uint128 transient a;
    uint128 transient b;
    bool transient c;
    address transient d;
    uint256 transient e;
}
