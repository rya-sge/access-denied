# Polkadot substrate

Substrate is a Software Development Kit (SDK) that uses Rust-based libraries and tools to enable you to build application-specific blockchains from modular and extensible components. Application-specific blockchains built with Substrate can run as standalone services or in parallel with other chains to take advantage of the shared security provided by the Polkadot ecosystem. Substrate includes default implementations of the core components of the blockchain infrastructure to allow you to focus on the application logic.

Every blockchain platform relies on a decentralized network of computers—called nodes—that communicate with each other about transactions and blocks. In general, a node in this context is the software running on the connected devices rather than the physical or virtual machine in the network. As software, Substrate-based nodes consist of two main parts with separate responsibilities:

- Client

   

  \- services to handle network and blockchain infrastructure activity

  - Native binary
  - Executes the Wasm runtime
  - Manages components like database, networking, mempool, consensus, and others
  - Also known as "Host"

- Runtime

   

  \- business logic for state transitions

  - Application logic
  - Compiled to [Wasm](https://webassembly.org/)
  - Stored as a part of the chain state
  - Also known as State Transition Function (STF)

**Substrate Node**RuntimeCall ExecutorWasm Runtime - STFClientNetwork and Blockchain
Infrastructure Services

![substrate-node](/home/ryan/Downloads/me/access-denied/assets/article/blockchain/polkadot/substrate-node.png)



https://docs.polkadot.com/develop/parachains/intro-polkadot-sdk/