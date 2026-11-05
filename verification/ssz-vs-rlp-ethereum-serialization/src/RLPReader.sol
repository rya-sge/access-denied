// SPDX-License-Identifier: MIT
pragma solidity 0.8.30;

/// @notice Strict RLP reader over calldata. Test code: not audited, do not deploy.
library RLPReader {
    error RLPTruncated();
    error RLPNonCanonical();
    error RLPExpectedList();
    error RLPExpectedString();
    error RLPTrailingBytes();
    error RLPFieldMissing();
    error RLPIntegerTooLong();

    /// @dev Header of the item at `p`, bounded by `limit`. Returns the payload range.
    function header(bytes calldata d, uint256 p, uint256 limit)
        internal
        pure
        returns (uint256 start, uint256 end, bool isList)
    {
        if (p >= limit) revert RLPTruncated();
        uint256 b0 = uint8(d[p]);
        if (b0 < 0x80) return (p, p + 1, false);
        if (b0 <= 0xb7) {
            start = p + 1;
            end = start + (b0 - 0x80);
            if (end > limit) revert RLPTruncated();
            if (b0 == 0x81 && uint8(d[start]) < 0x80) revert RLPNonCanonical();
            return (start, end, false);
        }
        if (b0 >= 0xc0 && b0 <= 0xf7) {
            start = p + 1;
            end = start + (b0 - 0xc0);
            if (end > limit) revert RLPTruncated();
            return (start, end, true);
        }
        isList = b0 > 0xbf;
        uint256 ll = b0 - (isList ? 0xf7 : 0xb7);
        start = p + 1 + ll;
        if (start > limit) revert RLPTruncated();
        if (d[p + 1] == 0) revert RLPNonCanonical();
        uint256 n;
        for (uint256 i = p + 1; i < start; ++i) {
            n = (n << 8) | uint8(d[i]);
        }
        if (n < 56) revert RLPNonCanonical();
        end = start + n;
        if (end > limit) revert RLPTruncated();
    }

    /// @dev Payload range of the single outer list, which must span all of `d`.
    function list(bytes calldata d) internal pure returns (uint256 start, uint256 end) {
        bool isList;
        (start, end, isList) = header(d, 0, d.length);
        if (!isList) revert RLPExpectedList();
        if (end != d.length) revert RLPTrailingBytes();
    }

    /// @dev Walks to item `k` of the list payload [s, e). Cost grows with k.
    function nth(bytes calldata d, uint256 s, uint256 e, uint256 k)
        internal
        pure
        returns (uint256 start, uint256 end, bool isList)
    {
        uint256 p = s;
        for (uint256 i = 0;; ++i) {
            if (p >= e) revert RLPFieldMissing();
            (start, end, isList) = header(d, p, e);
            if (i == k) return (start, end, isList);
            p = end;
        }
    }

    /// @dev The schema step: a string read as a canonical big-endian integer.
    function toUint(bytes calldata d, uint256 s, uint256 e) internal pure returns (uint256 v) {
        uint256 n = e - s;
        if (n > 32) revert RLPIntegerTooLong();
        if (n == 0) return 0;
        if (d[s] == 0) revert RLPNonCanonical();
        for (uint256 i = s; i < e; ++i) {
            v = (v << 8) | uint8(d[i]);
        }
    }
}
