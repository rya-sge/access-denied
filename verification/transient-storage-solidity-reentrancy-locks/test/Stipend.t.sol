// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import "../src/Common.sol";
import "../src/Stipend.sol";

contract StipendTest is Log {
    Payer payer;
    Tx t;

    function setUp() public {
        payer = new Payer();
        t = new Tx();
        VM.deal(address(payer), 1 ether);
    }

    function testTransferRecipientWritesItsOwnTransientStorage() public {
        OwnTransient r = new OwnTransient();
        Tx.Result[] memory o = t.exec(
            two(
                address(payer),
                abi.encodeCall(Payer.payTransfer, (payable(address(r)))),
                address(r),
                abi.encodeWithSignature("seen()")
            )
        );
        require(o[0].ok, "transfer succeeded");
        eq(word(o[1].ret), 1, "recipient wrote TSTORE under the stipend");
    }

    function testTransferRecipientCannotWriteStorage() public {
        OwnStorage r = new OwnStorage();
        (bool ok, ) = payer.paySend(payable(address(r)));
        require(!ok, "SSTORE blocked by the sentry");
        eq(r.seen(), 0, "no write");
    }

    /// The recipient re-enters the payer inside the stipend and changes the payer's state.
    function testStipendCallbackChangesPayerTransientState() public {
        CallsBack r = new CallsBack();
        Tx.Call[] memory c = new Tx.Call[](3);
        c[0] = Tx.Call(address(payer), abi.encodeCall(Payer.payTransfer, (payable(address(r)))));
        c[1] = Tx.Call(address(r), abi.encodeWithSignature("gasAtEntry()"));
        c[2] = Tx.Call(address(r), abi.encodeWithSignature("gasAfter()"));
        Tx.Result[] memory o = t.exec(c);
        require(o[0].ok, "transfer succeeded");
        eq(word(o[0].ret), 1, "payer saw its own flag set during the payment");
        emit log_named_uint("gas in receive at entry", word(o[1].ret));
        emit log_named_uint("gas left after the call back into the payer", word(o[2].ret));
    }

    function testStipendCallbackCannotWritePayerStorage() public {
        CallsBackStorage r = new CallsBackStorage();
        (bool ok, ) = payer.paySend(payable(address(r)));
        require(!ok, "SSTORE in the re-entered frame fails");
        eq(payer.smarked(), 0, "no write");
    }

    /// A transient lock works inside the stipend: the callback hits the guard.
    function testLockStopsTheStipendCallback() public {
        CallsBackQuiet r = new CallsBackQuiet();
        (bool ok, uint256 m) = payer.payGuarded(payable(address(r)));
        require(ok, "send succeeded");
        eq(m, 0, "guard stopped the write");
    }
}
