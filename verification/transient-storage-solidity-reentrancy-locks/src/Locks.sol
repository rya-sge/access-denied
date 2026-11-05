// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

/// Test contracts for an article. Not audited. Do not deploy.
/// Every lock exposes the same functions in the same order, so the dispatcher
/// costs the same and receipts are comparable between locks.

import {ReentrancyGuard} from "./vendor/oz-v5.1.0/ReentrancyGuard.sol";
import {ReentrancyGuardTransient} from "./vendor/oz-v5.1.0/ReentrancyGuardTransient.sol";

abstract contract Work {
    mapping(uint256 => uint256) internal cells;
    address internal constant SINK = address(0xdEaD);

    /// An external call, the thing a lock exists for. An empty body would not do: the legacy
    /// optimizer then removes the first of the two SSTOREs as a dead store, and the storage
    /// lock looks cheaper than it is.
    function _ping() internal {
        (bool ok, ) = SINK.call("");
        require(ok);
    }

    /// Five writes to fresh slots, about 111,000 gas, so the refund cap does not bind.
    function _work(uint256 key) internal {
        for (uint256 i = 0; i < 5; i++) {
            cells[key + i] = 1;
        }
    }
}

/// solc `uint256 transient`, one full word.
contract LockTransientUint is Work {
    uint256 private transient lock;

    modifier nonReentrant() {
        require(lock == 0, "locked");
        lock = 1;
        _;
        lock = 0;
    }

    function guarded() external nonReentrant { _ping(); }
    function guardedWork(uint256 key) external nonReentrant { _work(key); }
    function unguarded() external { _ping(); }
    function unguardedWork(uint256 key) external { _work(key); }
}

/// solc `bool transient`, the example in the Solidity documentation. A write to a packed
/// type reads the slot first, so each write is a TLOAD plus a TSTORE.
contract LockTransientBool is Work {
    bool private transient locked;

    modifier nonReentrant() {
        require(!locked, "locked");
        locked = true;
        _;
        locked = false;
    }

    function guarded() external nonReentrant { _ping(); }
    function guardedWork(uint256 key) external nonReentrant { _work(key); }
    function unguarded() external { _ping(); }
    function unguardedWork(uint256 key) external { _work(key); }
}

/// Inline assembly.
contract LockTransientYul is Work {
    modifier nonReentrant() {
        assembly {
            if tload(0) { revert(0, 0) }
            tstore(0, 1)
        }
        _;
        assembly { tstore(0, 0) }
    }

    function guarded() external nonReentrant { _ping(); }
    function guardedWork(uint256 key) external nonReentrant { _work(key); }
    function unguarded() external { _ping(); }
    function unguardedWork(uint256 key) external { _work(key); }
}

/// OpenZeppelin v5.1.0 ReentrancyGuardTransient, unmodified.
contract LockOZTransient is Work, ReentrancyGuardTransient {
    function guarded() external nonReentrant { _ping(); }
    function guardedWork(uint256 key) external nonReentrant { _work(key); }
    function unguarded() external { _ping(); }
    function unguardedWork(uint256 key) external { _work(key); }
}

/// OpenZeppelin v5.1.0 ReentrancyGuard, unmodified: 1 -> 2 -> 1.
contract LockOZStorage is Work, ReentrancyGuard {
    function guarded() external nonReentrant { _ping(); }
    function guardedWork(uint256 key) external nonReentrant { _work(key); }
    function unguarded() external { _ping(); }
    function unguardedWork(uint256 key) external { _work(key); }
}

/// Zero at rest: false -> true -> false, so the refund is the 19,900 of a restored empty slot.
contract LockStorageBool is Work {
    bool private locked;

    modifier nonReentrant() {
        require(!locked, "locked");
        locked = true;
        _;
        locked = false;
    }

    function guarded() external nonReentrant { _ping(); }
    function guardedWork(uint256 key) external nonReentrant { _work(key); }
    function unguarded() external { _ping(); }
    function unguardedWork(uint256 key) external { _work(key); }
}

/// `n` guarded calls in one transaction.
contract Batcher {
    function run(address target, uint256 n) external {
        for (uint256 i = 0; i < n; i++) {
            (bool ok, ) = target.call(abi.encodeWithSignature("guarded()"));
            require(ok, "batch call failed");
        }
    }
}
