# Multicall

Multicall is a  smart contract pattern in Ethereum and other EVM-compatible blockchains that allows bundling multiple function calls into a single transaction performed atomically. 

By aggregating several calls in the same transaction, this pattern offers several advantages:

- Lower gas costs since the base fee is paid only once
- Lowering API calls to RPC providers.
- Faster loading of web3 webpages, because multiple things get fetched in one call.
- All transactions are performed in the same block, mitigating frontrunning in certain cases.
- Allowing custom logic in the function call

### How Multicall Works

1. A user submits multiple function calls to a multicall contract.
2. The multicall contract sequentially executes these function calls.
3. The results of each call are collected and returned in a single response.
4. If any call fails (depending on implementation), the entire transaction may revert or continue execution.

https://blog.blockmagnates.com/ethereum-multicall-tutorial-5893d870f5ef

# Perform multicall on Ethereum

There are two types of accounts in Ethereum: Externally Owned Accounts (EOAs) and Contract Accounts. EOAs are controlled by private keys, and Contract Accounts are controlled by code.

When an EOA calls a contract, the `msg.sender` value during execution of the call provides the address of that EOA. This is also true if the call (`call`) was executed by a contract.

A smart contract can perform several different type of calls

- The [`CALL`](https://www.evm.codes/#f1?fork=shanghai) opcode. Whenever a CALL is executed, the *context* changes. New context means storage operations will be performed on the called contract, there is a new value (i.e. `msg.value`), and a new caller (i.e. `msg.sender`).

-  [`DELEGATECALL`](https://www.evm.codes/#f4) opcode, which is similar to `CALL`, but different in a very important way: it *does not* change the context of the call. This means the contract being delegatecalled will see the same `msg.sender`, the same `msg.value`, and operate on the same storage as the calling contract. This is very powerful, but can also be dangerous.

It's important to note that you cannot directly delegatecall from an EOA—an EOA can only call a contract, not delegatecall it.





### OpenZeppelin multicall

Abstract contract with a utility to allow batching together multiple calls on the same contract in a single transaction. Useful for allowing EOAs to perform multiple operations at once.

Contrary to `multicall3`, it works only on a specific smart contract which extends the library.

https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/Multicall.sol

Provides a function to batch together multiple calls in a single external call.

 * Consider any assumption about calldata validation performed by the sender may be violated if it's not especially
 * careful about sending transactions invoking {multicall}. For example, a relay address that filters function
 * selectors won't filter calls nested within a {multicall} operation.

NOTE: Since 5.0.1 and 4.9.4, this contract identifies non-canonical contexts (i.e. `msg.sender` is not {Context-_msgSender}).

 * If a non-canonical context is identified, the following self `delegatecall` appends the last bytes of `msg.data`to the subcall. This makes it safe to use with {ERC2771Context}. 
 * Contexts that don't affect the resolution of {Context-_msgSender} are not propagated to subcalls.

Version vulnerable if used with ERC-2771

```solidity
function multicall(bytes[] calldata data) external virtual returns (bytes[] memory results) {
        results = new bytes[](data.length);
        for (uint256 i = 0; i < data.length; i++) {
            results[i] = Address.functionDelegateCall(address(this), data[i]);
        }
        return results;
    }
```

Version 5.0.0

```solidity
abstract contract Multicall is Context {
    /**
     * @dev Receives and executes a batch of function calls on this contract.
     * @custom:oz-upgrades-unsafe-allow-reachable delegatecall
     */
    function multicall(bytes[] calldata data) external virtual returns (bytes[] memory results) {
        bytes memory context = msg.sender == _msgSender()
            ? new bytes(0)
            : msg.data[msg.data.length - _contextSuffixLength():];

        results = new bytes[](data.length);
        for (uint256 i = 0; i < data.length; i++) {
            results[i] = Address.functionDelegateCall(address(this), bytes.concat(data[i], context));
        }
        return results;
    }
```

Example:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Multicall.sol";

contract MulticallERC20 is ERC20, Ownable, Multicall {
    constructor(string memory name, string memory symbol) ERC20(name, symbol) {
        _mint(msg.sender, 1000000 * 10 ** decimals());
    }

    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
}
```



### Multicall3

Multicall3 is a fork from the library 'multicall` project by MakerDAO.

multicall aggregates results from multiple contract constant function calls.

Multicall2 is the same as Multicall, but provides addition functions that allow calls within the batch to fail. 

Multicall3 has two main use cases:

- Aggregate results from multiple contract reads into a single JSON-RPC request.
- Execute multiple state-changing calls in a single transaction.

https://github.com/makerdao/multicall

https://github.com/mds1/multicall3/tree/main

### Call multicall from a smart contract VS EOA

Because you cannot delegatecall from an EOA, this significantly reduces the benefit of calling Multicall3 from an EOA—any calls the Multicall3 executes will have the MultiCall3 address as the `msg.sender`. **This means you should only call Multicall3 from an EOA if the `msg.sender` does not matter.**

If you are using a contract wallet or executing a call to Multicall3 from another contract, you can either CALL or DELEGATECALL. 

- Calls will behave the same as described above for the EOA case
- delegatecalls will preserve the context. 

This means if you delegatecall to Multicall3 from a contract, the `msg.sender` of the calls executed by Multicall3 will be that contract. This can be very useful, and is how the Gnosis Safe [Transaction Builder](https://help.safe.global/en/articles/40841-transaction-builder) works to batch calls from a Safe.

Similarly, because `msg.value` does not change with a delegatecall, you must be careful relying on `msg.value` within a multicall. 

To learn more about this, see [here](https://github.com/runtimeverification/verified-smart-contracts/wiki/List-of-Security-Vulnerabilities#payable-multicall) and [here](https://samczsun.com/two-rights-might-make-a-wrong/).

### Uniswap V3 multicall

Enables calling multiple methods in a single call to the contract

https://docs.uniswap.org/contracts/v3/reference/periphery/base/Multicall

### MakerDAO multicall