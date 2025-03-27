

# Types

### Balance

```rust
pub struct Balance {
    value: i64,
}

#[derive(Copy, Debug, Default, Drop, Serde)]
pub struct BalanceDiff {
    pub before: Balance,
    pub after: Balance,
}
```

### Funding index

`FundingIndex` represents a global funding rate tracker for each synthetic asset in the system.
 It's used to calculate funding payments between long and short position holders.
To optimize performance, positions are only updated with the latest funding index when their
 owners execute transactions. 

The system then calculates the accumulated funding payment since

- the last interaction and adjusts the position's collateral balance accordingly.
- After each update, the current funding index is cached for each synthetic asset in the position.

```rust
pub struct FundingIndex {
    /// Signed 64-bit fixed-point number:
    /// 1 sign bit, 31-bits integer part, 32-bits fractional part.
    /// Represents values as: actual_value = stored_value / 2**32.
    pub value: i64,
}
```



### Position

```rust
pub struct Position {
    pub version: u8,
    pub owner_account: Option<ContractAddress>,
    pub owner_public_key: PublicKey,
    pub collateral_balance: Balance,
    pub synthetic_balance: IterableMap<AssetId, SyntheticBalance>,
}

/// Synthetic asset in a position.
/// - balance: The amount of the synthetic asset held in the position.
/// - funding_index: The funding index at the time of the last update.
#[derive(Copy, Drop, Serde, starknet::Store)]
pub struct SyntheticBalance {
    pub version: u8,
    pub balance: Balance, // Balance => i64
    pub funding_index: FundingIndex //  FundingIndex => i64,
}

#[derive(Copy, Debug, Drop, Hash, PartialEq, Serde)]
pub struct PositionId {
    pub value: u32,
}

#[derive(Copy, Debug, Drop, Serde, Default)]
pub struct PositionDiff {
    pub collateral_diff: Balance,
    pub synthetic_diff: Option<(AssetId, Balance)>,
}

#[derive(Copy, Debug, Drop, Serde, Default)]
pub struct PositionDiffEnriched {
    pub collateral_enriched: BalanceDiff,
    pub synthetic_enriched: Option<SyntheticDiffEnriched>,
}

#[derive(Copy, Debug, Drop, Serde)]
pub struct PositionData {
    pub synthetics: Span<SyntheticAsset>,
    pub collateral_balance: Balance,
}

```

