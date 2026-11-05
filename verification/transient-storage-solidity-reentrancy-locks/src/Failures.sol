// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

/// Test contracts for an article. Not audited. Do not deploy.

/// A lock whose reset was dropped to save 100 gas.
contract LeakyLock {
    uint256 private transient lock;
    uint256 public hits;

    modifier nonReentrant() {
        require(lock == 0, "locked");
        lock = 1;
        _;
    }

    function hit() external nonReentrant {
        hits += 1;
    }
}

/// The reset is correct, but one path leaves the frame without reaching it.
contract AssemblyExit {
    uint256 private transient lock;

    modifier nonReentrant() {
        require(lock == 0, "locked");
        lock = 1;
        _;
        lock = 0;
    }

    function plain() external nonReentrant {}

    /// Solidity `return` still runs the code after `_`.
    function solidityReturn() external nonReentrant returns (uint256) {
        return 1;
    }

    /// The opcode ends the frame, and the code after `_` never runs.
    function assemblyReturn() external nonReentrant {
        assembly {
            mstore(0, 1)
            return(0, 32)
        }
    }

    /// A revert rolls the lock back, so no reset is needed on that path.
    function reverts() external nonReentrant {
        revert("no");
    }
}

interface IBorrower {
    function onFlashLoan() external;
}

/// `settle` must only run inside a flash-loan callback, checked by a transient flag.
contract FlashLender {
    bool private transient inCallback;
    bool public immutable clears;
    uint256 public settled;

    constructor(bool clears_) {
        clears = clears_;
    }

    function flashLoan(IBorrower b) external {
        inCallback = true;
        b.onFlashLoan();
        if (clears) {
            inCallback = false;
        }
    }

    function settle() external {
        require(inCallback, "not in callback");
        settled += 1;
    }
}

contract HonestBorrower is IBorrower {
    function onFlashLoan() external {}
}

contract Stranger {
    function attack(FlashLender l) external {
        l.settle();
    }
}

/// A shared module: one transient budget, not keyed by account.
contract SharedModule {
    uint256 public transient budget;
    mapping(address => uint256) public spent;

    function begin(uint256 amount) external {
        budget = amount;
    }

    function spend(uint256 amount) external {
        budget -= amount;
        spent[msg.sender] += amount;
    }

    /// The fix ERC-4337 asks for: clear at the end of the operation.
    function end() external {
        budget = 0;
    }
}

contract Account {
    function execute(address to, bytes calldata data) external {
        (bool ok, bytes memory ret) = to.call(data);
        if (!ok) {
            assembly { revert(add(ret, 32), mload(ret)) }
        }
    }
}

/// Stand-in for EntryPoint.handleOps: unrelated senders, one transaction. Not the real EntryPoint.
contract MiniBundler {
    struct Op {
        Account sender;
        address to;
        bytes data;
    }

    event OpResult(uint256 index, bool ok);

    function handleOps(Op[] calldata ops) external returns (bool[] memory oks) {
        oks = new bool[](ops.length);
        for (uint256 i = 0; i < ops.length; i++) {
            (oks[i], ) = address(ops[i].sender).call(abi.encodeCall(Account.execute, (ops[i].to, ops[i].data)));
            emit OpResult(i, oks[i]);
        }
    }
}
