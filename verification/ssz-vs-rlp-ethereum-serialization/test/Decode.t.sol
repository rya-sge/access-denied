// SPDX-License-Identifier: MIT
pragma solidity 0.8.30;

import {Harness} from "../src/Harness.sol";
import {RLPReader} from "../src/RLPReader.sol";
import {SSZReader} from "../src/SSZReader.sol";
import {Expected} from "./Expected.sol";

interface Vm {
    function readFile(string calldata path) external view returns (string memory);
    function parseBytes(string calldata s) external pure returns (bytes memory);
    function expectRevert(bytes4 selector) external;
    function expectRevert() external;
}

/// @notice Test code: not audited, do not deploy.
contract DecodeTest {
    bool public constant IS_TEST = true;
    Vm internal constant vm = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));

    event log_named_uint(string key, uint256 val);

    Harness internal h;
    bytes internal wRlp;
    bytes internal wSsz;
    bytes internal lRlp;
    bytes internal lSsz;
    bytes internal txRlp;
    bytes internal txSsz;
    bytes internal bigRlp;
    bytes internal bigSsz;
    bytes internal txsRlp;
    bytes internal txsSsz;

    function _fx(string memory n) internal view returns (bytes memory) {
        return vm.parseBytes(vm.readFile(string.concat("fixtures/", n, ".hex")));
    }

    function setUp() public {
        h = new Harness();
        wRlp = _fx("withdrawal_rlp");
        wSsz = _fx("withdrawal_ssz");
        lRlp = _fx("withdrawals_rlp");
        lSsz = _fx("withdrawals_ssz");
        txRlp = _fx("tx_rlp");
        txSsz = _fx("tx_ssz");
        bigRlp = _fx("bigtx_rlp");
        bigSsz = _fx("bigtx_ssz");
        txsRlp = _fx("txs_rlp");
        txsSsz = _fx("txs_ssz");
    }

    function _gas(bytes memory cd) internal view returns (uint256 used) {
        address t = address(h);
        (bool warm, ) = t.staticcall(cd);
        warm;
        uint256 g = gasleft();
        (bool ok, ) = t.staticcall(cd);
        used = g - gasleft();
        require(ok, "call reverted");
    }

    function _net(string memory name, bytes memory cd, bytes memory base) internal {
        uint256 a = _gas(cd);
        uint256 b = _gas(base);
        emit log_named_uint(string.concat("net ", name), a - b);
    }

    function _call(bytes memory cd) internal view returns (bytes memory r) {
        (bool ok, bytes memory out) = address(h).staticcall(cd);
        require(ok, "reverted");
        return out;
    }

    function test_values_match_python() public view {
        require(h.rlpAmount(wRlp) == Expected.W0_AMOUNT, "rlp amount");
        require(h.sszAmount(wSsz) == Expected.W0_AMOUNT, "ssz amount");
        require(h.keccakOfRlp(wRlp) == Expected.W0_KECCAK, "keccak");
        require(h.sha256OfSsz(wSsz) == Expected.W0_SHA256, "sha256");
        require(h.withdrawalRoot(wSsz) == Expected.W0_ROOT, "hash_tree_root");
        require(h.rlpSumAll(lRlp) == Expected.SUM_AMOUNTS, "rlp sum");
        require(h.sszSumAll(lSsz) == Expected.SUM_AMOUNTS, "ssz sum");
        require(h.rlpTxValue(txRlp) == Expected.TX_VALUE, "rlp value");
        require(h.sszTxValue(txSsz) == Expected.TX_VALUE, "ssz value");
        require(h.rlpTxValue(bigRlp) == Expected.BIGTX_VALUE, "rlp big value");
        require(h.sszTxValue(bigSsz) == Expected.BIGTX_VALUE, "ssz big value");
        for (uint256 i = 0; i < 16; ++i) {
            require(h.rlpListAmount(lRlp, i) == h.sszListAmount(lSsz, i), "list parity");
        }
        for (uint256 i = 0; i < 32; i += 7) {
            require(h.rlpListTxHash(txsRlp, i) == h.sszListTxHash(txsSsz, i), "tx parity");
        }
    }

    function test_gas_single_withdrawal() public {
        bytes memory base = abi.encodeCall(Harness.noop, (wRlp));
        _net("rlpAmount", abi.encodeCall(Harness.rlpAmount, (wRlp)), base);
        base = abi.encodeCall(Harness.noop, (wSsz));
        _net("sszAmount", abi.encodeCall(Harness.sszAmount, (wSsz)), base);
        Harness.Withdrawal memory w = Harness.Withdrawal(
            uint64(Expected.W0_INDEX), uint64(Expected.W0_VALIDATOR), Expected.W0_ADDRESS, uint64(Expected.W0_AMOUNT)
        );
        bytes memory cd = abi.encodeCall(Harness.abiAmount, (w));
        emit log_named_uint("abi calldata bytes", cd.length);
        emit log_named_uint("gross abiAmount", _gas(cd));
        emit log_named_uint("gross noop 44 bytes", _gas(abi.encodeCall(Harness.noop, (wSsz))));
    }

    function test_gas_list_position() public {
        bytes memory bR = abi.encodeCall(Harness.noop2, (lRlp, 0));
        bytes memory bS = abi.encodeCall(Harness.noop2, (lSsz, 0));
        for (uint256 i = 0; i < 16; ++i) {
            emit log_named_uint("position", i);
            _net("rlpListAmount", abi.encodeCall(Harness.rlpListAmount, (lRlp, i)), bR);
            _net("sszListAmount", abi.encodeCall(Harness.sszListAmount, (lSsz, i)), bS);
        }
    }

    function test_gas_decode_all() public {
        _net("rlpSumAll", abi.encodeCall(Harness.rlpSumAll, (lRlp)), abi.encodeCall(Harness.noop, (lRlp)));
        _net("sszSumAll", abi.encodeCall(Harness.sszSumAll, (lSsz)), abi.encodeCall(Harness.noop, (lSsz)));
    }

    function test_gas_real_tx() public {
        _net("rlpTxValue small", abi.encodeCall(Harness.rlpTxValue, (txRlp)), abi.encodeCall(Harness.noop, (txRlp)));
        _net("sszTxValue small", abi.encodeCall(Harness.sszTxValue, (txSsz)), abi.encodeCall(Harness.noop, (txSsz)));
        _net("rlpTxValue big", abi.encodeCall(Harness.rlpTxValue, (bigRlp)), abi.encodeCall(Harness.noop, (bigRlp)));
        _net("sszTxValue big", abi.encodeCall(Harness.sszTxValue, (bigSsz)), abi.encodeCall(Harness.noop, (bigSsz)));
        emit log_named_uint("big tx rlp bytes", bigRlp.length);
        emit log_named_uint("big tx ssz bytes", bigSsz.length);
        bytes memory base = abi.encodeCall(Harness.noop2, (bigRlp, 0));
        for (uint256 k = 0; k < 12; ++k) {
            emit log_named_uint("field", k);
            _net("rlpTxField big", abi.encodeCall(Harness.rlpTxField, (bigRlp, k)), base);
        }
    }

    function test_gas_tx_list() public {
        bytes memory bR = abi.encodeCall(Harness.noop2, (txsRlp, 0));
        bytes memory bS = abi.encodeCall(Harness.noop2, (txsSsz, 0));
        emit log_named_uint("list rlp bytes", txsRlp.length);
        emit log_named_uint("list ssz bytes", txsSsz.length);
        uint256[4] memory at = [uint256(0), 7, 15, 31];
        for (uint256 j = 0; j < 4; ++j) {
            emit log_named_uint("position", at[j]);
            _net("rlpListTxHash", abi.encodeCall(Harness.rlpListTxHash, (txsRlp, at[j])), bR);
            _net("sszListTxHash", abi.encodeCall(Harness.sszListTxHash, (txsSsz, at[j])), bS);
        }
    }

    function test_gas_commitments() public {
        _net("keccakOfRlp", abi.encodeCall(Harness.keccakOfRlp, (wRlp)), abi.encodeCall(Harness.noop, (wRlp)));
        _net("sha256OfSsz", abi.encodeCall(Harness.sha256OfSsz, (wSsz)), abi.encodeCall(Harness.noop, (wSsz)));
        _net("withdrawalRoot", abi.encodeCall(Harness.withdrawalRoot, (wSsz)), abi.encodeCall(Harness.noop, (wSsz)));
    }

    function test_rlp_rejects_prefixed_single_byte() public {
        vm.expectRevert(RLPReader.RLPNonCanonical.selector);
        h.rlpAmount(hex"c58080808105");
    }

    function test_rlp_rejects_trailing_byte() public {
        vm.expectRevert(RLPReader.RLPTrailingBytes.selector);
        h.rlpAmount(hex"c480808001ff");
    }

    function test_rlp_rejects_integer_leading_zero() public {
        vm.expectRevert(RLPReader.RLPNonCanonical.selector);
        h.rlpAmount(hex"c6808080820001");
    }

    function test_rlp_rejects_overrun() public {
        vm.expectRevert(RLPReader.RLPTruncated.selector);
        h.rlpAmount(hex"c980808001");
    }

    function test_ssz_rejects_wrong_length() public {
        vm.expectRevert(SSZReader.SSZBadLength.selector);
        h.sszAmount(hex"00");
    }

    function test_ssz_rejects_bad_first_offset() public {
        vm.expectRevert(SSZReader.SSZBadOffset.selector);
        h.sszListTxHash(hex"05000000aa", 0);
    }

    function test_ssz_rejects_descending_offsets() public {
        vm.expectRevert(SSZReader.SSZBadOffset.selector);
        h.sszListTxHash(hex"0800000007000000aabb", 0);
    }
}
