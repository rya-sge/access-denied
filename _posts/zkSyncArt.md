# ZKsync Circuit Architecture: A Technical Deep Dive

## Introduction

ZKsync is a Layer 2 scaling solution for Ethereum that uses zero-knowledge proofs to validate transaction execution off-chain. At the heart of this system lies a sophisticated circuit architecture built on the **Boojum** proof system. This article provides a technical overview of the circuit design, covering the proof system fundamentals, individual circuit implementations, and how they interconnect to form a complete validity proof.

---

## 1. The Boojum Proof System

### 1.1 Field Selection

Boojum operates over the **Goldilocks field** with order `2^64 - 2^32 + 1`. This field is significantly smaller than the bn256 curve used in many other ZK systems, enabling:

- Faster proof generation
- Reduced memory requirements (proofs can be generated with 16GB GPU RAM)
- More efficient constraint satisfaction

### 1.2 Circuit Types (Gadgets)

Boojum provides low-level implementations of constraint system primitives:

```rust
// Core numeric types
pub struct Num<F: SmallField> { variable: Variable, ... }
pub struct Boolean<F: SmallField> { variable: Variable, ... }
pub struct UInt8<F: SmallField> { variable: Variable, ... }
pub struct UInt32<F: SmallField> { variable: Variable, ... }
pub struct UInt256<F: SmallField> { inner: [UInt32<F>; 8] }
```

Each type wraps a `Variable` (an index into the constraint system) and supports:
- Witness allocation (with or without values)
- Constraint enforcement
- Conditional selection

### 1.3 Hash Functions

The system implements four hash functions for different purposes:

| Hash Function | Use Case |
|---------------|----------|
| **Poseidon2** | Queue commitments, internal hashing (ZK-friendly) |
| **Keccak256** | Ethereum compatibility, address derivation |
| **SHA256** | Code decommitment verification |
| **Blake2s** | General purpose hashing |

### 1.4 Queue System

Queues are the fundamental data structure for inter-circuit communication:

```rust
struct CircuitQueue {
    head: HashState,      // Rolling hash of popped elements
    tail: HashState,      // Rolling hash of pushed elements
    length: UInt32,       // Current queue length
    witness: VecDeque<Witness>,
}
```

**Key operations:**
- `push()`: Increments length, updates head hash, stores witness
- `pop()`: Decrements length, updates tail hash, returns witness
- `final_check()`: Enforces `length == 0` and `head == tail`

The equality of rolling hashes at finalization proves that all popped elements match the pushed elements exactly.

### 1.5 Constraint Satisfaction (`check_if_satisfied`)

The satisfaction test verifies all circuit constraints are met:

1. **Prepare constants, variables, and witnesses**
2. **Create view subsets** for efficient column access
3. **Build path mappings** for gate selection at each row
4. **Evaluate general-purpose rows**: Gates with `UniqueOnRow` or `MultipleOnRow` placement
5. **Evaluate specialized rows**: Custom gates with specific placement data
6. **Verify all evaluations equal zero**

---

## 2. Circuit Architecture Overview

The ZKsync proving system comprises multiple specialized circuits that work together:

```
                    ┌─────────────┐
                    │   Main VM   │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────────┐
        │ Memory   │ │ Decommit │ │  Log Queue   │
        │  Queue   │ │  Queue   │ │              │
        └────┬─────┘ └────┬─────┘ └──────┬───────┘
             │            │              │
             ▼            ▼              ▼
     ┌───────────────┐ ┌────────────┐ ┌─────────────┐
     │RAMPermutation │ │CodeDecommit│ │DemuxLogQueue│
     └───────────────┘ └────────────┘ └──────┬──────┘
                                             │
            ┌────────────────────────────────┼────────────────────────────┐
            │                    │           │           │                │
            ▼                    ▼           ▼           ▼                ▼
     ┌─────────────┐     ┌───────────┐ ┌──────────┐ ┌──────────┐  ┌───────────┐
     │StorageSorter│     │ LogSorter │ │ Keccak   │ │  SHA256  │  │ ECRecover │
     └─────────────┘     └───────────┘ └──────────┘ └──────────┘  └───────────┘
```

---

## 3. Core Circuits

### 3.1 Main VM Circuit

The Main VM circuit is the instruction handler for EraVM execution. It processes opcodes in cycles and accumulates memory queries.

**Public Interface:**

