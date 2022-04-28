---
layout: post
title:  "Chiffrement hybride sur les courbes elliptiques avec ECIES"
date:   2022-04-22
last-update: 
categories: cryptographie 
tags: ecies courbe-elliptique chiffrement-hybride
description: Cet article présente le schéma de chiffrement intégré ECIES (Elliptic Curve Integrated Encryption Scheme) permettant de réaliser du chiffrement hybride.
image:
---

Cet article présente le schéma de chiffrement intégré ECIES (*Elliptic Curve Integrated Encryption Scheme*) permettant de réaliser du chiffrement hybride.

Il utilise les fonctions suivantes :

- Protocole d'échange de clé (sortie de Diffie-Hellman sur courbe elliptique) ;
- Une fonction de dérivation de clé ;
- Une fonction de hashage ;
- Du chiffrement symétrique ;
- Un MAC.

Il a été standardisé avec ANSI X9.63, IEEE 1363a, ISO 18033-2 et SECG SEC 1.

Les différents standards ont quelques différences mineures.

## Principe

### Rappel du chiffrement hybride 

On utilise une clé publique pour échanger une clé symétrique afin de pouvoir utiliser celle-ci pour chiffrer les données.

Par exemple pour envoyer un email chiffré, on ne va pas pouvoir faire du Diffie-hellman avec le destinataire. On lui envoie alors un 1er paquet avec la clé puis le paquet chiffré avec la clé symétrique.

### Paramètre

Public :

- Une courbe Elliptique E
- Un point G sur E d'ordre n (premier)
- Une fonction de dérivation de clé `KDF`
- Algorithme de chiffrement symétrique `Enc`
- MAC

Rappel : la difficulté repose sur le logarithme discret

- Clé secrète :
  $$
  k ∈ Z_n
  $$

- Clé publique

   $$
K = k * G
   $$

Pour rappel, la courbe elliptique est un groupe additif. Par conséquent, on ne peut faire que des additions ou des multiplications par des constantes.

- Certains standards ont des informations supplémentaires partagée S1 et S2

### Chiffrement

1. Tirer un nombre aléatoire uniformément

   $$
r ∈ Z^*_p
   $$

2. Calculer  un point `R` sur la courbe elliptique
   $$
   R = rG
   $$

3. On génère 2 clés `ke` et `Km` en appliquant la KDF sur r multiplié par la clé publique K


$$
(k_e  || k_M) = KDF(rK||S1)
$$

- `S` est juste là pour la séparation de domaine (on peut l'ignorer).
- `Ke` est la clé symétrique pour le chiffrement. 
- `Km` est la clé symétrique pour le MAC.
- Si on fait du chiffrement authentifié, on aura qu'une seule clé pour réaliser le chiffrement authentifié.

4. 

   $$
c = Enc_{ke}(m)
   $$

5. 

   $$
T = MAC_{kM}(c || S2)
   $$

6. Le message chiffré est `R||c||T`



## Déchiffrement

On a R||c||T  ainsi que la clé secrète `k`

1. On doit dériver les clés, pour cela on a besoin d'une valeur équivalente à  `r * K`. Vu qu'on n'a pas en notre possession `r`, on va pouvoir remplacer `r * k`par `k * R` grâce au raisonnement suivant :
   $$
   K = k * G
   $$

   $$
   R=r*G
   $$

   $$
   r * K = r * k * G = k * R
   $$

   

2. On dérive ensuite les clés grâce à la valeur `kR` trouvée au point 1.


$$
(k_e||k_M)=KDF(kR||S1)
$$


3. On vérifie le tag avec `km`
4. Si le tag est correct, on déchiffre avec `ke`

   $$
m = Dec_{ke} 
   $$



## Source

- Cours de cryptographie appliquée avancée (CAA) enseigné à la HEIG-VD en 2022
