---
layout: post
title: "Building a Wallet for Aztec — What a MetaMask for a Private Chain Has to Contain"
date:   2026-09-17
lang: en
locale: en-GB
categories: blockchain ethereum ZKP
tags: aztec zkp privacy wallet account-abstraction smart-wallet cryptography
description: "An Aztec wallet is a key store, a private-state database, a prover and a dApp gateway in one: components, build order, traps, and the wallets that exist today."
image: /assets/article/blockchain/aztec/2026-09-17-aztec-wallet-mindmap.png
isMath: false
---

[Aztec](https://aztec.network/) is a privacy-focused Layer 2 on Ethereum. A contract there has a private side, executed on the user's own device inside a zero-knowledge proof over encrypted *notes* that only their owner can read, and a public side executed by a sequencer. [An earlier article]({{site.url_complet}}/2026/09/08/how-aztec-works-private-execution-model/) covers that execution model; the phrase to keep from it is "on the user's own device", because that is where a wallet comes in.

A MetaMask-style wallet on Ethereum is a key store with a signing prompt: it holds a secret, shows a transaction, signs it, and hands the signature to a node that does everything else. On Aztec the node cannot do everything else. Private state exists only as encrypted notes that the user's keys decrypt; the proof that a private function ran correctly is produced by the user, not by a validator; the very question "what is my balance" can only be answered by software holding the user's keys. So an Aztec wallet is the key store *and* a private-state database *and* a zero-knowledge prover *and* the gateway through which dApps reach all three. The Aztec documentation's own phrasing is that wallets "also need to track private state" and "are also responsible for producing local proofs of execution".

This article lays out what such a wallet is made of, using the framework's own building blocks at version 5.2.0: the PXE (Private eXecution Environment) library, the account contracts, the wallet SDK that defines how a web page discovers and talks to a wallet, and the fee-payment contracts. It then proposes a build order, lists the traps the documentation and the reference extension warn about, and closes with the wallets that exist for Aztec at the time of writing.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What is different from an Ethereum wallet

Four responsibilities have no counterpart in an EVM wallet, and each shapes a component below.

- **Private state lives in the wallet.** Notes are published as encrypted logs; the wallet finds the ones addressed to its accounts, decrypts them, checks them against the note hash tree, and stores them. A balance is a local query over that store. No RPC endpoint can answer it.
- **The wallet proves.** Every transaction is broadcast as a proof of correct private execution. Simulation and proving happen in the wallet, in WebAssembly, and take from seconds to a minute on consumer hardware.
- **Every account is a contract.** There are no externally owned accounts. The wallet must deploy an account contract for each user and implement the contract's authorisation scheme (Schnorr, ECDSA, a passkey, anything else) on the client side.
- **Fees need a payer before the first transaction.** The native fee asset, Fee Juice, is bridged from Ethereum and non-transferable; a fresh account has none. A wallet either bridges it, or routes the fee through a fee-paying contract that accepts another token or sponsors the user.

To these the documentation adds a privacy duty that Ethereum wallets do not have: the wallet decides what a dApp may see of the user's private state and which cross-contract reads a contract may perform on the user's behalf, because on Aztec a "view" of private data is a disclosure.

## The components

![Component diagram of an Aztec browser-extension wallet: content script relaying page messages, background service worker running the wallet SDK protocol and approvals, offscreen document hosting the PXE, prover and key store, popup UI, and the Aztec node it syncs from]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-wallet-components-concept.png)

### Keys and accounts

An Aztec account carries several key pairs, all on the Grumpkin curve (see the [ephemeral-keys article]({{site.url_complet}}/2026/09/17/aztec-ephemeral-keys-ecdh-encryption-post-quantum/) for the curve). The protocol-mandated ones are derived from one root secret with SHA-512 and domain separators: the master nullifier key (spending notes), the incoming viewing key (decrypting received notes), and four reserved slots. The *signing* key is not protocol-mandated at all: it belongs to the account contract, and the reference wallet derives the root secret *from* a randomly generated signing key so that one value backs up both.

