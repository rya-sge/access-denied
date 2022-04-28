---
layout: post
title:  "Le chiffrement par bloc CBC"
date:   2022-02-27
last-update: 
categories: cryptographie 
tags: cbc chiffrement-bloc
description: Cet article présente le mode d'opération CBC en analysant également sa sécurité (réutilisation d'IV, répétition de blocs).
image: /assets/article/cryptographie/mode-chiffrement/cbc-bloc-repetition.png
---



Cet article présente le mode d'opération CBC (*Cipher block chaining*). 

Pour une meilleure compréhension, les questions suivantes seront abordées :

A) Est-ce que le mode opératoire transforme le chiffrement par bloc en un chiffrement par flot (Abr.  chiffrement par flots)

B) Est-ce que le chiffrement ou le déchiffrement sont parallélisables (Abr.  Paralléliser les opérations)

C) Est-ce qu'il est possible d'effectuer un déchiffrement partiel et/ou une rechiffrement partiel d'un  nouveau bloc ? (Abr.  Opération partielle)

D) Quelles sont les conséquences de la réutilisation d'IV (Abr. Réutilisation d'IV)

E) Quelles sont les implications sur le texte clair si on modifie 1 bit du texte chiffré ? (Abr.  Modification d'un bit du texte chiffré)

F) Est-ce qu'un padding est requis ? (Abr.  padding)

G) Lors de l'implémentation, est-ce que l'on doit avoir du chiffrement et du déchiffrement ou seulement l'un des 2 ? (Abr.  Opération nécessaire)

H) Est-ce qu'il y a des problèmes de sécurité ? (Abr.  Problème de sécurité)

## Présentation générale (CBC)

- On divise les données à chiffrer en blocs de la taille du bloc de l’algorithme de chiffrement.

- Chaque bloc de texte clair est combiné au moyen d'un xor avec le texte chiffré précédent.

  - Pour le premier bloc, celui-ci est combiné avec un vecteur d’initialisation (IV) aléatoire.
  - L’IV peut être envoyé en clair.

  

### 	Chiffrement

![](https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/CBC_encryption.svg/900px-CBC_encryption.svg.png)





### Déchiffrement

![](https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/CBC_decryption.svg/900px-CBC_decryption.svg.png)



Source : https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation

## Questions

### A) Chiffrement par flots  

Non, CBC ne génère pas un flux de bits pré-calculables, c'est-à-dire qu'on ne peut pas le calculer avant d'avoir le texte clair. Pour chiffrer le dernier bloc, vous avez besoin des blocs précédents ainsi que les textes clairs.

