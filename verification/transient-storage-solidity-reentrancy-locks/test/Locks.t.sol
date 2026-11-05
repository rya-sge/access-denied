// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import "../src/Common.sol";
import "../src/Locks.sol";

interface ILock {
    function guarded() external;
}


/// Each lock blocks a nested call, and allows a second call after a successful return.
contract GuardProbe {
    uint256 private transient lock;
    uint256 public entered;

    function outer(address to) external returns (bool innerOk) {
        require(lock == 0, "locked");
        lock = 1;
        (innerOk, ) = address(this).call(abi.encodeCall(this.inner, ()));
        to;
        lock = 0;
    }

    function inner() external {
        require(lock == 0, "locked");
        entered += 1;
    }
}

contract LocksTest is Log {
    function testAllLocksAcceptTwoCallsInOneTx() public {
        address[6] memory locks = [
            address(new LockTransientUint()),
            address(new LockTransientBool()),
            address(new LockTransientYul()),
            address(new LockOZTransient()),
            address(new LockOZStorage()),
            address(new LockStorageBool())
        ];
        Batcher b = new Batcher();
        for (uint256 i = 0; i < locks.length; i++) {
            b.run(locks[i], 2);
        }
    }

    function testNestedCallIsBlocked() public {
        GuardProbe p = new GuardProbe();
        bool innerOk = p.outer(address(0));
        require(!innerOk, "nested call must fail");
        eq(p.entered(), 0, "nothing entered");
    }
}
