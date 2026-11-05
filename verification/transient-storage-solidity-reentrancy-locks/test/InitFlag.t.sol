// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import "../src/Common.sol";
import "../src/InitFlag.sol";

contract InitFlagTest is Log {
    Token token;
    LegitBootstrap legit;
    EvilBootstrap evil;
    address constant THIEF = address(0xBAD);

    function setUp() public {
        token = new Token();
        legit = new LegitBootstrap();
        evil = new EvilBootstrap();
    }

    /// Model of the deployed code: the second call passes in the deploying transaction.
    function testUnconsumedFlagIsDrainedInTheDeployingTx() public {
        Impl impl = new Impl(false);
        Attacker a = new Attacker(impl, token, address(legit), address(evil), THIEF);
        eq(token.balanceOf(THIEF), 1_000_000, "swept");
        eq(token.balanceOf(a.account()), 0, "account emptied");
    }

    /// The flag dies with the transaction, so an account deployed earlier is not exposed.
    function testUnconsumedFlagRevertsInALaterTx() public {
        Impl impl = new Impl(false);
        Proxy p = new Proxy(address(impl), address(legit), abi.encodeCall(LegitBootstrap.init, ()));
        token.mint(address(p), 5);
        VM.expectRevert(Init.NotInitializable.selector);
        Impl(address(p)).initializeAccount(address(evil), abi.encodeCall(EvilBootstrap.sweep, (token, THIEF)));
    }

    /// PR #302: the first check consumes the flag, and the attack reverts.
    function testConsumedFlagStopsTheAttack() public {
        Impl impl = new Impl(true);
        VM.expectRevert(Init.NotInitializable.selector);
        new Attacker(impl, token, address(legit), address(evil), THIEF);
    }
}
