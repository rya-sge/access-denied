# EIP-7251 article: number checks

`check_numbers.py` recomputes the figures quoted in
`_posts/2026-11-20-eip-7251-max-effective-balance-consolidation.md`:

- the consolidation request fee (`fake_exponential(1, excess, 17)`) for several excess values;
- the Electra churn split (balance, activation/exit, consolidation) and the total active balance
  below which consolidations are ignored;
- the initial slashing penalty before and after Electra;
- effective balance hysteresis for `0x01` and `0x02` validators;
- the size of the pending consolidations queue.

Sources: EIP-7251 (ethereum/EIPs at `8194528a2ee9a4893a398a5871c470ab0ac3b09a`) and
`specs/electra/beacon-chain.md` (ethereum/consensus-specs at
`065bcd5c6ad96186cd2c0ac1c435f620a0b25373`).

Run: `python3 -I check_numbers.py` (Python 3.8+, no dependency).