Three consequences for the wallet:

- **The address is known before deployment.** `address = (H(public_keys_hash, partial_address) · G + Ivpk_m).x`, computable locally from the keys, the contract class and a salt. A user can receive notes before its account contract exists on chain, so the wallet must generate and display the address without touching the network, and must scan for notes that arrived before deployment.
- **Deployment is a transaction the wallet sends.** The account contract must be deployed and initialised; the reference extension does it through the sponsored fee-paying contract so that a new user needs no funds.
- **Protocol keys cannot be delegated to a hardware wallet today.** The documentation states the limitation directly: nullifier and viewing keys "need to be available in the wallet software itself and cannot be delegated to an external keystore". A hardware device can hold the *signing* key of an account contract designed for it; the keys that decrypt and spend notes stay in software.

Storage in the reference extension is a password-derived, non-extractable AES-256-GCM `CryptoKey`, obtained with PBKDF2 at 600,000 iterations, encrypting each account's root secret and salt with a fresh IV per record; the password is verified by decrypting a known plaintext rather than by comparing a hash.

### The PXE: the private half of the chain, locally

The PXE is a TypeScript library, `@aztec/pxe`, that runs in Node.js or a browser. It is the part of the wallet that makes it an Aztec wallet. It holds:

- **the key store**, from which oracles serve keys to the executing contract (the nullifier hiding key for spending, the address secret for decrypting);
- **the note database**, filled by *sync*: for every registered account and every registered sender, the PXE computes the discovery tags it can derive, fetches the matching logs from a node, and hands them to the contract's own `sync_state` function, which decrypts, dispatches by message type, confirms each note against the transaction's note hashes and stores it;
- **the contract function simulator**, which executes private bytecode with the oracles a contract needs (notes, keys, authwits, capsules, randomness), by default in a *kernelless* mode that computes what the kernel circuits would have produced without running them;
- **the address book** of complete addresses for recipients, and the **contract registry** of artifacts the user's contracts need.

Two facts about the PXE decide the wallet's architecture. It is stateful and long-running: it keeps a local database (IndexedDB in a browser) and Merkle-tree state, and a sync can take a while. And it needs WebAssembly, for the circuits it simulates and the proofs it produces.

In a Manifest V3 browser extension neither is possible in the service worker, which Chrome stops after five minutes of inactivity and which cannot run WASM. The reference extension therefore hosts the PXE in an **offscreen document**, an invisible page that survives, has IndexedDB, and runs WASM, while the service worker keeps the lightweight protocol logic and routes requests to it over a persistent port.

The PXE also exposes three **execution hooks** to the wallet, callbacks it invokes mid-simulation when a policy decision is needed, and a wallet that leaves them unset gets the conservative default:

- `authorizeUtilityCall` — fires when one contract's utility function calls into *another* contract, the way a private balance could be read by a contract the user never meant to expose it to. Absent, every cross-contract utility call is denied.
- `resolveTaggingSecretStrategy` — fires when a message is sent to a recipient with whom no handshake exists yet; the wallet chooses between a non-interactive handshake (published, reveals the recipient was contacted), an interactive one (needs the recipient online), an address-derived secret or an out-of-band one. Absent, a non-interactive handshake.
- `resolveCustomRequest` — a general channel for a contract to ask the wallet for something no oracle provides; the interactive handshake's recipient signature travels through it. Absent, such requests fail.

### The prover

After simulation, `pxe.proveTx(request)` executes the private functions again under the kernel circuits and produces the client-side proof. The documentation's own figure is 10 to 60 seconds; it runs in WASM (`@aztec/bb.js`), wants worker threads and therefore a cross-origin-isolated context, and is the reason the reference build patches worker files for `crossOriginIsolated`. A wallet has to keep the user informed during that minute, keep the page or extension context alive, and never block the approval UI on it.

