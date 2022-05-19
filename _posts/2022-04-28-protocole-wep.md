---
layout: post
title:  "Le protocole WEP et ses vulnérabilités"
date:   2022-04-28
categories: securite reseau
tags: wep wifi
description: Cet article présente le protocole Wifi WEP (Wired Equivalent Privacy) en se focalisant sur les aspects sécuritaires (confidentialité, intégrité, authenticité).
image: /assets/article/reseau/wep/wep-encrypt-rc4.png
---

Cet article présente le protocole Wifi WEP (*Wired Equivalent Privacy*) en se focalisant sur les aspects sécuritaires (confidentialité, intégrité, authenticité).



## Présentation

Ce paragraphe passe en revue les principaux points importants de sécurité d'un réseau Wifi (CIA) pour confidentialité / intégrité &  Authenticité .

Un réseau Wifi ne pouvant guère protéger la disponibilité (*Availibility*), la lettre A a été remplacée par Authenticité (*authenticity*).

### Confidentialité

- WEP chiffre les données en utilisant l'algorithme RC4 qui possède de grosses vulnérabilités.

- Il est notamment vulnérable à une réutilisation du *keystream*. La clé peut être récupérée en moins de 60 secondes.

- La clé est unique pour tous les clients et celle-ci permet de déchiffrer tout le trafic.


### Intégrité

WEP utilise l'ICV pour *Integrity Check Value*.

Cet ICV ne demande aucune clé pour être calculé.

### Authentification

Par défaut, tout le monde peut participer au réseau.

WEP propose néanmoins optionnellement une fonctionnalité d'authentification : `Shared Key Authentication`



### Protection contre les doublons

WEP n'offre aucune protection contre les doublons. On peut dès lors capturer des messages et les réinjecter des millions de fois.

## Les vulnérabilités

### Confidentialité

#### Clé partagée / *Shared key*

C'est une séquence "secrète" de 40 bits ou 104 bits appelée **passphrase**. La majorité du temps la clé est sous forme hexadécimale, p. ex  "MotDePasseWifiIncroyable" à partir de laquelle une clé en bit sera ensuite dérivée au moyen d'une KDF.

- Génération de la clé

Pour passer du mot de passe ASCII (hexadécimal) à des bits, il va falloir utiliser un algorithme de conversion. Ceux-ci sont en général propriétaires. Ainsi, il peut avoir des problèmes, car les algorithmes peuvent être différents entre cartes réseau, *Access Point*, etc.

- Taille de la clé 

La taille de l'IV, 24 bits ne peut pas compter dans la taille de la clé, car celui-ci est connu, il est envoyé en clair dans les trames. Cette taille d'IV est parfois ajouté à tort à la taille de la clé, p. ex pour déclarer que la taille de la clé fait 128 bits, ce qui est absolument faux.

- La clé est connue par l'AP et les STAs autorisées.

C'est pourquoi la clé n'est pas vraiment secrète. Si on a 400 stations de connectés, alors il y aura 400 stations au courant de la clé, plus l'AP, ce qui fait beaucoup.

**Pour résumer**

- La clé est une séquence "secrète" de 40 bits ou 104 bits
- Elle est connue par l'AP ainsi que par les STAs autorisés
- Il est possible de la dérivée à partir d'un mot de passe, l'algorithme utilisé pour effectuer la conversion mot de passe -> clé est propriétaire.

### IV 

L'objectif initial de l'IV est de rendre chaque clé dérivée de la *passphrase* unique.

#### Réflexion sur la taille de l'IV

- L'IV fait 24 bits
- Ce qui donne 2^24 = 16’777’216 combinaisons différentes
- L'IV est censé rendre chaque clé de chiffrement "unique".

2^24 peut donner l'impression que c'est beaucoup, mais dans la réalité pas du tout. Sur un réseau à trafic normal, on peut considérer que les IV seront épuisés en environ 1 heure. De plus, si l'incrément commence toujours à 0, alors on aura encore plus rapidement des IV réutilisés.

Malheureusement, dans les réseaux actuels, le nombre d'IV serait épuisé en 1 heure, voir en 25 minutes sur un réseau important.

