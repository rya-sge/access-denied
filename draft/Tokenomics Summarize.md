# Blockchain Tokenomics  - Overview

### 1. Bitcoin (BTC)

- Maximum supply: 21 million coins. 
- Issuance via Proof-of-Work mining; miners receive newly minted BTC + transaction fees.
- Every ~210,000 blocks (~4 years) the “block reward” is halved (halving), decreasing inflation over time. 
- Once 21 million is reached (estimated ~2140), issuance ends and supply becomes fixed.
- Key narrative: Scarcity (digital gold), decentralised issuance, predictable monetary policy.

------

### 2. Ethereum (ETH)

- Issuance: After the “Merge” Ethereum moved to Proof-of-Stake, with staking rewards rather than PoW mining.
- Inflation: There is no strict capped supply; base issuance replaced by fee burn (EIP-1559) which makes ETH potentially deflationary at times.
- Utility: ETH is used to pay transaction (“gas”) fees, participate in staking, secure the network, and serve as collateral in DeFi.
- Governance: ETH holders can stake, run validators (or delegate), and participate indirectly in network security.
- Tokenomics: Because of fee burn plus staking rewards, ETH’s effective supply dynamics depend heavily on network activity and staking participation.

------

### 3. Internet Computer (ICP)

- Native token: ICP. Two-token model: ICP and “cycles” used for computation. [learn.internetcomputer.org+2Cube Exchange+2](https://learn.internetcomputer.org/hc/en-us/articles/34574082263700-Tokenomics-Governance)
- ICP token utility: governance, network rewards (node providers), locking/maturity to earn voting rewards; conversion to cycles to pay for computation. [learn.internetcomputer.org+1](https://learn.internetcomputer.org/hc/en-us/articles/34090810571284-Tokenomics)
- Token flow: ICP minted to reward node providers and voters (inflationary); ICP burned when developers convert to cycles for compute (deflationary). [Medium+2Reddit+2](https://medium.com/@iantdover/the-tokenomics-of-internet-computer-protocol-are-quite-good-463a7a5880d3)
- Current model: The ecosystem aims for compute-burns to eventually exceed new issuance, making ICP net deflationary in the future. [Internet Computer Developer Forum+1](https://forum.dfinity.org/t/tokenomics-series-projecting-the-total-supply-of-icp/20205)
- Circulating supply metrics are published regularly. [Internet Computer Dashboard](https://dashboard.internetcomputer.org/circulation)

------

### 4. Arbitrum (ARB)

- Native governance token: ARB. [docs.arbitrum.foundation+1](https://docs.arbitrum.foundation/concepts/arb-token)
- Supply cap: ~10 billion ARB tokens. [Exponential DeFi+1](https://exponential.fi/assets/arbitrum/5e3d2f5e-9218-44db-a88d-a2bb07b0986f)
- Inflation: After initial allocation, ~2% annual inflation. [Exponential DeFi](https://exponential.fi/assets/arbitrum/5e3d2f5e-9218-44db-a88d-a2bb07b0986f)
- Allocation: ~43% of supply to the Arbitrum DAO treasury; ~27% to Offchain Labs team; ~18% to investors; ~12% airdrop to eligible users; ~1% to DAOs building ecosystem. [Exponential DeFi+1](https://exponential.fi/assets/arbitrum/5e3d2f5e-9218-44db-a88d-a2bb07b0986f)
- Vesting: Team/investor tokens subject to multi-year linear unlocks. [DropsTab](https://dropstab.com/coins/arbitrum/vesting)
- Utility: Governance participation in Arbitrum ecosystem; aligning incentives for ecosystem growth.
  - Gas is paid in Ether, not ARB

------

### 5. Optimism (OP)

- Token: OP. [community.optimism.io+1](https://community.optimism.io/op-token/op-token-overview)
- Supply: Total supply ~4.29 billion OP (approx). [DropsTab](https://dropstab.com/coins/optimism/vesting)
- Use case: Governance of the Optimism Collective and incentivising public goods in the ecosystem. [community.optimism.io](https://community.optimism.io/op-token/op-token-overview)
- Distribution: A portion to community/participants; low early circulating supply increasing over time; unlock schedules apply. [Reddit+1](https://www.reddit.com/r/CryptoCurrency/comments/v2d2xg/optimisms_op_tokenomics_are_solid_when_does_it/)
- Model emphasizes aligning token incentives with ecosystem growth (public goods, developer adoption).
  - Gas is paid in Eth, not in OP tokens

------

### 6. TAO

- I couldn’t find a well-documented tokenomics model for “TAO” that matched a major blockchain token under that exact name in the context you provided.
- If you meant a different token (e.g., “Tao” or maybe “Tao Network”), please clarify and I can check further.

------

### 7. Render (RNDR/RENDER)

- Token: RENDER (formerly RNDR) used in the Render Network. 
- Token has migrated from Ethereum and Polygon to Solana (see [https://know.rendernetwork.com/general-render-network/rndr-to-render-what-you-need-to-know/render-network-upgrade-portal-faq)](https://know.rendernetwork.com/general-render-network/rndr-to-render-what-you-need-to-know/render-network-upgrade-portal-faq))
- Utility: 
  - Users pay for rendering jobs with RENDER; 
  - node operators earn RENDER by providing GPU compute. 
- Supply: Initial mint ~536,870,912 RENDER (2^29) tokens. 
- Burning mechanism: Oversupply from old contract (~1.61 billion) to be burned. 
- Transition: Migrating contract (Ethereum → Solana) and future supply management in focus. [CryptoRank+1](https://cryptorank.io/price/render-token/vesting)

Reference: [CoinGecko](https://www.coingecko.com/learn/what-is-render-network-rndr-crypto), [Render Network Knowledge Base+1](https://know.rendernetwork.com/basics/token-metrics-summary), [Render Network Knowledge Base](https://know.rendernetwork.com/basics/token-metrics-summary), https://know.rendernetwork.com/general-render-network/rndr-to-render-what-you-need-to-know/render-network-upgrade-portal-faq

------

### 8. Cosmos (ATOM)

- Token: ATOM, the native token of the Cosmos Network / Cosmos Hub. [Tokenomist+1](https://tokenomist.ai/cosmos)
- Supply/dynamics: ATOM is inflationary (rather than fixed-cap). Inflation rate driven by staking participation. [CoinCodeCap](https://coincodecap.com/cosmos-atom-tokenomics)
- Distribution: Various allocations including seed sale, strategic sale, foundation, etc. [CoinCodeCap+1](https://coincodecap.com/cosmos-atom-tokenomics)
- Mechanisms: ATOM is used to stake and secure Cosmos Hub; 
  - validators stake ATOM, earn rewards; incentives designed for inter-chain activity. [Space and Time](https://spaceandtime.io/blog/atom-tokenomics-a-dive-into-scalability-and-sustainability)
- Governance: Ongoing discussion of “Cosmos 2.0” tokenomics to improve value capture and ecosystem alignment. [The Defiant](https://thedefiant.io/news/defi/cosmos-upgrades-proposed)
- https://forum.cosmos.network/t/atom-needs-to-capture-more-ecosystem-value/13673

------

### 9. Solana (SOL)

- Token: SOL. [Solana Compass+1](https://solanacompass.com/tokenomics)
- Inflationary model: Initially ~8% annual inflation, declining ~15% each “epoch-year” until floor ~1.5% annual inflation. [Reddit+1](https://www.reddit.com/r/solana/comments/17tu0xg/sol_tokenomics_could_someone_help_me_understand/)
- Distribution of inflation rewards: ~95% of inflation goes to validators (staking rewards); ~5% to the Solana Foundation for ecosystem growth. [Tokenomist](https://tokenomist.ai/solana)
- Utility: Used for paying transaction fees, staking, securing network, running validators. [Shrimpy Academy](https://academy.shrimpy.io/post/solana-tokenomics-explained)
- Supply status: No hard cap; circulating supply around ~445 million SOL (2025 estimate) but total supply can increase via inflation. [Gemini](https://www.gemini.com/cryptopedia/solana-circulating-supply-how-many-sol-tokens-are-there)

------

### 10. Morpho (MORPHO)

- Token: MORPHO, the native governance token of the Morpho Protocol. [Morpho Docs+1](https://docs.morpho.org/learn/governance/morpho-token/)
- Total supply: 1 billion MORPHO tokens. [Morpho Docs](https://docs.morpho.org/learn/governance/morpho-token/)
- Distribution:
  - ~35.4% controlled by Morpho governance/DAO. [Morpho Docs+1](https://docs.morpho.org/learn/governance/morpho-token/)
  - ~27.5% to strategic partners. [Morpho Docs](https://docs.morpho.org/learn/governance/morpho-token/)
  - ~15.2% to founders. [Morpho Docs](https://docs.morpho.org/learn/governance/morpho-token/)
  - Other allocations: early contributors, ecosystem development, users/launch pools. [Morpho Docs](https://docs.morpho.org/learn/governance/morpho-token/)
- Vesting: Founders, strategic partners, etc have multi-year lockups and linear vesting. [Morpho Docs+1](https://docs.morpho.org/learn/governance/morpho-token/)
- Circulating supply: At launch, relatively low circulating supply (~11.2%) but expected to increase over time. [Morpho Docs+1](https://docs.morpho.org/learn/governance/morpho-token)
- Utility: Governance, staking (if applicable) and aligning interests of users/holders with protocol growth.

------

### 11. Aave (AAVE)

- Token: AAVE, native to the Aave Protocol. [aave.com+1](https://aave.com/docs/developers/aave)
- Utility: Governance token; token holders vote on protocol changes, risk parameters, liquidity incentives. [aave.com](https://aave.com/docs/developers/aave)
- Recent proposal “Aavenomics” aims to revamp tokenomics to include buybacks, revenue sharing, safety modules. [CryptoNinjas+1](https://www.cryptoninjas.net/news/aave-and-aavenomics-token-buybacks-safety-nets-and-revenue-redistribution/)
- Tokenomics currently: supply/issuance details are documented but evolving; strong emphasis on aligning token value capture with platform revenue. [MEXC](https://www.mexc.com/price/AAVE/tokenomics)

------

### 12. Chainlink (LINK)

- Token: LINK, native to the Chainlink oracle network. [Chainlink+1](https://chain.link/economics)
- Maximum supply: 1 billion LINK tokens. [Kraken+1](https://www.kraken.com/learn/what-is-chainlink-link)
- Utility: Oracles providing data require LINK staking/collateral; token used for incentives to data providers, network security, and data reliability. [Shrimpy Academy+1](https://academy.shrimpy.io/post/chainlink-tokenomics-explained)
- Distribution: 350 million LINK released in public and private sales; remainder subject to emissions. [Kraken](https://www.kraken.com/learn/what-is-chainlink-link)
- Tokenomics emphasize scarcity + utility (staked collateral) + value capture via network growth.

------

### 13. NEAR Protocol (NEAR)

- Token: NEAR. [NEAR+1](https://near.org/blog/near-token-supply-and-distribution)
- Supply: Maximum supply ~1 billion NEAR tokens (according to earlier data) but subject to inflation and distribution. [CrossTech](https://crosstechpayments.com/near-protocol-the-future-of-web-3-0/)
- Distribution: At launch, large portion issued; remaining to be used for staking rewards and ecosystem incentives. [NEAR](https://near.org/blog/near-token-supply-and-distribution)
- Governance and upgrades: Community is proposing a “Tokenomics 2.0” update to refine inflation, decentralization, validator incentives. [NEAR Forum](https://gov.near.org/t/near-tokenomics-2-0-governance-proposa/41669)
- Utility: NEAR is used for staking (securing network), paying fees, participating in governance, and facilitating the protocol’s ecosystem of dApps.

Reference:

[Near - NEAR Token Supply and Distribution](https://www.near.org/blog/near-token-supply-and-distribution)