A design point that follows from the UTXO model is worth knowing before building the progress bar: a private execution trace depends only on the input notes, so what the simulation showed is exactly what the proof attests and what the chain will apply. The one way it fails afterwards is a note nullified by a competing transaction in the meantime.

### The transaction pipeline

![Sequence of a transaction through an Aztec wallet: the dApp sends an ExecutionPayload over the encrypted wallet-SDK channel, the background worker queues it for approval, the user approves in the popup, the offscreen wallet completes fee options, builds the execution request, simulates, collects authwits, proves in WASM and sends to the node, and the receipt travels back]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-wallet-transaction-sequence.png)

A dApp never hands the wallet a signed transaction; it hands an **`ExecutionPayload`**: a list of function calls, each with a target, a selector, arguments and a static flag; any pre-signed authorisation witnesses; capsules of side data; and optionally a fee payer. From there the wallet, in the `BaseWallet` class the SDK provides:

1. **completes the fee options** (`completeFeeOptions`): who pays and how, the one method the reference extension overrides;
2. **builds the `TxExecutionRequest`** through the account contract's entrypoint, which is where the account's authorisation scheme signs the calls;
3. **simulates**, kernelless, to estimate gas and to *capture the private authwits the transaction needs*: when a contract asks the account "may X do Y on your behalf", the simulation records the request and the wallet signs it once at the end, so dApps do not manage private authorisations themselves (public ones are different: they are on-chain state, set up beforehand);
4. **proves**;
5. **sends** the proven transaction to a node, which gossips it to the sequencers, and returns the hash.

The SDK's approval matrix is the policy layer over this: `sendTx` always requires the user's approval, a batch does if it contains a `sendTx`, and read-only calls such as `getAccounts`, `simulateTx` and `executeUtility` execute without a prompt once the dApp holds the capability.

### Fees

Fee Juice is the fee asset; it is bridged from an ERC-20 on Ethereum through the `FeeJuicePortal`, claimed on L2 about two blocks later, and is non-transferable once there. A new account cannot pay for its own claim, so the protocol lets one transaction claim and spend in the same go, and a wallet has three ways to make the first transaction possible:

- **bridge Fee Juice** to the address before deployment, so the account pays for itself; this needs L1 funds and a bridge flow in the wallet;
- **a fee-paying contract (FPC)**, the Aztec paymaster: it holds Fee Juice, declares itself fee payer in the transaction's non-revertible setup phase, and in exchange collects another token from the user, usually through a signed quote and an authwit; on mainnet, ecosystem FPCs are the practical route;
- **the Sponsored FPC**, which pays unconditionally and exists on testnet, devnet and the local network; the reference extension routes every transaction through it.

Whatever the choice, the wallet is the place where it is made, per transaction, and where the user is told who paid.

### The dApp connection: the wallet SDK protocol

On Ethereum a wallet injects `window.ethereum`. Aztec's `@aztec/wallet-sdk` defines a different protocol, because a page must not be able to detect which wallets are installed and because the messages that follow carry private state.

- **Discovery.** The dApp broadcasts a request over `window.postMessage`; a wallet answers only after the user clicks *Connect* in it, so a site cannot silently enumerate wallets.
- **Key exchange.** An ECDH exchange on P-256 (the Web Crypto curve, unrelated to Grumpkin) establishes a session key; every later message is AES-GCM encrypted, so a content script or another extension on the page cannot read wallet calls.
- **Verification.** Both sides derive a verification hash from the exchange and show it as a nine-emoji grid; the user confirms they match, which is the defence against a page interposing itself between dApp and wallet.
- **Capabilities.** The dApp requests what it wants (which accounts, which operations); the wallet grants, and remembers grants for trusted origins.

In the extension this is three pieces of code: a **content script** that only relays messages and never holds a key, the **background service worker** running `BackgroundConnectionHandler` for sessions, routing and approvals, and the **offscreen document** running the `BaseWallet` subclass. Sessions must survive the service worker being restarted, which means persisting them and re-establishing the port to the offscreen document on wake.

