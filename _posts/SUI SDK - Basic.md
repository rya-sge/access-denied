



# SUI Wallet SDK - Basic

### https://sdk.mystenlabs.com/dapp-kit/wallet-hooks/useSignAndExecuteTransaction

###  Commands Transactions

> [Documentation](https://sdk.mystenlabs.com/typescript/transaction-building/basics#transactions)

Programmable Transactions have two key concepts: inputs and commands.

Commands are steps of execution in the transaction. Each command in a Transaction takes a set of inputs, and produces results. The inputs for a transaction depend on the kind of command. Sui supports following commands

#### List

- ```
  tx.splitCoins(coin, amounts)
  ```

   \- Creates new coins with the defined amounts, split from the provided coin. Returns the coins so that it can be used in subsequent transactions.

  - Example: `tx.splitCoins(tx.gas, [100, 200])`

- ```
  tx.mergeCoins(destinationCoin, sourceCoins)
  ```

   \- Merges the sourceCoins into the destinationCoin.

  - Example: `tx.mergeCoins(tx.object(coin1), [tx.object(coin2), tx.object(coin3)])`

- ```
  tx.transferObjects(objects, address)
  ```

   \- Transfers a list of objects to the specified address.

  - Example: `tx.transferObjects([tx.object(thing1), tx.object(thing2)], myAddress)`

- ```
  tx.moveCall({ target, arguments, typeArguments })
  ```

   \- Executes a Move call. Returns whatever the Sui Move call returns.

  - Example: `tx.moveCall({ target: '0x2::devnet_nft::mint', arguments: [tx.pure.string(name), tx.pure.string(description), tx.pure.string(image)] })`

- ```
  tx.makeMoveVec({ type, elements })
  ```

  \- Constructs a vector of objects that can be passed into a moveCall. This is required as there’s no way to define a vector as an input.

  - Example: `tx.makeMoveVec({ elements: [tx.object(id1), tx.object(id2)] })`

- `tx.publish(modules, dependencies)` - Publishes a Move package. Returns the upgrade capability object.

#### Summary tab

| **Function**                                        | **Description**                                              | **Example Usage**                                            |
| --------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| `tx.splitCoins(coin, amounts)`                      | Creates new coins with the defined amounts, split from the provided coin. Returns the new coins for subsequent transactions. | `tx.splitCoins(tx.gas, [100, 200])`                          |
| `tx.mergeCoins(destinationCoin, sourceCoins)`       | Merges the `sourceCoins` into the `destinationCoin`.         | `tx.mergeCoins(tx.object(coin1), [tx.object(coin2), tx.object(coin3)])` |
| `tx.transferObjects(objects, address)`              | Transfers a list of objects to the specified address.        | `tx.transferObjects([tx.object(thing1), tx.object(thing2)], myAddress)` |
| `tx.moveCall({ target, arguments, typeArguments })` | Executes a Move call. Returns whatever the Sui Move call returns. | `tx.moveCall({ target: '0x2::devnet_nft::mint', arguments: [tx.pure.string(name), tx.pure.string(description), tx.pure.string(image)] })` |
| `tx.makeMoveVec({ type, elements })`                | Constructs a vector of objects that can be passed into a `moveCall`. | `tx.makeMoveVec({ elements: [tx.object(id1), tx.object(id2)] })` |
| `tx.publish(modules, dependencies)`                 | Publishes a Move package. Returns the upgrade capability object. | `tx.publish(modules, dependencies)`                          |

## SUI RPC methods 

> https://sdk.mystenlabs.com/typescript/sui-client#arguments

In addition to the RPC methods mentioned above, `SuiClient` also exposes some methods for working with Transactions.

### [`executeTransactionBlock`](https://sdk.mystenlabs.com/typescript/sui-client#executetransactionblock)



```
const tx = new Transaction();
// add transaction data to tx...
const { bytes, signature } = tx.sign({ client, signer: keypair });
const result = await client.executeTransactionBlock({
	transactionBlock: bytes,
	signature,
	requestType: 'WaitForLocalExecution',
	options: {
		showEffects: true,
	},
});
```

#### [Arguments](https://sdk.mystenlabs.com/typescript/sui-client#arguments)

- `transactionBlock` - either a Transaction or BCS serialized transaction data bytes as a Uint8Array or as a base-64 encoded string.

- `signature` - A signature, or list of signatures committed to the intent message of the transaction data, as a base-64 encoded string.

- `requestType`: `WaitForEffectsCert` or `WaitForLocalExecution`. Determines when the RPC node should return the response. Default to be `WaitForLocalExecution`

- ```
  options:
  ```

  

  - `showBalanceChanges`: Whether to show balance_changes. Default to be False
  - `showEffects`: Whether to show transaction effects. Default to be False
  - `showEvents`: Whether to show transaction events. Default to be False
  - `showInput`: Whether to show transaction input data. Default to be False
  - `showObjectChanges`: Whether to show object_changes. Default to be False
  - `showRawInput`: Whether to show bcs-encoded transaction input data

### [`signAndExecuteTransaction`](https://sdk.mystenlabs.com/typescript/sui-client#signandexecutetransaction)



```
const tx = new Transaction();
// add transaction data to tx
const result = await client.signAndExecuteTransaction({
	transaction: tx,
	signer: keypair,
	requestType: 'WaitForLocalExecution',
	options: {
		showEffects: true,
	},
});
```

#### [Arguments](https://sdk.mystenlabs.com/typescript/sui-client#arguments-1)

- `transaction` - BCS serialized transaction data bytes as a Uint8Array or as a base-64 encoded string.

- `signer` - A `Keypair` instance to sign the transaction

- `requestType`: `WaitForEffectsCert` or `WaitForLocalExecution`. Determines when the RPC node should return the response. Default to be `WaitForLocalExecution`

- ```
  options:
  ```

  - `showBalanceChanges`: Whether to show balance_changes. Default to be False
  - `showEffects`: Whether to show transaction effects. Default to be False
  - `showEvents`: Whether to show transaction events. Default to be False
  - `showInput`: Whether to show transaction input data. Default to be False
  - `showObjectChanges`: Whether to show object_changes. Default to be False
  - `showRawInput`: Whether to show bcs-encoded transaction input data

### [`waitForTransaction`](https://sdk.mystenlabs.com/typescript/sui-client#waitfortransaction)

Wait for a transaction result to be available over the API. This can be used in conjunction with `executeTransactionBlock` to wait for the transaction to be available via the API. This currently polls the `getTransactionBlock` API to check for the transaction.

```
const tx = new Transaction();
const result = await client.signAndExecuteTransaction({
	transaction: tx,
	signer: keypair,
});
const transaction = await client.waitForTransaction({
	digest: result.digest,
	options: {
		showEffects: true,
	},
});
```

#### [Arguments](https://sdk.mystenlabs.com/typescript/sui-client#arguments-2)

- `digest` - the digest of the queried transaction

- `signal` - An optional abort signal that can be used to cancel the request

- `timeout` - The amount of time to wait for a transaction. Defaults to one minute.

- `pollInterval` - The amount of time to wait between checks for the transaction. Defaults to 2 seconds.

- ```
  options:
  ```

  - `showBalanceChanges`: Whether to show balance_changes. Default to be False
  - `showEffects`: Whether to show transaction effects. Default to be False
  - `showEvents`: Whether to show transaction events. Default to be False
  - `showInput`: Whether to show transaction input data. Default to be False
  - `showObjectChanges`: Whether to show object_changes. Default to be False
  - `showRawInput`: Whether to show bcs-encoded transaction input data

### Summary tab

Here’s a summary table for **`executeTransactionBlock`**, **`signAndExecuteTransaction`**, and **`waitForTransaction`**:

| **Function**                                                 | **Description**                                              | **Arguments**                                                | **Example Usage**                                            |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| `client.executeTransactionBlock({ transactionBlock, signature, requestType, options })` | Executes a signed transaction block.                         | - `transactionBlock`: `Transaction` object, `Uint8Array`, or base64 string  - `signature`: One or more base64 signatures  - `requestType`: `"WaitForEffectsCert"` or `"WaitForLocalExecution"` (default)  - `options`: Flags for showing balance changes, effects, events, input, object changes, raw input | `js\nconst { bytes, signature } = tx.sign({ client, signer: keypair });\nconst result = await client.executeTransactionBlock({\n  transactionBlock: bytes,\n  signature,\n  requestType: 'WaitForLocalExecution',\n  options: { showEffects: true },\n});` |
| `client.signAndExecuteTransaction({ transaction, signer, requestType, options })` | Signs and executes a transaction in one step.                | - `transaction`: Transaction object, `Uint8Array`, or base64 string  - `signer`: Keypair instance  - `requestType`: `"WaitForEffectsCert"` or `"WaitForLocalExecution"` (default)  - `options`: Same flags as above | `js\nconst result = await client.signAndExecuteTransaction({\n  transaction: tx,\n  signer: keypair,\n  requestType: 'WaitForLocalExecution',\n  options: { showEffects: true },\n});` |
| `client.waitForTransaction({ digest, signal, timeout, pollInterval, options })` | Waits until a transaction is available via the API. Useful after submitting with `executeTransactionBlock`. | - `digest`: Digest of the transaction  - `signal`: Optional abort signal  - `timeout`: Wait time (default: 1 min)  - `pollInterval`: Interval between polls (default: 2s)  - `options`: Same flags as above |                                                              |



# Building Programmable Transaction Blocks

> https://docs.sui.io/guides/developer/sui-101/building-ptb

This guide explores creating a programmable transaction block (PTB) on Sui using the TypeScript SDK. For an overview of what a PTB is, see [Programmable Transaction Blocks](https://docs.sui.io/concepts/transactions/prog-txn-blocks) in the Concepts section. If you don't already have the Sui TypeScript SDK, follow the [install instructions](https://sdk.mystenlabs.com/typescript/install) on the Sui TypeScript SDK site.

This example starts by constructing a PTB to send Sui. If you are familiar with the legacy Sui transaction types, this is similar to a `paySui` transaction. To construct transactions, import the `Transaction` class, and construct it:

```ts
import { Transaction } from '@mysten/sui/transactions';

const tx = new Transaction();
```



Using this, you can then add transactions to this PTB.

```ts
// Create a new coin with balance 100, based on the coins used as gas payment.
// You can define any balance here.
const [coin] = tx.splitCoins(tx.gas, [tx.pure('u64', 100)]);

// Transfer the split coin to a specific address.
tx.transferObjects([coin], tx.pure('address', '0xSomeSuiAddress'));
```



You can attach multiple transaction commands of the same type to a PTB as well. For example, to get a list of transfers, and iterate over them to transfer coins to each of them:

```ts
interface Transfer {
	to: string;
	amount: number;
}

// Procure a list of some Sui transfers to make:
const transfers: Transfer[] = getTransfers();

const tx = new Transaction();

// First, split the gas coin into multiple coins:
const coins = tx.splitCoins(
	tx.gas,
	transfers.map((transfer) => tx.pure('u64', transfer.amount)),
);

// Next, create a transfer transaction for each coin:
transfers.forEach((transfer, index) => {
	tx.transferObjects([coins[index]], tx.pure('address', transfer.to));
});
```



After you have the Transaction defined, you can directly execute it with a `SuiClient` and `KeyPair` using `client.signAndExecuteTransaction`.

```ts
client.signAndExecuteTransaction({ signer: keypair, transaction: tx });
```



## Passing transaction results as arguments

> https://docs.sui.io/guides/developer/sui-101/building-ptb#passing-transaction-results-as-arguments

You can use the result of a transaction command as an argument in subsequent transaction commands. Each transaction command method on the transaction builder returns a reference to the transaction result.

```ts
// Split a coin object off of the gas object:
const [coin] = tx.splitCoins(tx.gas, [tx.pure.u64(100)]);
// Transfer the resulting coin object:
tx.transferObjects([coin], tx.pure.address(address));
```



When a transaction command returns multiple results, you can access the result at a specific index either using destructuring, or array indexes.

```ts
// Destructuring (preferred, as it gives you logical local names):
const [nft1, nft2] = tx.moveCall({ target: '0x2::nft::mint_many' });
tx.transferObjects([nft1, nft2], tx.pure.address(address));

// Array indexes:
const mintMany = tx.moveCall({ target: '0x2::nft::mint_many' });
tx.transferObjects([mintMany[0], mintMany[1]], tx.pure.address(address));
```