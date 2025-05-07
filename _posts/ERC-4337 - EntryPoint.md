# ERC-4337 - EntryPoint

**EntryPoint** - a singleton contract to execute bundles of `UserOperations`. Bundlers MUST whitelist the supported `EntryPoint`.

https://github.com/eth-infinitism/account-abstraction/tree/develop

## Functions

Here's a **summary tab** that categorizes the **events**, **functions**, and **errors** found in the `IEntryPoint` interface:

------

### Events

| Event Name                   | Description                                                  |
| ---------------------------- | ------------------------------------------------------------ |
| `UserOperationEvent`         | Emitted after a successful user operation.                   |
| `AccountDeployed`            | Emitted when a new account is deployed via user operation.   |
| `UserOperationRevertReason`  | Emitted when a user operation callData reverts with data.    |
| `PostOpRevertReason`         | Emitted when a postOp call reverts.                          |
| `UserOperationPrefundTooLow` | Emitted when prefund is insufficient and no refund is made.  |
| `BeforeExecution`            | Emitted before executing operations (handleOps/handleAggregatedOps). |
| `SignatureAggregatorChanged` | Emitted when the signature aggregator is changed.            |



------

### Functions

| Function Name         | Description                                                  |
| --------------------- | ------------------------------------------------------------ |
| `handleOps`           | Executes a batch of user operations without aggregators.     |
| `handleAggregatedOps` | Executes a batch of user operations grouped by aggregator.   |
| `getUserOpHash`       | Returns the unique hash of a user operation.                 |
| `getSenderAddress`    | Computes the contract address for initCode (reverts with address). |
| `delegateAndRevert`   | Helper for dry-run testing via `delegatecall`, always reverts. |
| `senderCreator`       | Returns the address of the immutable `SenderCreator` contract. |



------

### Errors

| Error Name                  | Description                                                  |
| --------------------------- | ------------------------------------------------------------ |
| `FailedOp`                  | Emitted if an operation fails during handleOps/handleAggregatedOps. |
| `FailedOpWithRevert`        | Same as `FailedOp`, but includes inner revert data (truncated). |
| `PostOpReverted`            | Indicates postOp reverted and includes return data.          |
| `SignatureValidationFailed` | Indicates signature aggregator verification failure.         |
| `SenderAddressResult`       | Used to return the computed sender address via revert.       |
| `DelegateAndRevert`         | Indicates result of `delegateAndRevert` helper function.     |

------

Would you like this summary exported as a markdown table or included in code documentation?



## Specification

Entrypoint interface

### `EntryPoint` interface

When passed on-chain, to the `EntryPoint` contract, the `Account` and the `Paymaster`, a “packed” version of the above structure called `PackedUserOperation` is used:

