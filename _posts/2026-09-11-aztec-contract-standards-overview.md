---
layout: post
title: "Aztec Contract Standards — AIP-20, AIP-721, ARC-1155, ARC-403, AIP-4626 and the Escrow Standard"
date:   2026-09-11
lang: en
locale: en-GB
categories: blockchain ethereum ZKP
tags: aztec zkp privacy token erc20 erc721 erc1155 erc4626 smart-contracts
description: "Aztec's ERC equivalents share one design: a private note balance and a public balance per account, transfers named by domain, authwits instead of approve."
image: /assets/article/blockchain/aztec/2026-09-11-aztec-contract-standards-overview-mindmap.png
isMath: false
---

Ethereum has ERC-20, ERC-721, ERC-1155 and ERC-4626, and a wallet, an exchange or a lending protocol can integrate any token that implements them without talking to its author. Aztec, a privacy-preserving L2 whose contracts run half on the user's device and half on a sequencer, needs the same kind of conventions, and they cannot be the Ethereum ones: a balance that lives in encrypted notes has no `balanceOf` anyone else can call, and an allowance table would publish exactly what the chain exists to hide.

The standards that fill that role are maintained by Wonderland in the `defi-wonderland/aztec-standards` repository and mirrored in the Aztec developer documentation. They are numbered after their Ethereum counterparts where one exists: AIP-20 (fungible token), AIP-721 (NFT), AIP-4626 (tokenized vault), with the newer ARC-1155 multi-token and the ARC-403 authorization hook, plus an Escrow standard with no ERC equivalent and two utilities. The repository mixes two prefixes, AIP for the older documents and ARC for the newer ones; they name the same family, and this article uses whichever spelling the repository does for each standard.

This article is the map. It reads every contract in the repository at one pinned commit, explains the conventions all of them share, then walks through each standard by what it adds and what it deliberately leaves out. A companion article covers [AIP-20 alone in depth and against ERC-20 and ERC-7984]({{site.url_complet}}/2026/09/11/aip-20-aztec-token-standard-vs-erc-20-erc-7984/); this one stays at the level of the family.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The family at a glance

