---
layout: post
title: "AIP-20, the Aztec Token Standard, Compared with ERC-20 and ERC-7984"
date:   2026-09-11
lang: en
locale: en-GB
categories: blockchain ethereum ZKP
tags: aztec zkp privacy erc20 erc7984 fhe token smart-contracts solidity
description: "AIP-20 gives each account a private note balance and a public one, swaps approve for authwits and reverts on shortfall. ERC-7984 hides amounts, never reverts."
image: /assets/article/blockchain/aztec/2026-09-11-aip20-vs-erc20-erc7984-mindmap.png
isMath: false
---

[ERC-20](https://eips.ethereum.org/EIPS/eip-20) fixed the interface of a fungible token in 2015: one public balance per address, an allowance table, and a `transfer` that either moves the full amount or reverts. Every later token standard has had to decide what to keep from that interface and what to give up, and a privacy-preserving token has to give up the most, because the thing ERC-20 makes public is the thing it exists to hide.

Two recent standards answer that question in incompatible ways. **AIP-20**, the Aztec Token Standard written by Wonderland and implemented in `defi-wonderland/aztec-standards`, gives every account two balances, a *private* one made of notes that only the owner's device can read and a *public* one that behaves like ERC-20, and names its transfer functions by the domains they cross: `transfer_private_to_public`, `transfer_public_to_private`, and so on. [ERC-7984](https://eips.ethereum.org/EIPS/eip-7984), the Confidential Fungible Token standard drafted by OpenZeppelin and Zama, keeps a single balance per address and a familiar `confidentialTransfer(to, amount)` signature, but every amount is a `bytes32` handle to a ciphertext that the contract can add and compare without ever seeing.

This article reads the AIP-20 reference implementation at a pinned commit, then sets it beside a Solidity ERC-20 and the OpenZeppelin ERC-7984 implementation on the axes that matter to an integrator: where the balance lives and who can read it, how a third party is authorised to spend, what happens when the balance is short, what an observer learns from a transfer, and how compliance logic is attached. The short version is that AIP-20 hides sender, recipient and amount on its private side but exposes total supply; ERC-7984 hides amounts and nothing else, and does not revert.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Three answers to "where is the balance?"

A fungible token is a ledger, and the design of the ledger determines everything downstream. The three standards keep the ledger in three different places.

- **ERC-20** keeps a `mapping(address => uint256)` in contract storage. Every node holds it, every node executes the arithmetic, and anyone can call `balanceOf`. There is no secret anywhere.
- **AIP-20** keeps two ledgers. The public one is a `Map<AztecAddress, PublicMutable<u128>>` in Aztec public state, updated by the sequencer exactly like an EVM mapping. The private one is a set of *notes*: each note is a small struct (owner, value, randomness) whose hash is inserted into the chain's note hash tree, and whose plaintext is delivered to the owner as an encrypted log. Spending a note means proving, on the owner's device, that a note with that hash exists and emitting its *nullifier*, a deterministic value that marks it spent without revealing which note it was. The [protocol article]({{site.url_complet}}/2026/09/08/how-aztec-works-private-execution-model/) on this site covers the tree structure and the private-then-public execution order; this article assumes it.
- **ERC-7984** keeps a `mapping(address => euint64)` where `euint64` is a handle to a ciphertext held by an FHE coprocessor. The contract runs on an ordinary EVM and calls into `FHE.add`, `FHE.le`, `FHE.select`, which return new handles. Nobody, including the contract, sees the plaintext; a holder reads their own balance by asking a key-management service to re-encrypt the handle to their key, subject to an on-chain access control list.

![Three storage models side by side: ERC-20 public mappings, AIP-20 public balance map plus private UintNotes with a nullifier tree and public total supply, and ERC-7984 ciphertext handles resolved by an FHE coprocessor]({{site.url_complet}}/assets/article/blockchain/aztec/token-standards-balance-models-concept.png)

The consequence that drives the rest of the comparison: in AIP-20 the secret is on the *client*, so the contract's private functions run there too and produce a zero-knowledge proof; in ERC-7984 the secret is in a *ciphertext* and the contract runs on the chain as usual, blind to its own inputs. The first model can branch on the balance (and revert); the second cannot.

## AIP-20 in detail

The material below is read from the `Token` contract in `src/token_contract/src/main.nr` of `defi-wonderland/aztec-standards` at the commit pinned in the references, built against Aztec `v5.0.0-rc.2`. The forum RFC of April 2025 is the specification; where the two disagree on a name, the implementation is quoted and the drift is noted.

### Storage and metadata

```rust
#[storage]
struct Storage<Context> {
    name: PublicImmutable<FieldCompressedString, Context>,
    symbol: PublicImmutable<FieldCompressedString, Context>,
    decimals: PublicImmutable<u8, Context>,
    private_balances: Owned<BalanceSet<Context>, Context>,
    total_supply: PublicMutable<u128, Context>,
    public_balances: Map<AztecAddress, PublicMutable<u128, Context>, Context>,
    minter: PublicImmutable<AztecAddress, Context>,
    auth_contract: PublicImmutable<AztecAddress, Context>,
}
```

Three details are worth reading off this struct before looking at any function.

- **Amounts are `u128`, not `uint256`.** Noir's native type is a field element of roughly 254 bits, and a `u128` fits inside one with room for range checks. The ERC-20 `uint256` habit does not carry over; a bridge that wraps an ERC-20 into AIP-20 has to bound the amount.
- **Name and symbol are `FieldCompressedString`**, a string of at most 31 bytes packed into one field. The constructors take `str<31>`. An ERC-20 name longer than 31 characters cannot be represented.
- **`total_supply` is public** and lives next to the private balances. This is a deliberate design choice with a privacy cost discussed below.

`private_balances` is an `Owned<BalanceSet>`. `BalanceSet` is a set of `UintNote`s keyed by owner, with `add(amount)` (create a note) and `try_sub(amount, max_notes)` (consume up to `max_notes` notes and return their sum). `Owned` is the per-owner container for private state, the private counterpart of `Map`, reached with `.at(owner)`. Reading the notes it holds requires their preimages, and only the owner's PXE (the private execution environment on the user's device) has them, which is why `balance_of_private` is a `#[utility]` function rather than a view: it runs unconstrained inside that PXE over the notes it stores. Another contract cannot call it from constrained code, and there is no equivalent of `balanceOf(other)` for private balances at all.

