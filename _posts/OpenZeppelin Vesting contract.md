# OpenZeppelin Vesting contract

A vesting wallet is an ownable contract that can receive native currency and ERC-20 tokens, and release these assets to the wallet owner, also referred to as "beneficiary", according to a vesting schedule.

Any assets transferred to this contract will follow the vesting schedule as if they were locked from the beginning. Consequently, if the vesting has already started, any amount of tokens sent to this contract will (at least partly) be immediately releasable.

By setting the duration to 0, one can configure this contract to behave like an asset timelock that holds tokens for a beneficiary until a specified time.

https://docs.openzeppelin.com/contracts/5.x/api/finance#VestingWallet