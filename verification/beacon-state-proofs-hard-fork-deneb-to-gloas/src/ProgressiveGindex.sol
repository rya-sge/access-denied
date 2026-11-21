// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

// Copied verbatim from the article "When a Merkle Proof Breaks at a Hard Fork: Beacon State
// Proofs from Deneb to Gloas" (section "Derive the length from the gindex", the Gloas function).
// The article prints it as a top-level function, but `internal` is not allowed on a free
// function (solc error 4126, "Free functions cannot have visibility"). It is therefore wrapped
// in a library here; the function itself is unchanged. Only this comment, the SPDX line, the
// pragma and the `library` wrapper were added. Not audited, do not deploy.

library Progressive {
    /// EIP-7916 position of chunk `i` in a progressive tree, root = 1.
    function progressiveGindex(uint256 i) internal pure returns (uint256) {
        uint256 g = 1;
        uint256 start;
        uint256 size = 1;
        while (i >= start + size) {
            g = 2 * g + 1;
            start += size;
            size <<= 2;
        }
        return 2 * g * size + (i - start);
    }
}