The metadata getters are `name()`, `symbol()` and `decimals()`. The RFC lists them as `get_name`, `get_symbol` and `get_decimals`; the implementation dropped the prefix, and the ERC-20 spelling is what ships.

### Two balances, and a transfer function per pair of domains

Because each account has a private and a public balance, "transfer" is not one operation but a matrix. AIP-20 names each cell explicitly instead of overloading one function:

| Function | Context | Debit | Credit | What an observer sees |
|---|---|---|---|---|
| `transfer_private_to_private(from, to, amount, nonce)` | private | notes of `from` | new note for `to` | nullifiers and note hashes only |
| `transfer_private_to_public(from, to, amount, nonce)` | private, enqueues public | notes of `from` | public balance of `to` | `Transfer(PRIVATE_ADDRESS, to, amount)` |
| `transfer_public_to_private(from, to, amount, nonce)` | private, enqueues public | public balance of `from` | new note for `to` | `Transfer(from, PRIVATE_ADDRESS, amount)` |
| `transfer_public_to_public(from, to, amount, nonce)` | public | public balance of `from` | public balance of `to` | `Transfer(from, to, amount)` |
| `transfer_private_to_commitment(from, commitment, amount, nonce)` | private | notes of `from` | a partial note | nullifiers, private log |
| `transfer_public_to_commitment(from, commitment, amount, nonce)` | public | public balance of `from` | a partial note | `Transfer(from, PRIVATE_ADDRESS, amount)` |
| `transfer_private_to_public_with_commitment(from, to, amount, nonce) -> Field` | private, enqueues public | notes of `from` | public balance of `to`, plus a fresh partial note | `Transfer(PRIVATE_ADDRESS, to, amount)` |

Every one of them carries a `from` parameter. There is no `transfer(to, amount)` that implicitly debits the caller, and there is no separate `transferFrom`; the same function serves both, and the `nonce` parameter decides which case applies (next section).

The `PRIVATE_ADDRESS` sentinel is a constant, the SHA-224 of the string `PRIVATE_ADDRESS`, used in the public `Transfer` event whenever one side of a movement is private and cannot be named. Together with the ERC-20 convention of `0x0` for mint and burn, it lets an indexer track every public-side movement with the same three-field event ERC-20 has. A private-to-private transfer emits nothing public.

### What a private transfer does

The interesting cell is `transfer_private_to_private`, because it is the one with no ERC-20 analogue. The sequence below is what the contract's private circuit does on the sender's device, and what the resulting transaction contains.

![Sequence of an AIP-20 private-to-private transfer: authwit check, optional ARC-403 hook, note selection and nullification with recursion, change and recipient notes emitted as encrypted logs, sequencer inserts hashes and nullifiers, recipient decrypts by tag]({{site.url_complet}}/assets/article/blockchain/aztec/aip20-private-transfer-sequence.png)

The body of the function is four calls:

```rust
#[authorize_once("from", "_nonce")]
#[external("private")]
fn transfer_private_to_private(from: AztecAddress, to: AztecAddress, amount: u128, _nonce: Field) {
    self.internal._call_auth_private(from, amount);
    self.internal._decrease_private_balance(from, amount, INITIAL_TRANSFER_CALL_MAX_NOTES);
    self.internal._increase_private_balance(to, amount);
}
```

`_decrease_private_balance` is where the note model shows through. An ERC-20 subtracts one integer. A note-based balance is a *set* of integers, so a debit has to pick notes whose sum covers the amount, nullify all of them, and hand the excess back as a new note, the same way a cash payment produces change:

```rust
#[internal("private")]
fn _decrease_private_balance(account: AztecAddress, amount: u128, max_notes: u32) {
    let change = self.internal._subtract_balance(account, amount, max_notes);
    self.storage.private_balances.at(account).add(change).deliver(
        MessageDelivery::onchain_constrained(),
    );
}
```