[https://crypto.stackexchange.com/questions/51251/is-the-cbc-mode-of-operation-a-stream-cipher-mode](https://crypto.stackexchange.com/questions/51251/is-the-cbc-mode-of-operation-a-stream-cipher-mode)

### B) Paralléliser les opérations 

Le chiffrement est séquentiel, mais le déchiffrement peut être parallélisé.

En effet, chaque bloc de texte chiffré dépend de tous les précédents.

Source intéressante : [http://www.bibmath.net/crypto/index.php?action=affiche&quoi=moderne/blocs](http://www.bibmath.net/crypto/index.php?action=affiche&quoi=moderne/blocs)

### C) Opération partielle  

Chiffrement : seulement le dernier bloc peut être modifié, car le reste des autres blocs dépend de la sortie précédente.

C'est pour ça qu'il n'est pas conseillé pour le chiffrement de disque dur.

Déchiffrement : Oui c'est possible en utilisant le bloc chiffré précédent.

### D) Réutilisation d'IV  

En réutilisant l'IV, on peut dès lors distinguer des messages qui commencent par les mêmes
blocs. En effet, dans ce cas, les textes chiffrés correspondants seront les mêmes.

Si on a les mêmes 2 premiers blocs, on aura les mêmes blocs de textes chiffrés.

Conclusion : 

- On arrive à remarquer des messages avec des préfixes identiques.
- Contrairement à CTR, on obtient cependant aucune information directe sur les textes clairs. 

### E) Modification d'un bit du texte chiffré  

Une erreur d’un simple bit dans le texte chiffré, par exemple dû à un bruitage de la liaison ou d’un disfonctionnement du dispositif de stockage, affecte un bloc et un bit du texte en clair reconstruit. En effet, le bloc contenant l’erreur est complètement brouillé et de plus il apparaît une erreur d’un bit dans le bloc suivant au même endroit que le bit erroné. Les autres blocs ne sont pas affectés par l’erreur ; on dit que le mode CBC est auto-récupérant.

Source : [https://orbilu.uni.lu/bitstream/10993/8992/1/2003_1%20Cryptographie%20symétrique.pdf](https://orbilu.uni.lu/bitstream/10993/8992/1/2003_1%20Cryptographie%20symétrique.pdf)



### F) Padding  

Le padding est nécessaire car le chiffrement par bloc, comme AES, demande une taille de bloc fixée. Il y a d'ailleurs une attaque exploitant ce principe : la padding Oracle Attack

Article sur le sujet https://crypto.stackexchange.com/questions/48628/why-is-padding-used-in-cbc-mode

### G) Opération nécessaire  

CBC nécessite les opérations de chiffrement et de déchiffrement.

### H) Problème de sécurité  

- Paradoxe des anniversaires

Avec CBC, le nombre de données que nous pouvons chiffrer est limité par la racine de la taille du bloc. Il faut donc faire attention à ce que cette taille de bloc ne soit pas trop faible.

- Plus on a de blocs, plus il y a un risque de collisions.

- Si la sortie de 2 blocs sont les mêmes, les entrées dans la boite de chiffrement sont les mêmes.

- La présence de 2 blocs identiques B et C indiquent que les entrées dans l'algorithme de chiffrement par bloc (p. ex. AES) sont identiques. On a ainsi :
  $$
  (B - 1)~XOR~PB = (C - 1)~XOR~PC
  $$
  
- La gravité de ce qu'un attaquant peut obtenir avec le XOR des textes clairs dépend des cas d'utilisation. Si il y a beaucoup de 0 dans l'un des textes clairs, on va pouvoir distinguer les 2 messages clairs en raison des propriétés du XOR. De même si l'on connait des parties du textes clairs, par exemple grâce aux headers.

Lien intéressant : [Maximum Number of Blocks to be Encrypted under One Key in CBC and CTR Mode?](https://crypto.stackexchange.com/questions/51518/maximum-number-of-blocks-to-be-encrypted-under-one-key-in-cbc-and-ctr-mode)

Démonstration :

La présence de 2 blocs identiques B et C indiquent que les entrées dans l'algorithme de chiffrement par bloc (p. ex. AES) sont identiques. On a ainsi (B - 1) XOR PB = (C - 1) XOR PC

- SI on connaît un des textes clairs (*plaintext*) => on peut récupérer l'autre
- Sinon on a un xor des textes clairs, ce qui est suffisant pour dire que la construction est cassée.
  Cette attaque est indépendante de l'IV (qu'il soit fixe ou non) car celui-ci ne joue aucun rôle pour les blocs répétés, hormis pour le 1er bloc.

![cbc-bloc-repetition](C:\Users\super\switchdrive2\HEIG\divers\mywebsite\accessDenied\assets\article\cryptographie\mode-chiffrement\cbc-bloc-repetition.png)





### Conclusion 

- Ce n'est pas le plus mauvais choix ;
- En cas de réutilisation d'IV (à ne pas faire !!!!), CBC se révèle préférable à CTR car cela entraîne moins de fuite d'informations sur les messages clairs ;

- Il faut faire attention à la répétition des blocs (Paradoxe des anniversaire) : 
  - Plus on a de bloc, plus il y a un risque de collisions (paradoxe des anniversaires) ce qui peut entraîner des fuites d'informations sur le texte clair, ce qui est très dangereux.

  

## Sources

- Cours de cryptographie (CRY) enseigné à la HEIG-VD en 2020
- Cours de cryptographie appliquée avancée (CAA) enseigné à la HEIG-VD en 2022