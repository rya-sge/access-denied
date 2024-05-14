---
layout: post
title:  "Diffie-Hellman expliqué en python"
date:   2021-10-28
last-update: 
categories: cryptography
tags: diffie-hellman asymétrique
description: Présentation du protocole de mise au point de clé Diffie-Hellman (key-agreement protocol) avec un exemple d'implémentation pour mieux comprendre les principes.
image: /assets/article/cryptographie/diffie-hellman/schema-echange.png
isMath: true
---

Cet article présente le protocole de mise au point de clé **Diffie-Hellman** (*key-agreement protocol*) avec un exemple d'implémentation pour mieux comprendre les principes.

- Le protocole **Diffie-Hellman** se base sur la difficulté du logarithme discret pour garantir le secret partagé, en l'occurrence la clé partagée dans le cas présent.


- Le canal utilisé pour l'échange doit être authentique car cette échange de clé est vulnérable face à une attaque *man-in-the-middle*.




## Schéma

![schema-echange]({{site.url_complet}}/assets/article/cryptographie/diffie-hellman/schema-echange.png)

## Résumé
- **Alice** 

$$
\begin{aligned}[b]
Clé~privée~:~nombre~a~aléatoire \\
Clé~publique =
A = g^a mod~p \\
Clé~partagée = B^a mod~p
\end{aligned}
$$


- **Bob**
$$
\begin{aligned}[b]
Clé~privée~:~nombre~b~aléatoire \\
Clé~publique = 
B = g^b mod~p \\
Clé~partagée = A^b~ mod~p
\end{aligned}
$$

## Implémentation

Le code python utilisé pour cette implémentation est issue en partie du challenge *Key Exchange*  du ctf BuckeyeCTF 2021 : [https://ctftime.org/event/1434/tasks/.](https://ctftime.org/event/1434/tasks/)

L'exemple donné dans cet article a pour objectif de permettre une meilleur compréhension du protocole **Diffie-Hellmann**, il ne s'agit pas d'une implémentation sûr par conséquent :

> Ne reprenez pas ce code dans la pratique!!!!

Le code dans son entier est disponible sur mon github à l'adresse suivante : [github.com/rya-sge/AD-ressources - cryptography/diffie-hellman-key-exchange.py](https://github.com/rya-sge/AD-ressources/blob/master/cryptography/diffie-hellman-key-exchange.py)

### 1) Mise en place

Alice et Bob doivent se mettre d'accord sur un groupe multiplicatif Zp* cryptographiquement sûr ainsi que sur un générateur g appartenant à Zp d'ordre q, premier.

Dans l'exemple ci-dessous, nous prenons p et g 

```python
Parameter known by Alice and Bob
p = 11476114425077445636913897780729058814788399522553701049280397688323001276391084717487591797788773737035134819088321086678078901084786890698833590212793893
g = 5
```



### 2) Génération des clés privées/publiques

#### Alice

Alice génère ensuite de manière aléatoire une clé secrète `a` appartenant à {1,... q-1}

```python
a = rand.randrange(2, p - 1)  # private key
A = pow(g, a, p)  # public key
# g ^ a === A  (mod p)
print(f"A = {A}")
```

Elle va ensuite envoyer sa clé publique A à Bob

#### Bob

Bob fait pareil de son côté

```python
 print("***Bob***")
 b = rand.randrange(2, p - 1)  # private key
 B = pow(g, b, p)  # public key
 print(f"b = {b}")
 print(f"B = {B}")
```

Puis il utilise la clé publique A d'Alice pour calculer la clé partagée
$$
\begin{aligned}[b]
Shared ~ key = A^b
\end{aligned}
$$

#### Alice 

Bob envoie également sa clé publique B à Alice, qui va faire pareil de son côté pour calculer la clé partagée.
$$
\begin{aligned}[b]
Shared ~ key = B^a
\end{aligned}
$$




### 3) Chiffrement et déchiffrement

Alice et Bob peuvent maintenant utiliser la clé partagée pour faire du chiffrement symétrique

Ici, pour l'exemple c'est du AES avec ECB (ne prenez jamais ECB en pratique)

#### Chiffrement 

```python
#Ne pas utiliser en production
#Do not use in production
print("***Encrypt message***")
key = hashlib.sha1(cun.long_to_bytes(shared_secret_A)).digest()[:16]
cipher = AES.new(key, AES.MODE_ECB)
ciphertext = cipher.encrypt(message)
ciphertext.hex()
cipherFlag = ciphertext.hex()
print(f"ciphertext = {cipherFlag}")
```

#### Déchiffrement

```python
#Ne pas utiliser en production
#Do not use in production
key = hashlib.sha1(cun.long_to_bytes(shared_secret_B)).digest()[:16]
ciphertext = bytes.fromhex(cipherFlag)
cipher = AES.new(key, AES.MODE_ECB)
plain = cipher.decrypt(ciphertext)
print("flag", plain.decode('utf-8'))
```



## Source 

- Cours de Cryptographie (CRY) enseigné à l'HEIG-VD en 2021
- Challenge *Key Exchange* du BuckeyeCTF 2021 : [https://ctftime.org/event/1434/tasks/](https://ctftime.org/event/1434/tasks/)
- Le code de l'article est disponible sur mon github personnel : [github.com/rya-sge/AD-ressources - cryptography/diffie-hellman-key-exchange.py](https://github.com/rya-sge/AD-ressources/blob/master/cryptography/diffie-hellman-key-exchange.py)

