// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.28;

import {Script, console} from "@forge-std/src/Script.sol";

import {Revengery} from "src/Revengery.sol";

contract Deploy is Script {
    function setUp() public {}

    function run() public {
        vm.broadcast();

        Revengery challenge = new Revengery();

        vm.writeFile(vm.envOr("OUTPUT_FILE", string("/tmp/deploy.txt")), vm.toString(address(challenge)));
    }
}