Reading and proving a note costs circuit constraints, so the number of notes a single call may consume is capped. AIP-20 caps the first attempt at **2** notes (`INITIAL_TRANSFER_CALL_MAX_NOTES`) and, if those do not cover the amount, recurses through a private self-call that takes **8** notes per round (`RECURSIVE_TRANSFER_CALL_MAX_NOTES`):

```rust
#[internal("private")]
fn _subtract_balance(account: AztecAddress, amount: u128, max_notes: u32) -> u128 {
    let subtracted = self.storage.private_balances.at(account).try_sub(amount, max_notes);
    if subtracted >= amount {
        subtracted - amount
    } else {
        assert(subtracted > 0, "Balance too low");
        let remaining = amount - subtracted;
        self.call_self.recurse_subtract_balance_internal(account, remaining)
    }
}
```

![Activity flow of AIP-20 balance subtraction: consume up to 2 notes, return change if enough, otherwise assert Balance too low when nothing was gathered or recurse with 8 notes per round on the remainder]({{site.url_complet}}/assets/article/blockchain/aztec/aip20-recursive-balance-subtraction-workflow.png)

Three properties follow from this code and matter to a caller:

- **A shortfall reverts.** `try_sub` returning zero notes asserts `"Balance too low"`, and the assertion is part of the proof, so a transaction that would overdraw a private balance cannot be proven at all. The failure is client-side and free; nothing reaches the chain.
- **The cost of a transfer depends on how fragmented the balance is.** Ten small incoming payments produce ten notes, and spending most of them takes one entry call plus one or two recursive rounds. A wallet that wants predictable proving time consolidates notes by paying itself.
- **The change note goes back to the sender as a fresh note**, delivered as an encrypted log with `onchain_constrained` delivery, meaning the circuit proves the log is a correct encryption of the note. The recipient's note is delivered the same way. Neither log names its owner; the recipient's PXE finds it by scanning for a tag derived from a shared secret between sender and recipient.

### Crossing between private and public

The two cross-domain functions are where the private-first execution order becomes visible. Private functions run on the client before the sequencer sees the transaction; public functions run on the sequencer afterwards. A private function can *enqueue* a public call but cannot read its result.

`transfer_private_to_public` debits notes privately, then enqueues `increase_public_balance_internal(to, amount)`, an `#[only_self]` public function that credits the balance and emits `Transfer(PRIVATE_ADDRESS, to, amount)`. The sender stays hidden; the recipient and the amount are public because a public balance changed by that amount.

`transfer_public_to_private` runs the other way: the private function creates the recipient's note first, then enqueues `decrease_public_balance_internal(from, amount)`. The order sounds backwards, since the credit is created before the debit is checked, but it is safe: if the public debit underflows, the public call reverts and the transaction's revertible side effects, the new note among them, are discarded. The debit itself is a plain `u128` subtraction whose underflow check is the balance check. What is public here is `from` and the amount; only the recipient is hidden.

Both functions are annotated `#[authorize_once]` and both call the private ARC-403 hook, but note `transfer_public_to_private`: the README states that it calls `authorize_private` while inherently revealing `from` and `amount` through the public debit. An authorization contract can tell the case apart from the `selector` argument it receives.

### Commitments: paying an address you do not know yet

The remaining cells of the matrix take a `commitment: Field` instead of a `to` address. A commitment is a *partial note*: a note whose owner is fixed in private execution and whose value is filled in later, possibly in public execution, possibly by a different contract. The recipient (or anyone acting for them) calls `initialize_transfer_commitment(to, completer)` to obtain the commitment, hands it to the payer, and the payer completes it with `transfer_public_to_commitment`, `transfer_private_to_commitment` or `mint_to_commitment`. The `completer` bound at initialisation must equal `msg_sender` at completion, which stops an arbitrary party from finishing a commitment they were shown.

This is the primitive that makes an AMM swap, a vault deposit or a vesting contract able to pay out privately when the amount is only known in public execution. A [dedicated article]({{site.url_complet}}/2026/09/09/aztec-partial-notes-private-defi-composability/) on this site covers the mechanism, the payment-endpoint pattern, and the double-completion hazard; here it is enough to note that ERC-20 has nothing comparable because it never needs it, and that ERC-7984 addresses the same composability problem with a callback instead (below).

### Authorization without `approve`

ERC-20's `approve`/`allowance`/`transferFrom` triple is absent. Every spending function takes `from` and a `nonce`, and the `#[authorize_once("from", "_nonce")]` macro implements the rule:

- If `from == msg_sender`, the account is spending its own tokens; `nonce` **must be zero** and no further check runs.
- Otherwise the macro demands an *authentication witness* (authwit): a signature by `from`'s account contract over the hash of the exact call (`caller`, function selector, arguments including `nonce`), scoped to this token contract, chain and version. In private context the witness is fetched from the user's PXE and verified inside the proof; in public context it is read from an on-chain authwit registry that `from` populated in advance. Either way a nullifier is emitted so the witness is consumed exactly once.

The difference from an allowance is not cosmetic. An ERC-20 approval is a standing *amount* that any call from the spender can draw against until it is exhausted or revoked, which is why "infinite approval" drains happen. An authwit authorises one *call* with fixed arguments: this spender, this amount, this recipient, this nonce. Repeating the same action needs a new nonce and a new witness. There is no allowance table to read, so `allowance(owner, spender)` has no equivalent, and there is no `Approval` event. The [account-abstraction article]({{site.url_complet}}/2026/09/09/aztec-native-account-abstraction-vs-erc-4337/) covers how the account contract validates the witness; from the token's point of view the macro is the whole story.