| Field                | Type      | Description                                                  |
| -------------------- | --------- | ------------------------------------------------------------ |
| `sender`             | `address` |                                                              |
| `nonce`              | `uint256` |                                                              |
| `initCode`           | `bytes`   | concatenation of factory address and factoryData (or empty), or [EIP-7702 data](https://eips.ethereum.org/EIPS/eip-4337#support-for-eip-7702-authorizations) |
| `callData`           | `bytes`   |                                                              |
| `accountGasLimits`   | `bytes32` | concatenation of verificationGasLimit (16 bytes) and callGasLimit (16 bytes) |
| `preVerificationGas` | `uint256` |                                                              |
| `gasFees`            | `bytes32` | concatenation of maxPriorityFeePerGas (16 bytes) and maxFeePerGas (16 bytes) |
| `paymasterAndData`   | `bytes`   | concatenation of paymaster fields (or empty)                 |
| `signature`          | `bytes`   |                                                              |

The core interface of the `EntryPoint` contract is as follows:

```solidity
function handleOps(PackedUserOperation[] calldata ops, address payable beneficiary);
```

The `beneficiary` is the address that will be paid with all the gas fees collected during the execution of the bundle.



### Paymaster

The paymaster must also have a deposit, which the `EntryPoint` will charge `UserOperation` costs from. The deposit (for paying gas fees) is separate from the stake (which is locked).

The `EntryPoint` must implement the following interface to allow Paymasters (and optionally Accounts) to manage their deposit:

```
// return the deposit of an account
function balanceOf(address account) public view returns (uint256);

// add to the deposit of the given account
function depositTo(address account) public payable;

// add to the deposit of the calling account
receive() external payable;

// withdraw from the deposit of the current account
function withdrawTo(address payable withdrawAddress, uint256 withdrawAmount) external;
```

## Security Considerations

The `EntryPoint` contract will need to be audited and formally verified, because it will serve as a central trust point for *all* [ERC-4337]. In total, this architecture reduces auditing and formal verification load for the ecosystem, because the amount of work that individual *accounts* have to do becomes much smaller (they need only verify the `validateUserOp` function and its “check signature and pay fees” logic) and check that other functions are `msg.sender == ENTRY_POINT` gated (perhaps also allowing `msg.sender == self`), but it is nevertheless the case that this is done precisely by concentrating security risk in the `EntryPoint` contract that needs to be verified to be very robust.

Verification would need to cover two primary claims (not including claims needed to protect paymasters, and claims needed to establish p2p-level DoS resistance):

- **Safety against arbitrary hijacking**: The `EntryPoint` only calls to the `sender` with `userOp.calldata` and only if `validateUserOp` to that specific `sender` has passed.
- **Safety against fee draining**: If the `EntryPoint` calls `validateUserOp` and passes, it also must make the generic call with calldata equal to `userOp.calldata`

### handleOps

Here the different step:

- Validate the different `ops`by calling `_iterateValidationPhase`
- Execute each user operation with _executeUserOp
- For each user operation, add the return value to the collected fee
- Compensate the beneficiary with the fee collection by each operation.

```solidity
function handleOps(
        PackedUserOperation[] calldata ops,
        address payable beneficiary
    ) external nonReentrant {
        uint256 opslen = ops.length;
        UserOpInfo[] memory opInfos = new UserOpInfo[](opslen);
        unchecked {
            _iterateValidationPhase(ops, opInfos, address(0), 0);

            uint256 collected = 0;
            emit BeforeExecution();

            for (uint256 i = 0; i < opslen; i++) {
                collected += _executeUserOp(i, ops[i], opInfos[i]);
            }

            _compensate(beneficiary, collected);
        }
    }
```



 Compensate the caller's beneficiary address with the collected fees of all UserOperations.

 * @param beneficiary - The address to receive the fees.
 * @param amount      - Amount to transfer

```solidity
    function _compensate(address payable beneficiary, uint256 amount) internal virtual {
        require(beneficiary != address(0), "AA90 invalid beneficiary");
        (bool success,) = beneficiary.call{value: amount}("");
        require(success, "AA91 failed send to beneficiary");
    }
```



### UML

![erc4337-entrypoint-uml](/home/ryan/Downloads/me/access-denied/assets/article/blockchain/ethereum/erc-4337/erc4337-entrypoint-uml.png)



### Report

 Sūrya's Description Report

 Files Description Table


 Contracts Description Table


|  Contract  |         Type        |       Bases      |                  |                 |
|:----------:|:-------------------:|:----------------:|:----------------:|:---------------:|
|     └      |  **Function Name**  |  **Visibility**  |  **Mutability**  |  **Modifiers**  |
||||||
| **EntryPoint** | Implementation | IEntryPoint, StakeManager, NonceManager, ReentrancyGuardTransient, ERC165, EIP712 |||
| └ | <Constructor> | Public ❗️ | 🛑  | EIP712 |
| └ | handleOps | External ❗️ | 🛑  | nonReentrant |
| └ | handleAggregatedOps | External ❗️ | 🛑  | nonReentrant |
| └ | getUserOpHash | Public ❗️ |   |NO❗️ |
| └ | getSenderAddress | External ❗️ | 🛑  |NO❗️ |
| └ | senderCreator | Public ❗️ |   |NO❗️ |
| └ | delegateAndRevert | External ❗️ | 🛑  |NO❗️ |
| └ | getPackedUserOpTypeHash | External ❗️ |   |NO❗️ |
| └ | getDomainSeparatorV4 | Public ❗️ |   |NO❗️ |
| └ | supportsInterface | Public ❗️ |   |NO❗️ |
| └ | _compensate | Internal 🔒 | 🛑  | |
| └ | _executeUserOp | Internal 🔒 | 🛑  | |
| └ | _emitUserOperationEvent | Internal 🔒 | 🛑  | |
| └ | _emitPrefundTooLow | Internal 🔒 | 🛑  | |
| └ | _iterateValidationPhase | Internal 🔒 | 🛑  | |
| └ | innerHandleOp | External ❗️ | 🛑  |NO❗️ |
| └ | _copyUserOpToMemory | Internal 🔒 |   | |
| └ | _getRequiredPrefund | Internal 🔒 |   | |
| └ | _createSenderIfNeeded | Internal 🔒 | 🛑  | |
| └ | _validateAccountPrepayment | Internal 🔒 | 🛑  | |
| └ | _callValidateUserOp | Internal 🔒 | 🛑  | |
| └ | _validatePaymasterPrepayment | Internal 🔒 | 🛑  | |
| └ | _callValidatePaymasterUserOp | Internal 🔒 | 🛑  | |
| └ | _validateAccountAndPaymasterValidationData | Internal 🔒 |   | |
| └ | _getValidationData | Internal 🔒 |   | |
| └ | _validatePrepayment | Internal 🔒 | 🛑  | |
| └ | _postExecution | Internal 🔒 | 🛑  | |
| └ | _getUserOpGasPrice | Internal 🔒 |   | |
| └ | _getOffsetOfMemoryBytes | Internal 🔒 |   | |
| └ | _getMemoryBytesFromOffset | Internal 🔒 |   | |
| └ | _getFreePtr | Internal 🔒 |   | |
| └ | _restoreFreePtr | Internal 🔒 |   | |
| └ | _getUnusedGasPenalty | Internal 🔒 |   | |
||||||
| **IAccount** | Interface |  |||
| └ | validateUserOp | External ❗️ | 🛑  |NO❗️ |
||||||
| **IAccountExecute** | Interface |  |||
| └ | executeUserOp | External ❗️ | 🛑  |NO❗️ |
||||||
| **IEntryPoint** | Interface | IStakeManager, INonceManager |||
| └ | handleOps | External ❗️ | 🛑  |NO❗️ |
| └ | handleAggregatedOps | External ❗️ | 🛑  |NO❗️ |
| └ | getUserOpHash | External ❗️ |   |NO❗️ |
| └ | getSenderAddress | External ❗️ | 🛑  |NO❗️ |
| └ | delegateAndRevert | External ❗️ | 🛑  |NO❗️ |
| └ | senderCreator | External ❗️ |   |NO❗️ |
||||||
| **IStakeManager** | Interface |  |||
| └ | getDepositInfo | External ❗️ |   |NO❗️ |
| └ | balanceOf | External ❗️ |   |NO❗️ |
| └ | depositTo | External ❗️ |  💵 |NO❗️ |
| └ | addStake | External ❗️ |  💵 |NO❗️ |
| └ | unlockStake | External ❗️ | 🛑  |NO❗️ |
| └ | withdrawStake | External ❗️ | 🛑  |NO❗️ |
| └ | withdrawTo | External ❗️ | 🛑  |NO❗️ |
||||||
| **IAggregator** | Interface |  |||
| └ | validateSignatures | External ❗️ | 🛑  |NO❗️ |
| └ | validateUserOpSignature | External ❗️ |   |NO❗️ |
| └ | aggregateSignatures | External ❗️ |   |NO❗️ |
||||||
| **INonceManager** | Interface |  |||
| └ | getNonce | External ❗️ |   |NO❗️ |
| └ | incrementNonce | External ❗️ | 🛑  |NO❗️ |
||||||
| **ISenderCreator** | Interface |  |||
| └ | createSender | External ❗️ | 🛑  |NO❗️ |
| └ | initEip7702Sender | External ❗️ | 🛑  |NO❗️ |
||||||
| **IPaymaster** | Interface |  |||
| └ | validatePaymasterUserOp | External ❗️ | 🛑  |NO❗️ |
| └ | postOp | External ❗️ | 🛑  |NO❗️ |
||||||
| **UserOperationLib** | Library |  |||
| └ | gasPrice | Internal 🔒 |   | |
| └ | encode | Internal 🔒 |   | |
| └ | unpackUints | Internal 🔒 |   | |
| └ | unpackHigh128 | Internal 🔒 |   | |
| └ | unpackLow128 | Internal 🔒 |   | |
| └ | unpackMaxPriorityFeePerGas | Internal 🔒 |   | |
| └ | unpackMaxFeePerGas | Internal 🔒 |   | |
| └ | unpackVerificationGasLimit | Internal 🔒 |   | |
| └ | unpackCallGasLimit | Internal 🔒 |   | |
| └ | unpackPaymasterVerificationGasLimit | Internal 🔒 |   | |
| └ | unpackPostOpGasLimit | Internal 🔒 |   | |
| └ | unpackPaymasterStaticFields | Internal 🔒 |   | |
| └ | hash | Internal 🔒 |   | |
| └ | _parseValidationData | Public ❗️ |   |NO❗️ |
| └ | _packValidationData | Public ❗️ |   |NO❗️ |
| └ | _packValidationData | Public ❗️ |   |NO❗️ |
| └ | calldataKeccak | Public ❗️ |   |NO❗️ |
| └ | min | Public ❗️ |   |NO❗️ |
| └ | finalizeAllocation | Public ❗️ |   |NO❗️ |
||||||
| **StakeManager** | Implementation | IStakeManager |||
| └ | getDepositInfo | External ❗️ |   |NO❗️ |
| └ | _getStakeInfo | Internal 🔒 |   | |
| └ | balanceOf | Public ❗️ |   |NO❗️ |
| └ | <Receive Ether> | External ❗️ |  💵 |NO❗️ |
| └ | _incrementDeposit | Internal 🔒 | 🛑  | |
| └ | _tryDecrementDeposit | Internal 🔒 | 🛑  | |
| └ | depositTo | Public ❗️ |  💵 |NO❗️ |
| └ | addStake | External ❗️ |  💵 |NO❗️ |
| └ | unlockStake | External ❗️ | 🛑  |NO❗️ |
| └ | withdrawStake | External ❗️ | 🛑  |NO❗️ |
| └ | withdrawTo | External ❗️ | 🛑  |NO❗️ |
||||||
| **NonceManager** | Implementation | INonceManager |||
| └ | getNonce | Public ❗️ |   |NO❗️ |
| └ | incrementNonce | External ❗️ | 🛑  |NO❗️ |
| └ | _validateAndUpdateNonce | Internal 🔒 | 🛑  | |
||||||
| **SenderCreator** | Implementation | ISenderCreator |||
| └ | <Constructor> | Public ❗️ | 🛑  |NO❗️ |
| └ | createSender | External ❗️ | 🛑  |NO❗️ |
| └ | initEip7702Sender | External ❗️ | 🛑  |NO❗️ |
||||||
| **Exec** | Library |  |||
| └ | call | Internal 🔒 | 🛑  | |
| └ | staticcall | Internal 🔒 |   | |
| └ | delegateCall | Internal 🔒 | 🛑  | |
| └ | getReturnData | Internal 🔒 |   | |
| └ | revertWithData | Internal 🔒 |   | |
| └ | revertWithReturnData | Internal 🔒 |   | |
||||||
| **Eip7702Support** | Library |  |||
| └ | _getEip7702InitCodeHashOverride | Internal 🔒 |   | |
| └ | _isEip7702InitCode | Internal 🔒 |   | |
| └ | _getEip7702Delegate | Internal 🔒 |   | |


 Legend

|  Symbol  |  Meaning  |
|:--------:|-----------|
|    🛑    | Function can modify state |
|    💵    | Function is payable |



