// SPDX-License-Identifier: MIT
pragma solidity 0.8.30;

import {RLPReader} from "./RLPReader.sol";
import {SSZReader} from "./SSZReader.sol";

/// @notice Decoding entry points measured by the tests. Test code: not audited, do not deploy.
contract Harness {
    uint256 private constant WITHDRAWAL_SIZE = 44;

    struct Withdrawal {
        uint64 index;
        uint64 validatorIndex;
        address addr;
        uint64 amount;
    }

    error WrongSelector();

    /// @dev Baseline: same dispatch and argument decoding, no work.
    function noop(bytes calldata d) external pure returns (uint256) {
        return d.length;
    }

    function noop2(bytes calldata d, uint256 i) external pure returns (uint256) {
        return d.length + i;
    }

    // ---- one withdrawal, read `amount` ----

    function rlpAmount(bytes calldata d) external pure returns (uint256) {
        (uint256 s, uint256 e) = RLPReader.list(d);
        (uint256 fs, uint256 fe, bool isList) = RLPReader.nth(d, s, e, 3);
        if (isList) revert RLPReader.RLPExpectedString();
        return RLPReader.toUint(d, fs, fe);
    }

    function sszAmount(bytes calldata d) external pure returns (uint256) {
        if (d.length != WITHDRAWAL_SIZE) revert SSZReader.SSZBadLength();
        return SSZReader.u64(d, 36);
    }

    function abiAmount(Withdrawal calldata w) external pure returns (uint256) {
        return w.amount;
    }

    // ---- element i of 16 withdrawals ----

    function rlpListAmount(bytes calldata d, uint256 i) external pure returns (uint256) {
        (uint256 s, uint256 e) = RLPReader.list(d);
        (uint256 is_, uint256 ie, bool isList) = RLPReader.nth(d, s, e, i);
        if (!isList) revert RLPReader.RLPExpectedList();
        (uint256 fs, uint256 fe, bool f) = RLPReader.nth(d, is_, ie, 3);
        if (f) revert RLPReader.RLPExpectedString();
        return RLPReader.toUint(d, fs, fe);
    }

    function sszListAmount(bytes calldata d, uint256 i) external pure returns (uint256) {
        if (d.length % WITHDRAWAL_SIZE != 0) revert SSZReader.SSZBadLength();
        if (i >= d.length / WITHDRAWAL_SIZE) revert SSZReader.SSZOutOfBounds();
        return SSZReader.u64(d, i * WITHDRAWAL_SIZE + 36);
    }

    // ---- decode every field of every withdrawal ----

    function rlpSumAll(bytes calldata d) external pure returns (uint256 sum) {
        (uint256 s, uint256 e) = RLPReader.list(d);
        uint256 p = s;
        while (p < e) {
            (uint256 is_, uint256 ie, bool isList) = RLPReader.header(d, p, e);
            if (!isList) revert RLPReader.RLPExpectedList();
            uint256 q = is_;
            for (uint256 k = 0; k < 4; ++k) {
                (uint256 fs, uint256 fe, bool f) = RLPReader.header(d, q, ie);
                if (f) revert RLPReader.RLPExpectedString();
                if (k == 2) {
                    if (fe - fs != 20) revert RLPReader.RLPNonCanonical();
                } else {
                    uint256 v = RLPReader.toUint(d, fs, fe);
                    if (v > type(uint64).max) revert RLPReader.RLPIntegerTooLong();
                    if (k == 3) sum += v;
                }
                q = fe;
            }
            if (q != ie) revert RLPReader.RLPTrailingBytes();
            p = ie;
        }
    }

    function sszSumAll(bytes calldata d) external pure returns (uint256 sum) {
        if (d.length % WITHDRAWAL_SIZE != 0) revert SSZReader.SSZBadLength();
        for (uint256 p = 0; p < d.length; p += WITHDRAWAL_SIZE) {
            SSZReader.u64(d, p);
            SSZReader.u64(d, p + 8);
            sum += SSZReader.u64(d, p + 36);
        }
    }

    // ---- real type-2 transaction: field k of 12, RLP payload after the type byte ----

    function rlpTxField(bytes calldata d, uint256 k) external pure returns (uint256 s, uint256 e) {
        bytes calldata body = d[1:];
        (uint256 ls, uint256 le) = RLPReader.list(body);
        (s, e, ) = RLPReader.nth(body, ls, le, k);
    }

    /// @dev Transaction{payload, signature}: offset to the union, selector, then a fixed field.
    function sszTxValue(bytes calldata d) external pure returns (uint256) {
        uint256 start = SSZReader.u32(d, 0);
        if (start != 8) revert SSZReader.SSZBadOffset();
        if (uint8(d[start]) != 7) revert WrongSelector();
        return SSZReader.u256(d, start + 1 + 101);
    }

    function rlpTxValue(bytes calldata d) external pure returns (uint256) {
        bytes calldata body = d[1:];
        (uint256 ls, uint256 le) = RLPReader.list(body);
        (uint256 s, uint256 e, bool isList) = RLPReader.nth(body, ls, le, 6);
        if (isList) revert RLPReader.RLPExpectedString();
        return RLPReader.toUint(body, s, e);
    }

    // ---- element i of a list of real transactions, hashed ----

    function rlpListTxHash(bytes calldata d, uint256 i) external pure returns (bytes32) {
        (uint256 s, uint256 e) = RLPReader.list(d);
        (uint256 is_, uint256 ie, ) = RLPReader.nth(d, s, e, i);
        return keccak256(d[is_:ie]);
    }

    function sszListTxHash(bytes calldata d, uint256 i) external pure returns (bytes32) {
        (uint256 s, uint256 e) = SSZReader.variableElement(d, i);
        return keccak256(d[s:e]);
    }

    // ---- committing to a withdrawal ----

    function keccakOfRlp(bytes calldata d) external pure returns (bytes32) {
        return keccak256(d);
    }

    function sha256OfSsz(bytes calldata d) external pure returns (bytes32) {
        return sha256(d);
    }

    /// @dev hash_tree_root(Withdrawal) from its 44 SSZ bytes: four chunks, three hashes.
    function withdrawalRoot(bytes calldata d) external pure returns (bytes32) {
        if (d.length != WITHDRAWAL_SIZE) revert SSZReader.SSZBadLength();
        bytes32 c0 = bytes32(bytes8(d[0:8]));
        bytes32 c1 = bytes32(bytes8(d[8:16]));
        bytes32 c2 = bytes32(bytes20(d[16:36]));
        bytes32 c3 = bytes32(bytes8(d[36:44]));
        return sha256(abi.encodePacked(sha256(abi.encodePacked(c0, c1)), sha256(abi.encodePacked(c2, c3))));
    }
}
