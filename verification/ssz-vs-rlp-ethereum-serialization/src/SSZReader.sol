// SPDX-License-Identifier: MIT
pragma solidity 0.8.30;

/// @notice SSZ reads over calldata. Test code: not audited, do not deploy.
library SSZReader {
    error SSZOutOfBounds();
    error SSZBadLength();
    error SSZBadOffset();

    /// @dev Little-endian uint64 at `off`: eight bytes, swapped into EVM order.
    function u64(bytes calldata d, uint256 off) internal pure returns (uint64 v) {
        if (off + 8 > d.length) revert SSZOutOfBounds();
        uint256 x;
        assembly ("memory-safe") {
            x := shr(192, calldataload(add(d.offset, off)))
        }
        x = ((x & 0x00ff00ff00ff00ff) << 8) | ((x >> 8) & 0x00ff00ff00ff00ff);
        x = ((x & 0x0000ffff0000ffff) << 16) | ((x >> 16) & 0x0000ffff0000ffff);
        v = uint64((x << 32) | (x >> 32));
    }

    /// @dev Little-endian uint32 at `off`, as used by offsets.
    function u32(bytes calldata d, uint256 off) internal pure returns (uint32 v) {
        if (off + 4 > d.length) revert SSZOutOfBounds();
        uint256 x;
        assembly ("memory-safe") {
            x := shr(224, calldataload(add(d.offset, off)))
        }
        x = ((x & 0x00ff00ff) << 8) | ((x >> 8) & 0x00ff00ff);
        v = uint32((x << 16) | (x >> 16));
    }

    /// @dev Little-endian uint256 at `off`.
    function u256(bytes calldata d, uint256 off) internal pure returns (uint256 v) {
        if (off + 32 > d.length) revert SSZOutOfBounds();
        v = swap256(_load(d, off));
    }

    function _load(bytes calldata d, uint256 off) private pure returns (uint256 x) {
        assembly ("memory-safe") {
            x := calldataload(add(d.offset, off))
        }
    }

    function swap256(uint256 x) internal pure returns (uint256) {
        uint256 m = 0x00ff00ff00ff00ff00ff00ff00ff00ff00ff00ff00ff00ff00ff00ff00ff00ff;
        x = ((x & m) << 8) | ((x >> 8) & m);
        m = 0x0000ffff0000ffff0000ffff0000ffff0000ffff0000ffff0000ffff0000ffff;
        x = ((x & m) << 16) | ((x >> 16) & m);
        m = 0x00000000ffffffff00000000ffffffff00000000ffffffff00000000ffffffff;
        x = ((x & m) << 32) | ((x >> 32) & m);
        m = 0x0000000000000000ffffffffffffffff0000000000000000ffffffffffffffff;
        x = ((x & m) << 64) | ((x >> 64) & m);
        return (x << 128) | (x >> 128);
    }

    /// @dev Bounds of element `i` of a list of variable-size elements, in O(1).
    function variableElement(bytes calldata d, uint256 i) internal pure returns (uint256 s, uint256 e) {
        uint256 first = u32(d, 0);
        if (first == 0 || first % 4 != 0 || first > d.length) revert SSZBadOffset();
        uint256 n = first / 4;
        if (i >= n) revert SSZOutOfBounds();
        s = u32(d, i * 4);
        e = i + 1 == n ? d.length : u32(d, (i + 1) * 4);
        if (s > e || e > d.length) revert SSZBadOffset();
    }
}
