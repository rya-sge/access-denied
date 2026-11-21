// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

/// Tests of the article's verifier (src/BeaconProof.sol, copied verbatim). Test code only:
/// not audited, do not deploy. The real proof comes from snapshot.json, written by
/// mainnet_state.py on a fresh finalized mainnet state (not the article's slot 15,580,064).

import "../src/BeaconProof.sol";
import "../src/ProgressiveGindex.sol";

/// Minimal cheatcode interface, so the project needs no forge-std.
interface Vm {
    function readFile(string calldata path) external view returns (string memory);
    function parseJsonBytes32(string calldata json, string calldata key) external pure returns (bytes32);
    function parseJsonBytes32Array(string calldata json, string calldata key) external pure returns (bytes32[] memory);
    function parseJsonUint(string calldata json, string calldata key) external pure returns (uint256);
    function envOr(string calldata name, string calldata defaultValue) external view returns (string memory);
    function createSelectFork(string calldata url) external returns (uint256);
    function expectRevert(bytes4 selector) external;
}

Vm constant VM = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));

/// External entry points around the internal library functions, so the gas report can
/// measure them. Written for these tests; not part of the article.
contract Harness {
    function verify(bytes32 root, bytes32 leaf, bytes32[] calldata proof, uint256 gindex) external view {
        BeaconProof.verify(root, leaf, proof, gindex);
    }

    function validatorFieldGindex(uint64 headerSlot, uint256 index, uint256 field) external pure returns (uint256) {
        return BeaconProof.validatorFieldGindex(headerSlot, index, field);
    }

    function blockRoot(uint256 timestamp) external view returns (bytes32) {
        return BeaconProof.blockRoot(timestamp);
    }

    /// The flow of the article's sequence diagram: 4788 read, slot proof at gindex 8,
    /// layout selected from the proven slot, field proof.
    function verifyWithdrawalCredentials(
        uint256 timestamp,
        uint64 slot,
        bytes32[] calldata slotProof,
        uint256 index,
        bytes32 credentials,
        bytes32[] calldata proof
    ) external view {
        bytes32 root = BeaconProof.blockRoot(timestamp);
        BeaconProof.verify(root, le64(slot), slotProof, BeaconProof.SLOT_GINDEX);
        BeaconProof.verify(root, credentials, proof, BeaconProof.validatorFieldGindex(slot, index, 1));
    }

    function progressiveGindex(uint256 i) external pure returns (uint256) {
        return Progressive.progressiveGindex(i);
    }

    /// SSZ uint64 leaf: little-endian, right-padded with zeros.
    function le64(uint64 v) public pure returns (bytes32 out) {
        uint256 r;
        for (uint256 k = 0; k < 8; k++) {
            r |= uint256((v >> (8 * k)) & 0xff) << (8 * (31 - k));
        }
        out = bytes32(r);
    }
}

