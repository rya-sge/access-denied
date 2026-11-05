// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

/// Test contracts for an article. Not audited. Do not deploy.

/// Pays with `transfer` and `send`, the 2,300 gas stipend. Its own address is warm
/// during the payment, so a recipient can call back for 100 gas plus the callee's code.
contract Payer {
    uint256 public transient marked;
    uint256 public smarked;
    uint256 private transient lock;

    receive() external payable {}

    function payTransfer(address payable to) external returns (uint256) {
        to.transfer(1);
        return marked;
    }

    function paySend(address payable to) external returns (bool ok, uint256 m) {
        ok = to.send(1);
        m = marked;
    }

    function mark() external {
        marked = 1;
    }

    function markStorage() external {
        smarked = 1;
    }

    /// Same payment behind a transient lock: the callback hits the guard and fails.
    function payGuarded(address payable to) external returns (bool ok, uint256 m) {
        require(lock == 0, "locked");
        lock = 1;
        ok = to.send(1);
        m = marked;
        lock = 0;
    }

    function markGuarded() external {
        require(lock == 0, "locked");
        marked = 1;
    }
}

/// `receive` writes the recipient's own transient storage.
contract OwnTransient {
    uint256 public transient seen;

    receive() external payable {
        seen = 1;
    }
}

/// `receive` writes the recipient's own storage: blocked by the EIP-2200 check.
contract OwnStorage {
    uint256 public seen;

    receive() external payable {
        seen = 1;
    }
}

/// `receive` re-enters the payer and reports the gas it had and what was left, in transient storage.
contract CallsBack {
    uint256 public transient gasAtEntry;
    uint256 public transient gasAfter;

    receive() external payable {
        uint256 g = gasleft();
        Payer(payable(msg.sender)).mark();
        uint256 h = gasleft();
        gasAtEntry = g;
        gasAfter = h;
    }
}

contract CallsBackStorage {
    receive() external payable {
        Payer(payable(msg.sender)).markStorage();
    }
}

/// Like CallsBack, but swallows a failure so `send` still succeeds.
contract CallsBackQuiet {
    receive() external payable {
        (bool ok, ) = msg.sender.call(abi.encodeCall(Payer.markGuarded, ()));
        ok;
    }
}
