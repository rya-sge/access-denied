// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import "../src/Common.sol";
import "../src/Failures.sol";

contract FailuresTest is Log {
    Tx t;

    function setUp() public {
        t = new Tx();
    }

    function testLeakyLockBreaksBatchNotSingleCalls() public {
        LeakyLock l = new LeakyLock();
        l.hit();
        l.hit(); // two transactions: fine
        eq(l.hits(), 2, "separate transactions");
        bytes memory d = abi.encodeCall(LeakyLock.hit, ());
        Tx.Result[] memory r = t.exec(two(address(l), d, address(l), d));
        require(r[0].ok, "first call passes");
        require(!r[1].ok, "second call of the batch fails");
        eq(l.hits(), 3, "only the first batched call counted");
    }

    function testAssemblyReturnSkipsTheReset() public {
        AssemblyExit a = new AssemblyExit();
        bytes memory p = abi.encodeCall(AssemblyExit.plain, ());

        Tx.Result[] memory r = t.exec(two(address(a), abi.encodeCall(AssemblyExit.solidityReturn, ()), address(a), p));
        require(r[1].ok, "Solidity return runs the reset");

        r = t.exec(two(address(a), abi.encodeCall(AssemblyExit.assemblyReturn, ()), address(a), p));
        require(r[0].ok, "assembly return succeeds");
        require(!r[1].ok, "lock left set for the rest of the transaction");

        r = t.exec(two(address(a), abi.encodeCall(AssemblyExit.reverts, ()), address(a), p));
        require(!r[0].ok, "reverted");
        require(r[1].ok, "the revert rolled the lock back");
    }

    function testFlashFlagLeftOpen() public {
        FlashLender l = new FlashLender(false);
        HonestBorrower b = new HonestBorrower();
        Stranger s = new Stranger();
        Tx.Result[] memory r = t.exec(
            two(
                address(l),
                abi.encodeCall(FlashLender.flashLoan, (b)),
                address(s),
                abi.encodeCall(Stranger.attack, (l))
            )
        );
        require(r[0].ok && r[1].ok, "stranger entered after the callback ended");
        eq(l.settled(), 1, "settled");
        VM.expectRevert(abi.encodeWithSignature("Error(string)", "not in callback"));
        s.attack(l); // a later transaction: flag gone
    }

    function testFlashFlagCleared() public {
        FlashLender l = new FlashLender(true);
        HonestBorrower b = new HonestBorrower();
        Stranger s = new Stranger();
        Tx.Result[] memory r = t.exec(
            two(
                address(l),
                abi.encodeCall(FlashLender.flashLoan, (b)),
                address(s),
                abi.encodeCall(Stranger.attack, (l))
            )
        );
        require(r[0].ok && !r[1].ok, "stranger refused");
    }

    function _bundle(bool clear) internal returns (SharedModule m, Account a, Account b, bool[] memory oks) {
        m = new SharedModule();
        a = new Account();
        b = new Account();
        MiniBundler bundler = new MiniBundler();
        MiniBundler.Op[] memory ops = new MiniBundler.Op[](clear ? 4 : 3);
        uint256 i = 0;
        ops[i++] = MiniBundler.Op(a, address(m), abi.encodeCall(SharedModule.begin, (100)));
        ops[i++] = MiniBundler.Op(a, address(m), abi.encodeCall(SharedModule.spend, (40)));
        if (clear) {
            ops[i++] = MiniBundler.Op(a, address(m), abi.encodeCall(SharedModule.end, ()));
        }
        ops[i++] = MiniBundler.Op(b, address(m), abi.encodeCall(SharedModule.spend, (60)));
        oks = bundler.handleOps(ops);
    }

    function testBundleResidueIsSpentByAnotherSender() public {
        (SharedModule m, , Account b, bool[] memory oks) = _bundle(false);
        require(oks[2], "unrelated sender spent the residue");
        eq(m.spent(address(b)), 60, "sender B spent budget that A set");
    }

    function testBundleClearedBudget() public {
        (SharedModule m, , Account b, bool[] memory oks) = _bundle(true);
        require(!oks[3], "B refused");
        eq(m.spent(address(b)), 0, "nothing spent");
    }
}