contract BeaconProofTest {
    bool public constant IS_TEST = true;

    event log_named_uint(string key, uint256 val);
    event log_named_bytes32(string key, bytes32 val);
    event log_string(string val);

    uint256 constant G_WC_1M_FULU = 12_578_413_029_757_441;
    uint256 constant G_WC_1M_DENEB = 6_385_963_542_123_009;
    uint256 constant G_WC_0_FULU = 12_578_413_021_757_441;
    uint256 constant G_WC_0_DENEB = 6_385_963_534_123_009;

    Harness h;
    string json;
    bytes32 root;
    bytes32 leaf;
    bytes32[] branch;
    uint64 slot;

    function setUp() public {
        h = new Harness();
        json = VM.readFile("snapshot.json");
        root = VM.parseJsonBytes32(json, ".block_root");
        leaf = VM.parseJsonBytes32(json, ".proof.leaf");
        branch = VM.parseJsonBytes32Array(json, ".proof.branch");
        slot = uint64(VM.parseJsonUint(json, ".header.slot"));
    }

    function eq(uint256 a, uint256 b, string memory what) internal pure {
        require(a == b, what);
    }

    function prefix(bytes32[] memory p, uint256 n) internal pure returns (bytes32[] memory out) {
        out = new bytes32[](n);
        for (uint256 i = 0; i < n; i++) out[i] = p[i];
    }

    function concat(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 d;
        while ((b >> (d + 1)) != 0) d++;
        return (a << d) | (b - (1 << d));
    }

    function depth(uint256 g) internal pure returns (uint256 d) {
        while ((g >> (d + 1)) != 0) d++;
    }

    // ---------------------------------------------------------------- real proof

    function testRealProofVerifies() public {
        eq(branch.length, 53, "53 siblings");
        uint256 g = h.validatorFieldGindex(slot, 1_000_000, 1);
        eq(g, G_WC_1M_FULU, "gindex 12,578,413,029,757,441");
        uint256 g0 = gasleft();
        h.verify(root, leaf, branch, g);
        emit log_named_uint("gas, external verify of the 53-sibling proof (incl. call overhead)", g0 - gasleft());
        emit log_named_uint("header slot", slot);
        emit log_named_bytes32("block root", root);
    }

    function testRevertWhen_Truncated52() public {
        bytes32[] memory p = prefix(branch, 52);
        VM.expectRevert(BeaconProof.BadProofLength.selector);
        h.verify(root, leaf, p, G_WC_1M_FULU);
    }

    function testRevertWhen_Extended54() public {
        bytes32[] memory p = new bytes32[](54);
        for (uint256 i = 0; i < 53; i++) p[i] = branch[i];
        VM.expectRevert(BeaconProof.BadProofLength.selector);
        h.verify(root, leaf, p, G_WC_1M_FULU);
    }

    function testRevertWhen_EmptyProofLeafEqualsRoot() public {
        bytes32[] memory p = new bytes32[](0);
        VM.expectRevert(BeaconProof.BadProofLength.selector);
        h.verify(root, root, p, G_WC_1M_FULU);
        VM.expectRevert(BeaconProof.BadProofLength.selector);
        h.verify(root, root, p, 1);
        VM.expectRevert(BeaconProof.BadProofLength.selector);
        h.verify(root, root, p, BeaconProof.SLOT_GINDEX);
    }

    function testRevertWhen_WrongLeaf() public {
        VM.expectRevert(BeaconProof.BadProof.selector);
        h.verify(root, bytes32(uint256(leaf) ^ 1), branch, G_WC_1M_FULU);
    }

    function testSlotProofAtGindex8() public view {
        bytes32[] memory sp = VM.parseJsonBytes32Array(json, ".slot_proof.branch");
        eq(sp.length, 3, "3 siblings");
        h.verify(root, h.le64(slot), sp, BeaconProof.SLOT_GINDEX);
    }

    function testBalanceProof48() public view {
        bytes32[] memory bp = VM.parseJsonBytes32Array(json, ".balance_proof.branch");
        eq(bp.length, 48, "48 siblings");
        uint256 g = concat(concat(concat(11, 76), 2), (1 << 38) + 250_000);
        eq(g, 393_625_162_993_808, "balance gindex");
        h.verify(root, VM.parseJsonBytes32(json, ".balance_proof.chunk"), bp, g);
    }

    // ---------------------------------------------------------------- Deneb / Electra gindices

    function testDenebAndElectraGindices() public view {
        uint64 electra = BeaconProof.ELECTRA_SLOT;
        eq(electra, 364_032 * 32, "ELECTRA_SLOT");
        eq(h.validatorFieldGindex(electra - 1, 1_000_000, 1), G_WC_1M_DENEB, "Deneb 1e6");
        eq(h.validatorFieldGindex(electra, 1_000_000, 1), G_WC_1M_FULU, "Electra 1e6");
        eq(h.validatorFieldGindex(electra - 1, 0, 1), G_WC_0_DENEB, "Deneb 0");
        eq(h.validatorFieldGindex(electra, 0, 1), G_WC_0_FULU, "Electra 0");
        eq(depth(G_WC_1M_DENEB), 52, "Deneb proof length 52");
        eq(depth(G_WC_1M_FULU), 53, "Electra proof length 53");
        // The library constants are concat(11, 43) and concat(11, 75).
        eq(BeaconProof.VALIDATORS_DENEB, concat(11, 43), "363");
        eq(BeaconProof.VALIDATORS_ELECTRA, concat(11, 75), "715");
        eq(concat(concat(concat(concat(11, 75), 2), (1 << 40) + 1_000_000), 9), G_WC_1M_FULU, "concat chain");
        // First Electra block: execution block 22,431,084 stores the root of slot 11,649,023,
        // so a proof from it must take the Deneb path (base 363), not 715.
        eq(h.validatorFieldGindex(11_649_023, 1_000_000, 1) >> 44, 363, "slot 11,649,023 -> 363");
        eq(h.validatorFieldGindex(11_649_024, 1_000_000, 1) >> 44, 715, "slot 11,649,024 -> 715");
    }

    function testRevertWhen_DenebGindexOnFuluProof() public {
        // A stale Deneb gindex with the 53 Fulu siblings: wrong length.
        VM.expectRevert(BeaconProof.BadProofLength.selector);
        h.verify(root, leaf, branch, G_WC_1M_DENEB);
    }

    function testRevertWhen_DenebGindexWith52Siblings() public {
        // Right length for Deneb, but the path goes elsewhere in the Fulu tree.
        bytes32[] memory p = prefix(branch, 52);
        VM.expectRevert(BeaconProof.BadProof.selector);
        h.verify(root, leaf, p, G_WC_1M_DENEB);
    }

    function testRevertWhen_IndexTooLarge() public {
        VM.expectRevert(BeaconProof.IndexTooLarge.selector);
        h.validatorFieldGindex(slot, 1 << 40, 1);
    }

    function testRevertWhen_FieldTooLarge() public {
        VM.expectRevert(BeaconProof.IndexTooLarge.selector);
        h.validatorFieldGindex(slot, 0, 8);
    }

    // ---------------------------------------------------------------- Gloas arithmetic (draft)

    function testGloasProgressiveGindices() public view {
        // validators at Gloas state gindex 358, so 2918 from the block root; balances 359 / 2919.
        eq(concat(11, 358), 2918, "2918");
        uint256 g0 = concat(concat(concat(2918, 2), h.progressiveGindex(0)), 9);
        uint256 g1m = concat(concat(concat(2918, 2), h.progressiveGindex(1_000_000)), 9);
        uint256 gLast = concat(concat(concat(2918, 2), h.progressiveGindex(2_398_407)), 9);
        eq(g0, 93_377, "validator 0 = 93377");
        eq(depth(g0), 16, "length 16");
        eq(g1m, 100_278_884_853_593, "validator 1e6 = 100278884853593");
        eq(depth(g1m), 46, "length 46");
        eq(depth(gLast), 49, "validator 2,398,407 length 49");
        // The article's balance chunk gindex 1,567,394,265,915 is the chunk itself (no field step).
        eq(concat(concat(2919, 2), h.progressiveGindex(250_000)), 1_567_394_265_915, "balance chunk");
        eq(depth(1_567_394_265_915), 40, "balance length 40");
    }

    // ---------------------------------------------------------------- forked mainnet

    /// Runs only with FORK_URL set, and only while the snapshot root is in the 4788 buffer.
    function testForkFullFlow() public {
        string memory url = VM.envOr("FORK_URL", string(""));
        if (bytes(url).length == 0) {
            emit log_string("FORK_URL not set: fork test skipped");
            return;
        }
        VM.createSelectFork(url);
        Harness fh = new Harness();
        uint256 ts = VM.parseJsonUint(json, ".eip4788.timestamp");
        bytes32[] memory sp = VM.parseJsonBytes32Array(json, ".slot_proof.branch");
        emit log_named_uint("fork block", block.number);
        emit log_named_uint("4788 timestamp", ts);
        // Full flow first, so the 4788 account and its storage are cold, as in a real transaction.
        fh.verifyWithdrawalCredentials(ts, slot, sp, 1_000_000, leaf, branch);
        require(fh.blockRoot(ts) == root, "4788 root != snapshot block root");
        VM.expectRevert(BeaconProof.NoRoot.selector);
        fh.blockRoot(ts + 1);
    }
}
