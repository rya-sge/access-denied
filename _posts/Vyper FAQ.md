# Vyper FAQ



> In the Vyper programming language, what symbol is used to initiate a single-line comment?

\#

> The syntax for comments in Vyper is identical to which other popular programming language, reflecting Vyper's design philosophy?

Python

> If a software project does not include any specific licensing information, what is generally the default legal status of the code?

It is considered unlicensed, meaning all rights are typically reserved by the author.

> What is the primary reason for processing source code written in a high-level language before it can run on a blockchain execution environment like the EVM?

To translate the human-readable code into low-level machine instructions that the execution environment can understand.

> Which specific output from the compilation process represents the code that is actually stored on the blockchain and executed by the EVM?

Runtime Bytecode

> Which two essential components are produced as output when a Vyper smart contract is successfully compiled?

The Application Binary Interface (ABI) and the EVM Bytecode.

> If a variable needs to store whole numbers which might include negative values, which general category of data type should be chosen?

Signed integer types (e.g., intN)

> Which Vyper data type is specifically designed to store Ethereum account or contract identifiers?

address

> In statically typed programming languages like Vyper, when must the data type of a variable be known?

At compile-time (before execution)





> In Vyper, what is the default value assigned to a state variable declared as `counter: uint256` if no initial value is provided?

0



> When a Vyper state variable is declared simply as `config_data: bytes32`, what is its default visibility and accessibility?

Internal: Accessible only from within the contract or inheriting contracts.

> What programming construct is often used to specify whether a function or method can be called from code outside of its defining structure or module?

Visibility modifiers or decorators (e.g., public, private, external).

> In Vyper, what keyword is used to begin the definition of a function?

def

> How can a function designated as `external` within a smart contract typically be invoked?

Only through transactions or calls originating from outside the contract.

> What generally characterizes an operation within a smart contract that results in a change to the data stored permanently on the blockchain?

It is considered a transaction, requires network resources (gas), and needs confirmation by the network.

> Under what circumstances does calling a Vyper function marked with `@view` incur gas costs for the initiator?

When the `@view` function is called by another function as part of an on-chain transaction's execution.



> What is a common convention used to identify the special function responsible for a contract's one-time initialization?

Using a specific reserved name (like `__init__` or `constructor`) often combined with a special marker or decorator.

> Which decorator must be applied to the constructor function in a Vyper contract?

@deploy

>  In Vyper, which operator is specifically used for integer division that rounds the result down to the nearest whole number?

//

> If you need to create a custom, composite data type that bundles several related fields (which can be of different types) together under a single identifier, what construct would you typically define?

Struct



>  How do you access the first element of a Vyper list named `my_list` which has a fixed size?

Using index 0, like `my_list[0]`.



> In Vyper, what is the primary purpose of using a `struct`?

To group several related variables under a single custom data type name.

## Code

```python
# pragma version ^0.4.0
# State variable to store the favorite number
my_favorite_number: public(uint256) # Intended initial value is 7
# Existing functions (e.g., to store or retrieve the number)
# ...
# Constructor to set the initial value
@deploy
def __init__():
    # Initialize the favorite number to 7 upon deployment
    self.my_favorite_number = 7
```

