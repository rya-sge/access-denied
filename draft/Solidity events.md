# Solidity events

In Solidity, events provide a mechanism for smart contracts to emit structured logs that external applications, such as decentralized frontends, can listen to and react to. They enable communication between the blockchain and off-chain applications by storing them in transaction log/receipt instead of contract' state, making them cost-effective and efficient.

This article explores the purpose and usage of events in Solidity, demonstrates them through examples, and highlights a common mistake related to variable name conflicts when emitting events.

[TOC]



------

### Advantages of Events

- **Low Gas Cost**: Events store data in logs, which are cheaper than using contract storage.
- **Efficient Communication**: They serve as a notification mechanism for frontends and external services.
- **Traceability**: Events leave a transparent, immutable record of activity that is ideal for audits and analytics.

## Details

### Definition

Events are declared using the `event` keyword and emitted using the `emit` keyword. 

Events can be defined at file level or as inheritable members of contracts (including interfaces and libraries). 

Once emitted, the data is accessible via Ethereum nodes and can be monitored by external applications using libraries like Ethers.js or Web3.js.

Basic syntax:

```solidity
event EventName(type indexed parameter1, type parameter2);
```

The `indexed` keyword allows up to three parameters to be included in a topic index, making them filterable when querying logs.

### Storage

When you call them, they cause the arguments to be stored in the transaction’s log - a special data structure in the blockchain. 

- These logs are associated with the address of the contract that emitted them
- They are incorporated into the blockchain, and stay there as long as a block is accessible (forever as of now, but this might change in the future). 
- The Log and its event data is not accessible from within contracts (not even from the contract that created them).

### Merkle Proof

It is possible to request a Merkle proof for logs, so if an external entity supplies a contract with such a proof, it can check that the log actually exists inside the blockchain. You have to supply block headers because the contract can only see the last 256 block hashes.



Solidity doc: 0.8.29 https://docs.soliditylang.org/en/v0.8.29/contracts.html#events



## Indexed events

Indexing can be used for filtering the events for specific values.

