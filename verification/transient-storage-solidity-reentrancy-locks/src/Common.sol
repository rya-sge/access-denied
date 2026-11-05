// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

/// Test contracts for an article. Not audited. Do not deploy.

/// Minimal cheatcode interface, so the project needs no forge-std.
interface Vm {
    function deal(address who, uint256 amount) external;
    function prank(address who) external;
    function expectRevert(bytes4 selector) external;
    function expectRevert(bytes calldata reason) external;
}

Vm constant VM = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));

/// One transaction: a test calls `exec` once, and every sub-call shares the same
/// transient storage. Failures are returned, not bubbled.
contract Tx {
    struct Call {
        address to;
        bytes data;
    }

    struct Result {
        bool ok;
        bytes ret;
    }

    function exec(Call[] calldata calls) external payable returns (Result[] memory out) {
        out = new Result[](calls.length);
        for (uint256 i = 0; i < calls.length; i++) {
            (out[i].ok, out[i].ret) = calls[i].to.call(calls[i].data);
        }
    }
}

abstract contract Log {
    bool public constant IS_TEST = true;

    event log_named_uint(string key, uint256 val);
    event log_string(string val);

    function one(address to, bytes memory data) internal pure returns (Tx.Call[] memory c) {
        c = new Tx.Call[](1);
        c[0] = Tx.Call(to, data);
    }

    function two(address a, bytes memory x, address b, bytes memory y) internal pure returns (Tx.Call[] memory c) {
        c = new Tx.Call[](2);
        c[0] = Tx.Call(a, x);
        c[1] = Tx.Call(b, y);
    }

    function eq(uint256 a, uint256 b, string memory what) internal pure {
        require(a == b, what);
    }

    function word(bytes memory b) internal pure returns (uint256) {
        return abi.decode(b, (uint256));
    }
}
