# Sparrow wallet features

Sparrow supports all the features you would expect from a modern Bitcoin wallet:

- Full support for single sig and multisig wallets on common script types
- A range of connection options: Public servers, Bitcoin Core and private Electrum servers
- Standards based including full PSBT support
- Support for all common hardware wallets in USB and airgapped modes
- Full coin and fee control with comprehensive coin selection
- Labeling of all transactions, inputs and outputs
- Lightweight and multi platform
- Send and receive to PayNyms, both directly (BIP47) and collaboratively
- Built in Tor
- Testnet, regtest and signet support

## Features

### 1. **Full Support for Single Sig and Multisig Wallets on Common Script Types**

- **Single sig wallets**: Wallets where one private key is needed to authorize transactions.
- **Multisig wallets**: Wallets requiring multiple signatures to approve a transaction (e.g., 2-of-3).
- Common script types include:
  - **P2PKH (Pay-to-Public-Key-Hash)**: Legacy Bitcoin addresses.
  - **P2SH (Pay-to-Script-Hash)**: Often used for multisig and other advanced scripts.
  - **P2WPKH/P2WSH (Pay-to-Witness-Public-Key-Hash/Script-Hash)**: Native SegWit for lower fees and better efficiency.

### 2. **A Range of Connection Options**

- **Public servers**: Connects to shared Electrum servers for convenience.
- **Bitcoin Core**: Allows connection to a user's own full Bitcoin node for maximum privacy and trust.
- **Private Electrum servers**: Users can set up and connect to their own Electrum Personal Server for enhanced privacy.

### 3. **Standards-Based, Including Full PSBT Support**

- **PSBT (Partially Signed Bitcoin Transactions)**: A standard for creating, signing, and finalizing transactions across different wallets or devices.
- Ensures compatibility with other wallets and services that support PSBT.

### 4. **Support for All Common Hardware Wallets**

- Works with popular hardware wallets (e.g., Ledger, Trezor, Coldcard).
- **USB mode**: Directly connect hardware wallets via USB.
- **Airgapped mode**: Offline signing for enhanced security, useful for devices without internet connectivity.

### 5. **Full Coin and Fee Control with Comprehensive Coin Selection**

- **Coin control**: Allows users to choose specific UTXOs (Unspent Transaction Outputs) to spend, useful for privacy or fee optimization.
- **Fee control**: Users can set transaction fees manually to balance cost and speed.

### 6. **Labeling of All Transactions, Inputs, and Outputs**

- Helps track and categorize transactions for better organization and clarity.
- Useful for auditing, tax reporting, or understanding spending patterns.

### 7. **Lightweight and Multi-Platform**

- Does not require a full Bitcoin node (unless chosen by the user), making it lightweight.
- Available on multiple platforms like Windows, macOS, and Linux.

### 8. **Send and Receive to PayNyms**

- **PayNyms**: Privacy-enhancing feature of [BIP47](https://en.bitcoin.it/wiki/BIP_0047) that allows users to share a reusable payment code without revealing wallet details.
- Enables direct or collaborative transactions without exposing addresses.

See [paynym](https://paynym.rs)

### 9. **Built-in Tor**

- Provides optional anonymity by routing traffic through the Tor network.
- Helps obscure the user's IP address and increases privacy.

### 10. **Testnet, Regtest, and Signet Support**

- **Testnet**: Public Bitcoin test network for experimenting with transactions without using real Bitcoin.
- **Regtest**: Private test environment where users can create their own blocks.
- **Signet**: Newer test network offering more reliable and predictable conditions for testing.

These features make Sparrow Wallet versatile, secure, and well-suited for various Bitcoin use cases, from basic transactions to advanced privacy setups.

## Reference

- [Sparrow wallet](https://sparrowwallet.com)
- https://sparrowwallet.com/features/

