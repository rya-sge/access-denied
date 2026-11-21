"""Recompute the numbers quoted in the EIP-7251 article.

Functions are transcribed from EIP-7251 (fee) and consensus-specs
specs/electra/beacon-chain.md (churn, slashing, effective balance), commit
065bcd5c6ad96186cd2c0ac1c435f620a0b25373. Amounts are in ETH, not Gwei, except
where the spec rounds to EFFECTIVE_BALANCE_INCREMENT (1 ETH), which is the same.
"""

def fake_exponential(factor, numerator, denominator):
    i, output, acc = 1, 0, factor * denominator
    while acc > 0:
        output += acc
        acc = (acc * numerator) // (denominator * i)
        i += 1
    return output // denominator

def balance_churn(total_active_eth):
    return max(128, total_active_eth // 65536)

def activation_exit_churn(total):
    return min(256, balance_churn(total))

def consolidation_churn(total):
    return balance_churn(total) - activation_exit_churn(total)

def effective_balance(balance, eb, max_eb):
    # hysteresis: down 0.25 ETH, up 1.25 ETH (phase0 preset)
    if balance + 0.25 < eb or eb + 1.25 < balance:
        return min(int(balance), max_eb)
    return eb

print("fee (wei) by excess:")
for x in (0, 12, 17, 50, 100, 200, 300, 400, 500):
    print(f"  excess={x:4d} fee={fake_exponential(1, x, 17)}")

print("smallest total active balance with consolidation churn > 32 ETH:")
t = 128 * 65536
while consolidation_churn(t) <= 32:
    t += 1
print(" ", t)

T = 34_000_000
print(f"T={T}: balance churn {balance_churn(T)}, activation/exit {activation_exit_churn(T)}, "
      f"consolidation {consolidation_churn(T)} ETH/epoch, {consolidation_churn(T)*225} ETH/day")

print("initial slashing penalty: pre-Electra 32/32 =", 32 / 32,
      "| Electra 32 ETH:", 32 / 4096, "| Electra 2048 ETH:", 2048 / 4096)

print("0x01 at 33.3 ETH -> EB", effective_balance(33.3, 32, 32))
print("0x02 at 33.3 ETH -> EB", effective_balance(33.3, 32, 2048))
print("0x02 at 33.2 ETH -> EB", effective_balance(33.2, 32, 2048))
print("pending consolidations queue size (bytes):", 262144 * 16)
