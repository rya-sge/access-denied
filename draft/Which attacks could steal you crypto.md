### Understanding Clipper Malware, Poisoning Attacks, and Fake Crypto Wallets: Protecting Crypto Users

As cryptocurrencies continue to gain popularity, so does the rise in cyber threats targeting crypto users. Among the various threats are clipper malware, poisoning attacks, and fake or malicious crypto wallet apps. Understanding these threats is crucial for anyone involved in the cryptocurrency ecosystem.

## 1. Clipper Malware

Clipper malware is a type of malicious software specifically designed to steal cryptocurrency by intercepting and modifying clipboard data. When a user copies a cryptocurrency address to send or receive funds, the malware replaces it with an address controlled by the attacker. Since crypto transactions are irreversible, if a user fails to notice the address change, their funds are sent directly to the attacker’s wallet.

**How it works:**

- **Infection:** Clipper malware can be distributed through various channels, including malicious websites, phishing emails, or infected software downloads.
- **Execution:** Once installed, the malware monitors the clipboard for cryptocurrency addresses.
- **Modification:** When the user copies a wallet address, the malware instantly replaces it with the attacker's address.
- **Theft:** The user unknowingly sends cryptocurrency to the attacker, resulting in a permanent loss of funds.

**Protection:**

- Always double-check wallet addresses before completing a transaction.
- Use trusted security software that can detect and block clipper malware.
- Download software only from official or reputable sources.

## 2. Poisoning Attacks

The goal of Poisoning attacks is to corrupt a user’s transaction history by injecting malicious data, making it difficult to differentiate between legitimate and fraudulent transactions.

**How it works:**

- **Injection:** Attackers flood a target’s wallet with tiny, seemingly legitimate transactions. These transactions often have addresses similar to those the user commonly interacts with.
- **Confusion:** The aim is to confuse the user by making it harder to track actual transactions, potentially leading to incorrect actions, such as sending funds to a malicious address. If the user relies on its address history, for example on Etherscan, 
- **Exploitation:** If a user mistakenly sends funds to an address they believe to be legitimate, the attacker can gain control over those funds.

**Known example**



**Protection:**

- From a UX perpspective, don't show by default the transfer with 0 as value to increase the cost of the attack.
- Don't copy past address from an like Etherscan. 
- Don't check only the beginning and the end of your address. Check also the middle. note that this is not totally sufficient but it is harder for an attacker to find an address which match the begging, the end as well as middle.
- 
- **Regularly clean up transaction history** and be cautious of unexpected or unsolicited transactions.
- Use wallets with strong anti-poisoning features or transaction filtering capabilities.
- Educate yourself on recognizing phishing attempts and suspicious transactions.

Difference with clipper malware

The essence of both attacks is very similar - the victim must copy the wrong address. There is only one difference - in case of address poisoning, the victim copies the address from the transaction history, and in this attack type victim’s device is NOT infected with malware. In the case of crypto-clipper attack, the device is typically infected by a malware that attacks the clipboard and substitutes a similar but incorrect address.  To protect yourself from the first attack - use the address list in your wallet. To protect yourself from the second attack - always check the address after it has been in the clipboard of your device.

https://x.com/officer_cia/status/1796979666177097872



https://www.chainalysis.com/blog/address-poisoning-scam/#:~:text=An%20address%20poisoning%20attack%20is,looking%20for%20frequently%20used%20addresses.

### Example

Victim:  https://etherscan.io/address/0x1e227979f0b5bc691a70deaed2e0f39a6f538fd5

Address poisoner: https://etherscan.io/address/0xd9a1c3788d81257612e2581a6ea0ada244853a91

3. Fake/Malicious Crypto Wallets

Fake or malicious crypto wallets are designed to look like legitimate wallets but are, in fact, created to steal cryptocurrency. These apps often appear in app stores or are distributed via phishing sites and can easily deceive unsuspecting users.

**How it works:**

- **Impersonation:** Attackers create apps that mimic popular crypto wallets in terms of design and functionality.
- **Distribution:** These apps are often promoted through phishing campaigns, fraudulent websites, or even compromised legitimate platforms.
- **Theft:** Once installed, these apps can steal private keys, seed phrases, or directly siphon off funds without the user’s knowledge.

**Known example**

### Current Transfer

![image-20241216104827394](../../../../.config/Typora/typora-user-images/image-20241216104827394.png)



Phisnger address: 0xd9A1C3788D81257612E2581A6ea0aDa244853a91

![image-20241216105014771](../../../../.config/Typora/typora-user-images/image-20241216105014771.png)



![image-20241216105508091](../../../../.config/Typora/typora-user-images/image-20241216105508091.png)

Official: 0x**d9A1**b0B1e1aE382DbDc898Ea68012FfcB2**853a91**

Fake: 0x**d9A1**C3788D81257612E2581A6ea0aDa244**853a91**

TransferFrom (EVM)

![img](https://trezor.io/content/wysiwyg/Images_sorted/SUPPORT/Airdrop%20scam/Airdrop%20scam%201.png)

https://trezor.io/support/a/address-poisoning-attacks

**Protection:**

- Always download wallet apps from official websites or trusted app stores.
- Verify the authenticity of the app developer and read user reviews before installation.
- Use hardware wallets or reputable software wallets with a proven security track record.

ENS: https://x.com/CyversAlerts/status/1786363410243858869

### Detectuib

https://trezor.io/support/a/address-poisoning-attacks

![img](https://trezor.io/content/wysiwyg/Images_sorted/SUPPORT/Airdrop%20scam/Airdrop%20scam%201.png)



## 4. Types of Attacks Targeting Crypto Users

Cryptocurrency users face a wide array of attacks, including but not limited to:

- **Phishing Attacks:** These involve tricking users into revealing their private keys or seed phrases through fake websites, emails, or messages.
- **Man-in-the-Middle (MITM) Attacks:** Here, attackers intercept communication between the user and the service, altering the transaction or stealing credentials.
- **SIM Swapping:** Attackers take control of a victim’s phone number by tricking or bribing telecom employees, allowing them to bypass two-factor authentication (2FA) and gain access to crypto accounts.
- **Ransomware:** This is malware that encrypts the user’s files, with attackers demanding cryptocurrency as ransom to decrypt the data.
- **Dusting Attacks:** Small amounts of cryptocurrency are sent to a large number of wallets to trace transactions and eventually identify the wallet owners, leading to potential targeted attacks.

### Conclusion

The increasing value and adoption of cryptocurrencies have made them a lucrative target for cybercriminals. Clipper malware, poisoning attacks, fake wallets, and other forms of attacks highlight the importance of vigilance and robust security measures. To safeguard your assets, it’s essential to stay informed, use trusted software, and adopt best practices in crypto security. By doing so, you can navigate the digital currency landscape more safely and with greater confidence.



Which attacks could steal you crypto:

- Fake/malicious apps crypto wallet

- Clip attack (change addresses)
- Poisoning attack

## Clipper malwre (clip attack) 

Cryptocurrency clipping occurs when malware substitutes a crypto recipient’s wallet address with the bad actor’s wallet during a transaction.

Clipper malware steals Bitcoin by modifying the victim’s clipboard activity and substituting the destination wallet with the attacker’s.

https://coinmarketcap.com/community/articles/66bfc4b59fd6d879029c17bb/

https://www.einfochips.com/blog/clipper-malware-what-is-it-and-how-does-it-impact-android-users/

Note that this kind of attacker is also tarjing the traditional financial ssystem: https://cyble.com/blog/dissecting-iban-clipper/

https://www.malwarebytes.com/blog/detections/trojan-clipper

https://www.kaspersky.com/about/press-releases/new-clipper-malware-steals-us400000-in-cryptocurrencies-via-fake-tor-browser

https://perception-point.io/blog/behind-the-attack-paradies-clipper-malware/

https://github.com/NightfallGT/BTC-Clipper

https://www.einfochips.com/blog/clipper-malware-what-is-it-and-how-does-it-impact-android-users/

## Poisoning attack

https://consensys.io/blog/spoofing-sweepers-and-clipboard-hacks-how-to-stay-safe-from-scams

## Fake/malicious apps crypto wallet

https://thehackernews.com/2024/01/italian-businesses-hit-by-weaponized.html

(Clipper malware)



Ethereum

Fake erc-20