```rust
// Input
pub struct VmInputData<F: SmallField> {
    pub rollback_queue_tail_for_block: [Num<F>; QUEUE_STATE_WIDTH],
    pub memory_queue_initial_state: QueueTailState<F, FULL_SPONGE_QUEUE_STATE_WIDTH>,
    pub decommitment_queue_initial_state: QueueTailState<F, FULL_SPONGE_QUEUE_STATE_WIDTH>,
    pub per_block_context: GlobalContext<F>,
}

// Output
pub struct VmOutputData<F: SmallField> {
    pub log_queue_final_state: QueueState<F, QUEUE_STATE_WIDTH>,
    pub memory_queue_final_state: QueueState<F, FULL_SPONGE_QUEUE_STATE_WIDTH>,
    pub decommitment_queue_final_state: QueueState<F, FULL_SPONGE_QUEUE_STATE_WIDTH>,
}
```

**Execution Flow:**

1. **Prestate creation**: Handle exceptions, resources, edge cases, select opcodes
2. **Opcode execution**: Process each instruction type:
   ```rust
   pub enum Opcode {
       Invalid, Nop, Add, Sub, Mul, Div, Jump, Context,
       Shift, Binop, Ptr, NearCall, Log, FarCall, Ret, UMA
   }
   ```
3. **State diff accumulation**: Collect register updates, memory queries, queue modifications
4. **Queue finalization**: Output memory, decommitment, and log queues

**Key Insight:** The VM is "local" - it uses witness values for memory access. The RAMPermutation circuit later enforces global memory consistency.

---

### 3.2 RAMPermutation Circuit

Enforces correct memory query execution by proving the sorted and unsorted memory queues contain the same elements.

**Logic:**

1. **Permutation argument**: Generate challenges and accumulators to prove queue equivalence
2. **Sorting enforcement**: Verify queries are sorted by `(memory_page, index, timestamp)`
3. **Read consistency**:
   - Same `(page, index)` as previous → value must match
   - Different `(page, index)` → value must be zero (fresh memory)
4. **Non-deterministic writes**: Count and verify bootloader heap writes

```rust
pub struct RamPermutationInputData<F: SmallField> {
    pub unsorted_queue_initial_state: QueueState<F, FULL_SPONGE_QUEUE_STATE_WIDTH>,
    pub sorted_queue_initial_state: QueueState<F, FULL_SPONGE_QUEUE_STATE_WIDTH>,
    pub non_deterministic_bootloader_memory_snapshot_length: UInt32<F>,
}
```

---

### 3.3 DemuxLogQueue Circuit

Demultiplexes the unified log queue into six specialized queues:

| Queue | Purpose |
|-------|---------|
| `storage_access_queue` | Storage read/write operations |
| `events_access_queue` | Event emissions |
| `l1messages_access_queue` | L2→L1 messages |
| `keccak256_access_queue` | Keccak precompile calls |
| `sha256_access_queue` | SHA256 precompile calls |
| `ecrecover_access_queue` | ECRecover precompile calls |

**Routing Logic:**

```rust
let is_storage_aux_byte = UInt8::equals(cs, &aux_byte_for_storage, &popped.aux_byte);
let is_precompile_aux_byte = UInt8::equals(cs, &aux_byte_for_precompile_call, &popped.aux_byte);
let is_keccak_address = UInt160::equals(cs, &keccak_precompile_address, &popped.address);
// ... route to appropriate queue based on aux_byte and address
```

---

### 3.4 CodeDecommitter Circuit

Unpacks bytecode from decommit requests and verifies code integrity via SHA256 hashing.

**Process:**

1. Pop decommit request from queue
2. Write opcodes to memory page
3. Compute SHA256 hash of all written code
4. Verify hash matches the expected code hash

```rust
pub struct CodeDecommittmentFSM<F: SmallField> {
    pub sha256_inner_state: [UInt32<F>; 8],
    pub hash_to_compare_against: UInt256<F>,
    pub current_index: UInt32<F>,
    pub current_page: UInt32<F>,
    pub num_rounds_left: UInt16<F>,
    // ...
}
```

---

## 4. Sorting Circuits

### 4.1 StorageSorter

Sorts and deduplicates storage requests to produce the final state diff for L1 submission.

**Key Features:**
- Permutation argument proves sorted queue contains same elements as unsorted
- Deduplication: Only the final write to each `(address, key)` pair is output
- Rollback handling: Cancelled writes are excluded

**Push Conditions:**
- Read at depth 0
- Cell value changed
- Write that was declined (not by rollback)

### 4.2 LogSorter

Used for both `EventsSorter` and `L1MessagesSorter`. Sorts logs and handles rollbacks.

**Rollback Logic:**
When a function reverts, it emits an identical event with `rollback = true`. The circuit:
1. Sorts logs by timestamp
2. Detects matching pairs (same key, timestamp) where one has rollback flag
3. "Self-destructs" the pair, excluding both from output

```rust
let same_log = UInt32::equals(cs, &sorted_item.timestamp, &previous_item.timestamp);
let is_sequential_rollback = Boolean::multi_and(cs, &[
    this_item_is_non_trivial_rollback,
    previous_item_is_non_trivial_write,
]);
same_log.conditionally_enforce_true(cs, is_sequential_rollback);
```