One limit: the macro authorises exactly one `from`. A batch that debits several holders in one call cannot be expressed through it.

### Minting, burning and the public supply

Two initialisers define two supply models. `constructor_with_initial_supply` mints the whole supply publicly to one address and never sets `minter`, so the three mint functions are permanently unusable. `constructor_with_minter` sets a single immutable `minter` address (typically a bridge or a vault) that can call `mint_to_public`, `mint_to_private` and `mint_to_commitment`. Burning is symmetric: `burn_public(from, amount, nonce)` and `burn_private(from, amount, nonce)`, both authwit-gated on `from`.

Every private mint and burn enqueues a public update to `total_supply` and emits `Transfer(0x0, PRIVATE_ADDRESS, amount)` or `Transfer(PRIVATE_ADDRESS, 0x0, amount)`. So the *amount* of a private mint is public, and only its recipient is hidden. The same holds for private burns. This is the price of a queryable `total_supply()`, and it is where AIP-20's privacy differs most from ERC-7984, whose `confidentialTotalSupply()` returns a handle. An AIP-20 token whose supply changes rarely leaks little; a token that mints per deposit, as a vault share token does, publishes every deposit amount.

The RFC lists `mint_to_private(from, to, amount)`; the implementation takes `(to, amount)` and derives the minter from `msg_sender`. Follow the implementation.

### ARC-403: a pluggable authorization hook

The `auth_contract` field is an immutable address set at construction. When non-zero, every transfer and burn calls it after the authwit check and before any balance change: `authorize_private(from, amount, selector)` from private functions, `authorize_public(from, amount, selector)` from public ones. If the hook reverts, the token operation reverts. Mints are not hooked, since the `minter` gate already covers them.

```rust
#[internal("private")]
fn _call_auth_private(from: AztecAddress, amount: u128) {
    let auth = self.storage.auth_contract.read();
    if !auth.eq(AztecAddress::zero()) {
        let selector = self.context.selector().to_field();
        self.call(AuthorizationContract::at(auth).authorize_private(from, amount, selector));
    }
}
```

The hook deliberately does **not** receive `to`. Commitment-based transfers seal the recipient inside a hash the sender never sees, so the recipient cannot be supplied consistently, and the standard omits it rather than pass it sometimes. The documented consequence: a policy can stop a blocked address from *spending*, but not from *receiving*. An allowlist, a pause switch, a transfer cap or a sanctions screen can all be expressed this way; a recipient-side restriction cannot.

## The ERC-20 baseline

