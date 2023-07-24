---
layout: post
title:  "Le mode opératoire ECB"
date:   2022-04-22
locale: fr-FR
last-update: 
categories: cryptographie 
tags: cbc chiffrement-bloc
description: Cet article présente le mode opératoire ECB avec une analyse sur sa sécurité (confidentialité, intégrité, authenticité).
image: /assets/article/cryptographie/mode-chiffrement/ecb-encryption.png
---

Cet article présente le mode opératoire ECB (*Electronic Code Book*). 

Pour une meilleure compréhension, les questions suivantes seront abordées :

A) Est-ce que le mode opératoire transforme le chiffrement par bloc en un chiffrement par flot (Abr.  chiffrement par flots)

B) Est-ce que le chiffrement ou le déchiffrement sont parallélisables (Abr.  Paralléliser les opérations)

C) Est-ce qu'il est possible d'effectuer un déchiffrement partiel et/ou une rechiffrement partiel d'un nouveau bloc ? (Abr.  Opération partielle)

D) Quelles sont les conséquences de la réutilisation d'IV (Abr. Réutilisation d'IV)

E) Quelles sont les implications sur le texte clair si on modifie 1 bit du texte chiffré ? (Abr.  Modification d'un bit du texte chiffré)

F) Est-ce qu'un padding est requis ? (Abr.  padding)

G) Lors de l'implémentation, est-ce que l'on doit avoir du chiffrement et du déchiffrement ou seulement l'un des 2 (Abr.  Opération nécessaire)

H) Est-ce qu'il y a des problèmes de sécurité ? (Abr.  Problème de sécurité)



## Présentation générale

Fonctionnement général :

Le mode ECB n'utilise pas d'IV et les blocs sont chiffrés de manière indépendante les uns des autres.

### Chiffrement

![](https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/ECB_encryption.svg/1920px-ECB_encryption.svg.png)

Source image : [https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation)

### Déchiffrement

![](https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/ECB_decryption.svg/902px-ECB_decryption.svg.png)

Source : [https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation)

## Questions

#### A) Chiffrement par flots

Non, ECB ne génère pas un flux de bits pré-calculables.

#### B) Paralléliser les opérations 

Le chiffrement et le déchiffrement peuvent être parallélisés.

#### C) Opération partielle 

Oui, chaque bloc est indépendant des autres blocs. On peut par conséquent chiffrer ou déchiffrer un bloc sans que cela n'impacte les autres blocs.

#### D) Réutilisation d'IV 

Il n'y a pas d'IV dans ECB, c'est d'ailleurs l'une de ses faiblesses.

#### E) Modification d'un bit du texte chiffré 

Seul le bloc clair correspondant sera impacté. Les autres blocs ne seront pas impactés par cette modification car chaque bloc est indépendant.

#### F) Padding 

Oui car taille bloc fixe

#### G) Opération nécessaire 

ECB nécessite les opérations de chiffrement et de déchiffrement.

#### H) Problème de sécurité 

**Adversaire passif :**

ECB n'implémente aucun IV, ainsi deux blocs de textes clairs identiques seront chiffrés de manières identiques. Il y a  par conséquent une perte potentielle de confidentialité.

Exemple de vulnérabilité si on chiffre une image

On pourrait voir l’image car dans une image, beaucoup de blocs contigus sont identiques. Ils seront modifiés par le système de chiffrement, mais, avec ECB, donneront le même texte chiffré. Cela permet de toujours voir les formes dans l’image.

**Adversaire actif :**

Face à un adversaire actif, celui-ci peut réaliser 2 types d'attaque :

-  Il peut facilement introduire un ou plusieurs nouveaux blocs de texte chiffré de manière délibérée.

OU

- Il peut changer l’ordre des blocs durant la transmission. 

Le mode ECB résiste donc très mal aux attaques visant à modifier l’intégrité du texte chiffré.



Article très intéressant présentant des exemples d'attaque : [https://blackboxhacking.blogspot.com/2016/11/attaque-ecb-bloc-shuffling.html](https://blackboxhacking.blogspot.com/2016/11/attaque-ecb-bloc-shuffling.html)

## Conclusion

- Ce mode de chiffrement n'est absolument pas recommandé.

- Il pourrait potentiellement être utilisé si chaque bloc est garanti être différent, mais c'est un cas rare et la menace d'un adversaire actif resterait présente.

## Sources

- Cours de cryptographie (CRY) enseigné à la HEIG-VD en 2020
- Cours de cryptographie appliquée avancée (CAA) enseigné à la HEIG-VD en 2022
- https://blackboxhacking.blogspot.com - Attaque ECB bloc shuffling
- Pour les schémas de chiffrement et déchiffrement: [https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation)