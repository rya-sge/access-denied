// SPDX-License-Identifier: MIT
pragma solidity >=0.8.28;

/// Test contracts for an article. Not audited. Do not deploy.

contract PersistentFirst {
    uint256 public s = 1;
    uint256 transient t;

    function run() external returns (uint256, uint256) {
        t = 1;
        delete s;
        delete t;
        return (s, t);
    }
}

contract TransientFirst {
    uint256 public s = 1;
    uint256 transient t;

    function run() external returns (uint256, uint256) {
        t = 1;
        delete t;
        delete s;
        return (s, t);
    }
}

/// A reentrancy lock released with `delete`, next to a persistent clear.
/// `close` reaches the persistent `delete` before the transient one.
contract GuardedVault {
    address public owner = msg.sender;
    mapping(address => uint256) public credit;
    uint256 transient lock;

    constructor() {
        credit[address(1)] = 5;
    }

    function close(address who) external {
        require(lock == 0, "locked");
        lock = 1;
        delete credit[who];
        delete lock;
    }

    function closeTwice(address who) external {
        this.close(who);
        this.close(who);
    }
}

/// Same contract with `lock = 0`: no `delete` on the transient variable, so no trigger.
contract AssignedVault {
    address public owner = msg.sender;
    mapping(address => uint256) public credit;
    uint256 transient lock;

    constructor() {
        credit[address(1)] = 5;
    }

    function close(address who) external {
        require(lock == 0, "locked");
        lock = 1;
        delete credit[who];
        lock = 0;
    }

    function closeTwice(address who) external {
        this.close(who);
        this.close(who);
    }
}
