---
layout: post
title:  "Le Logarithme Discret sur courbe elliptique avec SageMath"
date:   2021-07-30
categories: cryptographie
tags: courbe-elliptique sage logarithme-discret
description: Cet article traite du problème du logarithme discret sur une courbe elliptique. Il contient un exemple faisant appel à la librairie python SageMath.
isMath: true 
---



Cet article traite du problème du **logarithme discret** sur une **courbe elliptique**. La première partie présente les notions théoriques tandis que la seconde est un exemple traité avec la libraire python SageMath.

## Définition

### Courbe elliptique

Une courbe elliptique se définit par l'équation suivante. L'ensemble des points (x,y ) de la courbe sont les points appartenant à F^2 vérifiant l'équation
$$
n = x^3 + a * x + b
$$



### Logarithme discret

Le logarithme discret sur courbe elliptique se présente de la façon suivante :

Connaissant 2 points sur la courbe, Q et G, Trouver d tel que

$$
Q = d * G
$$
Le logarithme discret sur courbe elliptique est un problème difficile, il est d'ailleurs plus difficile à résoudre que sur un groupe multiplicatif. C'est pour cela que le nombre de bits pour la taille de la clé est en général plus petit. Vous pouvez constater cette différence par vous-même en allant voir la taille des clés recommandées par ECRYPT-CSA (Coordination & Support Action) sur le site *keylength* : [https://www.keylength.com/fr/3/](https://www.keylength.com/fr/3/)

Malgré cette difficulté, certaines courbes elliptiques permettent  de calculer "facilement" le logarithme discret.

### Pohlig-Hellman 

L'algorithme de *Pohlig-Hellman* permet de résoudre facilement le problème du logarithme discret si  dans un groupe cyclique G, son ordre n peut être factorisé en petit nombre premiers. Il fait notamment appel au théorème des restes chinois (CRT).

Je ne vais pas détaillé plus cet algorithme car *SageMath* l'implémente. Ci vous êtes curieux, vous pouvez aller lire ces articles qui expliqueront plus en détail cet algorithme :

- [connect.ed-diamond.com - Le logarithme discret contre les tunnels sécurisés](https://connect.ed-diamond.com/MISC/MISCHS-006/Le-logarithme-discret-contre-les-tunnels-securises)
- [www-math.ucdenver.edu - Pohlig-Hellman Algorithm](http://www-math.ucdenver.edu/~wcherowi/courses/m5410/phexample.pdf)



## Exemple

Cette partie présente un exemple de résolution du logarithme discret sur courbe elliptique avec *SageMath*. Celui-ci est tiré d'un challenge bcc du CTF **redpwnCTF 2021** : [https://ctftime.org/task/16438](https://ctftime.org/task/16438)

Pour la résolution, le code et les explications, j'ai repris trois excellent write-ups écrits par d'autres équipes :

- [https://high0101.medium.com/redpwnctf-blecc-crypto-b35997c73a5f](https://high0101.medium.com/redpwnctf-blecc-crypto-b35997c73a5f)
- [c1rcu5_w0lv35 - ctftime.org/team/119580](https://ctftime.org/writeup/29157)
- [https://github.com/cscosu/ctf-writeups/tree/master/2021/redpwn_ctf/crypto](https://github.com/cscosu/ctf-writeups/tree/master/2021/redpwn_ctf/crypto)



### Présentation

La consigne du challenge donnait certains nombres et il fallait déterminer d.

> p = 17459102747413984477
>
> a = 2
>
> b = 3
>
> G = (15579091807671783999, 4313814846862507155)
>
> Q = (8859996588597792495, 2628834476186361781)
>
> d = ???
>
> Can you help me find `d`?

- Dans les nombres donnés, on a p qui est premier.  On peut dès lors supposer que c'est lui 
- a et b sont les coefficients de l'équation de la courbe.

### Résolution

Pour résoudre ce challenge, il faut déjà définir la courbe elliptique :

```python
EC = EllipticCurve(GF(p), [a, b])
```

Plus d'informations ici : 

- [doc.sagemath.org - Elliptic curve constructor](https://doc.sagemath.org/html/en/reference/arithmetic_curves/sage/schemes/elliptic_curves/constructor.html)
- [www2.math.ritsumei.ac.jp - Elliptic curves over a general ring](http://www2.math.ritsumei.ac.jp/doc/static/reference/curves/sage/schemes/elliptic_curves/ell_generic.html)

On définit ensuite les points G et Q données comme des points sur la courbe elliptique :

```python
G = EC(15579091807671783999, 4313814846862507155)
#Define the point Q on the curve
Q = EC(8859996588597792495, 2628834476186361781)
```

Une fois cela, on peut facilement calculer le logarithme discret avec la fonction *discrete_log*. Celle-ci implémente les algorithmes de *Pohlig-Hellman*, voir définition plus haut, et *Baby step giant step*.

La documentation sage de cette fonction se trouve à l'adresse suivante : [voir la documentation](https://doc.sagemath.org/html/en/reference/groups/sage/groups/generic.html)

On peut déterminer si l'algorithme de *Pohlig–Hellman* s'applique en trouvant l'ordre de la courbe puis en calculant les facteurs de cet ordre.

```python
#Find the order of the curve
order = EC.order()
#Find the factors
factor(order)
```

### Code

Voici le code en entier

Source principal : [https://github.com/cscosu/ctf-writeups/tree/master/2021/redpwn_ctf/crypto](https://github.com/cscosu/ctf-writeups/tree/master/2021/redpwn_ctf/crypto)

```python
from Crypto.Util.number import long_to_bytes

p = 17459102747413984477
a = 2
b = 3

#Define the elliptic curve with the coefficients a and b
EC = EllipticCurve(GF(p), [a, b])

#Define the point G on the curve
G = EC(15579091807671783999, 4313814846862507155)

#Define the point Q on the curve
Q = EC(8859996588597792495, 2628834476186361781)

#Calculate the discrete logarithme
d = G.discrete_log(Q)

#Get the challenge flag by converting d in bytes
print(long_to_bytes(d))

```





## Sources

De nombreuses sources ont été utilisées pour cet article. En voici la liste complète :

### Théorie et définition 

- Cours de cryptographie (CRY) enseigné à l'HEIG-VD en 2020
- Longueur des clés : [https://www.keylength.com/fr/3/](https://www.keylength.com/fr/3/)
- Pohlig-Hellman :
  - [connect.ed-diamond.com - Le logarithme discret contre les tunnels sécurisés](https://connect.ed-diamond.com/MISC/MISCHS-006/Le-logarithme-discret-contre-les-tunnels-securises)
  - [www-math.ucdenver.edu - Pohlig-Hellman Algorithm](http://www-math.ucdenver.edu/~wcherowi/courses/m5410/phexample.pdf)

### Exemple

- redpwnCTF 2021 : [https://ctftime.org/task/16438](https://ctftime.org/task/16438)

- [https://high0101.medium.com/redpwnctf-blecc-crypto-b35997c73a5f](https://high0101.medium.com/redpwnctf-blecc-crypto-b35997c73a5f)
- [c1rcu5_w0lv35 - ctftime.org/team/119580](https://ctftime.org/writeup/29157)
- [https://github.com/cscosu/ctf-writeups/tree/master/2021/redpwn_ctf/crypto](https://github.com/cscosu/ctf-writeups/tree/master/2021/redpwn_ctf/crypto)