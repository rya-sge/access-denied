---
layout: post
title:  "Le mode d'opération de chiffrement GCM"
date:   2022-04-22
last-update: 
categories: cryptographie 
tags: cbc chiffrement-bloc
description: Cet article présente le mode de chiffrement authentifié GCM avec une analyse sur sa sécurité (confidentialité, intégrité, authenticité et la génération d'IV).
image: /assets/article/cryptographie/mode-chiffrement/gcm-schema.PNG
---



## Présentation

GCM pour `Galois/counter mode` permet d'effectuer du chiffrement authentifié. Ainsi, en plus de la confidentialité, il permet de garantir l'authenticité et l'intégrité.

- Construction : 
  - Il mélange le *Galois message authentication code* avec le chiffrement par bloc CTR.
  - La taille des blocs est de 128 bits.
- Le message chiffré, C, a la même nombre de bits que le message clair.

- GCM utilise des multiplications dans GF(2^128) 
  - Coefficient des polynômes est soit 0 soit 1
  - Les polynômes ont maximum un degré 127
  - Nombre d'éléments : 2^127
  - Construction du polynôme :

$$
Z_2[x]/x^{128} + x^7 + x^2 + 1
$$

![gcm-construction]({{site.url_complet}}/assets/article/cryptographie/mode-operation/gcm-construction.PNG)

- Il a été standardisé dans la NIST SP800-38D [NIST 2007]. Le document est disponible à l'adresse suivante : [nvlpubs.nist.gov - nistspecialpublication800-38d.pdf](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf)
- Remarques :
  - Utilisation : IPSec, TLS et SSH
  - Meilleure performance que CCM
  - Souvent le choix "par défaut" pour réaliser du chiffrement authentifié [en 2021]

### Vecteur d'initialisation 

- Il accepte un vecteur d'initialisation de n'importe quelle taille

- Néanmoins, la taille de l'IV recommandé pour des raisons de performances est de 96 bits. 

  - Citation du NIST

  > For IVs, it is recommended that implementations restrict support to the length of 96 bits, to promote interoperability, efficiency, and simplicity of design. 

- L'IV (nonce) ne doit jamais être répété. CTR étant utilisé, on a la même vulnérabilité que pour celui-ci :  le XOR des textes chiffrés est égal au XOR des textes clairs ce qui est catastrophique.

### Tag d'authentification

- Le tag peut avoir plusieurs longueurs différentes : 128, 120, 112, 104, ou 96
- C'est possible d'avoir un tag d'une longueur de 23 ou 64 bits, mais des conditions spéciales s'appliquent (citation du NIST) :

> The bit length of the tag, denoted t, is a security parameter, as discussed in Appendix B. In general, t may be any one of the following five values: 128, 120, 112, 104, or 96. For certain applications, t may be 64 or 32; guidance for the use of these two tag lengths, including requirements on the length of the input data and the lifetime of the key in these cases, is given in Appendix C. 

Source : [NIST 2007]

#### Authenticated dada (AD)

Les AD pour `authenticated data` permettent d’authentifier des données sans les chiffrer. Ces données n’auront donc pas de texte chiffré associé mais seront considérées pour le calcul du tag.

Un exemple typique est l’authentification de certaines valeurs dans les paquets réseau qui sont utiles au routage.

Le NIST cite par exemple l'adresse, les ports, la version des protocoles, etc.



## Construction

### Éléments principaux

GCM comporte quatre entrées (1):

- Une clé secrète ;
- Un vecteur d’initialisation (IV) ;
- Un texte en clair ;
- et une entrée pour des données authentifiées supplémentaires (AD).

Il a deux sorties :

- Un message chiffré de la même longueur que le message clair
- Une étiquette d’authentification (TAG).


Sources : [[NIST 2007]](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf)

### Transmission

Les informations suivantes doivent être transmises au destinataire :

- Les données authentifiées (AD)
- Les données chiffrées
- Le tag
- L'IV
  - Pour rappel, l'IV n'a pas besoin d'être confidentiel.

Avertissement :

- La constante H est calculée avec la clé privée. Elle ne doit en aucun cas être transmise !!!!!!!!!!!!!!!!!

### Schéma

Chiffrement

![gcm-schema]({{site.url_complet}}/assets/article/cryptographie/mode-chiffrement\gcm-schema.PNG)

Source du schéma : cours de cryptographie appliquée avancée (CAA) enseigné à la HEIG-VD en 2022.

Remarque :

- Le compteur commence à 2 (et pas à 0).
- La longueur des AD et du texte chiffré est aussi authentifié.

### Déchiffrement

Dans GCM, nous allons tout d’abord vérifier l’intégrité du texte chiffré.

1. Pour cela, nous recalculons tout d’abord H avec la clé privée K. 
   - Le résultat étant déterministe, on obtiendra toujours la même constante avec la même clé privée.
2. Puis ensuite le TAG en utilisant les blocs de textes chiffrés et la constante H
3. Nous comparons le TAG calculé avec celui que nous avons reçu.
4. S’il est correct, alors nous pouvons déchiffrer le message à l’aide de CTR. C'est une opération coûteuse en temps.

### Utilisation

- Difficile à utiliser ;
- Le nombre de messages que l'on peut chiffrer avec la même clé est limité ;
- La taille des messages que l'on peut chiffrer est aussi limitée ;
- La taille de l'IV doit être de 96 bits.

### Limitation

- La taille d'un message ne devrait pas être plus de 2^32 - 2 blocs.
  - Avec par ex. AES et des blocs de 128 bits, cela donne (4 294 967 294 * 128 ) 549'755'813'632 bits, soit 68'719' 476'704 bytes.
- Pour GCM avec des IVs tirés de manière aléatoire, le nombre de message chiffré sous la même clé ne devrait pas être plus que 2^32(=4'294'967'296)
  - Raison : le paradoxe des anniversaires, on veut que la probabilité de collisions soient inférieur à 2^-32
- Pour des IVs déterministiques :
  -  Le nombre de messages est 2^64 (dépends aussi de la manière de diviser l'IV)
  -  Des problèmes de synchronisation peuvent apparaître : si on a par exemples trois machines qui s'envoient des messages avec la même clé, comment peut-on synchroniser le compteur ? Une solution possible serait de réserver des bits dans l'IV comme identifiant de l'appareil.
- La réutilisation de l'IV dans GCM casse la confidentialité (comme pour CTR) et l'intégrité. On ne peut ensuite authentifier aucun message.

### Prise de note & remarques

- En utilisant un compteur déterministique, on pourra chiffrer 2^96 messages car l'IV fait 96 bits ;

- Les AD ne sont pas obligatoires ;

- Si on a seulement des AD, alors cela revient à réaliser du CCM. Ce n'est pas recommandé, mais c'est possible **[à vérifier]**.



## Sécurité

### Constante H

Si la constante H est volée par un attaquant, alors l'intégrité de la construction est cassée.

La constante H est utilisée pour le calcul du Tag. Par conséquent, l'attaquant peut modifier n'importe quel bloc de texte chiffré puis recalculer le tag correspondant à l'aide de la constante H.

### IV répété

GCM utilise CTR. Si l’on répète l’IV dans GCM, on peut obtenir un XOR des textes clairs, comme pour CTR (c.f. une question précédente).

Quelques sources pour approfondir le sujet :

- [MDN contributors, 2022] -  [https://developer.mozilla.org/en-US/docs/Web/API/AesGcmParams](https://developer.mozilla.org/en-US/docs/Web/API/AesGcmParams)
- [Sbai Azmi, 2017] - [https://www.cert-devoteam.fr/1166-2/](https://www.cert-devoteam.fr/1166-2/)
- [NIST 2007] 




## Espace mémoire

- Dans le cas de l'IOT, GCM peut se révéler plus coûteux en espace à transmettre, comme tous les modes de chiffrement authentifiés, car en plus du message chiffré, il y a également le tag à ajouter.
- Contrairement à ChaCha20, il est possible de diminuer la taille du tag dans certains conditions. Ainsi pour effectuer du chiffrement authentifié dans l'IOT, GCM peut être préféré à ChaCha20.



## Bibliographie

Sources principales :

- NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY, 2007. *Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC* [en ligne]. Gaithersburg, MD 20899-8930 : NIST, novembre 2007. NIST Special Publication 800-38D.  [Consulté le 2 mai 2022]. Disponible à l’adresse: [nvlpubs.nist.gov - nistspecialpublication800-38d.pdf](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf)
- Cours de cryptographie appliquée avancée (CAA) enseigné à la HEIG-VD en 2022.
- Cours de Cryptographie (CRY) enseigné à la HEIG-VD en 2020.

Sources secondaires :

- [crypto.stackexchange.com - Ciphertext and tag size and IV transmission with AES in GCM mode](https://crypto.stackexchange.com/questions/26783/ciphertext-and-tag-size-and-iv-transmission-with-aes-in-gcm-mode)
- [crypto.stackexchange.com - Leaving authentication data blank less secure for AES GCM?](https://crypto.stackexchange.com/questions/15699/leaving-authentication-data-blank-less-secure-for-aes-gcm)
- SBAI AZMI, 2017. TLS: Les suites cryptographiques. In : *cert-devoteam* [en ligne]. 29 mai 2017. [Consulté le 2 mai 2022]. Disponible à l’adresse: [https://www.cert-devoteam.fr/1166-2/](https://www.cert-devoteam.fr/1166-2/)
- [MDN CONTRIBUTORS](https://developer.mozilla.org/en-US/docs/Web/API/AesGcmParams/contributors.txt), 2022. AesGcmParams. In : *MDN* [en ligne]. 29 avril 2022. [Consulté le 2 mai 2022]. Disponible à l’adresse: [https://developer.mozilla.org/en-US/docs/Web/API/AesGcmParams](https://developer.mozilla.org/en-US/docs/Web/API/AesGcmParams)