// SPDX-License-Identifier: MIT
pragma solidity >=0.8.28;

import "../src/Collision.sol";

contract CollisionTest {
    bool public constant IS_TEST = true;

    event log_named_uint(string key, uint256 val);

    function testOutcomes() public {
        (uint256 s, uint256 t) = new PersistentFirst().run();
        emit log_named_uint("PersistentFirst s", s);
        emit log_named_uint("PersistentFirst t", t);
        (s, t) = new TransientFirst().run();
        emit log_named_uint("TransientFirst s", s);
        emit log_named_uint("TransientFirst t", t);
        GuardedVault v = new GuardedVault();
        v.close(address(1));
        emit log_named_uint("GuardedVault owner intact", v.owner() == address(this) ? 1 : 0);
        (bool ok, ) = address(new GuardedVault()).call(abi.encodeCall(GuardedVault.closeTwice, (address(1))));
        emit log_named_uint("GuardedVault second close ok", ok ? 1 : 0);
    }

    function testPersistentFirstCorrect() public {
        (uint256 s, uint256 t) = new PersistentFirst().run();
        require(s == 0 && t == 0, "wrong location cleared");
    }

    function testTransientFirstCorrect() public {
        (uint256 s, uint256 t) = new TransientFirst().run();
        require(s == 0 && t == 0, "wrong location cleared");
    }

    function testLockedOwnerIntact() public {
        GuardedVault v = new GuardedVault();
        v.close(address(1));
        require(v.owner() == address(this), "owner zeroed by delete lock");
    }

    function testLockReleased() public {
        new GuardedVault().closeTwice(address(1));
    }

    /// Passes on every profile, 0.8.33 via-IR included: the workaround.
    function testAssignmentAvoidsTheBug() public {
        AssignedVault v = new AssignedVault();
        v.closeTwice(address(1));
        require(v.owner() == address(this), "owner zeroed");
        require(v.credit(address(1)) == 0, "credit not cleared");
    }
}