For reference, the interface everything else is measured against, in the form the [OpenZeppelin v5](https://docs.openzeppelin.com/contracts/5.x/erc20) implementation gives it:

```solidity
interface IERC20 {
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 value) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 value) external returns (bool);
    function transferFrom(address from, address to, uint256 value) external returns (bool);
}
```

The behaviours that matter for the comparison, all of them in `_update`: a transfer with `value > balance` reverts (`ERC20InsufficientBalance` in OpenZeppelin v5); `transferFrom` decrements the allowance unless it is `type(uint256).max`; `Transfer` is emitted with both addresses and the amount in clear; and compliance logic, when a project needs it, is added by overriding `_update` or by a hook contract that `_update` calls. This site's [ERC-20 library comparison]({{site.url_complet}}/2026/02/13/erc20-library-comparison-openzeppelin-solady-solarity/) covers the implementation differences between OpenZeppelin, Solady and Solarity; none of them touch the visibility model, which is total.

## ERC-7984 in brief

ERC-7984 (status: Draft, created July 2025) keeps the ERC-20 function set and swaps every amount for a `bytes32` pointer. The specification is technology-agnostic about what the pointer resolves to; the OpenZeppelin implementation resolves it to a Zama FHEVM `euint64`.

```solidity
interface IERC7984 {
    event ConfidentialTransfer(address indexed from, address indexed to, bytes32 indexed amount);
    event OperatorSet(address indexed holder, address indexed operator, uint48 until);
    event AmountDisclosed(bytes32 indexed handle, uint256 amount);

    function confidentialTotalSupply() external view returns (bytes32);
    function confidentialBalanceOf(address account) external view returns (bytes32);
    function isOperator(address holder, address spender) external view returns (bool);
    function setOperator(address operator, uint48 until) external;
    function confidentialTransfer(address to, bytes32 amount) external returns (bytes32);
    function confidentialTransfer(address to, bytes32 amount, bytes calldata data) external returns (bytes32);
    function confidentialTransferFrom(address from, address to, bytes32 amount) external returns (bytes32);
    function confidentialTransferFrom(address from, address to, bytes32 amount, bytes calldata data) external returns (bytes32);
    // ...AndCall variants of each, invoking onConfidentialTransferReceived on the recipient
}
```

Four behaviours define it, each covered in depth in the [ERC-7984 implementation analysis]({{site.url_complet}}/2026/02/24/erc7984-openzeppelin-analysis/) on this site:

- **No revert on shortfall.** The contract cannot branch on an encrypted comparison, so `_update` computes `success = amount <= balance` as an encrypted boolean and transfers `FHE.select(success, amount, 0)`. A transfer from an empty balance succeeds, emits `ConfidentialTransfer`, and moves zero. The *return value* of every transfer function is the handle of the amount that was moved, and the caller has to decrypt it to learn which case occurred.
- **Operators instead of allowances.** `setOperator(operator, until)` grants a time-bounded right to move *any* amount, because an amount-bounded allowance would require the contract to compare against a ciphertext it cannot read. Every holder is implicitly their own operator. The documentation's own warning: an operator can take everything until the timestamp expires.
- **Optional input proofs and callbacks.** The `data` overload carries an input proof that the sender knows the plaintext of a freshly encrypted amount. The `AndCall` overloads invoke `onConfidentialTransferReceived` on a recipient contract, which returns an encrypted boolean; a `false` reverses the credit. This is ERC-7984's answer to composability: the recipient contract learns it was paid and can act, without a separate approval step.
- **Disclosure is explicit and irrevocable.** A holder (or anyone with ACL access to a handle) calls `requestDiscloseEncryptedAmount`, which marks the handle publicly decryptable, then `discloseEncryptedAmount` with a threshold-decryption proof from the KMS emits `AmountDisclosed` in clear. Nothing is ever hidden about *addresses*: `from` and `to` are public in every event.

## Side by side

| Axis | ERC-20 | AIP-20 | ERC-7984 |
|---|---|---|---|
| Balance representation | `uint256` in public storage | private: set of `u128` notes on the owner's device; public: `u128` in public state | `euint64` ciphertext handle |
| Who can read a balance | anyone | private: owner only, via unconstrained `balance_of_private`; public: anyone | owner and ACL grantees, via re-encryption by the KMS |
| Hidden in a transfer | nothing | private→private: sender, recipient, amount; cross-domain: the private side only | amount only; `from` and `to` are public |
| Total supply | public | **public** `u128`, updated by every mint and burn | encrypted handle |
| Transfer signature | `transfer(to, amount)`, `transferFrom(from, to, amount)` | `transfer_<src>_to_<dst>(from, to, amount, nonce)`, seven variants | `confidentialTransfer(to, handle[, data])`, `confidentialTransferFrom(...)`, eight variants |
| Third-party spending | standing amount allowance, `Approval` event | single-use authwit over the exact call, nonce-scoped, no allowance state | time-limited operator, any amount, `OperatorSet` event |
| Insufficient balance | reverts | reverts (`"Balance too low"` in the proof, or `u128` underflow in public) | succeeds and transfers zero; caller decrypts the returned handle to find out |
| Events | `Transfer(from, to, value)` | `Transfer(from, to, amount)` on public-side moves, with `0x0` and `PRIVATE_ADDRESS` sentinels; nothing for private→private | `ConfidentialTransfer(from, to, handle)`; amount unreadable |
| Recipient not known at call time | not supported | partial-note commitments | not supported; callbacks let the recipient react instead |
| Receiver contract hook | none (ERC-1363 adds one) | none; a contract receives by completing a commitment or holding a public balance | `onConfidentialTransferReceived`, returns `ebool`, `false` reverses |
| Compliance attachment | override `_update` | ARC-403 external auth contract, receives `(from, amount, selector)`, not `to` | extensions: `ERC7984Restricted`, `ERC7984Freezable`, observer access |
| Metadata | `name`, `symbol`, `decimals` (optional) | `name`, `symbol` as 31-byte compressed strings, `decimals` | `name`, `symbol`, `decimals`, `contractURI` |
| Where the trust sits | EVM consensus | the user's proof, verified by the rollup; no decryption service | FHE coprocessor and threshold KMS for decryption and ACL |
| Cost driver | storage writes | notes consumed per transfer (2, then 8 per recursive round) | FHE operations per transfer |

Four of these rows need more than a cell.

### What an observer learns

An ERC-20 transfer publishes everything. An ERC-7984 transfer publishes the *graph*: who paid whom, when, and how often, with only the weights removed. Traffic analysis on that graph is the standard's acknowledged limit and the reason the specification lists side channels under security considerations. An AIP-20 private-to-private transfer publishes nullifiers and note hashes that an outsider cannot link to accounts; the graph itself is hidden. The trade is that the moment a private balance touches the public side, the public half of the movement is as visible as ERC-20, and the *amount* of every mint and burn is visible through `total_supply` even when the recipient is not.

A practical reading: AIP-20 protects the *user's* activity as long as it stays private; ERC-7984 protects the *amounts* everywhere but never the counterparties.

### Authorization models

The three models answer "how does a contract move my tokens?" with three different objects. ERC-20 stores an integer per (owner, spender) pair and decrements it. ERC-7984 stores a timestamp per pair and checks `block.timestamp <= until`, with no amount because it cannot compare one. AIP-20 stores nothing: the authorisation is a signed message over the specific call, produced off-chain and verified inside the proof (private) or read from a registry (public), and burned by a nullifier on use.

Consequences for an integrator: with ERC-20 the risk is a stale infinite approval; with ERC-7984 it is a live operator window during which any amount can be taken; with AIP-20 it is that every distinct action needs its own witness and its own nonce, which pushes complexity into the wallet rather than the token.

### Failure semantics

ERC-20 and AIP-20 share the property that a transfer either fully succeeds or the transaction fails; the difference is only where the check runs (EVM versus proof or AVM). ERC-7984 breaks that property by design. A protocol that composes ERC-7984 tokens has to treat every transfer as "moved *some* amount, possibly zero", request decryption of the returned handle, and reconcile asynchronously. A protocol composing AIP-20 tokens can assume the amount moved if the transaction landed, and the price it pays is that a private call cannot depend on public state computed in the same transaction, which is what commitments exist to work around.

### Compliance and observers

ERC-20 compliance is a code-level override. ERC-7984's extensions add restriction lists and freezes on top of the same ciphertext model, plus an observer role that can decrypt a holder's balance. AIP-20 externalises the policy into a separate contract through ARC-403, keeping the token interface untouched, but hands that contract less information than either of the others: it sees the spender, the amount and which function is running, and never the recipient. An observer role does not exist in AIP-20 as of the pinned commit; a viewing key given to an auditor is a wallet-level arrangement, not a token-level one.

## Conclusion

AIP-20 is an ERC-20 whose single balance has been split along the private/public seam of the Aztec execution model, and whose one `transfer` has been split into a function per pair of domains. The private side is a note set, so a debit selects and nullifies notes and returns change, bounded at 2 then 8 notes per round; the public side is an ordinary `u128` map with an ERC-20-style event. Authorisation drops `approve` for single-use authwits carried by a `from` plus `nonce` pair, commitments (partial notes) cover the case where the recipient is fixed before the amount is, and ARC-403 lets a policy contract veto spends without seeing recipients. Total supply stays public, which means mint and burn amounts are public even when their owners are not.

ERC-7984 keeps one balance and one call signature and encrypts the amounts, at the cost of an operator model with no amount bound, a transfer that cannot revert on shortfall, and a transaction graph that stays fully visible. The two standards are not competing implementations of one idea; they hide different things, fail differently, and put the trust in different places (a client-side proof versus a coprocessor and a decryption committee). Which one fits depends on whether the requirement is hidden counterparties or hidden amounts, and on whether the integrator can live with asynchronous reconciliation or with client-side proving.

![Mindmap of AIP-20 versus ERC-20 and ERC-7984 covering balance location, the AIP-20 interface, private transfer mechanics, authorization models, failure and disclosure behaviour, and compliance hooks]({{site.url_complet}}/assets/article/blockchain/aztec/2026-09-11-aip20-vs-erc20-erc7984-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Note** | The unit of private state on Aztec: a struct (owner, value, randomness) whose hash is inserted into the note hash tree and whose plaintext is delivered to the owner as an encrypted log. An AIP-20 private balance is a set of `UintNote`s. |
| **Nullifier** | A deterministic value emitted when a note is spent, derived from the note and the owner's nullifier key; the chain rejects a second emission, which prevents double spending without revealing which note was consumed. |
| **BalanceSet** | The aztec-nr state variable wrapping a set of `UintNote`s for one owner, with `add(amount)` to create a note and `try_sub(amount, max_notes)` to consume up to `max_notes` notes and return their sum. |
| **Change note** | The fresh note returned to the sender for the difference between the notes consumed and the amount transferred, since notes cannot be partially spent. |
| **Authwit** | Authentication witness: a signature by an account contract over the hash of one exact call, consumed once via a nullifier. AIP-20 uses it in place of ERC-20 allowances whenever `from` differs from `msg_sender`. |
| **PXE** | Private Execution Environment: the client-side component that holds a user's notes and keys, executes private functions and produces the proof. `balance_of_private` runs there and nowhere else. |
| **Partial note / commitment** | A note whose owner is fixed in private execution and whose value is completed later, possibly in public execution, by a designated completer. AIP-20's `*_to_commitment` functions consume one. |
| **PRIVATE_ADDRESS** | The sentinel address (SHA-224 of the string) used in AIP-20's public `Transfer` event to stand for the private side of a cross-domain movement. |
| **ARC-403** | The optional authorization hook: an external contract the token calls with `(from, amount, selector)` before every transfer and burn, whose revert aborts the operation. |
| **Ciphertext handle** | In ERC-7984, the `bytes32` (an `euint64` in the OpenZeppelin implementation) that references an encrypted amount held by the FHE coprocessor; the contract computes on handles and never sees plaintext. |

### Security Implementation Checklist

Both AIP-20 and ERC-7984 are interfaces that several teams implement independently, and the properties below are the ones a wrong implementation loses. Rows are grouped by the standard they apply to.

#### AIP-20 implementations

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Every spending function (transfers, burns) is annotated `#[authorize_once("from", nonce)]` or performs the equivalent authwit check and nullifier emission. | A caller debits any account, or a witness is replayed. |
| ☐ | A `from == msg_sender` call rejects a non-zero nonce. | A witness intended for a third party is reusable by the owner's own call path, or nonces lose their meaning. |
| ☐ | `_subtract_balance` asserts `subtracted > 0` before recursing and only returns change when `subtracted >= amount`. | A zero-note round recurses forever, or a shortfall is accepted and change is computed from an underflow. |
| ☐ | The change note and the recipient note are delivered with constrained delivery (`onchain_constrained`) from the private circuit. | A malicious sender submits a valid nullifier set with an unreadable or absent recipient log; funds are burned. |
| ☐ | Cross-domain functions debit in the enqueued public call with a checked `u128` subtraction and rely on the transaction reverting on underflow. | A public-to-private transfer credits a note that survives a failed public debit, minting from nothing. |
| ☐ | Commitment completion binds `completer` to `msg_sender`, and the integrating application completes each commitment once, since neither the protocol nor the token enforces single completion. | Anyone who sees a commitment finishes it, or a second completion collides with the first and the second payment is lost. |
| ☐ | The minter is checked on all three `mint_to_*` paths, and the no-minter constructor leaves `minter` unset. | Unbounded supply. |
| ☐ | `total_supply` updates enqueued from private mint and burn are `#[only_self]`. | A third party inflates or deflates the public supply without moving tokens. |
| ☐ | The ARC-403 hook, when set, runs after the authwit check and before any balance mutation, and its revert propagates. | A policy is bypassed, or a rejected transfer has already changed state. |
| ☐ | Documentation states that private mint and burn amounts are public through `total_supply` and the sentinel events. | Integrators assume amount privacy that the token does not provide. |

#### ERC-7984 implementations

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | `_update` computes the transferred amount with `FHE.select(success, amount, 0)` and returns its handle; callers are told it can be zero. | A caller assumes the requested amount moved and releases counter-value for nothing. |
| ☐ | Operator expiry is checked with `block.timestamp <= until` and the holder is the only party who can set their own operator. | An expired operator keeps draining, or a third party appoints itself. |
| ☐ | `FHE.allow` grants on new balance and transferred-amount handles are limited to `from`, `to` and the contract. | A stranger gains decryption rights on a balance. |
| ☐ | Disclosure entry points are restricted to the handle owner or a dedicated role, and repeated disclosure of a running aggregate is rate-limited. | An observer publishes another party's balance, or sequential supply disclosures leak individual amounts by differencing. |
| ☐ | Transfer-and-call paths reverse the credit when the callback returns an encrypted `false`, and are protected against reentrancy. | Funds are stuck in a contract that rejected them, or a callback re-enters `_update`. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| AIP-20 has no `balanceOf` for private balances that another contract can call; `balance_of_private` is an unconstrained utility for the owner's PXE. | Design protocols so that the token proves solvency by *transferring*, never by having a third party read a private balance. |
| `nonce` must be `0` when `from` is the caller, and a fresh non-zero value with a matching authwit otherwise. | Wallet code generates and tracks nonces per (token, action); do not reuse a nonce across two witnesses for the same action. |
| Amounts are `u128` and names are at most 31 bytes. | Bound bridged ERC-20 amounts and truncate or reject long names before deployment. |
| Private transfers of a fragmented balance recurse in rounds of 8 notes and take longer to prove. | Consolidate notes with a self-transfer when a wallet holds many small ones. |
| `total_supply()` and the sentinel `Transfer` events expose the amount of every private mint and burn. | Do not use per-user mints as a private funding path if amounts are sensitive; batch or use a public mint to a pool followed by private transfers. |
| The ARC-403 hook never receives `to`. | Recipient-side policies (blocking receipt) are not expressible; enforce them on spend instead, or at the application layer. |
| `transfer_public_to_private` calls `authorize_private` but reveals `from` and `amount` on chain. | Authorization contracts should branch on `selector` if they treat the private hook as evidence of privacy. |
| An ERC-7984 transfer returns a handle for the amount actually moved, which may be zero. | Treat every confidential transfer as pending until the returned handle is decrypted and reconciled. |

## Frequently Asked Questions

**Q: Why does AIP-20 have seven transfer functions where ERC-20 has two?**

Because each Aztec account has a private balance and a public balance, and a transfer can debit either and credit either. AIP-20 names every combination explicitly (`transfer_private_to_public`, `transfer_public_to_private`, and so on) rather than overloading one function, and adds commitment-targeted variants for the case where the recipient is fixed before the amount is. ERC-20's `transfer` and `transferFrom` collapse into one function per cell, since the `from` parameter and the `nonce` cover both the self-spend and the delegated-spend cases.

**Q: What does the `nonce` parameter do, and why must it be zero when I spend my own tokens?**

The nonce exists for the authwit path. When `from` differs from the caller, the token requires a witness signed by `from`'s account contract over the exact call, and the nonce is part of the signed message so that the same action can be authorised more than once with distinct witnesses. When `from` is the caller, no witness is involved, and the macro requires the nonce to be zero, which keeps the two cases distinct and turns a stray non-zero nonce into a visible error instead of an ignored parameter.

**Q: What happens if a private transfer needs more notes than the cap allows?**

The first attempt consumes up to 2 notes. If their sum is below the amount, the contract makes a private self-call with the remainder, consuming up to 8 notes per round, and repeats until the gathered sum covers the amount. If any round gathers nothing, the assertion `"Balance too low"` fails and the proof cannot be produced. The excess from the final round is returned to the sender as a new note.

**Q: Is an AIP-20 private mint fully private?**

Only the recipient is. `mint_to_private` creates the recipient's note in private execution but enqueues a public update to `total_supply` and emits `Transfer(0x0, PRIVATE_ADDRESS, amount)`, so the amount is visible on chain. The same applies to `burn_private`. This follows from AIP-20's choice to keep `total_supply` as a readable public value, where ERC-7984 keeps it encrypted.

**Q: In what sense does ERC-7984 "not revert" on an insufficient balance, and why?**

An FHE contract cannot branch on an encrypted comparison, so it cannot execute `require(balance >= amount)`. Instead `_update` computes an encrypted boolean and selects either `amount` or zero as the transferred value. The transaction succeeds, the event fires with a handle, and the return value is the handle of what was moved. Only a party with decryption rights can tell whether the transfer did anything. AIP-20, whose private functions run on the client with plaintext notes, asserts the balance inside the proof and fails outright.

**Q: How do the three standards let a smart contract spend a user's tokens, and what is the risk in each?**

ERC-20 uses an amount allowance: the user approves a spender for an amount, and the risk is a standing (often unlimited) approval that survives long after the interaction. ERC-7984 uses a time-limited operator with no amount bound, because the contract cannot compare against a ciphertext; the risk is that the operator can take the whole balance until expiry. AIP-20 uses an authwit: a single-use signature over one exact call, nullified on consumption; the risk moves to the wallet, which must produce a witness and nonce per action, and the model cannot express a batch that debits several holders.

**Q: A DEX wants to pay a user an amount computed from public reserves. How does each standard handle it?**

ERC-20 has no problem: everything is public and synchronous. ERC-7984 lets the DEX transfer the encrypted output and, with the `AndCall` variants, notifies a recipient contract through a callback; the recipient can react but cannot learn the amount without decryption. AIP-20 uses a commitment: the user initialises a partial note naming themselves as owner in private execution, the DEX completes it with the amount in public execution via `transfer_public_to_commitment` or `mint_to_commitment`, and the result is a private note for the user whose amount was decided after the private phase ended.

## References

### Analyzed source

- [defi-wonderland/aztec-standards](https://github.com/defi-wonderland/aztec-standards) — analyzed at commit [`a3859e5ab2a41185543e9b4189ef1033dfcd1b65`](https://github.com/defi-wonderland/aztec-standards/tree/a3859e5ab2a41185543e9b4189ef1033dfcd1b65) (branch `dev`, after tag `prerelease-0200230`, built against Aztec `v5.0.0-rc.2`), 2026-09-11
- [OpenZeppelin/openzeppelin-confidential-contracts](https://github.com/OpenZeppelin/openzeppelin-confidential-contracts) — `ERC7984.sol` read from the `master` branch on 2026-09-11; the exact revision was not pinned, see the [dedicated analysis]({{site.url_complet}}/2026/02/24/erc7984-openzeppelin-analysis/) for a pinned reading

### Specifications

- [Request for Comments: AIP-20 Aztec Token Standard](https://forum.aztec.network/t/request-for-comments-aip-20-aztec-token-standard/7737) — Wonderland, Aztec forum, April 2025
- [AIP-20: Fungible Token](https://docs.aztec.network/developers/docs/aztec-nr/standards/aip-20) — Aztec developer documentation
- [ERC-20: Token Standard](https://eips.ethereum.org/EIPS/eip-20)
- [ERC-7984: Confidential Fungible Token](https://eips.ethereum.org/EIPS/eip-7984) — Draft
- [ERC-1363: Payable Token](https://eips.ethereum.org/EIPS/eip-1363) — the callback pattern ERC-7984's `AndCall` variants follow

### Documentation

- [OpenZeppelin Contracts v5, ERC-20](https://docs.openzeppelin.com/contracts/5.x/erc20)
- [OpenZeppelin Confidential Contracts, ERC7984](https://docs.openzeppelin.com/confidential-contracts/token)
- [aztec-arc403-extensions](https://github.com/defi-wonderland/aztec-arc403-extensions) — reference authorization contracts for the ARC-403 hook

### Related articles

- [Aztec Contract Standards — AIP-20, AIP-721, ARC-1155, ARC-403, AIP-4626 and the Escrow Standard]({{site.url_complet}}/2026/09/11/aztec-contract-standards-overview/)
- [How Aztec Works — Private Execution, Notes and Nullifiers, and a Comparison with Zama FHE, Zcash, Canton and Railgun]({{site.url_complet}}/2026/09/08/how-aztec-works-private-execution-model/)
- [Partial Notes on Aztec — Deferred Completion and Private DeFi Composability]({{site.url_complet}}/2026/09/09/aztec-partial-notes-private-defi-composability/)
- [Native Account Abstraction on Aztec, Compared with ERC-4337]({{site.url_complet}}/2026/09/09/aztec-native-account-abstraction-vs-erc-4337/)
- [Technical Analysis of the OpenZeppelin ERC-7984 Implementation]({{site.url_complet}}/2026/02/24/erc7984-openzeppelin-analysis/)
- [ERC-20 Implementation Comparison — OpenZeppelin, Solady, and Solarity Solidity Library]({{site.url_complet}}/2026/02/13/erc20-library-comparison-openzeppelin-solady-solarity/)
