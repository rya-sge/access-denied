// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

/// Test contracts for an article. Not audited. Do not deploy.

/// Raw slot access, so a test controls the key.
contract Raw {
    function tset(uint256 k, uint256 v) external {
        assembly { tstore(k, v) }
    }

    function tget(uint256 k) external view returns (uint256 v) {
        assembly { v := tload(k) }
    }

    function sset(uint256 k, uint256 v) external {
        assembly { sstore(k, v) }
    }

    function sget(uint256 k) external view returns (uint256 v) {
        assembly { v := sload(k) }
    }

    function tsetThenRevert(uint256 k, uint256 v) external {
        assembly {
            tstore(k, v)
            revert(0, 0)
        }
    }
}

/// Frames: write in the outer frame, write in a reverted inner frame, read back.
contract Frames {
    Raw public immutable raw;

    constructor(Raw r) {
        raw = r;
    }

    function inner() external {
        raw.tset(0, 2); // nested call, rolled back with this frame
        raw.tset(1, 7);
        revert("inner");
    }

    function outer() external returns (uint256 slot0, uint256 slot1) {
        raw.tset(0, 1);
        try this.inner() {} catch {}
        slot0 = raw.tget(0);
        slot1 = raw.tget(1);
    }
}

/// Calls Raw's code in its own context.
contract Delegator {
    function viaDelegatecall(address impl, uint256 k, uint256 v) external {
        (bool ok, ) = impl.delegatecall(abi.encodeCall(Raw.tset, (k, v)));
        require(ok);
    }

    function viaCallcode(address impl, uint256 k, uint256 v) external {
        bytes memory d = abi.encodeCall(Raw.tset, (k, v));
        bool ok;
        assembly { ok := callcode(gas(), impl, 0, add(d, 32), mload(d), 0, 0) }
        require(ok);
    }

    function local(uint256 k) external view returns (uint256 v) {
        assembly { v := tload(k) }
    }
}

contract StaticProbe {
    /// A failed TSTORE in a static frame is an exceptional halt: every forwarded gas unit is gone.
    function tryWrite(Raw raw, uint256 forwarded) external view returns (bool ok, uint256 consumed) {
        uint256 before = gasleft();
        (ok, ) = address(raw).staticcall{gas: forwarded}(abi.encodeCall(Raw.tset, (0, 1)));
        consumed = before - gasleft();
    }

    function tryRead(Raw raw) external view returns (bool ok, uint256 v) {
        bytes memory r;
        (ok, r) = address(raw).staticcall(abi.encodeCall(Raw.tget, (0)));
        v = abi.decode(r, (uint256));
    }
}
