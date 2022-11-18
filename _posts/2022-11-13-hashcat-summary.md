---
layout: post
title: Recover your passwords with Hashcat
date:  2022-11-13
locale: en-GB
lang: en
categories: securite 
tags: hashcat hash
description: Hashcat is a security tool allowing to recover passwords form a hash on a large number of hash functions (md5, sha1, sha256)
image: /assets/article/outil-securite/hashcat/tryHackMe-hashid-2.PNG
---

Hashcat is a security tool allowing to recover passwords form a hash on a large number of hash functions (md5, sha1, sha256)

> Warning: This article is published for informational purposes to help you better understand how hash functions work and their potential vulnerabilities or misuse. All of the hashes recovered in this article come either from my own hashes or from ethical hacking contests.



## Usage

```bash
hashcat -m <hash_type> -a <attack_mode> -o <output_file> hashfile
,! [mask|wordfiles|directories]
```

Other possible options

--status to show progress

--increment-min and--increment-max allow to set an interval for the length of the password

The different *hash modes* are available here: [https://hashcat.net/wiki/doku.php?id=hashcat](https://hashcat.net/wiki/doku.php?id=hashcat)

### Format

It is possible to use hashcat on PCAPNG, PCAP or CAP files by converting them to the correct format with [cap2hashcat](https://hashcat.net/cap2hashcat/)

CTF challenges on this principle: [https://ctftime.org/writeup/29552](https://ctftime.org/writeup/29552)



### Attack_mode

The different modes are as follows

> ```
>   # | Mode
>  ===+======
>   0 | Straight (wordlists)
>   1 | Combination
>   3 | Brute-force
>   6 | Hybrid Wordlist + Mask
>   7 | Hybrid Mask + Wordlist
>   9 | Association
> ```

- Mode 0 corresponds to a dictionary attack. This is the default mode
- mode 1: with it, you can combine dictionaries 

Example : hascat -m 0 -a 1 hash.txt dico1.txt dico2.txt

- Mode 3 : Brute-force will test all possible attack combinations. It allows among other things to break the passwords written in leetspeak (ex : P455W0rD)
- Mode 6 combines brute force with masks 
- Mode 7 combines masks with wordlists
- Mode 9 allows you to indicate clues that will be used for the attack, for example by combining it with rules. As a hint, the hashcat documentation gives the example of the username that sometimes ends up in the password. This mode still seems to be at an experimental stage, here is this post for more info:[https://hashcat.net/forum/thread-9534.html](https://hashcat.net/forum/thread-9534.html)

**Example**

NLM hash 

```bash
hashcat -m 3000  'hash' /usr/share/wordlists/rockyou.txt    
```

To print the result

```bash
hashcat -m 3000  'hash' --show  
```

### Dictionaries attack

To run dictionaries attack, you will need some dictionaries.

One of the commonly used dictionaries is `rockyou.txt.` Some dictionaries are available by default on kali linux, there are located in: `/usr/share/wordlists/` .

**Example**

```bash
hashcat -m 1420 A60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c:sha256 /usr/share/wordlists/rockyou.txt
```



### Rules

The rules are rules concerning the generation of passwords. You can create your own rules or use those already provided by Kali. They are interesting if we manage to determine certain "patterns" in the target passwords. The hashcat documentation, for example, indicates that many users add a number to their password to increase complexity. We may then want to create a rule that will add the number 1 to the passwords tested.

```bash
hashcat -m1000 -a3 -1 ?l?u -i --increment-min 4 --increment-max 7 -o 6.txt XPHash.txt --force --potfile-disable ?1?1?1?1?1?1?1 --rules /usr/share/hashcat/rules
```

To run our rule-based attack, we will use the following command:

```bash
hashcat -m 0 bfield.hash /usr/share/wordlists/rockyou.txt -r rules --debug-mode=1 --debug-file=matched.rule
```

Some rules : `/usr/share/hashcat/rules/leetspeak.rule`

References

- [https://hashcat.net/wiki/doku.php?id=rule_based_attack](https://hashcat.net/wiki/doku.php?id=rule_based_attack)
- [https://ensiwiki.ensimag.fr/images/c/c6/Hashcatvsjtr.pdf](https://ensiwiki.ensimag.fr/images/c/c6/Hashcatvsjtr.pdf)

#### Example

A write-up written for the Board Meeting Gone Wrong challenge shows an interesting example of the use of these rules. The rules were used to generate a leetspeak animal password dictionary. 

The challenge data indicated "He likes animals, he likes to speak like he's a hacker to make himself seem cool"

```bash
hashcat --stdout animals.txt -r /usr/share/hashcat/rules/leetspeak.rule  > animal_leet.txt
```

Reference: [https://ctftime.org/writeup/24404](https://ctftime.org/writeup/24404)

## Challenge 

### CSAW CTF - SALT

This challenge is taken from the CSAW CTF.

Instruction:

> Can you crack this? Your hash: a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c. 
> Your salt: the encryption method of the hash.
> UPDATE Friday 9PM: To streamline your efforts we would like to give you some more details about the format for the hash encryption method. An example: if you think the hash is RIPEMD-128, use ripemd128 for the salt.

Reference: [CSAW CTF / Crack me](https://ctftime.org/writeup/30169)

**Solution:**

WIth hashcat, you can precise the value of the salt at the end of the hash.

```bash
hashcat -m 1420 A60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c:sha256 /usr/share/wordlists/rockyou.txt
```

### AUCTF 2020 

#### Crack Me

> Hash: 33f966f258879f252d582d45cef37e5e
>
> NOTE: The flag is NOT in the standard auctf{} format
>
> Author: OG_Commando
>



**Solution**:

We can identify the probable hash with hashid. The first 2 are MD2 and MD5. As MD5 is more widespread, I tested this one first. The corresponding mode 0.

![hahs-identifier-auctf]({{site.url_complet}}/assets/article/outil-securite/hashcat/hahs-identifier-auctf.PNG)

I specify the dictionary, rockyou.txt and mode 0. I don't need to specify a dictionary attack because that's the default attack.

```bash
hashcat -m 0 33f966f258879f252d582d45cef37e5e /usr/share/wordlists/rockyou.txt
```

Result: `33f966f258879f252d582d45cef37e5e:bad4ever`

Reference: [https://ctftime.org/task/11011](https://ctftime.org/task/11011)

#### Salty 357

> You might need this: 1337
>
> Hash: 5eaff45e09bec5222a9cfa9502a4740d
>
> NOTE: The flag is NOT in the standard auctf{}         format



**Solution**

After having tested mode 10. It is finally with mode 20 that the attack succeeds The password was therefore of the form **md5($salt.$pass)**

```bash
hashcat -m 20  5eaff45e09bec5222a9cfa9502a4740d:1337 /usr/share/wordlists/rockyou.txt
```

Result with hashcat : 5eaff45e09bec5222a9cfa9502a4740d:1337:treetop   

Reference: [https://ctftime.org/task/11049](https://ctftime.org/task/11049)



### picoCTF 2018 - HEEEEEEERE'S Johnny!

Be careful to surround the hash with single quotes so that the $ is not interpreted.

```bash
hashcat -m 1800 '$6$HRMJoyGA$26FIgg6CU0bGUOfqFB0Qo9AE2LRZxG8N3H.3BK8t49wGlYbkFbxVFtGOZqVIq3qQ6k0oetDbn2aVzdhuVQ6US.'  /usr/share/wordlists/rockyou.txt 
```

Result in hashcat :

`$6$HRMJoyGA$26FIgg6CU0bGUOfqFB0Qo9AE2LRZxG8N3H.3BK8t49wGlYbkFbxVFtGOZqVIq3qQ6k0oetDbn2aVzdhuVQ6US.:hellokitty`
                                                 

Reference: [https://ctftime.org/task/6820](https://ctftime.org/task/6820)

### TryHackeMe

Theses hashes are taken from the room [Hashing - Crypto 101](https://tryhackme.com/room/hashingcrypto101)

**Hash 1**

```bash
hashid -m '$2a$06$7yoU3Ng8dHTXphAg913cyO6Bjs3K5lBnwq5FJyA6d01pMSrddr1ZG'
```

![tryHackMe-hashid-1]({{site.url_complet}}/assets/article/outil-securite/hashcat/tryHackMe-hashid-1.PNG)

```bash
hashcat -m 3200 '$2a$06$7yoU3Ng8dHTXphAg913cyO6Bjs3K5lBnwq5FJyA6d01pMSrddr1ZG'  /usr/share/wordlists/rockyou.txt
```

Result:`$2a$06$7yoU3Ng8dHTXphAg913cyO6Bjs3K5lBnwq5FJyA6d01pMSrddr1ZG:85208520`

**Hash 2**

![tryHackMe-hashid-2]({{site.url_complet}}/assets/article/outil-securite/hashcat/tryHackMe-hashid-2.PNG)



```bash
hashcat -m 1400 9eb7ee7f551d2f0ac684981bd1f1e2fa4a37590199636753efe614d4db30e8e1  /usr/share/wordlists/rockyou.txt
```

Result: `9eb7ee7f551d2f0ac684981bd1f1e2fa4a37590199636753efe614d4db30e8e1:halloween`

**Hash 3**

```bash
hashid -m '$6$GQXVvW4EuM$ehD6jWiMsfNorxy5SINsgdlxmAEl3.yif0/c3NqzGLa0P.S7KRDYjycw5bnYkF5ZtB8wQy8KnskuWQS3Yr1wQ0'
```

![tryHackMe-hashid-3]({{site.url_complet}}/assets/article/outil-securite/hashcat/tryHackMe-hashid-3.PNG)



```bash
hashcat -m 1800 '$6$GQXVvW4EuM$ehD6jWiMsfNorxy5SINsgdlxmAEl3.yif0/c3NqzGLa0P.S7KRDYjycw5bnYkF5ZtB8wQy8KnskuWQS3Yr1wQ0'  /usr/share/wordlists/rockyou.txt
```

Result: 

`$6$GQXVvW4EuM$ehD6jWiMsfNorxy5SINsgdlxmAEl3.yif0/c3NqzGLa0P.S7KRDYjycw5bnYkF5ZtB8wQy8KnskuWQS3Yr1wQ0:spaceman`

## Others tools

Softwares : [John the Ripper](https://www.openwall.com/john/), [RainbowCrack](http://project-rainbowcrack.com)

RainbowCrack provides the ability to find/recover passwords using rainbow tables. It is implemented by Philippe Oechslin

Online: [https://crackstation.net](https://crackstation.net)

This site contains a massive table of pre-computed hashes. These were made from the Wikipedia database as well as dictionaries. However, the hash must not have been salted to be able to be found.

Online: [https://md5decrypt.net](https://md5decrypt.net), [https://hashkiller.io/listmanager](https://hashkiller.io/listmanager)

## Reference

- [https://hashcat.net/hashcat/](https://hashcat.net/hashcat/)

