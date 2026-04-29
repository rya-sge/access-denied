## H-Inherit - Anybody can be the new owner

The owners should be the first beneficiary instead of msg.sender

```solidity
  if (beneficiaries.length == 1) {
       // owner should be the beeficiars
       owner = msg.sender;
        _setDeadline();
  }
```

As a result, the msg.sender can take ownership of the contract and use it to withdraw the funds by calling `sendETH` and ` sendERC20`.

### L-Potential Denial of Service

The following loop

```solidity
 for (uint256 i = 0; i < divisor; i++) {
                address payable beneficiary = payable(beneficiaries[i]);
                (bool success,) = beneficiary.call{value: amountPerBeneficiary}("");
                require(success, "something went wrong");
            }
```

If one of the beneficiary is a smart contract, it could block the transfer of funds by always reverting..

Recommendation: 

- Don't revert
- Indicate each payment was successful and allows retry for failed payment



## H- Reentrancy

THere is a re-entrancy in the function ẁithdrawInheritedFunds

Recommandation: Add a non-reenter modifier

## M - Precision loss 

buyOutEstateNFT

```
  uint256 finalAmount = (value / divisor) * multiplier;
```

Use instead:

```
  uint256 finalAmount = (value *  multiplier) / divisor ;
```

## Safe

 createEstate should use _safeMint