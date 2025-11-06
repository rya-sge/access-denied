## [Vyper Vested Claims](https://codehawks.cyfrin.io/c/2025-02-vyper-vested-claims)

This smart contract is designed for distributing tokens with a vesting schedule. The contract uses Merkle trees for claims, allowing 31% of tokens to be released at the Token Generation Event (TGE) and the remaining 69% to be released linearly over time.

https://github.com/CodeHawks-Contests/2025-02-vyper-vested-claims/tree/main/src

[TOC]



## Code

### Vested Claim

```python

"""
@title Vested Claims
@license MIT
@author Krakovia
@notice This contract is used to distribute tokens to users, 31% TGE, 69% linear vesting
"""

interface IERC20:
    def transfer(_to: address, _value: uint256) -> bool: nonpayable

vesting_start_time: public(uint256)
vesting_end_time:   public(uint256)
merkle_root:        public(bytes32)
token:              public(address)
owner:              public(address)
claimed_amount:     public(HashMap[address, uint256])

event Claimed:
    user:   indexed(address)
    amount: uint256
event MerkleRootUpdated:
    merkle_root: indexed(bytes32)
event TokensRescued:
    to:     indexed(address)
    amount: uint256

@deploy
def __init__(merkle_root: bytes32, token: address, vesting_start_time: uint256, vesting_end_time: uint256):
    """
    @notice Initialize the contract with the merkle root, token address, vesting start and end time
    @param merkle_root: bytes32, the merkle root of the vesting list
    @param token: address, the address of the token contract
    @param vesting_start_time: uint256, the start time of the vesting
    @param vesting_end_time: uint256, the end time of the vesting
    """
    self.merkle_root = merkle_root
    self.token = token
    self.vesting_start_time = vesting_start_time
    self.vesting_end_time = vesting_end_time
    self.owner = msg.sender
    log MerkleRootUpdated(merkle_root)

def onlyOwner():
    """
    @notice This function is used to restrict access to the owner only
    """
    assert msg.sender == self.owner, "Only owner can call this function"

@pure
def _hash_pair(a: bytes32, b: bytes32) -> bytes32:
    """
    @notice This function is used to hash a pair of bytes32
    @param a: bytes32
    @param b: bytes32
    @return bytes32: the hash of the pair
    """
    if convert(a, uint256) < convert(b, uint256):
        return keccak256(concat(a, b))
    return keccak256(concat(b, a))

def _verify_proof(proof: DynArray[bytes32, 20], leaf: bytes32) -> bool:
    """
    @notice This function is used to verify the merkle proof
    @param proof: DynArray[bytes32, 20], the merkle proof
    @param leaf: bytes32, the leaf node
    @return bool: True if the proof is valid
    """
    computed_hash: bytes32 = leaf
    for proof_element: bytes32 in proof:
        computed_hash = self._hash_pair(computed_hash, proof_element)
    return computed_hash == self.merkle_root

def verify_proof(user: address, amount: uint256, proof: DynArray[bytes32, 20]) -> bool:
    """
    @notice This function is used to verify the merkle proof
    @param user: address, the address of the user
    @param amount: uint256, the amount of tokens
    @param proof: DynArray[bytes32, 20], the merkle proof
    @return bool: True if the proof is valid
    """
    return self._verify_proof(
        proof,
        keccak256(
            concat(
                convert(user, bytes20),
                convert(amount, bytes32)
            )
        )
    )

@view
def _calculate_vested_amount(total_amount: uint256) -> uint256:
    """
    @notice This function is used to calculate the vested amount
    @param total_amount: uint256, the total amount of tokens
    @return vested: uint256, the vested amount
    """
    current_time: uint256 = block.timestamp
    start_time:   uint256 = self.vesting_start_time
    end_time:     uint256 = self.vesting_end_time
    vested:       uint256 = 0

    if current_time >= end_time:
        return total_amount

    vesting_duration: uint256 = end_time - start_time
    elapsed:          uint256 = current_time - start_time
    instant_release:  uint256 = (total_amount * 31) // 100
    linear_vesting:   uint256 = (total_amount * 69) // 100

    vested = instant_release + (linear_vesting * elapsed) // vesting_duration
    return vested

@external
def set_merkle_root(merkle_root: bytes32):
    """
    @notice This function is used to set the merkle root
    @param merkle_root bytes32, the new merkle root
    @dev This function can only be called by the owner
    """
    self.onlyOwner()
    self.merkle_root = merkle_root
    log MerkleRootUpdated(merkle_root)

@external
def rescue_tokens(to: address, amount: uint256):
    """
    @notice This function is used to rescue tokens from the contract
    @param to address, the address to send the tokens to
    @param amount uint256, the amount of tokens to send
    @dev this is a "better safe then sorry" function, use it only in case of emergency
    @dev This function can only be called by the owner
    """
    self.onlyOwner()
    log TokensRescued(to, amount)
    _success: bool = extcall IERC20(self.token).transfer(to, amount)
    assert _success, "Transfer failed"


@external
def claim(user: address, total_amount: uint256, proof: DynArray[bytes32, 20]) -> bool:
    """
    @notice This function is used to claim the tokens
    @dev Anyone can claim for any user
    @param user address, the address of the user
    @param total_amount uint256, the total amount of tokens
    @param proof DynArray[bytes32, 20], the merkle proof
    @return bool True if the claim is successful
    """
    # Checks
    assert self.verify_proof(user, total_amount, proof), "Invalid proof"
    assert block.timestamp >= self.vesting_start_time, "Claiming is not available yet"

    claimable:      uint256 = 0
    current_amount: uint256 = self.claimed_amount[user]
    vested:         uint256 = self._calculate_vested_amount(total_amount)

    # Calculate how much the user can claim now
    if vested > current_amount:
        claimable = vested - current_amount

    assert claimable > 0, "Nothing to claim"
    # Update the claimed amount - Effects
    self.claimed_amount[user] += claimable
    # invariant: claimed amount should always be less than or equal to amount (better safe then sorry)
    assert current_amount + claimable <= total_amount, "Claimed amount exceeds total amount"
    log Claimed(user, claimable)
    
    # Transfer the claimable amount to the user - Interactions
    _success: bool = extcall IERC20(self.token).transfer(user, claimable)
    assert _success, "Transfer failed"
    return True

@view
@external
def claimable_amount(user: address, total_amount: uint256) -> uint256:
    """
    @notice this function is needed on the frontend to show the claimable amount
    @param user address, the address of the user
    @param total_amount uint256, the total amount of tokens
    @return claimable uint256, the amount of tokens that can be claimed
    @dev the data is NOT verified against the merkle root
    @dev no on-chain contract should/will use this function
    """
    assert block.timestamp >= self.vesting_start_time, "Claiming is not available yet"

    claimable:      uint256 = 0
    current_amount: uint256 = self.claimed_amount[user]
    vested:         uint256 = self._calculate_vested_amount(total_amount)

    # Calculate how much the user can claim now
    if vested > current_amount:
        claimable = vested - current_amount

    return claimable

```

