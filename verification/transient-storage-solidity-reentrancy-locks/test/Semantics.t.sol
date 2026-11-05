// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import "../src/Common.sol";
import "../src/Semantics.sol";

contract SemanticsTest is Log {
    Raw raw;
    Raw other;
    Tx t;

    function setUp() public {
        raw = new Raw();
        other = new Raw();
        t = new Tx();
    }

    /// Value visible to a later call of the same transaction, gone in the next one.
    function testScopeIsTheTransaction() public {
        Tx.Result[] memory r = t.exec(
            two(address(raw), abi.encodeCall(Raw.tset, (0, 42)), address(raw), abi.encodeCall(Raw.tget, (0)))
        );
        eq(word(r[1].ret), 42, "same tx");
        eq(raw.tget(0), 0, "next tx"); // a separate transaction because of `isolate`
    }

    function testIsolatedPerContractAndFromStorage() public {
        t.exec(two(address(raw), abi.encodeCall(Raw.tset, (0, 1)), address(raw), abi.encodeCall(Raw.sset, (0, 9))));
        eq(raw.sget(0), 9, "storage slot 0 untouched by TSTORE");
        Tx.Result[] memory r = t.exec(
            two(address(raw), abi.encodeCall(Raw.tset, (5, 7)), address(other), abi.encodeCall(Raw.tget, (5)))
        );
        eq(word(r[1].ret), 0, "other contract reads its own space");
    }

    /// The EIP's rollback: the whole frame, inner calls included, and nothing else.
    function testRevertedFrameRollsBackNestedWrites() public {
        Frames f = new Frames(raw);
        (uint256 a, uint256 b) = f.outer();
        eq(a, 1, "outer write kept, inner write rolled back");
        eq(b, 0, "write of a nested call rolled back");
    }

    function testSuccessfulReturnKeepsTheValue() public {
        Tx.Result[] memory r = t.exec(
            two(address(raw), abi.encodeCall(Raw.tset, (3, 1)), address(raw), abi.encodeCall(Raw.tget, (3)))
        );
        eq(word(r[1].ret), 1, "survives RETURN");
    }

    function testRevertRestoresThePreviousValueNotZero() public {
        Tx.Call[] memory c = new Tx.Call[](3);
        c[0] = Tx.Call(address(raw), abi.encodeCall(Raw.tset, (0, 5)));
        c[1] = Tx.Call(address(raw), abi.encodeCall(Raw.tsetThenRevert, (0, 6)));
        c[2] = Tx.Call(address(raw), abi.encodeCall(Raw.tget, (0)));
        Tx.Result[] memory r = t.exec(c);
        require(!r[1].ok, "second call reverted");
        eq(word(r[2].ret), 5, "restored to 5");
    }

    /// DELEGATECALL and CALLCODE: the caller's space, the implementation stays empty.
    function testDelegatecallAndCallcodeUseTheCallerSpace() public {
        Delegator d = new Delegator();
        Tx.Call[] memory c = new Tx.Call[](4);
        c[0] = Tx.Call(address(d), abi.encodeCall(Delegator.viaDelegatecall, (address(raw), 1, 11)));
        c[1] = Tx.Call(address(d), abi.encodeCall(Delegator.viaCallcode, (address(raw), 2, 22)));
        c[2] = Tx.Call(address(d), abi.encodeCall(Delegator.local, (1)));
        c[3] = Tx.Call(address(raw), abi.encodeCall(Raw.tget, (1)));
        Tx.Result[] memory r = t.exec(c);
        eq(word(r[2].ret), 11, "delegatecall wrote the caller");
        eq(word(r[3].ret), 0, "implementation untouched");
    }

    /// TSTORE in a static frame fails and burns what was forwarded; TLOAD works.
    function testStaticContext() public {
        StaticProbe p = new StaticProbe();
        (bool ok, uint256 consumed) = p.tryWrite(raw, 50_000);
        require(!ok, "TSTORE must fail");
        emit log_named_uint("gas consumed by a failed static TSTORE, 50000 forwarded", consumed);
        require(consumed >= 50_000, "all forwarded gas consumed");
        (bool ok2, uint256 v) = p.tryRead(raw);
        require(ok2 && v == 0, "TLOAD allowed");
    }
}