You can add the attribute `indexed` to up to three parameters which adds them to a special data structure known as [“topics”](https://docs.soliditylang.org/en/v0.8.29/abi-spec.html#abi-events) instead of the data part of the log. 

A topic can only hold a single word (32 bytes) so if you use a [reference type](https://docs.soliditylang.org/en/v0.8.29/types.html#reference-types) for an indexed argument, the Keccak-256 hash of the value is stored as a topic instead.

All parameters without the `indexed` attribute are [ABI-encoded](https://docs.soliditylang.org/en/v0.8.29/abi-spec.html#abi) into the data part of the log.

Topics allow you to search for events, for example when filtering a sequence of blocks for certain events. You can also filter events by the address of the contract that emitted the event.

For example, the code below uses the web3.js `subscribe("logs")` [method](https://web3js.readthedocs.io/en/1.0/web3-eth-subscribe.html#subscribe-logs) to filter logs that match a topic with a certain address value:

```javascript
var options = {
    fromBlock: 0,
    address: web3.eth.defaultAccount,
    topics: ["0x0000000000000000000000000000000000000000000000000000000000000000", null, null]
};
web3.eth.subscribe('logs', options, function (error, result) {
    if (!error)
        console.log(result);
})
    .on("data", function (log) {
        console.log(log);
    })
    .on("changed", function (log) {
});
```



### Dynamic types

When you attempt to index dynamic data types like `string`, `bytes`, `array`, or `struct` in Solidity, they don't get stored in their original form. Instead, the Ethereum log system stores the Keccak-256 hash of these data types.  As a result, when you emit an event with an indexed string, you can't search logs using the actual string—only its hash is stored, not the string itself.

### Anonymous events

The hash of the signature of the event is one of the topics, except if you declared the event with the `anonymous` specifier. 

This means that it is not possible to filter for specific anonymous events by name, you can only filter by the contract address. 

Here the advantage of anonymous events:

- They are cheaper to deploy and call. 

- It also allows you to declare four indexed arguments rather than three.

```
    event SomeEvent(uint256 blocknum, uint256 timestamp) anonymous;
```

https://www.rareskills.io/post/ethereum-events

### Note

Since the transaction log only stores the event data and not the type, you have to know the type of the event, including which parameter is indexed and if the event is anonymous in order to correctly interpret the data. In particular, it is possible to “fake” the signature of another event using an anonymous event.

Example



1. **Fixed-Size Topics:** Ethereum’s “topics”, where indexed event parameters reside, are always 32 bytes. Strings, being dynamic in size, would disrupt this fixed size. Using the hash, which is consistently 32 bytes, maintains this uniformity.
2. **Efficiency and Cost:** Hashing ensures that every indexed parameter occupies a predictable space, regardless of the original string’s length. This results in optimized storage on the blockchain, which keeps associated costs in check.
3. **Searchability:** The Keccak-256 hash is unique for unique inputs. Even small changes in a string result in vastly different hashes, making it straightforward to differentiate between different strings when filtering logs.

Reference: [coinsbench - Understanding Indexed Strings in Solidity Events](https://coinsbench.com/understanding-indexed-strings-in-solidity-events-19ba75986de6), [What does the indexed keyword do?](https://ethereum.stackexchange.com/questions/8658/what-does-the-indexed-keyword-do)

## Retrieve events off-chain

Events on the other hand can be retrieved much more easily. Here are the Ethereum client options:

- `events`
- `events.allEvents`
- `getPastEvents`

Each of these require specifying the smart contract address the querier wishes to examine, and returns a subset (or all) of the events a smart contract emitted according to the query parameters specified.

To summarize: Ethereum does not provide a mechanism to get all transactions for a smart contract, but it does provide a mechanism for getting all events from a smart contract.

Why is this? Making events quickly retrievable requires additional storage overhead. If Ethereum did this for every transaction, this would make the chain considerably larger. With events, solidity programmers can be selective about what kind of information is worth paying the additional storage overhead for, to enable quick off-chain retrieval.

https://www.rareskills.io/post/ethereum-events

------

## Example

### Solidity doc 

Here an example from the offocial solidity doc [0.8.29](https://docs.soliditylang.org/en/v0.8.29/contracts.html#events)

An event `Deposit`is defined with two indexed events: `from`and `id`and one event `value`stored in the data part of the log.

The event is called in the function `deposit`when a client perform a deposit.

```solidity
// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.4.21 <0.9.0;

contract ClientReceipt {
    event Deposit(
        address indexed from,
        bytes32 indexed id,
        uint value
    );

    function deposit(bytes32 id) public payable {
        // Events are emitted using `emit`, followed by
        // the name of the event and the arguments
        // (if any) in parentheses. Any such invocation
        // (even deeply nested) can be detected from
        // the JavaScript API by filtering for `Deposit`.
        emit Deposit(msg.sender, id, msg.value);
    }
}
```

The use in the JavaScript API is as follows:

```javascript
var abi = /* abi as generated by the compiler */;
var ClientReceipt = web3.eth.contract(abi);
var clientReceipt = ClientReceipt.at("0x1234...ab67" /* address */);

var depositEvent = clientReceipt.Deposit();

// watch for changes
depositEvent.watch(function(error, result){
    // result contains non-indexed arguments and topics
    // given to the `Deposit` call.
    if (!error)
        console.log(result);
});


// Or pass a callback to start watching immediately
var depositEvent = clientReceipt.Deposit(function(error, result) {
    if (!error)
        console.log(result);
});
```

The output of the above looks like the following (trimmed):

```json
{
   "returnValues": {
       "from": "0x1111…FFFFCCCC",
       "id": "0x50…sd5adb20",
       "value": "0x420042"
   },
   "raw": {
       "data": "0x7f…91385",
       "topics": ["0xfd4…b4ead7", "0x7f…1a91385"]
   }
}
```



### A Simple Bank Contract

Another example from ChatGPT

The following contract allows users to deposit and withdraw ETH. Events are emitted during each operation to record what happened.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
// Vulnerable contract, don't use it
contract Bank {
    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);

    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
        emit Deposited(msg.sender, msg.value);
    }
	
	// Vulnerable function, don't copy/past it
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient funds");
        balances[msg.sender] -= amount;
        payable(msg.sender).transfer(amount);
        emit Withdrawn(msg.sender, amount);
    }
}
```

In this contract:

- The `Deposited` event logs when a user deposits funds.
- The `Withdrawn` event logs withdrawals.
- Both events include the user's address as an indexed parameter, allowing external tools to filter events per user.

#### Listening to Events with ETherJS

Here's a basic Ethers.js implementation that connects to the `Bank` contract and listens for the `Deposited` and `Withdrawn` events.

```javascript
import { ethers } from "ethers";

// Connect to Ethereum provider (e.g., MetaMask)
const provider = new ethers.providers.Web3Provider(window.ethereum);

// Bank contract ABI (relevant event definitions only)
const abi = [
  "event Deposited(address indexed user, uint256 amount)",
  "event Withdrawn(address indexed user, uint256 amount)"
];

// Replace with your deployed contract address
const contractAddress = "0xYourContractAddressHere";

const bankContract = new ethers.Contract(contractAddress, abi, provider);

// Listen for Deposited events
bankContract.on("Deposited", (user, amount, event) => {
  console.log(`${user} deposited ${ethers.utils.formatEther(amount)} ETH`);
  console.log("Event data:", event);
});

// Listen for Withdrawn events
bankContract.on("Withdrawn", (user, amount, event) => {
  console.log(`${user} withdrew ${ethers.utils.formatEther(amount)} ETH`);
  console.log("Event data:", event);
});
```

To use this script, ensure the user has connected their wallet via MetaMask and that the page is authorized to interact with the Ethereum provider.

## Misc

------

### Variable Name Conflicts When Emitting Events

A frequent source of bugs occurs when local variables or function parameters unintentionally have the same name as state variables. In Solidity, local scope takes precedence, meaning the local variable hides the state variable within the function’s context.

Example:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UserLogger {
    event UserLogged(address user, string message);

    address public user = msg.sender;

    function logInput(address user) public {
        // Here, 'user' refers to the parameter, not the state variable
        emit UserLogged(user, "Input parameter was logged");
    }

    function logState() public {
        emit UserLogged(user, "State variable was logged");
    }
}
```

In `logInput`, the function parameter `user` overrides the contract’s state variable of the same name. As a result, the event logs the parameter, not the stored address.

This behavior can lead to incorrect assumptions in emitted data if not caught. To avoid it, it is common practice to name function parameters with a distinguishing prefix (such as `_user`).

------

## Gas

According to aderyn: 

Index event fields make the field more quickly accessible to off-chain tools that parse events. However, note that each index field costs extra gas during emission, so it's not necessarily best to index the maximum allowed per event (three fields). Each event should use three indexed fields if there are three or more fields, and gas usage is not particularly of concern for the events in question. If there are fewer than three fields, all of the fields should be indexed.

## Popular example

Here the main events defined in several known ERC such as ERC-20, ERC-721 and ERC-1155

### ERC-20

[ERC-20](https://eips.ethereum.org/EIPS/eip-20)

Perhaps the most well-known events are those emitted by ERC20 tokens when they are transferred. The sender, receiver, and amount are recorded in an event.

####  Transfer

MUST trigger when tokens are transferred, including zero value transfers.

A token contract which creates new tokens SHOULD trigger a Transfer event with the `_from` address set to `0x0` when tokens are created.

```
event Transfer(address indexed _from, address indexed _to, uint256 _value)
```

####  Approval

MUST trigger on any successful call to `approve(address _spender, uint256 _value)`.

```
event Approval(address indexed _owner, address indexed _spender, uint256 _value)
```

### ERC-721

See [ERC-721 spec](https://eips.ethereum.org/EIPS/eip-721)

```solidity
    /// @dev This emits when ownership of any NFT changes by any mechanism.
    ///  This event emits when NFTs are created (`from` == 0) and destroyed
    ///  (`to` == 0). Exception: during contract creation, any number of NFTs
    ///  may be created and assigned without emitting Transfer. At the time of
    ///  any transfer, the approved address for that NFT (if any) is reset to none.
    event Transfer(address indexed _from, address indexed _to, uint256 indexed _tokenId);

    /// @dev This emits when the approved address for an NFT is changed or
    ///  reaffirmed. The zero address indicates there is no approved address.
    ///  When a Transfer event emits, this also indicates that the approved
    ///  address for that NFT (if any) is reset to none.
    event Approval(address indexed _owner, address indexed _approved, uint256 indexed _tokenId);

    /// @dev This emits when an operator is enabled or disabled for an owner.
    ///  The operator can manage all NFTs of the owner.
    event ApprovalForAll(address indexed _owner, address indexed _operator, bool _approved);
```

https://www.rareskills.io/post/ethereum-events

### ERC-1155

See [ERC-1155](https://eips.ethereum.org/EIPS/eip-1155)

```solidity
 /**
        @dev Either `TransferSingle` or `TransferBatch` MUST emit when tokens are transferred, including zero value transfers as well as minting or burning (see "Safe Transfer Rules" section of the standard).
        The `_operator` argument MUST be the address of an account/contract that is approved to make the transfer (SHOULD be msg.sender).
        The `_from` argument MUST be the address of the holder whose balance is decreased.
        The `_to` argument MUST be the address of the recipient whose balance is increased.
        The `_id` argument MUST be the token type being transferred.
        The `_value` argument MUST be the number of tokens the holder balance is decreased by and match what the recipient balance is increased by.
        When minting/creating tokens, the `_from` argument MUST be set to `0x0` (i.e. zero address).
        When burning/destroying tokens, the `_to` argument MUST be set to `0x0` (i.e. zero address).        
    */
    event TransferSingle(address indexed _operator, address indexed _from, address indexed _to, uint256 _id, uint256 _value);

    /**
        @dev Either `TransferSingle` or `TransferBatch` MUST emit when tokens are transferred, including zero value transfers as well as minting or burning (see "Safe Transfer Rules" section of the standard).      
        The `_operator` argument MUST be the address of an account/contract that is approved to make the transfer (SHOULD be msg.sender).
        The `_from` argument MUST be the address of the holder whose balance is decreased.
        The `_to` argument MUST be the address of the recipient whose balance is increased.
        The `_ids` argument MUST be the list of tokens being transferred.
        The `_values` argument MUST be the list of number of tokens (matching the list and order of tokens specified in _ids) the holder balance is decreased by and match what the recipient balance is increased by.
        When minting/creating tokens, the `_from` argument MUST be set to `0x0` (i.e. zero address).
        When burning/destroying tokens, the `_to` argument MUST be set to `0x0` (i.e. zero address).                
    */
    event TransferBatch(address indexed _operator, address indexed _from, address indexed _to, uint256[] _ids, uint256[] _values);

/**
@dev MUST emit when approval for a second party/operator address to manage all tokens for an owner address is enabled or disabled (absence of an event assumes disabled).        
*/
    event ApprovalForAll(address indexed _owner, address indexed _operator, bool _approved);

/**
@dev MUST emit when the URI is updated for a token ID.
URIs are defined in RFC 3986.
The URI MUST point to a JSON file that conforms to the "ERC-1155 Metadata URI JSON Schema".
*/
event URI(string _value, uint256 indexed _id);

```



### ERC-6909

https://eips.ethereum.org/EIPS/eip-6909

```solidity
/// @dev Thrown when owner balance for id is insufficient.
    /// @param owner The address of the owner.
    /// @param id The id of the token.
    error InsufficientBalance(address owner, uint256 id);

    /// @dev Thrown when spender allowance for id is insufficient.
    /// @param spender The address of the spender.
    /// @param id The id of the token.
    error InsufficientPermission(address spender, uint256 id);

    /// @notice The event emitted when a transfer occurs.
    /// @param sender The address of the sender.
    /// @param receiver The address of the receiver.
    /// @param id The id of the token.
    /// @param amount The amount of the token.
    event Transfer(address caller, address indexed sender, address indexed receiver, uint256 indexed id, uint256 amount);

    /// @notice The event emitted when an operator is set.
    /// @param owner The address of the owner.
    /// @param spender The address of the spender.
    /// @param approved The approval status.
    event OperatorSet(address indexed owner, address indexed spender, bool approved);
```



## Conclusion

Events are a fundamental part of Ethereum smart contract development, allowing for efficient logging and responsive frontends. While events themselves are simple to implement, careful attention must be paid to the context in which they're emitted, especially when it comes to variable naming. Using clear naming conventions and thoroughly testing emitted outputs ensures reliable and maintainable smart contracts.



## Gas cost

Events are substantially cheaper than writing to storage variables. Events are not intended to be accessible by smart contracts, so the relative lack of overhead justifies a lower [gas cost](https://rareskills.io/post/gas-optimization).

The formula for how much gas an event costs is as follows ([source](https://github.com/wolflo/evm-opcodes/blob/main/gas.md#a8-log-operations)):

```markdown
375 + 375 * num_topics + 8 * data_size + mem_expansion_cost
```

Each event costs at least 375 gas. 

An additional 375 is paid for each indexed parameter. A non-anonymous event has the event selector as an indexed parameter, so that cost is included most of the time. 

Then we pay 8 times the number of 32 byte words written to the chain. Because this region is stored in memory before being emitted, the memory expansion cost must be accounted for also.

The most significant factor in an event’s gas cost is the number of indexed events, so don’t index the variables if it isn’t necessary.

https://github.com/wolflo/evm-opcodes/blob/main/gas.md#a8-log-operations

```
gas_cost = 375 + 375 * num_topics + 8 * data_size + mem_expansion_cost
```



---

## What Is an Event?

Events in Solidity are constructs that allow contracts to log data. Once emitted, events are stored on the blockchain within transaction logs. These logs are not accessible from within the contract, but are available to external systems (such as a web3 frontend or indexer).



Events are intended to be consumed off-chain.

There are two kinds of parameters in this one event: `indexed` and `non-indexed`. Indexed parameters are also known as “topics”, and are the searchable parameters in events. We’ll talk more about those shortly. 

An event is broken down like so:

**Address:** The address of the contract or account the event is emitted from.

**Topics:** The indexed parameters of the event.

https://blog.chain.link/events-and-logging-in-solidity/

## Reference

https://www.rareskills.io/post/ethereum-events
