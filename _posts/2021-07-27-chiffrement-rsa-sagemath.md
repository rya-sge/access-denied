---
layout: post
title:  "Chiffrement RSA avec SageMath"
date:   2021-07-27
categories: cryptographie
tags: nodejs javascript serveur backend
description: Cet article explique comment implémenter le chiffrement RSA avec SageMath. C'est un logiciel permettant de réaliser des opérations mathématiques, particulièrement intéressant pour faire de la cryptographie. De plus, il est possible d'importer des libraires python.
---

Cet article explique comment implémenter le chiffrement **RSA** avec *SageMath*. C'est un logiciel permettant de réaliser des opérations mathématiques, particulièrement intéressant pour faire de la cryptographie. De plus, il est possible d'importer des libraires python.

Il est possible d'éditer du code SageMath en utilisant juypter. Pour cela il faut lancer en ligne de commande : *sage -n* ou sage -n jupyter

Plus d'informations est disponible sur la documentation d'installation de Sage : [https://doc.sagemath.org/html/en/installation/launching.html]( https://doc.sagemath.org/html/en/installation/launching.html)
$$
n = p * Q
$$

$$
n = p * q \\
φ(n) = (p - 1)(q - 1) \\
c = m^e \ mod \ φ(n) \\
m = c^d \ mod \ φ(n)
$$


### Rappel sur le chiffrement RSA


$$
\textrm{module de chiffrement} \\
n = p * q \\
\textrm{Indicatrice d'Euler} \\
φ(n) = (p - 1)(q - 1) \\
\textrm{Chiffrement} \\
c = m^e \ mod \ φ(n) \\
\textrm{Déchiffrement} \\
m = c^d \ mod \ φ(n)
$$



### SageMath

#### Fonctions proposées par la librairie

- Pour le déchiffrement, la fonction  *inverse_mod* permet de calculer d très facilement
- En déclarant le groupe multiplicatif avec *Integers(n)*, tous les calculs vont se faire modulo n ce qui simplifie l'écriture.



#### Algorithme

L'objectif ici sera de chiffrer puis déchiffrer un message(ascii) avec RSA.

Pour chiffrer, il faut :

1. Convertir en byte message à chiffrer 

   ->Ce fait en ajout *b* avant la chaîne de caractère

2. Convertir en long les bytes obtenus

   -> Ce fait avec la fonction *bytes_to_long* de de la librairie *Crypto.Util.number*

3. Appliquer le chiffrement RSA sur le message

Pour déchiffrer, on suppose le message chiffré sous forme d'un nombre

1. Appliquer le déchiffrement RSA sur ce nombre

2. Convertir le résultat (long) en byte

   -> Ce fait avec la fonction *long_to_bytes* de la librairie *Crypto.Util.number*

3. Décoder en ascii le résultat obtenu

   -> Ce fait avec la fonction  python native *decode*

#### Code

```python
from Crypto.Util.number import long_to_bytes, bytes_to_long

def encrypt(m, e):
    return m ^ e

def decrypt(c, d):
    return c ^ d


def main():
    #---
    e = 65537
    n = 228430203128652625114739053365339856393
    
    c = 126721104148692049427127809839057445790
    m = b'flag{68ab82df34}'
    print("Initial message : ", m)
    m = bytes_to_long(m)
    print("Messsage in long : ", m)
    
    p = 12546190522253739887
    q = 18207136478875858439
    phi = (p - 1) * (q - 1)
    d = inverse_mod(e, phi)
    
    #Create field group in n
    F = Integers(n)
    m = F(m)
  
    c = encrypt(m , e)
    print("Cipher : ", c)
    m = decrypt(c, d)
    
    m = long_to_bytes(m)
    print("Decrypted message : ", m.decode('utf-8'))
    
main()

```



### Sources

- Cours de Cryptographie (CRY) enseigné à l'HEIG-VD en 2020
- Ce code a été initialement écrit pour résoudre le challenge [Baby](https://ctftime.org/task/16441) lors du  [redpwnCTF 2021](https://ctftime.org/event/1327)
  - Le message chiffré, n et e sont ceux du challenges
- Documentation Sage : [https://www.sagemath.org/fr/documentation.html](https://www.sagemath.org/fr/documentation.html)

