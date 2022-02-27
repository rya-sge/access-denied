---
layout: post
title:  "Les Courbes Elliptiques avec SageMath"
date:   2022-02-27
last-update: 
categories: cryptographie programmation
tags: logarithme-discret courbe-elliptique sage
description: Cet article explique l'implémentation des courbes elliptiques avec la librairie SageMath, par exemple la définition et l'addition des points sur une courbe.
image: /assets/article/cryptographie/sagemath/ec/cover-image.PNG
---



## Introduction

Cet article explique l'implémentation des courbes elliptiques avec **SageMath**  à travers des exemples, la définition de quelques fonctions spéciales (MISC) ainsi que le cas spécifique du logarithme discret.

La documentation de SageMath peut être trouvée à l'adresse suivante :

- [doc.sagemath.org - arithmetic_curves/index.html](https://doc.sagemath.org/html/en/reference/arithmetic_curves/index.html)
- [doc.sagemath.org - Elliptic curves over a general ring](https://doc.sagemath.org/html/en/reference/arithmetic_curves/sage/schemes/elliptic_curves/ell_generic.html)





## Exemple

### Déclaration

- Définir la courbe

$$
y^2 = x^3 + x + 2~sur~ GF(5) 
$$

```python
E = EllipticCurve(GF(5), [1, 2])
```



- Définir un point P sur la courbe

```python
P = E(1,2)
```



Dans la partie  **Opérations** ci-dessous, le point P ainsi que la courbe utilisée  auront toujours la même valeur.



### Opérations

- Imprimer les coordonnées x, y : `Point.xy()`

```python
P.xy()
```

Résultat : (1 , 2)

Attention : la fonction xy() ne fonctionnera pas pour le point à l'infini

- Déterminer si un point est le point à l'infini : `is_zero()`

```python
P.is_zero()
```

Résultat : False

- Obtenir le point à l'infini : `E(0)` 

Exemple :

```python
E(0)
```

Résultat : (0 : 1 : 0)

```python
T = E(0, 1 , 0)
T.is_zero()
```

Résultat : True

- Additionner 2 points

```python
Q = (1, 3)
R = P + Q
```

- Multiplier un point par une constante

```python
Q = 14 * P
Q.xy()
```

Résultat : (4, 0)

- Tirer un nombre aléatoire

```python
Q = E.random_element()
Q.xy()
```

Exemple de résultat : (1, 3)

### Miscs

E correspond à la courbe elliptique.

`E.change_ring(R)`

Retourner la b *self* à R

Lien documentation : [doc.sagemath.org- EllipticCurve_generic.change_ring]( https://doc.sagemath.org/html/en/reference/arithmetic_curves/sage/schemes/elliptic_curves/ell_generic.html#sage.schemes.elliptic_curves.ell_generic.EllipticCurve_generic.change_ring)

`E.lift_x(x)` 

Retourner tous les points avec une coordonnées x données.

Lien documentation : [doc.sagemath.org - EllipticCurve_generic.lift_x](https://doc.sagemath.org/html/en/reference/arithmetic_curves/sage/schemes/elliptic_curves/ell_generic.html#sage.schemes.elliptic_curves.ell_generic.EllipticCurve_generic.lift_x)

```python
E.lift_x(1)
```

Résultat : (1 : 3 : 1)

```python
E.lift_x(2)
```

Résultat : 

*No point with x-coordinate 2 on Elliptic Curve defined by y^2 = x^3 + x + 2 over Finite Field of size 5*

## Logarithme discret

Voici un exemple pour calculer le logarithme discret sur courbe elliptique.

Dans les faits, calculer le logarithme discret peut être très couteux en temps de calcul.

```python
P = E (1, 2)
q = P.order()
Q = 3 * P
s = P.discrete_log(Q, ord = q)
print(s)
```

Résultat : 3

J'ai écrit un autre article plus complet sur le sujet : 

[rya-sge.github.io/access-denied - Logarithme Discret sur courbe elliptique avec SageMath](https://rya-sge.github.io/access-denied/2021/07/30/logarithme-discret-courbe-elliptique/)

## Sources

- Cours de cryptographie (CRY) enseigné à la HEIG-VD en 2020
- Cours de cryptographie appliquée avancée (CAA)  enseigné à la HEIG-VD en 2022
- Documentation SageMath : [doc.sagemath.org - Elliptic curves over a general ring](https://doc.sagemath.org/html/en/reference/arithmetic_curves/sage/schemes/elliptic_curves/ell_generic.html)
- Autres articles du site sur le sujet : [Access Denied - Logarithme Discret sur courbe elliptique avec SageMath](https://rya-sge.github.io/access-denied/2021/07/30/logarithme-discret-courbe-elliptique/)

