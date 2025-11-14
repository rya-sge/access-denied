CCIP

Before diving into the [tutorials](https://docs.chain.link/ccip/tutorials/evm/cross-chain-tokens#tutorials), it's important first to understand the overall procedure for enabling your tokens in CCIP. This procedure involves deploying tokens and token pools, registering administrative roles, and configuring token pools to enable secure token transfers using CCIP. The diagram below outlines the entire process:

![Process for enabling a token in CCIP.](https://docs.chain.link/images/ccip/CCIP_enabled_tokens_flowchart.jpg)

### [Understanding the Procedure](https://docs.chain.link/ccip/tutorials/evm/cross-chain-tokens#understanding-the-procedure)

The steps in the diagram highlight the flow of actions needed to enable a token for cross-chain transfers. These steps will be the foundation of the tutorials. Whether you're working with an Externally Owned Account (EOA) or a **Smart Account** (such as one using a multisig scheme), the overall logic remains the same. You'll follow the same process to enable cross-chain token transfers, configure pools, and register administrative roles.

In the following tutorials, we will walk through each step of the process to give you hands-on experience, from deploying your token to registering and configuring token pools. The process will apply equally whether you use an EOA or a Smart Account (such as with multisig transactions), ensuring flexibility across different account types.

### [Key Steps to Keep in Mind:](https://docs.chain.link/ccip/tutorials/evm/cross-chain-tokens#key-steps-to-keep-in-mind)

1. **Token Deployment**: If the token is not yet deployed, you'll deploy an [ERC20-compatible token](https://docs.chain.link/ccip/concepts/cross-chain-token/evm/tokens).
2. **Admin Registration**: The token administrator must be registered in the [`TokenAdminRegistry`](https://docs.chain.link/ccip/api-reference/evm/v1.6.2/token-admin-registry) via self-service.
3. **Pool Deployment and Configuration**: [Token pools](https://docs.chain.link/ccip/concepts/cross-chain-token/evm/token-pools#common-requirements) are deployed, linked to tokens, and configured to manage cross-chain token transfers.

The tutorials will implement the logic of this process, which involves deploying and configuring token pools and registering administrative roles, step-by-step.

## Burn and mint model

## **How to Enable Custom Tokens in Chainlink CCIP Using Hardhat**

Cross-chain interoperability is one of the biggest challenges in blockchain development. Chainlink’s **Cross-Chain Interoperability Protocol (CCIP)** provides a secure and standardized way to move tokens and data across different networks. While CCIP natively supports several major tokens, developers can also enable their **own custom ERC-20 tokens** to participate in cross-chain transfers.

This article explains the **key steps** involved in enabling a custom token within Chainlink CCIP using **Hardhat**.

------

### **1. Token Deployment**

The process begins with deploying an **ERC-20 token** that supports minting and burning.
 To be compatible with CCIP’s **burn-and-mint model**, the token contract must allow:

- **Burning** tokens on the source chain.
- **Minting** tokens on the destination chain.

This ensures that the total supply remains consistent across networks during transfers. Developers often use a **BurnMintERC20** implementation, which grants admin privileges for managing mint and burn permissions.

------

### **2. Creating Token Pools**

Next, a **token pool** must be deployed for each blockchain where the token will operate.
 A token pool acts as an intermediary between CCIP’s router and the token contract. For burn-and-mint tokens, a **BurnMintTokenPool** is used.

The pool handles:

- Receiving burn requests from CCIP on the source chain.
- Initiating mint operations on the destination chain.
- Maintaining mappings between corresponding tokens across networks.

------

### **3. Assigning Administrative Roles**

After deployment, the pool needs authorization to manage the token’s minting and burning.
 This involves transferring the token’s **admin role** to the token pool, ensuring that CCIP can automatically perform these operations during cross-chain transfers. Proper role assignment is essential to prevent manual intervention and ensure a trust-minimized process.

------

### **4. Registering Tokens in CCIP**

Once tokens and pools are configured, they must be **registered with CCIP**.
 This registration links each token’s contract and pool to the CCIP router and specifies how tokens map across chains.
 Enabling the token in CCIP allows it to appear as a supported asset for cross-chain transfers via Chainlink’s messaging infrastructure.

------

### **5. Cross-Chain Transfer Execution**

When the setup is complete, tokens can move seamlessly between chains.
 Here’s what happens during a transfer:

1. The sender initiates a transfer via CCIP.
2. The token is **burned** on the source chain.
3. CCIP relays the message to the destination chain.
4. The corresponding amount is **minted** on the destination network.

This ensures a consistent total supply across all connected blockchains, while maintaining the same token identity and behavior.

------

### **Conclusion**

Enabling a custom token within **Chainlink CCIP** involves a series of smart contract configurations rather than manual bridging. By combining **ERC-20 tokens**, **burn-and-mint token pools**, and **Chainlink’s cross-chain router**, developers can unlock seamless interoperability between networks such as **Ethereum, Avalanche, and Arbitrum**.