### Address Poisoning in Blockchain: Understanding the Threat, Examples, and Protections

Blockchain technology is hailed for its decentralized and secure nature, but it is not immune to threats. One such emerging issue is **address poisoning**, a tactic used by attackers to mislead users and compromise transactions. In the blockchain context, address poisoning refers to the manipulation of wallet address history to deceive users into sending funds to malicious addresses.

This article delves into what address poisoning is, how it works, real-world examples, and steps users can take to protect themselves.

------

### **What is Address Poisoning in Blockchain?**

In blockchain networks like Bitcoin or Ethereum, wallet addresses are long alphanumeric strings used to send and receive cryptocurrency. Address poisoning exploits the reliance of users on transaction history and address familiarity. The attacker generates a wallet address that closely resembles a legitimate one and then interacts with the victim’s wallet by sending tiny, often valueless, transactions.

The goal is to “poison” the wallet history by inserting the fake address into the victim's transaction list, hoping the victim later mistakes it for their legitimate address when initiating a transaction.

------

### **How Does Address Poisoning Work?**

### Preparation

**Creation of a Similar Address** (Vanity address):

Attackers use different tools to generate wallet addresses with prefixes or patterns resembling the victim's genuine address.

For Bitcoin, you can use for example [Vanity](https://en.bitcoin.it/wiki/Vanitygen)

For a complete address you have 2 which is computationnaly infisible but for a few charcers, for example the first 4 bytes and the last 4 bytes, it is only 2^3¹6

### Attack

**Sending a Dust Transaction**:

A dust transaction (a transaction involving an extremely small amount of cryptocurrency, often just a fraction of a cent) is sent from the fake address to the victim's wallet.

**Manipulating Wallet History** 

The victim’s wallet interface now displays the fake address in the transaction history, mixed with legitimate addresses. The address book is now poisoning

### Exploitation

The exploitation will depends if the victim fells in the trap or not.

When the victim later initiates a transaction and selects an address from the history, they might inadvertently choose the attacker’s address, sending funds directly to the attacker.

------

### **Examples of Address Poisoning**

#### **Example 1: A New Ethereum Wallet User**

A new user of an Ethereum wallet frequently transacts with a specific address. 

1. An attacker observes the user’s address on the blockchain and generates a lookalike address (e.g., a slight change in the last few characters). 
2. The attacker sends 0.00001 ETH to the user’s wallet. The poisoned address appears in the wallet history. 
3. The user, in haste, selects the poisoned address for a later transaction, losing their funds.

#### **Example 2: Bitcoin Dusting Attack**

In a Bitcoin-based attack, the attacker sends dust amounts to multiple wallets, including one belonging to a targeted victim. They create a fake address resembling a commonly used one from the victim’s wallet history. If the victim fails to double-check the full address during their next transaction, the attacker successfully reroutes the funds.

### Example

## Address Poisoning in the wild 

To wrap this subject up, let's review how an address poisoning attack looks in practice.

On May 3rd, 2024, an address poisoning attack, which also used event spoofing, enabled an attacker to steal 1155 WBTC tokens - worth over $68M. While the funds were [ultimately returned](https://cointelegraph.com/news/wbtc-thief-returns-71-million), this incident is a good case study to examine how these attacks look in a real-world attack scenario. Let's take a look.

To start the attack, the attacker has generated an address similar to the one that the WBTC holder has legitimately interacted with:

Legitimate address: **0xd9A1**b0B1e1aE382DbDc898Ea68012FfcB2**853a91**

Attacker's address: **0xd9a1**c3788d81257612e2581a6ea0ada244**853a91**

#### Preparation:

Step 1: Target acquisition

The attacker notices a [movement](https://etherscan.io/tx/0xb18ab131d251f7429c56a2ae2b1b75ce104fe9e83315a0c71ccf2b20267683ac) from an address holding millions of dollars worth of tokens. Usually, attackers use bots that monitor new transactions being added to the chain to find targets worth pursuing

Step 2: Generate a similar address

To start the attack, the attacker has generated an address similar to the one that the WBTC holder has legitimately interacted with:

Legitimate address: 0xd9A1b0B1e1aE382DbDc898Ea68012FfcB2853a91

Attacker's address: 0xd9a1c3788d81257612e2581a6ea0ada244853a91

As you can [see](https://etherscan.io/txs?a=0xd9a1c3788d81257612e2581a6ea0ada244853a91&p=2), the first on-chain activity

#### Attack

Step 3: Event Spoofing

The attacker employs an Event spoofing attack to gain additional credibility and potentially further poison the victim's wallet, creating [a malicious contract](https://etherscan.io/token/0x5e70ac37cd4c27c0fe0329df4a6c3547d57ac81e) named ERC-20 Token. Then, the attacker issues a ￼transaction￼ that causes many token transfer events to be emitted - all of them are spoofed transfers of a scam token worth nothing.

In one of them, the spoofed event shows a transfer of funds from the WBTC holder (the victim) to the fake, attacker-controlled address.

Step 4: Dusting Attack

Finally, to get into the victim's address book, the attacker-controlled address [￼sends](https://etherscan.io/tx/0x87c6e5d56fea35315ba283de8b6422ad390b6b9d8d399d9b93a9051a3e11bf73)￼ a tiny dust transaction involving 0.00021 ETH (worth less than a dollar).

#### Exploitation

Finally, the WBTC holder goes to make another transaction. They go into their address book and see an address similar to the one they've just interacted with - 0xd9a1...853a91.

They check their recent transactions and see that they've just sent 0.05 of _something_ to this address. Since they've just sent 0.05 ETH to another address that looks very similar, they figure that this is the address that they want to interact with. They [send their WBTC](https://etherscan.io/tx/0x3374abc5a9c766ba709651399b6e6162de97ca986abc23f423a9d893c8f5f570) to this address... and lose it. 



Reference: https://www.blockaid.io/blog/a-deep-dive-into-address-poisoning

------

### **Why is Address Poisoning Effective?**

1. **Human Error**:

Cryptocurrency wallet addresses are long and complex, leading many users to rely on shortcuts like recent transaction history instead of verifying the entire address.

1. **Lack of Awareness**:

Many users are unaware of address poisoning tactics, making them easy targets.

1. **Interface Design**:

Wallet interfaces often truncate addresses for readability, showing only the first few and last few characters, which attackers exploit.

Fortunately, more and more wallets are detecting these transactions and indicating them as potentially fraudulent. This is the case, for example, of the [Trezor](https://trezor.io/support/a/address-poisoning-attacks?srsltid=AfmBOopitr2vs98uXV-_wDdWPxQ78WflYEdE-6Pzw0TUGz3KlQu620l9) hardware wallet.

------

### **How to Protect Against Address Poisoning**

1. **Always Verify the Full Address**:

Before sending funds, compare the full wallet address character by character, rather than relying solely on truncated displays or history entries.

1. **Use Address Labels**:

Many wallets allow users to assign custom labels to frequently used addresses. This ensures that legitimate addresses are easily recognizable.

1. **Avoid Using Transaction History for Payments**:

Instead of selecting addresses from history, use a fresh copy-paste from a verified source.

1. **Enable Transaction Confirmation Prompts**:

Wallets with additional confirmation steps can help catch errors or malicious activity before finalizing a transaction.

1. **Be Wary of Dust Transactions**:

Small, unsolicited deposits in your wallet could be a red flag. Do not engage with or attempt to spend dust amounts as they could be part of an attack.

1. **Regularly Update Wallet Software**:

Ensure your wallet application has the latest security updates, as developers often introduce features to counteract new threats like address poisoning.



See also [Metamask - Address poisoning scams](https://support.metamask.io/privacy-and-security/staying-safe-in-web3/address-poisoning-scams/)

------

### **Mitigation at the Ecosystem Level**

1. **Improved Wallet Interfaces**:

Developers can create wallet interfaces that highlight suspicious or new addresses and provide warnings about dust transactions.

1. **Blockchain Analytics Tools**:

Tools that flag suspicious addresses or transactions can be integrated into wallet systems to reduce user vulnerability.

1. **Educating Users**:

Public awareness campaigns and wallet-provider documentation can teach users about address poisoning and how to avoid it.

------

### **Conclusion**

Address poisoning is a growing concern in the blockchain space, leveraging user habits and interface design to exploit victims. By understanding the mechanics of address poisoning and taking precautions like verifying addresses and avoiding reliance on transaction history, users can significantly reduce their risk. Meanwhile, wallet providers and blockchain developers must continue enhancing security features to safeguard users against evolving threats.

As the blockchain ecosystem matures, staying vigilant and adopting robust practices will be key to ensuring safe and secure transactions.