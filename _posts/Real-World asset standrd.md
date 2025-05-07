# Real-World asset standrd

# [ERC: Universal RWA Interface](https://ethereum-magicians.org/t/erc-universal-rwa-interface/23972)

https://ethereum-magicians.org/t/erc-universal-rwa-interface/23972/2

This proposal introduces a minimal, standardized interface for Real World Asset (RWA) tokenization that is designed to be maximally compatible across existing token standards such as ERC-20, ERC-721, and ERC-1155. It focuses on providing only the essential compliance and enforcement functions common to regulated assets, without imposing specific implementation patterns or additional optional features.

Non-essential capabilities like pausing, metadata handling, or identity integrations are intentionally excluded from the standard, as they tend to be opinionated and vary greatly depending on the specific RWA use case. This approach ensures broad interoperability and minimal friction for adoption while allowing developers to extend functionality as needed within their own contracts.