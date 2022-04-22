```
layout: post
title:  "Le chiffrement par bloc CTR"
date:   2022-02-27
last-update: 
categories: cryptographie 
tags: cbc chiffrement-bloc
description: Cet article présente le mode de chiffrement CTR avec une analyse sur sa sécurité (confidentialité, intégrité, authenticité et la génération d'IV).
image: /assets/article/cryptographie/mode-chiffrement/ctr-reuse-IV.png
```

Cet article présente le mode de chiffrement  CTR (*Counter Mode*). 

Pour une meilleure compréhension, les questions suivantes seront abordées :

A) Est-ce que le mode opératoire transforme le chiffrement par bloc en un chiffrement par flot (Abr. chiffrement par flots)

B) Est-ce que le chiffrement ou le déchiffrement sont parallélisables (Abr.  Paralléliser les opérations)

C) Est-ce qu'il est possible d'effectuer un déchiffrement partiel et/ou une rechiffrement partiel d'un  nouveau bloc ? (Abr. Opération partielle)

D) Quelles sont les conséquences de la réutilisation d'IV (Abr.  Réutilisation d'IV)

E) Quelles sont les implications sur le texte clair si on modifie 1 bit du texte chiffré ? (Abr.  Modification d'un bit du texte chiffré)

F) Est-ce qu'un padding est requis ? (Abr.  padding)

G) Lors de l'implémentation, est-ce que l'on doit avoir du chiffrement et du déchiffrement ou seulement l'un des 2 (Abr. : Opération nécessaire)

H) Est-ce qu'il y a des problèmes de sécurité ? (Abr.  Problème de sécurité)

I) Peut-on l'utiliser pour chiffrer un disque dur ?

## Présentation 

Fonctionnement générale :

- Le mode CTR utilise un nonce (appelé aussi IV) ainsi qu'un compteur, incrémenté pour chaque bloc,
- Le compteur doit être à usage unique, pareil pour le nonce/IV

### Chiffrement 

![](https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/CTR_encryption_2.svg/902px-CTR_encryption_2.svg.png)

Source image : [https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation)

### Déchiffrement 

![](https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/CTR_decryption_2.svg/902px-CTR_decryption_2.svg.png)

Source image : [https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation)

### Questions

#### A) Chiffrement par flots

C'est effectivement le cas. Tout simplement pour 2 raisons :

- Chaque bloc est indépendant les uns des autres, ce n'est pas une condition mais peut faciliter le pré-calculage des blocs
- Chiffrement : Le texte clair va être xoré avec la sortie du bloc de chiffrement, ce n'est pas le texte clair qui est chiffré avec la clé mais le *nonce* et le compteur. Comme le *nonce* et le compteur  sont connus à l'avance, on peut dès lors pré-calculer le flux.
- Déchiffrement : même raisonnement que pour le chiffrement

#### B) Paralléliser les opérations 

Le chiffrement et le déchiffrement sont parallélisables. C'est pourquoi il peut être intéressant de l'utiliser pour une base de données.



#### C) Opération partielle 

Oui, car le chiffrement et le déchiffrement peuvent être parallélisées



#### D) Réutilisation d'IV 

Pour CTR, si l’on réutilise un IV, on peut obtenir le XOR des blocs de *plaintext*. En effet,
réutiliser l’IV dans CTR revient au même qu’utiliser la même clef dans le chiffrement
de Vernam.
$$
P1~XOR~P2 = C1~XOR~C2
$$
**Schéma :**

- L'IV est en 2 parties : nonce(rouge) et le compteur(orange)
- Texte claire / plaintext (P1 & P2): en bleu
- Message chiffré (C1 et C2) : rouge aussi

![ctr-reuse-IV]({{site.url_complet}}/assets/article/cryptographie/mode-chiffrement/ctr-reuse-IV.png)

**Détail du calcul**

After_encryption1 XOR P1 = C1
After_encryption2 XOR P2 = C2
Vu que After_encryption1 et After_encryption2 sont identiques, on les remplace par l'inconnue **A**

```
Etape 1 :
A XOR P1 = C1
A XOR P2 = C2

Etape 2 :
P1 XOR C1 = A
P2 XOR C2 = A

Etape 3 :
P1 XOR C1 = P2 XOR C2

Résultat final :
P1 XOR P2 = C1 XOR C2


```



#### E) Modification d'un bit du texte chiffré 

Cela va changer le bit correspondant dans le texte clair correspondant au bloc

#### F) Padding 

Pas nécessaire car il s'agit d'un chiffrement par flot.

#### G) Opération nécessaire 

Seule l'opération de chiffrement est requise

#### H) Problème de sécurité 

L'IV doit être de taille suffisante. Sinon on peut l'attaquer avec le paradoxe des anniversaires. Pour trouver une collision sur un IV de 8 bits c'est 2l/2 = 28/2 = 24 = 16.
$$
2 ^ 8 = 256 ~ possibilités
$$
$$
2 ^ 4 = 16
$$

Il faudra en moyenne 16 textes claires et leur texte chiffré pour en avoir 2 avec le même IV et ainsi pouvoir effectuer un XOR.

Remarques :

- Il faut faire attention à avoir compteur assez grand pour la taille des messages. Le compteur étant déterministe, il n'est pas sujet à l'attaque par le paradoxe des anniversaires. 

- Le nonce peut être tiré soit de manière déterministe soit de manière aléatoire
  - Pour un IV de 64 bits :
    - Si aléatoire =>Paradoxe des anniversaires, 2^32 messages pour 64 bits avant d'avoir une collision
    - Si déterministe =>2^64 messages avant d'avoir une collision

#### I) Utilisation

Le chiffrement par bloc CTR n'est pas adapté au chiffrement de disque dur car :

- Il ne propose pas de chiffrement authentifié, l'intégrité des données n'est pas garantie.
  - Par exemple, un attaquant peut *flipper* un bit du message chiffré ce qui flippera le bit du message clair correspondant.
- Il nécessite de stocker un compteur.

## Conclusion 

- CTR est meilleur si on protège l'intégrité. Néanmoins dans ce cas autant utiliser GCM.
- En cas de réutilisation d'IV, CTR est plus problématique que CBC car l'attaquant obtient des informations sur le message clair.

## Sources

- Cours de cryptographie (CRY) enseigné à la HEIG-VD en 2020
- Cours de cryptographie appliquée avancée (CAA) enseigné à la HEIG-VD en 2022
- Pour les schémas de chiffrement et déchiffrement: [https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation)