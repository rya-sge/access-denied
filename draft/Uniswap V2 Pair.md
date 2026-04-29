

### Uniswap V2 Pair



`skim(address to)`

Force balances to match reserves.

Example:

If contract balance has:

-  20 tokens0 and 40 token1
- And 10 tokens in reserve0 and 12 tokens in reserve1,

The function will transfer to `to`:

token0: 20 - 10 = 10

token1: 40 -12 =38

Note that the function will revert if the reserve of token0 or token1 is superior to the contract balance since we will have an `underflow` (ds-math-sub-underflow).



`sync`

force reserves to match balances

 _update(IERC20(token0).balanceOf(address(this)), IERC20(token1).balanceOf(address(this)), reserve0, reserve1);

### Uniswap V2 Factory

### CreatePair

The function performs the following check:

- Token A and tokenB must have different address (error `UniswapV2: IDENTICAL_ADDRESSES`)
- Token0 (tokenA or Token B) cannot be the zero address (error `UniswapV2: ZERO_ADDRESS`)
- The pair must not exist (error `UniswapV2: PAIR_EXISTS`)

This check means you can not create a new pool if the pair already exists

### Fees

Only the address `feeToSetter`, set at deployment, can update this vlaue.

Note that the value `feeToSetter` is not used inside the factory contract, but instead inside the contract `UniswapV2Pair`.