### The approval UI

The popup is where the wallet's policies become visible: connection requests with the emoji grid, transaction requests with the calls decoded to something a person can read, capability grants, account creation and deployment, and the proving progress. The reference extension keeps pending requests in the service worker with a badge count, and answers the dApp only after the popup's decision travels back.

## What has to be built, in order

A working order, each step testable on a local network (`aztec start --local-network`) before the next.

| Step | Deliverable | Depends on |
|---|---|---|
| 1 | Key generation, encrypted storage, password flow; deterministic address shown without network access | Web Crypto, `@aztec/accounts`, `@aztec/aztec.js/keys` |
| 2 | PXE running in the wallet's process (Node, web page, or offscreen document), synced against a node | `@aztec/pxe`, a node URL, WASM shipping |
| 3 | Account deployment, paid by the Sponsored FPC on a test network | step 2, `SponsoredFeePaymentMethod` |
| 4 | A `BaseWallet` subclass: accounts, `completeFeeOptions`, `sendTx` with authwit capture; a first transfer end to end | steps 2–3 |
| 5 | The wallet SDK protocol: discovery, key exchange, emoji verification, capabilities, approval matrix | `@aztec/wallet-sdk`, step 4 |
| 6 | Sender registration and contact management, so notes from known counterparties are discovered; scanning from before deployment | step 2 |
| 7 | The three PXE hooks with real policies and prompts | step 5 |
| 8 | Backup and recovery: keys, contract salt, registered senders, and any note delivered off chain | steps 1 and 6 |
| 9 | Fee options beyond sponsorship: a Fee Juice bridge, ecosystem FPC quotes | step 4 |
| 10 | Own-node option, or a documented choice of node, for users who do not want a third party to see their tag queries | step 2 |

The reference implementation for steps 1 to 5 is the `test-extension` in the Aztec documentation examples (`docs/examples/webapp-tutorial/test-extension` at v5.2.0), which the six-part *Building a Wallet Extension* tutorial walks through. It is a tutorial, not a product: single account contract, sponsored fees only, no recovery.

## The traps

Collected from the documentation and the reference extension's comments.

- **Backing up the seed is not backing up the wallet.** Keys let the wallet re-derive addresses and re-scan the chain, but discovery needs the tagging secrets: on-chain handshakes can be rediscovered, address-derived tags only for senders the wallet re-registers, and a note delivered *off chain* (`MessageDelivery::offchain()`) is not on the chain at all. A recovery flow must restore registered senders and off-chain notes, or tell the user which funds it cannot see.
- **Deployment before receipt is unnecessary, scanning before deployment is not.** Users share their address before deploying; the wallet must scan blocks older than the deployment.
- **A "view" is a disclosure.** Reading a token balance is a utility function over private notes. When a dApp or a contract asks for it across a contract boundary, the `authorizeUtilityCall` hook is the only thing standing between the user's balance and an unknown contract; the default denies, and a wallet that auto-approves to reduce prompts has removed the protection.
- **The node sees the tags you ask for.** Sync queries a node by tag; the node learns which tags, and so which transactions, an IP address is interested in. The documentation names this as a known trade-off and running one's own node as the mitigation; oblivious retrieval is a stated long-term goal, not a feature.
- **The service worker dies.** Five minutes idle and Chrome stops it; the PXE, the proof in progress and the session table must not live there. Offscreen document for state, persisted sessions for the protocol, a port with reconnection for the two to talk.
- **Oracle versions must match.** Every contract records the Aztec.nr oracle version it was compiled against; a PXE on an older major refuses to run it. A wallet ships a PXE, so it ships a version, and its update cadence is a compatibility promise to every dApp.
- **The Sponsored FPC is not on mainnet.** A wallet that only knows sponsorship works on the local network and testnet and fails on mainnet, where ecosystem FPCs or bridged Fee Juice are the options.
- **Two "senders".** The account that sends a transaction and the *sender for tags* are different notions; the wallet supplies the latter by default and a contract may override it. Registering "the sender" for discovery means the tagging sender.