---

## 5. Precompile Circuits

### 5.1 ECRecover Circuit

Implements the Ethereum `ecrecover` precompile for signature verification on the secp256k1 curve.

**Algorithm:**

1. **Input validation**: Check `r`, `s` are in scalar field, `x` coordinate is valid
2. **Recover x-coordinate**: `x = r + kn` where `k ∈ {0, 1}`
3. **Compute t**: `t = x³ + b` (curve equation)
4. **Quadratic residue check**: Compute Legendre symbol via `t^((p-1)/2)`
5. **Compute square root**: Derive y-coordinate
6. **MSM for public key**: `Q = (s * X - hash * G) / r`
7. **Address derivation**: `keccak256(Q)[12:]`

**Exception Handling:**
Invalid inputs are swapped for hardcoded valid values, and exception flags are returned to indicate the result should be discarded.

### 5.2 Keccak256 Circuit

Processes keccak256 precompile calls using the sponge construction.

**State Machine:**

```rust
pub struct Keccak256RoundFunctionFSM<F: SmallField> {
    pub read_precompile_call: Boolean<F>,
    pub read_unaligned_words_for_round: Boolean<F>,
    pub completed: Boolean<F>,
    pub keccak_internal_state: [[[UInt8<F>; 8]; 5]; 5], // 5x5 lane structure
    pub timestamp_to_use_for_read: UInt32<F>,
    pub timestamp_to_use_for_write: UInt32<F>,
    // ...
}
```

**Flow:**
1. Read precompile call metadata (input/output memory locations)
2. Read input data from memory
3. Run Keccak permutation rounds
4. Write 32-byte hash result to memory

### 5.3 SHA256 Circuit

Similar structure to Keccak, implementing the SHA256 compression function.

**Key Difference:** Uses 8x32-bit internal state (`[UInt32<F>; 8]`) and processes 64-byte blocks.

```rust
let sha256_output = sha256::round_function::round_function_over_uint32(
    cs,
    &mut current_sha256_state,
    &memory_queries_as_u32_words,
);
```

---

## 6. Circuit Testing

Circuit tests follow a standard pattern (example: ECRecover):

```rust
// 1. Define geometry and constraints
let geometry = ...;
let max_variables = ...;

// 2. Configure builder with gates and placement strategy
let builder = configure();

// 3. Add lookup tables
cs.add_lookup_table::<...>();

// 4. Allocate witnesses
let r = UInt256::allocate(cs, signature.r);
let s = UInt256::allocate(cs, signature.s);

// 5. Run circuit logic
let (success, recovered_address) = ecrecover_precompile_inner_routine(cs, ...);

// 6. Verify results
assert!(recovered_address == expected_address);
assert!(cs.check_if_satisfied());
```

---

## 7. Public Input Commitment

Every circuit finalizes by computing a commitment to its public inputs:

```rust
let compact_form = ClosedFormInputCompactForm::from_full_form(cs, &structured_input, round_function);
let input_commitment = commit_variable_length_encodable_item(cs, &compact_form, round_function);

for el in input_commitment.iter() {
    let gate = PublicInputGate::new(el.get_variable());
    gate.add_to_cs(cs);
}
```

This commitment links circuits together and enables recursive proof composition.

---

## 8. FSM (Finite State Machine) Pattern

All circuits use a common FSM pattern for handling large workloads across multiple proof instances:

```rust
// Select between fresh start or continuation
let state = QueueState::conditionally_select(
    cs,
    start_flag,
    &observable_input.initial_state,    // Fresh start
    &hidden_fsm_input.current_state,    // Continue from previous
);

// Process up to `limit` elements
for _ in 0..limit {
    // ... circuit logic
}

// Output either final result or intermediate state
let output = QueueState::conditionally_select(
    cs,
    completed,
    &final_state,
    &intermediate_state,
);
```

---

## Summary

The ZKsync circuit architecture demonstrates a modular, well-structured approach to ZK proof systems:

1. **Boojum** provides efficient primitives over the Goldilocks field
2. **Queues** enable verifiable data passing between circuits
3. **Main VM** executes EraVM instructions with witness-based memory access
4. **RAM/Storage/Log circuits** enforce global consistency and sorting
5. **Precompile circuits** implement Ethereum-compatible cryptographic operations
6. **FSM pattern** enables scalable proof generation for large workloads

This architecture enables ZKsync to prove correct execution of thousands of transactions in a single batch, providing Ethereum-level security with L2 scalability.

---

## References

- [era-boojum](https://github.com/matter-labs/era-boojum) - Boojum proof system
- [era-zkevm_circuits](https://github.com/matter-labs/era-zkevm_circuits) - Circuit implementations
- [ZKsync Protocol Documentation](https://docs.zksync.io/zksync-protocol)