De plus, RC4 a des vulnérabilités connues avec certains IV faibles, qui vont alors révéler des informations à propos de la clé WEP.

#### Implémentation 

Des problèmes peuvent aussi venir de son implémentation :

- Si l'IV est aléatoire, en raison du paradoxe des anniversaires, des risques de collisions auront lieu à partir de 2^12 IV générés, ce qui réduit encore le nombre de possibilités.
- Un IV déterministe permet d'obtenir plus de possibilités, on incrémente un compteur à partir de 0. On aura alors le maximum de combinaisons possibles : 2^24.

#### Conséquence 

La réutilisation d'un IV provoque la réutilisation du *keystream*, ce qui est une catastrophe pour la confidentialité.

### Chiffrement

Le chiffrement consiste à effectuer un xor entre données + ICV avec le *keystream*. Dans l'image ci-dessous, la partie chiffrée est en gris.

Le *keystream* est calculé à partir de la clé et de l'IV

- Chiffrement

$$
Ciphertext = (Data + ICV )~XOR~Keystream
$$

- Déchiffrement

$$
(Data + ICV) = Ciphertext~XOR~keystream
$$

- Schéma


![wep-encrypt]({{site.url_complet}}/assets/article/reseau/wep/wep-encrypt.png)



#### Génération du keystream

Le *keystream* sera généré avec l'algorithme RC4. Celui-ci utilise comme graine(*seed*) la clé commune à tout le réseau ainsi que l'IV.

![wep-encrypt-rc4]({{site.url_complet}}/assets/article/reseau/wep/wep-encrypt-rc4.png)

## Intégrité

Il utilise **l'ICV / Integrity Check Value** qui s'apparente à un CRC-32. C'est acceptable pour détecter des erreurs aléatoires, mais pas pour des erreurs délibérées (fait par un attaquant,  NDLR).

Il est possible de modifier un message sans être détecté  et sans connaitre la clé de chiffrement. Il suffit pour cela de recalculer l'ICV correspondant aux données modifiées.

Conclusion : WEP ne protège pas l'intégrité des communications

## Authentification

Par défaut, tout le monde peut participer au réseau.

WEP propose néanmoins optionnellement une fonctionnalité d'authentification à travers une **Shared Key Authentication**.

- Celle-ci consiste en à challenge envoyé par l'AP à la STA et celle-ci doit le chiffrer puis le renvoyer.
- Cet échange est en clair et on peut par conséquent obtenir le challenge en clair.
- De plus, même dans ce cas-là seul la STA sera authentifiée, l'AP ne le sera pas. On n'a alors pas d'authentification mutuelle.
- Problème de sécurité :

Un attaquant peut capturer le challenge en clair, la réponse chiffrée envoyée par la station puis effectuer un xor pour obtenir le *keystream*.
$$
Plaintext~challenge~XOR~Ciphertext~challenge = Keystream
$$
Avec ce *keystream*, l'attaquant peut utiliser pour injecter des trames valides dans le réseau ou pour s'authentifier. Il utilisera alors le *keystream* pour chiffrer le challenge.

De plus, si on récupère des trames avec l'IV utilisé pour générer le *keystream*, on peut aussi déchiffrer le message.

### Protection contre les doublons

WEP n'offre aucune protection contre les doublons. On peut dès lors capturer une trame et la réinjecter autant de fois que l'on souhaite.

Ce manque de protection est à l'origine d'une des plus grandes failles de WEP : celle-ci se basait sur la réutilisation du *keystream*. En réinjectant une trame, l'attaquant forçait la réutilisation du *keystream* (plus ou moins vu que les données étaient identiques)



## Conclusion

WEP n'a absolument pas été conçu pour être sûr.  Actuellement, il est totalement cassé.

- L'algorithme de chiffrement choisi, RC4, est un mauvais choix, il avait déjà des faiblesses connues au moment de l'adoption. Il est vulnérable à la réutilisation du *keystream*, ce qui arrive très vite dû à la faible taille de l'IV.

- La partie secrète de la clé est la même pour tout le monde sur le réseau
- Plusieurs attaques existent (FMS, attaque par fragmentation, attaque CHOPCHOP, attaque Pyshkin Tews Weinmann).