## The wallets that exist today

As of September 2026, with Aztec's V5 line in alpha (the fees documentation speaks of "mainnet alpha"):

| Wallet | Form | Notes |
|---|---|---|
| [Azguard](https://azguardwallet.io/) | Browser extension (Chrome Web Store), with side panel | Self-custody wallet built for Aztec; live on the public testnet since May 2025; the wallet the Aztec documentation's *Wallets* page currently points browser users to; source on [GitHub](https://github.com/AzguardWallet). Manages Fee Juice alongside private and public balances. |
| [Obsidion](https://app.obsidion.xyz/) | Web wallet | Built around account abstraction: sign-in with passkeys (WebAuthn) or Google/Apple, an email registry so tokens can be sent to an email address, encrypted snapshot sync for recovery across devices. Acquired by Aztec Labs on 27 May 2026 together with the ZKPassport identity project. |
| `aztec-wallet` CLI | Command line, part of the Aztec toolchain | The reference wallet maintained by the Aztec team: create and deploy accounts, register contracts and senders, create authwits, bridge Fee Juice, send and simulate, profile. For developers and operators. |
| Sandbox test accounts and `EmbeddedWallet` | Library (`@aztec/wallets`) | Not a user wallet: a wallet class a dApp or a test embeds in its own process, with pre-funded accounts on the local network. What the webapp tutorial uses before switching to an extension. |
| The tutorial extension | Source in `aztec-packages` docs examples | The reference for extension builders, deliberately minimal. |

The Aztec documentation's *Wallets* page says ecosystem teams are building more and defers to the ecosystem page for the current list; no hardware wallet and no mobile wallet with in-app proving is listed there at the time of writing.

## Conclusion

An Aztec wallet is four products that Ethereum lets a wallet skip, plus the one it does not.

- **A key store** for several Grumpkin key pairs per account, where the protocol keys cannot leave the software and the address is computable before deployment.
- **A private-state database**, the PXE, that discovers notes by tag, decrypts them, validates them against the tree and answers every balance query; stateful, WASM-bound, and therefore hosted outside a service worker.
- **A prover** that turns a simulated private execution into the proof the chain accepts, in tens of seconds on the user's device.
- **A fee strategy** that gets a brand-new account past its first transaction: sponsorship on test networks, an FPC or bridged Fee Juice elsewhere.
- **A dApp gateway** with a protocol of its own: user-gated discovery, ECDH-encrypted sessions, emoji verification, capabilities, and an approval matrix.

The privacy duties are the part with no Ethereum precedent: which contract may read what, which handshake to publish, which node to trust with tag queries, and what a backup must contain beyond the seed. Two wallets exist for users today, Azguard as an extension and Obsidion as a web wallet, alongside the team's CLI and the embedded library; the reference extension shows the structure, and the build order above is what remains to make it a product.

![Mindmap of building an Aztec wallet covering what differs from Ethereum, the components (keys and accounts, PXE, prover, transaction pipeline, fees, wallet SDK protocol, approval UI), the build order, the traps, and the wallets available today]({{site.url_complet}}/assets/article/blockchain/aztec/2026-09-17-aztec-wallet-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **PXE** | Private eXecution Environment, `@aztec/pxe`: the client-side library holding keys, notes and the simulator, which runs private functions and produces proofs. |
| **Account contract** | The contract that *is* an Aztec account; it defines how a transaction is authorised (Schnorr, ECDSA, passkey, custom) and exposes the entrypoint the wallet calls. |
| **Complete address** | An address together with the public keys behind it, needed to encrypt to a recipient; broadcast at account deployment or registered by hand. |
| **`ExecutionPayload`** | What a dApp hands a wallet: function calls, pre-signed authwits, capsules and an optional fee payer; not a signed transaction. |
| **Authwit** | An authentication witness, the signed authorisation an account gives a contract to act on its behalf; private ones are captured during simulation, public ones are on-chain state. |
| **Kernelless simulation** | The PXE's default simulation mode, which computes the kernel circuits' outputs in TypeScript instead of running them, for speed and to capture authwits. |
| **Fee Juice** | The native, non-transferable fee asset, bridged from an ERC-20 on Ethereum through the `FeeJuicePortal`. |
| **FPC** | Fee-paying contract, Aztec's paymaster: declares itself fee payer in the setup phase and collects another token, or nothing (Sponsored FPC). |
| **Wallet SDK protocol** | `@aztec/wallet-sdk`'s dApp-to-wallet protocol: user-gated discovery over `postMessage`, P-256 ECDH, AES-GCM sessions, emoji verification, capabilities. |
| **Execution hook** | A PXE callback (`authorizeUtilityCall`, `resolveTaggingSecretStrategy`, `resolveCustomRequest`) through which the wallet applies a policy mid-simulation. |

### Security Implementation Checklist

For a team building a wallet, or reviewing one.

#### Keys and storage

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Root secrets and salts are encrypted at rest with a password-derived, non-extractable key (PBKDF2 with a high iteration count, AES-GCM, fresh IV per record) and are never held in the service worker or a content script. | Extension storage is readable by anyone with the profile; a plaintext secret there is the whole wallet. |
| ☐ | Password verification decrypts a known plaintext rather than comparing a stored hash. | A stored hash is an offline brute-force target. |
| ☐ | The address is derived locally and shown before deployment, and the contract class and salt used are stored with the account. | An address derived with a different class or salt is unreachable; funds sent to it are lost. |
| ☐ | Backup includes the contract salt, registered senders and off-chain notes, and the recovery UI states what it cannot restore. | A seed-only backup silently loses funds delivered off chain or from unregistered senders. |

#### Private state and privacy

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | `authorizeUtilityCall` is implemented with a per-call decision that inspects caller and target (address and class id), and is never auto-approved. | An unknown contract reads the user's balances and notes through a utility call. |
| ☐ | Private state is disclosed to a dApp only under a granted capability, per origin, with the grant visible and revocable. | Any page that connects can enumerate the user's notes. |
| ☐ | The tagging strategy is chosen consciously: the non-interactive default is disclosed to the user as "the chain will show this address was contacted", and interactive handshakes are only chosen when the recipient can be reached. | An unexpected on-chain handshake reveals a relationship; an interactive one fails the send. |
| ☐ | The node used for sync is user-configurable and the trade-off (the node sees the queried tags) is documented. | Users assume the node learns nothing. |
| ☐ | Sync covers blocks before the account's deployment. | Notes received before deployment are never found. |

#### Transactions and dApp channel

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | `sendTx`, and any batch containing one, requires explicit approval with the calls decoded; read-only methods do not create prompts the user learns to click through. | Prompt fatigue, or a transaction sent without consent. |
| ☐ | Private authwits are captured from the simulation of the transaction being approved and signed only for it; nothing signs an arbitrary message hash a dApp supplies. | A dApp obtains a blanket authorisation to move the user's tokens. |
| ☐ | Discovery answers only after a user action; sessions use the SDK's ECDH and AES-GCM channel; the emoji verification is shown and required for new origins. | A page enumerates installed wallets, or interposes itself between dApp and wallet. |
| ☐ | Sessions and pending approvals survive a service worker restart, and stale sessions from a refreshed tab are terminated. | Approvals are lost, or a dead session keeps a capability alive. |
| ☐ | The fee payer of each transaction is shown, and the wallet has a working fee path on the target network (sponsor, FPC or Fee Juice). | Transactions fail on mainnet, or the user pays a fee it did not see. |
| ☐ | The shipped PXE's oracle version is tracked against the contracts users interact with, and updates are timely. | Contracts compiled against a newer Aztec.nr fail to execute in the wallet. |

## Frequently Asked Questions

**Q: Why can the wallet not just ask a node for the user's balance, as an Ethereum wallet does?**

Because a private balance is not on the node in readable form. It is a set of notes published as encrypted logs, findable only by tags derived from secrets the recipient shares with each sender, and decryptable only with the recipient's viewing key. The node stores the logs and indexes them by tag; it does not know which tags are the user's, nor what the logs say.

The wallet's PXE computes the tags, fetches the logs, decrypts them, checks each note against the note hash tree and stores it; "balance" is then a query on that local store.

**Q: What does the PXE need from the wallet, and what does the wallet need from the PXE?**

In each direction:

- **wallet → PXE**: a node to sync from, the accounts and their keys, the senders to watch, the contract artifacts to run, a storage backend, and the three optional policy hooks;
- **PXE → wallet**: the simulator, the note database, the key store's oracles, `proveTx`, and note discovery.

The wallet's `BaseWallet` subclass sits on top: it turns a dApp's `ExecutionPayload` into an execution request through the account contract, calls the PXE to simulate and prove, and sends the result to the node.

**Q: Can a hardware wallet hold an Aztec account's keys?**

Only the signing key, and only for an account contract designed for that signature scheme. The nullifier and incoming viewing keys are needed inside the PXE's oracles during simulation and sync, and the documentation states that in the current architecture they "need to be available in the wallet software itself and cannot be delegated to an external keystore". A hardware-backed Aztec wallet today is therefore a hybrid: the device authorises transactions, the software decrypts and spends notes.

**Q: How does a brand-new user send a first transaction without any funds?**

Three routes, all decided in the wallet's `completeFeeOptions`:

- on the local network, devnet and testnet, the **Sponsored FPC** pays unconditionally, so account deployment and the first transfers cost the user nothing;
- on mainnet, an **ecosystem FPC** pays Fee Juice in exchange for another token, under a signed quote and an authwit, in the transaction's setup phase;
- or the user **bridges Fee Juice** from Ethereum to its future address and the account pays for its own deployment, the protocol allowing a claim and a spend in one transaction.

**Q: What does the wallet SDK protocol protect against that `window.ethereum` does not?**

Two things. Enumeration: discovery requires the user to click in the wallet before it answers, so a page cannot learn which wallets are installed. Interposition and eavesdropping: after an ECDH exchange on P-256, every message is AES-GCM encrypted, so other scripts on the page cannot read calls that may carry private state, and the emoji grid derived from the exchange lets the user check that the dApp and the wallet share the same session and no page sits in between.

**Q: What must a backup contain, beyond the seed?**

Three things:

- the **contract class and salt** of each account, without which the address cannot be re-derived;
- the **registered senders**, without which address-derived tags cannot be recomputed and their notes not found;
- any **note delivered off chain**, which exists nowhere but in the wallet that received it.

On-chain handshakes can be rediscovered from the chain with the keys alone. A recovery flow that restores only the seed re-derives the accounts and finds the handshaked notes; it should say which of the rest it could not recover.

**Q: Which wallets can I use on Aztec today?**

As of September 2026:

- **Azguard**, a browser extension live on the public testnet and the one the Aztec documentation currently points browser users to;
- **Obsidion**, a web wallet with passkey and email sign-in, acquired by Aztec Labs in May 2026;
- the **`aztec-wallet`** command-line reference wallet, for developers;
- for dApps and tests rather than users, the **`EmbeddedWallet`** library and the sandbox's test accounts.

The documentation notes that more are being built and lists none for hardware or mobile at the time of writing.

## References

### Aztec documentation

- [Wallets](https://docs.aztec.network/developers/docs/foundational-topics/wallets) — responsibilities of a wallet: account setup, transaction lifecycle, authorisations, key management, recipient addresses, private state
- [Private Execution Environment (PXE)](https://docs.aztec.network/developers/docs/foundational-topics/pxe) — components, oracle versioning
- [Execution hooks](https://docs.aztec.network/developers/docs/foundational-topics/pxe/execution_hooks) — `authorizeUtilityCall`, `resolveTaggingSecretStrategy`, `resolveCustomRequest`
- [Keys](https://docs.aztec.network/developers/docs/foundational-topics/accounts/keys) — key types, derivation, address derivation, the external-keystore limitation
- [Accounts](https://docs.aztec.network/developers/docs/foundational-topics/accounts) — account contracts, Schnorr and ECDSA reference implementations
- [Fees](https://docs.aztec.network/developers/docs/foundational-topics/fees) — Fee Juice, bridging, FPCs, the Sponsored FPC's availability
- [Note discovery](https://docs.aztec.network/developers/docs/foundational-topics/advanced/storage/note_discovery) — tags, strategies, the node-side privacy trade-off
- [Building a Wallet Extension](https://docs.aztec.network/developers/docs/tutorials/js_tutorials/wallet-extension) — the six-part tutorial: architecture, wallet protocol, PXE integration, accounts, transactions, approval UI
- [Wallet SDK: dApp integration](https://docs.aztec.network/developers/docs/tutorials/js_tutorials/webapp/wallet-sdk/dapp-integration) and [wallet extension integration](https://docs.aztec.network/developers/docs/tutorials/js_tutorials/webapp/wallet-sdk/wallet-integration)
- [Wallets (participate)](https://docs.aztec.network/participate/basics/wallets) — the user-facing list: Azguard, the CLI wallet, sandbox developer wallets
- [Aztec Wallet CLI reference](https://docs.aztec.network/developers/docs/cli/aztec_wallet_cli_reference)

### Analyzed source

- [AztecProtocol/aztec-packages](https://github.com/AztecProtocol/aztec-packages) — analyzed at tag [v5.2.0](https://github.com/AztecProtocol/aztec-packages/tree/v5.2.0), commit [`49a592109ec4f18d79212b43d621891aaf36f7b6`](https://github.com/AztecProtocol/aztec-packages/tree/49a592109ec4f18d79212b43d621891aaf36f7b6), 2026-09-17: `docs/examples/webapp-tutorial/test-extension/` (the reference extension), the `@aztec/pxe`, `@aztec/wallet-sdk`, `@aztec/wallets` and `@aztec/accounts` packages at 5.2.0

### Wallets

- [Azguard Wallet](https://azguardwallet.io/) — [Chrome Web Store listing](https://chromewebstore.google.com/detail/azguard-wallet/pliilpflcmabdiapdeihifihkbdfnbmn), [GitHub organisation](https://github.com/AzguardWallet)
- [Obsidion Wallet](https://app.obsidion.xyz/) — [Aztec Labs acquires Obsidion, pledges to keep ZKPassport open-source (Crypto Briefing, 27 May 2026)](https://cryptobriefing.com/aztec-labs-acquires-obsidion-zkpassport/)
- [Request for Grant Proposals: Wallets (Aztec forum)](https://forum.aztec.network/t/request-for-grant-proposals-wallets/6136)

### Related articles

- [How Aztec Works — Private Execution, Notes and Nullifiers, and a Comparison with Zama FHE, Zcash, Canton and Railgun]({{site.url_complet}}/2026/09/08/how-aztec-works-private-execution-model/)
- [Native Account Abstraction on Aztec, Compared with ERC-4337]({{site.url_complet}}/2026/09/09/aztec-native-account-abstraction-vs-erc-4337/)
- [Ephemeral Keys on Aztec — Encrypting to an Address, the Curve Behind It, and What a Quantum Computer Would Break]({{site.url_complet}}/2026/09/17/aztec-ephemeral-keys-ecdh-encryption-post-quantum/)
- [Randomness on Aztec — One Oracle, Four Uses, and Why the Circuit Never Checks It]({{site.url_complet}}/2026/09/17/aztec-randomness-notes-oracle-unconstrained/)
- [Partial Notes on Aztec — Deferred Completion and Private DeFi Composability]({{site.url_complet}}/2026/09/09/aztec-partial-notes-private-defi-composability/)
