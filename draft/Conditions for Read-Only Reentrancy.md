## Conditions for Read-Only Reentrancy

- There is some **state**: ;
- There is an **external call**, and this state is modified after the call;
- There is another contract, which depends on this state (**utilized by getter**).

Next, let’s examine the following screenshot:

The read-only [reentrancy](https://www.quicknode.com/guides/ethereum-development/smart-contracts/a-broad-overview-of-reentrancy-attacks-in-solidity-contracts/) is a Reentrancy scenario where a `view` the function is reentered which in most cases is unguarded as it does not modify the contract’s state.

However, if the state is inconsistent, wrong values could be reported. Other protocols relying on a return value, can be tricked into reading the wrong state to perform unwanted actions. Check out [this](https://chainsecurity.com/curve-lp-oracle-manipulation-post-mortem/) blog and [this](https://quillaudits.medium.com/decoding-220k-read-only-reentrancy-exploit-quillaudits-30871d728ad5) article to know more about this.

https://blog.pessimistic.io/read-only-reentrancy-in-depth-6ea7e9d78e85

https://www.chainsecurity.com/blog/curve-lp-oracle-manipulation-post-mortem

A rrentrancy could be occurent if  a token with a fallback function is called, which is the case for :

1) ERC-721 and ERC-1155 if the recipient to is a smart contract
2) Ether with the function receive or fallback

During the execution of the fallback, not all tokens have been sent, therefore balances are not fully updated while the total supply of the LP token has already decreased. 

Hence, an attacker can take control of the execution flow while the pool’s state is inconsistent. Pool balances and total supply do not match. Note that the function remove_liquidity_imbalance is similar to remove_liquidity but allows users to withdraw liquidity in an imbalanced way. Hence, if an imbalanced withdrawal taking just 1 wei of ETH is made, the balance will be significantly higher than with the regular remove_liquidity. Hence, the inconistency can be amplified.

## Solution: 

- Make the reentrancy locks public to allow developers to decide whether or not they want to revert in case the lock is active.
- Revert in view function if the lock is active.