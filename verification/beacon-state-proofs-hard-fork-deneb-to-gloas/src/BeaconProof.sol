// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

// Copied verbatim from the article "When a Merkle Proof Breaks at a Hard Fork: Beacon State
// Proofs from Deneb to Gloas" (_posts/2026-11-04-beacon-state-proofs-hard-fork-deneb-to-gloas.md,
// section "Derive the length from the gindex"). Only this comment, the SPDX line and the
// pragma were added. Reference code for discussion: not audited, do not deploy.

library BeaconProof {
    address internal constant BEACON_ROOTS = 0x000F3df6D732807Ef1319fB7B8bB8522d0Beac02;

    uint64 internal constant ELECTRA_SLOT = 11_649_024; // 364032 * 32

    uint256 internal constant SLOT_GINDEX = 8; // BeaconBlockHeader.slot
    uint256 internal constant VALIDATORS_DENEB = 363; // concat(11, 43)
    uint256 internal constant VALIDATORS_ELECTRA = 715; // concat(11, 75), Fulu included

    error NoRoot();
    error BadProofLength();
    error BadProof();
    error IndexTooLarge();

    /// Reverts when 4788 has no root for `timestamp`.
    function blockRoot(uint256 timestamp) internal view returns (bytes32 root) {
        (bool ok, bytes memory ret) = BEACON_ROOTS.staticcall(abi.encode(timestamp));
        if (!ok || ret.length != 32) revert NoRoot();
        root = abi.decode(ret, (bytes32));
        if (root == bytes32(0)) revert NoRoot();
    }

    /// The gindex fixes the number of steps. The caller cannot choose the depth.
    function verify(bytes32 root, bytes32 leaf, bytes32[] calldata proof, uint256 gindex) internal view {
        if (gindex < 2) revert BadProofLength();
        bytes32 node = leaf;
        uint256 i;
        for (uint256 g = gindex; g > 1; g >>= 1) {
            if (i == proof.length) revert BadProofLength();
            bytes32 sibling = proof[i++];
            node = g & 1 == 1 ? sha256(abi.encodePacked(sibling, node)) : sha256(abi.encodePacked(node, sibling));
        }
        if (i != proof.length) revert BadProofLength();
        if (node != root) revert BadProof();
    }

    /// concat(validators, 2, 2**40 + index, 8 + field), for a header proven at `headerSlot`.
    function validatorFieldGindex(uint64 headerSlot, uint256 index, uint256 field) internal pure returns (uint256) {
        if (index >= 1 << 40 || field >= 8) revert IndexTooLarge();
        uint256 base = headerSlot < ELECTRA_SLOT ? VALIDATORS_DENEB : VALIDATORS_ELECTRA;
        return (((base << 41) | index) << 3) | field;
    }
}
