

Smart contract - Memory data structure

### Memory Data Structure

Contract memory is a simple byte array, where data can be stored in 32 bytes (256 bit) or 1 byte (8 bit) chunks and read in 32 bytes (256 bit) chunks. 

The image below illustrates this structure along with the read/write functionality of contract memory.

[![img](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2F33d7994b-a4b5-4268-8d53-85f214944599_717x437.png)](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2F33d7994b-a4b5-4268-8d53-85f214944599_717x437.png)

source: https://takenobu-hs.github.io/downloads/ethereum_evm_illustrated.pdf

This functionality is determined by the 3 opcodes that operate on memory.

| Opcode        | Description                                                  |      |
| ------------- | ------------------------------------------------------------ | ---- |
| MSTORE (x, y) | Store a 32 byte (256-bit) value “y” starting at memory location “x” |      |
|               |                                                              |      |
|               |                                                              |      |



- - 
- MLOAD (x) - Load 32 bytes (256-bit) starting at memory location “x” onto the call stack
- MSTORE8 (x, y) - Store a 1 byte (8-bit) value “y” at memory location “x” (the least significant byte of the 32-byte stack value).

You can think of the memory location as simply the array index of where to start writing/reading the data. If you want to write/read more than 1 byte of data you simply continue writing or reading from the next array index.

https://noxx.substack.com/p/evm-deep-dives-the-path-to-shadowy-d6b?s=r

# Solidity assembly 101

 PUSH1 which tells the EVM to push the next 1 byte of data, 0x00 (0 in decimal), to the call stack.

Next, we have CALLDATALOAD which pops off the first value on the stack (0) as input.

This opcode loads in the calldata to the stack using the “input” as an offset. Stack items are 32 bytes in size but our calldata is 36 bytes. The pushed value is msg.data[i:i+32] where “i” is this input. This ensures only 32 bytes are pushed to the stack but enables us to access any part of the calldata.



https://noxx.substack.com/p/evm-deep-dives-the-path-to-shadowy-d6b?s=r



1. **sstore** -> Stores data to storage
2. **sload** -> Loads data from storage
3. **log1** -> Emits an event
4. **mstore** -> Stores data to memory
5. **return** -> Returns data from memory

https://medium.com/@kulman.david/solidity-assembly-by-example-part-1-b58d6de9c1cd

https://noxx.substack.com/p/evm-deep-dives-the-path-to-shadowy