### ERC20 Token

```python

from ethereum.ercs import IERC20
implements: IERC20

# ERC20
name:        public(String[32])
symbol:      public(String[32])
decimals:    public(uint8)
totalSupply: public(uint256)
balanceOf:   public(HashMap[address, uint256])
allowance:   public(HashMap[address, HashMap[address, uint256]])

@deploy
def __init__():
    _supply: uint256 = 1_000_000 * 10**18
    self.name                  = "Token"
    self.symbol                = "TKN"
    self.decimals              = 18
    self.totalSupply           = _supply
    self.balanceOf[msg.sender] = _supply
    log IERC20.Transfer(empty(address), msg.sender, _supply)

# ERC20 Functions

def _update(_from: address, _to: address, _value: uint256):
    self.balanceOf[_from] -= _value
    self.balanceOf[_to]   += _value
    log IERC20.Transfer(_from, _to, _value)

def _transfer(_from: address, _to: address, _value: uint256):
    self._update(_from, _to, _value)

@external
def transfer(_to: address, _value: uint256) -> bool:
    self._transfer(msg.sender, _to, _value)
    return True

@external
def transferFrom(_from: address, _to: address, _value: uint256) -> bool:
    self.allowance[_from][msg.sender] -= _value
    self._transfer(_from, _to, _value)
    return True

@external
def approve(_spender: address, _value: uint256) -> bool:
    self.allowance[msg.sender][_spender] = _value
    log IERC20.Approval(msg.sender, _spender, _value)
    return True

@external
def burn(_value: uint256):
    self._update(msg.sender, empty(address), _value)
    self.totalSupply -= _value

```



## Vulnerability


Two vulnerabilitis have been reported on this projet

### Integer Division Rounding in Vesting Calculation Can Lead to Token Loss (Meidum)

[2025-02-vyper-vested-claims/s/35](https://codehawks.cyfrin.io/c/2025-02-vyper-vested-claims/s/35)

#### Summary

The `_calculate_vested_amount` function uses integer division to calculate the instant release and linear vesting portions, which can lead to token loss due to rounding errors when the total amount is not perfectly divisible by 100.

#### Vulnerability Details

The vesting calculation splits the total amount into two parts using integer division:





### Impact

- **Token Loss**: Some tokens might be permanently locked in the contract because they can never be claimed due to rounding errors
- **Accounting Discrepancy**: The sum of all claimed tokens might be less than the total tokens allocated in the Merkle tree
- **Fairness Issue**: Users with certain allocation amounts might lose more tokens proportionally than others

The severity is low because:

1. The contract correctly returns the full amount at the end of vesting with `if current_time >= end_time: return total_amount`
2. The percentage of tokens lost is very small (typically 1 token)
3. It's a precision issue rather than a security vulnerability

### Recommendation

While the contract already handles the end of vesting correctly, for better precision during the vesting period, consider one of these approaches:

1. Adjust one of the percentages to ensure they sum to 100% after division:

```python
instant_release = (total_amount * 31) // 100

linear_vesting = total_amount - instant_release  # Ensure no tokens are lost
```



1. Or calculate the percentage first, then apply it once:

```

```



### Missing #pragma version 0.4.0 in VestedAirdrop (Low)

https://codehawks.cyfrin.io/c/2025-02-vyper-vested-claims/s/80



#### Summary

The contract does not specify the Vyper compiler version.

#### Vulnerability Details

- Vyper requires the `#pragma version` directive to ensure compatibility with the intended compiler version.
- Missing this may lead to compilation errors or unexpected behavior if the code is compiled with a different version.

#### Impact

- The contract may fail to compile or behave unpredictably with newer compiler versions.

#### Recommendations

- Add the compiler version directive

```
\# @version 0.4.0
```

