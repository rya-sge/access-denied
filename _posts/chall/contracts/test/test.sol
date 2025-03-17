// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.28;

import "forge-std/Test.sol";
import "../src/Revengery.sol";
import "@openzeppelin/utils/cryptography/ECDSA.sol";

contract RevengeryTest is Test {
    Revengery revengery;
    address owner;
    address attacker;
    address signer = 0x8E2227b11dd10a991b3CB63d37276daC4E4b9417;

    function setUp() public {
        owner = vm.addr(1);
        attacker = vm.addr(2);
        vm.prank(owner);
        revengery = new Revengery();
    }

    function testInitialOwner() public {
        assertEq(revengery.owner(), owner);
    }

    function testSolveAsOwner() public {
        vm.prank(owner);
        revengery.solve();
        assertTrue(revengery.isSolved());
    }

    function testSolveAsNonOwner() public {
        vm.prank(attacker);
        vm.expectRevert("Ownable: caller is not the owner");
        revengery.solve();
    }

    function testChangeOwnerWithValidSignature() public {
        bytes32 hash = keccak256(abi.encodePacked(attacker));
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(uint256(uint160(owner)), hash);
        bytes memory signature = abi.encodePacked(r, s, v);

        vm.prank(owner);
        revengery.changeOwner(signature, hash, attacker);
        assertEq(revengery.owner(), attacker);
    }

    function testChangeOwnerWithInvalidSignature() public {
        bytes32 hash = keccak256(abi.encodePacked(attacker));
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(uint256(uint160(attacker)), hash);
        bytes memory signature = abi.encodePacked(r, s, v);

        vm.prank(owner);
        vm.expectRevert("New owner should have been authenticated by the signer");
        revengery.changeOwner(signature, hash, attacker);
    }

    function testChangeOwnerWithZeroAddress() public {
        bytes32 hash = keccak256(abi.encodePacked(address(0)));
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(uint256(uint160(signer)), hash);
        bytes memory signature = abi.encodePacked(r, s, v);

        vm.prank(owner);
        vm.expectRevert("New owner should not be the zero address");
        revengery.changeOwner(signature, hash, address(0));
    }
}