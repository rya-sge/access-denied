# SUI stack

Participating in hackathons is always a great way to discover new technologies.

The BSA  hackathon and its many teams introduced me to the many tools available on the SUI blockchain and motivated me to take a closer look at them: Walrus (decentralized storage), Seal (encryption and access storage), Sui Stack Messaging SDK, Nautilus (TEE), and the zk-login.

- Walrus is a decentralized blob storage network which allows to store and serve media such as images, sounds or in AI-related use case clean data sets of training data. Walrus enables encoding of unstructured data blobs into smaller slivers distributed and stored over a network of storage nodes.

Website: https://www.walrus.xyz

- Seal is a decentralized secrets management (DSM) service that relies on access control policies defined and validated on Sui. This can be used to keep data secure, notably with Walrus to provide encryption and access control. For that, Seal uses the Boneh–Franklin scheme as Identity-Based Encryption (IBE).

Website: https://seal.mystenlabs.com

Doc: https://seal-docs.wal.app

- Sui Stack Messaging SDK provides an end-to-end encrypted messaging solution for Web3 applications by combining three key components: Sui smart contracts, Walrus (decentralized storage) and Seal (encryption)

- Nautilus is a framework for secure and verifiable off-chain computation. It allows to delegate sensitive or resource-intensive tasks to a trusted execution environment (AWS Nitro Enclave TEE). AWS-signed enclave attestations can be verified with Move Smart contracts.

Website: https://sui.io/nautilus

Documentation: https://docs.sui.io/concepts/cryptography/nautilus

- ZK-Login: it  allows to send transactions from a Sui address using an OAuth credential, without publicly linking the two by using Zero-knowledge proofs (Groth16 zkSNARK).

Website: https://sui.io/zklogin

Doc: https://docs.sui.io/concepts/cryptography/zklogin



For the hackaton, with my great teamate  [Djason Gadiou](https://www.linkedin.com/in/djason-gadiou/) and Stan, we implement a  decentralized identity (W3C) for Sui in Move  with the document storage made on Walrus.

Github is available here: https://github.com/hliosone/sui-identity-hub

Many thanks to the BSA for this great hackathon, always a pleasure to participate.