| Standard | Contract | Ethereum analogue | What it standardises |
|---|---|---|---|
| AIP-20 / ARC-20 | `Token` | [ERC-20](https://eips.ethereum.org/EIPS/eip-20) | Fungible token with a private and a public balance per account |
| AIP-721 / ARC-721 | `NFT` | [ERC-721](https://eips.ethereum.org/EIPS/eip-721) | Non-fungible token with private or public ownership per id |
| ARC-1155 | `MultiToken` | [ERC-1155](https://eips.ethereum.org/EIPS/eip-1155) | Many fungible ids in one contract, each balance private or public |
| ARC-403 | any `AuthorizationContract` | (no single ERC; closest to ERC-1400/3643 transfer hooks) | Pluggable policy called before every transfer and burn |
| AIP-4626 | `Vault` + `VaultDeployer` | [ERC-4626](https://eips.ethereum.org/EIPS/eip-4626), [ERC-7575](https://eips.ethereum.org/EIPS/eip-7575) | Yield vault whose shares are a separate AIP-20 token |
| Escrow | `Escrow` + Logic library | — | Keyed private custody controlled by a policy contract |
| — | `GenericProxy`, `Dripper` | — | Call forwarding; development faucet |

Everything below refers to the repository at commit `a3859e5`, built against Aztec `v5.0.0-rc.2`; the exact revision is pinned in the references.

![Dependency map of the Aztec standards: Token and MultiToken call an ARC-403 authorization contract, the Vault mints a separate AIP-20 shares token and is wired by a VaultDeployer, a Logic contract owns an Escrow that spends Token and NFT private balances, and Dripper and GenericProxy call into Token]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-standards-dependency-map-concept.png)

## Conventions every standard shares

The standards are consistent enough that learning one teaches most of the others. Six conventions recur.

### Two balances per account

Every asset contract keeps a *private* balance and a *public* balance for each account. The public one is ordinary sequencer state, a `Map<AztecAddress, PublicMutable<u128>>` for tokens or a `Map<Field, PublicMutable<AztecAddress>>` of owners for NFTs, and behaves like an EVM mapping. The private one is a set of *notes*, small structs whose hash sits in the chain's note hash tree and whose plaintext only the owner's PXE (the private execution environment on the user's device) holds. Spending a note emits its nullifier; nobody else can tell which note was spent or by whom. The [protocol article]({{site.url_complet}}/2026/09/08/how-aztec-works-private-execution-model/) on this site covers the machinery; here it is enough that a private balance is a bag of notes and a public balance is an integer.

Each standard defines its own note type: `UintNote { owner, randomness, value: u128 }` for AIP-20, `NFTNote { token_id }` for AIP-721, `MultiTokenNote { token_id, value }` for ARC-1155. All three support *partial notes* (below).

### Transfers named by the domains they cross

There is no overloaded `transfer`. A function is named `transfer_<source>_to_<destination>` with `private`, `public` or `commitment` in each slot, so the caller states which balance is debited and which is credited:

- `transfer_private_to_private` runs entirely on the client and emits nothing public.
- `transfer_private_to_public` and `transfer_public_to_private` cross domains: the private half runs first and *enqueues* a public call that the sequencer executes afterwards.
- `transfer_public_to_public` is a plain public function.
- `transfer_private_to_commitment` and `transfer_public_to_commitment` credit a partial note instead of an address.

Aztec executes private functions before public ones and a private function cannot read the result of a call it enqueues, so the cross-domain functions are written to be safe under that order: `transfer_public_to_private` creates the recipient's note first and enqueues the public debit; if the debit underflows, the public call reverts and the transaction's revertible private side effects, the note included, are discarded.

### `from` plus `nonce` instead of `approve`

No standard has `approve`, `allowance` or `transferFrom`. Every spending function takes a `from` and a `nonce` and carries the `#[authorize_once("from", "_nonce")]` macro. When `from` is the caller, the nonce must be zero and no further check runs. When it is not, the macro demands an *authentication witness* (authwit): a signature by `from`'s account contract over the exact call, including the nonce, verified inside the proof for private functions and read from an on-chain registry for public ones, and nullified so it works once. The [account-abstraction article]({{site.url_complet}}/2026/09/09/aztec-native-account-abstraction-vs-erc-4337/) covers the witness format; for the standards, the consequences are that authorisation is per call rather than per amount, and that a single call can authorise only one `from`.

### Commitments, for a recipient fixed before the amount

`initialize_transfer_commitment(to, completer) -> Field` creates a partial note owned by `to` whose value is filled in later by whoever is `completer`, in public or private execution, through `transfer_*_to_commitment` or `mint_to_commitment`. This is how a vault can mint a share amount that is only computable in public execution to a recipient chosen in private execution. The completer must equal `msg_sender` at completion; nothing in the protocol or the token stops a commitment being completed twice, which the [partial-notes article]({{site.url_complet}}/2026/09/09/aztec-partial-notes-private-defi-composability/) discusses at length.

### A public event with a sentinel for the hidden side

Public-side operations emit an ERC-style event, `Transfer { from, to, amount }`, `Transfer { from, to, token_id }` or `TransferSingle { from, to, id, amount }`. When one side of the movement is private, that side is replaced by the constant `PRIVATE_ADDRESS`, the SHA-224 of the string, so an indexer sees `Transfer(PRIVATE_ADDRESS, bob, 100)` for a private-to-public move. `0x0` marks mint origin and burn destination as on Ethereum. Fully private operations emit nothing.

### Bounded note consumption

A private debit has to gather notes whose values sum to the amount, nullify them all, and return the excess as a new "change" note. Reading and proving a note costs circuit constraints, so the standards cap it: the first attempt consumes at most 2 notes (`INITIAL_TRANSFER_CALL_MAX_NOTES`), and if that is short the contract recurses through a private self-call taking 8 per round (`RECURSIVE_TRANSFER_CALL_MAX_NOTES`). A round that gathers nothing fails the proof with `"Balance too low"`. Two smaller conventions follow from the same circuit economics: amounts are `u128`, not `uint256`, and `name`/`symbol` are 31-byte strings packed into a single field.

## AIP-20 / ARC-20 — the fungible token

`Token` is the reference for everything else, and the companion article dissects it. In the family view, three facts matter.

Its storage is the pattern the others vary:

```rust
private_balances: Owned<BalanceSet<Context>, Context>,
total_supply: PublicMutable<u128, Context>,
public_balances: Map<AztecAddress, PublicMutable<u128, Context>, Context>,
minter: PublicImmutable<AztecAddress, Context>,
auth_contract: PublicImmutable<AztecAddress, Context>,
```

It has two supply models chosen at construction: `constructor_with_initial_supply` mints everything publicly to one address and leaves `minter` unset, so minting is permanently disabled; `constructor_with_minter` names a single immutable minter (a bridge, a vault, a faucet) that can call `mint_to_public`, `mint_to_private` and `mint_to_commitment`.

And `total_supply` is public. Every private mint or burn enqueues a public supply update and emits `Transfer(0x0, PRIVATE_ADDRESS, amount)`, so the *amount* of a private mint is visible even though the recipient is not. This is the one place where the family's privacy differs by standard: ARC-1155 has no `total_supply` and leaks nothing on a private mint.

## ARC-403 — the authorization hook

ARC-403 is not an asset but a policy interface. A token constructed with a non-zero `auth_contract` calls it on every transfer and burn, after the authwit check and before any balance changes, and reverts if the hook reverts:

```rust
fn authorize_private(from: AztecAddress, amount: u128, selector: Field)  // from private token functions
fn authorize_public(from: AztecAddress, amount: u128, selector: Field)   // from public token functions
```

`selector` is the calling token function's own selector, so a policy can treat `transfer_public_to_private` (which reveals `from` and the amount publicly despite calling the private hook) differently from `transfer_private_to_private`. Mints are not hooked; the minter gate already covers them.

The hook never receives `to`. Commitment transfers seal the recipient inside a hash the sender cannot see, so the recipient cannot be supplied consistently, and the standard omits it everywhere rather than pass it sometimes. The documented consequence is that a policy can stop a blocked account from spending but not from receiving. Allowlists, pause switches, transfer caps and sanctions screens fit; recipient-side blocks do not. Reference policies live in a separate `aztec-arc403-extensions` repository.

`Token` and `MultiToken` implement the hook (the multi-token variant adds an `id` parameter). `NFT` and `Vault` do not. The token's own history records the hazard of an external call before a balance write: a reentrancy fix in the refund ordering (PR #298) is why the hook sits where it does.

## AIP-721 / ARC-721 — the NFT

`NFT` keeps the transfer matrix of AIP-20 with `token_id: Field` in place of `amount`, and replaces the balance sets with ownership maps:

```rust
private_nfts: Owned<PrivateSet<NFTNote, Context>, Context>,
nft_exists: Map<Field, PublicMutable<bool, Context>, Context>,
public_owners: Map<Field, PublicMutable<AztecAddress, Context>, Context>,
minter: PublicImmutable<AztecAddress, Context>,
```

`nft_exists[id]` is the global existence bit and is set on any mint and cleared on any burn. `public_owners[id]` is the owner while the token is public and is written to zero when it moves private, so a public `owner_of` returning zero for an existing id means "held privately by someone". A private transfer pops exactly one `NFTNote` with the matching id from the sender's set (`"nft not found"` otherwise) and creates one for the recipient. Token id zero is rejected at mint.

Three differences from AIP-20 are easy to miss: there is no ARC-403 hook, the metadata getters are `public_get_name`/`public_get_symbol` rather than `name`/`symbol`, and the private reader is `get_private_nfts(owner, page_index)`, which returns a page of ids with a flag saying whether more pages exist. Events follow the AIP-20 matrix with `token_id` as the third field.

## ARC-1155 — the multi-token

`MultiToken` holds many fungible ids in one contract. Every balance function gains an `id: Field` argument, and the storage collapses all of an owner's ids into a single private set whose notes describe their own id:

```rust
private_balances: Owned<MultiBalanceSet<Context>, Context>,   // MultiTokenNote { token_id, value }
public_balances: Map<Field, Map<AztecAddress, PublicMutable<u128, Context>, Context>, Context>,
```

A private debit of id `x` selects notes where `token_id == x` inside that set, with the same 2-then-8 caps. `initialize_transfer_commitment` is id-agnostic: the completer binds both the id and the amount when it finishes the note.

Two deliberate omissions define the standard. There is no `decimals` and no `total_supply`, so a private mint or burn has no public footprint at all. And the `TransferSingle` event is emitted only when the id is already public, that is on any operation that touches a public balance or completes a commitment in public; mint-to-private, burn-from-private and private-to-private emit nothing, because an id-bearing event would reveal which asset moved. There are no batch functions and no `TransferBatch`. The ARC-403 hook is present in its id-bearing form, so a policy can differ per id.

## AIP-4626 — the tokenized vault

The vault is where the family departs furthest from its Ethereum model. An ERC-4626 vault *is* its share token; an AIP-4626 vault is a standalone contract that references two AIP-20 tokens, the underlying `asset` and a `shares` token whose `minter` is the vault, a structure closer to ERC-7575. The vault holds the asset publicly, but each leg of a deposit or withdrawal can be private or public, which multiplies the function surface: `deposit`, `issue` (exact shares out), `withdraw` (exact assets out) and `redeem` (shares in) each exist in public, private and cross-domain variants named `<op>_<source>_to_<destination>`.

The interesting design problem is that the exchange rate is public state, and a private function cannot read it. The vault offers two answers:

- **Standard pattern**: the caller supplies both `assets` and `shares` (for example `deposit_private_to_private(from, to, assets, shares, nonce)`). Public execution checks the pair against the rate; a mismatch either reverts or leaves the difference to the vault, never to the user.
- **Exact pattern**: the caller supplies `assets` and a `min_shares` floor (`deposit_private_to_private_exact`). The private half moves the assets, mints `min_shares` immediately so the user can use them, and opens a commitment on the shares token; the enqueued public half computes the true share amount and mints the outstanding remainder to the commitment, so the recipient is never named in public.

![Sequence of the AIP-4626 exact deposit: the private vault half opens a shares commitment, pulls assets via transfer_private_to_public, mints min_shares privately and enqueues settlement; the public half recomputes the rate and mints the outstanding shares to the commitment]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-vault-exact-deposit-sequence.png)

The ordering inside the private half is itself a security decision: the asset transfer happens before the share mint, a comment in the source noting it "neutralizes ARC-403 reentrancy", since the asset token may call an external hook.

Conversion uses a virtual-shares offset, `shares = assets · (total_supply + vault_offset) / (total_assets + 1)`, the OpenZeppelin defence against inflation attacks on an empty vault; choosing the offset is left to the deployer. The README is candid about the standard's status: the multiplication can overflow `u128` for large inputs (an open TODO), `max_*` and `preview_*` are advisory and see only public share balances, assets sent to the vault's *private* balance are unrecoverable because the vault has no keys, and several `*_public_to_private*` functions can leak the `to` address because every other argument is public and the authwit hash can be brute-forced over candidate recipients. The section is headed "not yet production-ready".

Deployment needs a `VaultDeployer`: a disposable contract, one instance per vault, whose private initializer derives both addresses, publishes both instances, enqueues both constructors and links them with `set_shares_token`. A reusable public factory is not possible yet because instance publication is a private-only operation.

## The Escrow standard

The Escrow is the one standard with no Ethereum counterpart, because it solves a problem Ethereum does not have: a contract cannot hold a private balance unless it has *keys*, since reading a note needs the incoming-viewing key and spending it needs the nullifier key.

The `Escrow` contract is therefore a keyed, storage-less, initializer-less private contract with exactly two functions, `withdraw(token, amount, recipient)` and `withdraw_nft(nft, token_id, recipient)`, each of which calls `transfer_private_to_private` from the escrow's own balance. Its owner is not stored anywhere: it is the `AztecAddress` encoded in the contract instance's *salt*, so the owner is immutable and determines the escrow's address. The only check is `salt == msg_sender` (`"Not Authorized"` otherwise). The escrow need not even be publicly deployed; it exists as soon as someone can compute its address and holds its keys.

The owner is a *Logic* contract, which implements the policy (vesting schedule, clawback, milestone release) and is the part that varies per use case. A Logic library standardises the mechanics: `_get_escrow(context, class_id, secret_key)` recomputes the escrow address from a secret key with the Logic contract's own address as salt; `_share_escrow(context, account, escrow, secret_key)` delivers the address and the secret key to a participant as a private log; `_withdraw` and `_withdraw_nft` forward to the escrow. A bundled `key_derivation` module reproduces the protocol's key derivation in Noir so the secret key never leaves private execution; it depends on an unaudited SHA-512 library, which the README flags.

![Escrow lifecycle in private execution: the depositor derives the escrow address through the Logic contract, funds it with a private transfer, shares the secret key as a private log, and the recipient later withdraws through Logic, which the escrow accepts only from its salt owner]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-escrow-lifecycle-sequence.png)

Because every step is a private function calling another private function, an escrow leaves no public trace: no event, no public state, no enqueued call. The cost is that the Logic contract carries the whole security burden; the library checks keys and class ids but cannot check that the policy is sound.

## Utilities: GenericProxy and Dripper

`GenericProxy` is a set of private forwarders, `forward_private_0(target, selector)` through `forward_private_8(target, selector, args: [Field; 8])`, plus one variant that returns a field. It relays `call_private_function` with no authorisation and no storage; a callee that inspects `msg_sender` sees the proxy. `Dripper` is a faucet: `drip_to_public` and `drip_to_private` mint a `u64` amount of any token that names the Dripper as its minter. Its README says "do not use in production" and means it.

## What the family does not standardise

Reading the repository as a whole, some absences are as informative as the contents.

- **No allowance queries.** Since authorisation is an authwit over a call, there is no `allowance(owner, spender)` view and no `Approval` event in any standard.
- **No third-party balance reads for private state.** `balance_of_private` and `get_private_nfts` are unconstrained utility functions that run only in the owner's PXE. A protocol proves solvency by transferring, not by reading.
- **No receiver callbacks.** Nothing corresponds to ERC-1363 or ERC-721's `onERC721Received`; composability goes through commitments instead.
- **No metadata URI for NFTs**, and no per-id metadata for multi-tokens: `name` and `symbol` only.
- **No upgradeability**: it was removed from the vault (PR #295), and no contract exposes an upgrade path.
- **No `total_supply` for NFTs or multi-tokens**, on purpose.
- **No recipient-side policy** in ARC-403, because commitment transfers keep the recipient out of the sender's view.

## Conclusion

The Aztec standards are a single design applied five times. Each asset gives every account a private note balance and a public balance, names its transfers by the domains they cross, authorises third-party spending with a per-call authwit carried in `from` and `nonce`, uses partial-note commitments when a recipient must be fixed before an amount, and emits ERC-shaped events with a `PRIVATE_ADDRESS` sentinel on the public side only. AIP-20 sets the pattern and keeps a public total supply; AIP-721 swaps balances for ownership maps and drops the hook; ARC-1155 folds many ids into one note set and drops total supply so that private mints leak nothing; ARC-403 externalises policy into a contract that sees the spender, the amount and the function but never the recipient; AIP-4626 splits vault and share token and offers a standard and an exact pattern for private legs, with several documented limits; the Escrow standard gives a contract keys and a salt-encoded owner so that a policy contract can hold private funds without any public footprint.

For an integrator, the practical summary is that the family is consistent enough that the conventions transfer between contracts, and that the places where privacy is weaker than it looks are documented in the READMEs rather than hidden: the public supply in AIP-20, the public side of every cross-domain move, the `to` leak in some vault functions, and the vault's open overflow issue.

![Mindmap of the Aztec contract standards covering shared conventions, AIP-20, AIP-721, ARC-1155, ARC-403, AIP-4626, the Escrow standard and the utilities]({{site.url_complet}}/assets/article/blockchain/aztec/2026-09-11-aztec-contract-standards-overview-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **AIP / ARC** | Aztec Improvement Proposal / Aztec Request for Comments, the two prefixes the repository uses for the same family of standards; the number mirrors the Ethereum ERC where one exists. |
| **Note** | The unit of private state: a struct whose hash is inserted into the note hash tree and whose plaintext only the owner's PXE holds; a private balance is a set of notes. |
| **Nullifier** | The value emitted when a note is spent, unlinkable to the note by outsiders and rejected if emitted twice. |
| **PXE** | Private Execution Environment, the client-side component that holds keys and notes and executes private functions to produce a proof. |
| **Authwit** | Authentication witness: a signature by an account contract over one exact call, used once, that lets a caller spend on behalf of `from` in place of an ERC-20 allowance. |
| **Commitment / partial note** | A note whose owner is fixed in private execution and whose value is completed later by a designated completer, used by `*_to_commitment` and `mint_to_commitment`. |
| **PRIVATE_ADDRESS** | The sentinel address, SHA-224 of the string, that stands for the private side of a cross-domain movement in public events. |
| **Minter** | The single immutable address allowed to call the `mint_to_*` functions of a token, NFT or multi-token; unset means minting is disabled. |
| **Exact pattern** | The vault variant in which the caller gives a floor (`min_shares` or `min_assets`) and public execution settles the remainder through a commitment at the true rate. |
| **Logic contract** | The application-specific contract that owns one or more Escrows (its address is their salt) and decides when and to whom they release funds. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| No standard exposes `approve`/`allowance`; spending on behalf of a user needs an authwit for the exact call and a fresh nonce. | Build authwit generation into the wallet flow; nonce is `0` only when `from` is the caller. |
| Private balances cannot be read by another contract; `balance_of_private` is an unconstrained utility. | Never gate logic on it; let the token's transfer prove sufficiency. |
| Cross-domain transfers reveal the public side (`from` or `to`, and the amount) in a public event with `PRIVATE_ADDRESS` on the other side. | Treat only `private_to_private` as fully private when reasoning about leakage. |
| AIP-20 `total_supply` is public, so private mint and burn amounts are public; ARC-1155 has no supply. | Pick ARC-1155 when mint amounts are sensitive, or mint publicly to a pool and distribute privately. |
| A commitment can be completed twice; the token does not prevent it. | Track completion in the application and complete exactly once. |
| ARC-403 hooks receive `(from, amount, selector)` and never `to`; NFT and Vault are not hooked. | Enforce recipient-side rules on spend or at the application layer; do not assume the vault runs the token's policy. |
| AIP-721 metadata getters are `public_get_name`/`public_get_symbol`, unlike the token's `name`/`symbol`; `public_owner_of` returns zero for a privately held id. | Do not share a metadata adapter between token and NFT; treat zero as "private", not "nonexistent" (check `nft_exists` semantics via mint/burn events). |
| Vault `max_*` and `preview_*` see only public state; several `*_public_to_private*` functions can leak `to`; the conversion can overflow `u128`. | Quote off previews with a margin, prefer exact-pattern functions under volatility, and bound amounts for the asset's scale. |
| Assets sent to the vault's private balance are lost. | Send yield and donations to the vault's public balance only. |
| An Escrow accepts calls only from the address in its salt; the Logic contract is the whole policy. | Audit the Logic contract as the trust boundary; the escrow itself has no policy. |

## Frequently Asked Questions

**Q: Why are there both "AIP" and "ARC" prefixes, and are they different standards?**

They are the same family. The older documents (AIP-20, AIP-721, AIP-4626) and the developer documentation use "Aztec Improvement Proposal"; the newer additions in the repository (ARC-403, ARC-1155) use "ARC", and a recent README calls the plain token "a standard ARC-20". The number, not the prefix, identifies the standard, and it mirrors the Ethereum ERC where one exists.

**Q: What do all the standards share, in one sentence each?**

- Every account has a private note balance and a public balance for each asset.
- Transfers are named `transfer_<source>_to_<destination>` over `private`, `public` and `commitment`.
- Third-party spending uses a per-call authwit carried by `from` and `nonce`, not an allowance.
- A recipient can be fixed before the amount through a partial-note commitment.
- Public-side operations emit an ERC-style event with `PRIVATE_ADDRESS` in place of the hidden party; fully private operations emit nothing.
- Private debits consume at most 2 notes, then 8 per recursive round.

**Q: Which standards implement the ARC-403 hook, and why not all of them?**

`Token` (AIP-20) and `MultiToken` (ARC-1155) call an authorization contract on every transfer and burn when one is configured; the multi-token passes the id as well. `NFT` has no hook field at all, and `Vault` does not call one directly, though the tokens it moves may. The hook never receives the recipient because commitment transfers hide the recipient from the sender, and the standard chose to omit `to` everywhere rather than pass it inconsistently.

**Q: How does an AIP-4626 vault mint shares to a private recipient when the exchange rate is only readable in public execution?**

Two ways. In the standard pattern the caller supplies both `assets` and `shares`, and public execution checks the pair against the rate, reverting or keeping any surplus for the vault. In the exact pattern the caller supplies `assets` and `min_shares`; the private half mints `min_shares` at once and opens a commitment on the shares token, and the enqueued public half computes the true share amount and mints the remainder to that commitment, so the recipient is never named in public.

**Q: Why does an Escrow need keys, and how does it know its owner without storage?**

A contract can only read a note with the incoming-viewing key and spend it with the nullifier key, so a contract that holds private balances must have a key set; the escrow derives its keys from a single secret key that the Logic contract shares with participants through a private log. The owner is the address encoded in the contract instance's salt, which is part of the address derivation, so it is immutable and needs no storage; the escrow's only check is that `msg_sender` equals that salt.

**Q: An application wants to hide the amounts of private mints. Which token standard should it use and why?**

ARC-1155. AIP-20 keeps a public `total_supply`, and every private mint or burn enqueues a public update and emits `Transfer(0x0, PRIVATE_ADDRESS, amount)`, so the amount is visible. ARC-1155 has no `total_supply`, no `decimals`, and emits `TransferSingle` only when the token id is already public; mint-to-private, burn-from-private and private-to-private leave no public footprint. The trade is losing a supply query and per-id metadata.

**Q: What can an outside observer learn from each kind of operation?**

From a private-to-private transfer, mint-to-private on ARC-1155, or an escrow withdrawal: nullifiers and note hashes that cannot be linked to accounts, and nothing else. From a cross-domain transfer: the public party and the amount (or token id), with the private party replaced by the sentinel. From a public-to-public transfer, a public mint or burn, or an AIP-20 private mint's supply update: everything, as on Ethereum. From the vault's `*_public_to_private*` functions: possibly the recipient, through the documented authwit brute-force.

## References

### Analyzed source

- [defi-wonderland/aztec-standards](https://github.com/defi-wonderland/aztec-standards) — analyzed at commit [`a3859e5ab2a41185543e9b4189ef1033dfcd1b65`](https://github.com/defi-wonderland/aztec-standards/tree/a3859e5ab2a41185543e9b4189ef1033dfcd1b65) (branch `dev`, after tag `prerelease-0200230`, built against Aztec `v5.0.0-rc.2`), 2026-09-11

### Specifications and documentation

- [Aztec Contract Standards](https://docs.aztec.network/developers/docs/aztec-nr/standards) — developer documentation index
- [AIP-20: Fungible Token](https://docs.aztec.network/developers/docs/aztec-nr/standards/aip-20)
- [AIP-721: Non-Fungible Token](https://docs.aztec.network/developers/docs/aztec-nr/standards/aip-721)
- [AIP-4626: Tokenized Vault](https://docs.aztec.network/developers/docs/aztec-nr/standards/aip-4626)
- [Request for Comments: AIP-20 Aztec Token Standard](https://forum.aztec.network/t/request-for-comments-aip-20-aztec-token-standard/7737) — Wonderland, Aztec forum
- [Request for Comments: AIP-4626 Tokenized Vault](https://forum.aztec.network/t/request-for-comments-aip-4626-tokenized-vault/8079) — Wonderland, Aztec forum
- [ERC-20: Token Standard](https://eips.ethereum.org/EIPS/eip-20), [ERC-721: Non-Fungible Token Standard](https://eips.ethereum.org/EIPS/eip-721), [ERC-1155: Multi Token Standard](https://eips.ethereum.org/EIPS/eip-1155), [ERC-4626: Tokenized Vaults](https://eips.ethereum.org/EIPS/eip-4626), [ERC-7575: Multi-Asset ERC-4626 Vaults](https://eips.ethereum.org/EIPS/eip-7575), [ERC-1363: Payable Token](https://eips.ethereum.org/EIPS/eip-1363), [ERC-1400: Security Token Standard](https://github.com/ethereum/EIPs/issues/1411), [ERC-3643: T-REX](https://eips.ethereum.org/EIPS/eip-3643)

### Extension repositories

- [defi-wonderland/aztec-arc403-extensions](https://github.com/defi-wonderland/aztec-arc403-extensions) — reference authorization contracts
- [defi-wonderland/aztec-escrow-extensions](https://github.com/defi-wonderland/aztec-escrow-extensions) — example Logic contracts (vesting, clawback)

### Related articles

- [AIP-20, the Aztec Token Standard, Compared with ERC-20 and ERC-7984]({{site.url_complet}}/2026/09/11/aip-20-aztec-token-standard-vs-erc-20-erc-7984/)
- [How Aztec Works — Private Execution, Notes and Nullifiers, and a Comparison with Zama FHE, Zcash, Canton and Railgun]({{site.url_complet}}/2026/09/08/how-aztec-works-private-execution-model/)
- [Partial Notes on Aztec — Deferred Completion and Private DeFi Composability]({{site.url_complet}}/2026/09/09/aztec-partial-notes-private-defi-composability/)
- [Native Account Abstraction on Aztec, Compared with ERC-4337]({{site.url_complet}}/2026/09/09/aztec-native-account-abstraction-vs-erc-4337/)
- [Aztec: A Privacy-First Layer 2 for Ethereum]({{site.url_complet}}/2025/10/29/aztec-architecture-overview/)
