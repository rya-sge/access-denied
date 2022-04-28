---
layout: post
title:  "Tester la résistance d'un crypto système à un niveau d'attaques"
date:   2022-04-24
last-update: 
categories: cryptographie 
tags: ind-cpa ind-caa asymetrique
description: Cet article aborde les différents tests et jeux auxquels on peut soumettre un crypto système pour vérifier sa robustesse (p.ex. IND-CPA et IND-CAA).
image: /assets/article/cryptographie/asymetrique/ind-cpa.PNG
---

Cet article aborde les différents tests et jeux auxquels on peut soumettre un crypto système pour vérifier sa robustesse, en particulier les jeux IND-CPA et IND-CAA.

Lors de ces jeux, il y a un challenger qui génère les clés et un adversaire qui va tenter de casser le système.

On suppose que l'adversaire :

- Peut chiffrer tout ce qu'il veut
- Peut déchiffrer tout ce qu'il veut

Cet article présente 2 de ces jeux :

- *Indistinguishability under Chosen-Plaintext Attacks* (IND-CPA)
- *Indistinguishability under Chosen-Ciphertext Attacks* (IND-CAA)

##  IND-CPA



L'adversaire peut faire des attaques à textes clairs choisis. C'est toujours le cas dans la cryptographie asymétrique car la clé publique est connue.

1. Le challenger génère les clés (p.ex. RSA) puis envoie la clé publique à l'adversaire.
2. L'adversaire choisit 2 messages M0 et M1 et les envoie au challenger.
3. Le challenger flip un bit b et chiffre le message clair résultant. Puis il l'envoie à l'adversaire.
4. L'adversaire doit deviner le quel des 2 messages a été chiffrés.

![ind-cpa]({{site.url_complet}}/assets/article/cryptographie/asymetrique/ind-cpa.PNG)

Source image : Cours de cryptographie appliquée avancée (CAA) enseigné à la HEIG-VD en 2022

Un cryptosystème est dit IND-PCA si un adversaire efficace (s'exécutant en temps polynomial) en un avantage négligeable par rapport à du *guessing*

Définition formelle : Un système est IND-CPA si `Pr[gagner le jeu IND-CPA] - 1/2`est négligeable pour tout adversaire s'exécutant en temps polynomial

### Exemple

> Est-ce que TextBook RSA est IND-CPA ?

Solution

TextBook RSA n'est pas IND-CPA car il est déterministique. En cryptographie asymétrique, on est obligé d'avoir un chiffrement non-déterministe pour avoir un semblant de sécurité.

Dans le jeu (comme dans la réalité), l'adversaire possède la clé publique, il peut chiffrer lui-même M0 et M1 et vérifier s'ils correspondent à y.

Exemple dans un cas réel : si on utilise TextBook RSA pour chiffrer des salaires, alors on peut chiffrer nous-mêmes une liste de salaires et comparer les textes chiffrés obtenus avec les textes chiffrés dans la base de données.



### Limitation du modèle

Un modèle passant le test  IND-CPA peut cependant être vulnérable à des attaques de type  *chosen ciphertext attack* (attaque à texte chiffré choisi)

Une attaque connue est l'attaque Bleichenbecher. L'attaquant peut choisir des textes chiffrés qui vont être déchiffrés par une machine. C'est une attaque par oracle typique.

Le standard `RSA PKCS#1 v1.5`est vulnérable à cette attaque.

Exemple de scénario :

Un client parle avec un serveur légitime. En tant qu'attaquant, on intercepte un message chiffré et on l'envoie au serveur. Celui-ci va le déchiffrer et éventuellement renvoyer un message d'erreur ou prendre plus de temps pour le déchiffrement, ce qui peut être suffisant pour casser le système.

Exemple : ROBOT attack sur SSL/TLS

## **Indistinguishability under Chosen-Ciphertext Attacks (IND CCA)**

![ind-caa]({{site.url_complet}}/assets/article/cryptographie/asymetrique/ind-caa.PNG)

Source image : Cours de cryptographie appliquée avancée (CAA) enseigné à la HEIG-VD en 2022

### IND CCA1

L'adversaire peut demander à déchiffrer tout ce qu'il veut.

Le *challenger* déchiffre pour l'adversaire les messages et renvoie les textes clairs correspondants.

L'adversaire choisit 2 messages M0 et M1 et les envoie au *challenger*.

Le *challenger* va flipper un bit b d'un des deux messages claires, chiffrer le message avec le bit modifié et le renvoyer.



### IND-CCA2

L'adversaire peut demander à nouveau de pouvoir déchiffrer n'importe quel message, sauf le message chiffré `y` .

Il peut le faire par exemple pour des éléments malléables : il peut prendre `y`, le multiplier par deux et demander le déchiffrement.

- On peut facilement ici casser des constructions comme PKS1.5
- À amener au standard RSA-OAEP, l'adversaire n'arrive pas à distinguer un seul bit

Exemple

> Un crypto système utilise RSA-KEM avec le mode de chiffrement ECB, sans chiffrement authentifié. Pour quelle raison ce système n'est pas IND-CCA2 ?

Solution :

Aucun tag n'est calculé, l'adversaire peut alors modifier le message chiffré `y` du jeu tout en gardant la même valeur de u.

L'adversaire peut alors créer des messages différents de `y` tout en gardant certaines caractéristiques identiques. 2 messages pourraient avoir les caractéristiques suivantes :
1) Modifié le second bloc du message chiffré tout en gardant identique le 1er bloc
2) Modifié le 1er bloc tout en gardant le second identique

ECB étant déterministique, le déchiffrement des blocs laissés identiques donneront les bons blocs de messages clairs. Ainsi avec 2 messages chiffrés modifiés, on peut récupérer le message clair en entier.

## Sources

- Source image : Cours de cryptographie appliquée avancée (CAA) enseigné à la HEIG-VD en 2022
- [fr.wikipedia.org - Niveaux d'attaques](https://fr.wikipedia.org/wiki/Niveaux_d%27attaques)