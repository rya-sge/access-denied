---
layout: post
title:  "Les regex en Javascript"
date:   2021-10-13
categories: programmation web
tags: regex javascript
description: Présentation et utilisation des regex en Javascript
image: 
---

Les expressions régulières permettent de sélectionner / déterminer si des chaines de caractères correspondent à un certains "patterns/modèles". Il ne s'agit cependant pas d'un langage de programmation.

**Exemple**

On pourrait vouloir utiliser des regex pour sélectionner des numéros, comme celui-ci

`555-973-2468`

La regex correspondante serait :

`\d\d\d-\d\d\d\-\d\d\d\d`

### Quelques moteurs

Il existe de nombreux outils pour faire des regex

- RegexBuddy

- RegexMobile

En ligne :

- [https://regexr.com](https://regexr.com)
- [https://www.regexpal.com](https://www.regexpal.com)

## Principales constructions

- Classe de caractères (. , \s, \d)  qui distinguent différents type de caractères (lettres ou digits) 

- Jeux de caractères([a-z]) où il y  a la correspondance avec n'importe quel caractère s'y trouvant
- Opérateur logique ou : < | > où la string doit correspondre à la valeur de gauche ou de droite
- Quantificateurs  (*, +, ?, {n}, {n,m}) qui indiquent le nombre de fois que l'expression doit correspondre.

- Barrières (^$) qui indiquent le début et la fin de chaque mot

- Groupes ( `),(?<name>), (?:)`) qui extraient et se souviennent (ou pas) des informations de l'entrées

- Assertions (x(?=y)) qui aident à définir des expressions conditionnels


Par défaut, le comportement d'une regex est :

- Non global : le premier élément en partant de la gauche est sélectionné et pas les suivant
- Sensible à la casse : prend en compte les majuscules

## Flags

- `g`pour effectuer une recherche global. C'est-à-dire qu'on ne s'arrête pas au 1er élément correspondant mais qu'on sélectionne tous ceux répondant aux critères

  - ​	La regex `/zz/g` appliqué au mot pizzazz sélectionne 2 fois le ZZ

    ​	Réponse :  pi**zz**a**zz**

- `i`pour  être insensible à la casse

- `m`pour une recherche multi-ligne

### Exemple

```javascript
const re1 = /world +c/; // Aucun flag
const re2 = /world +c/g; // recherche globale
const re3 = /world +c/i; // recherche insensible à la casse
const re4 = /world +c/m; // recherche multiline
const re5 = /world +c/gi // recherche globable et insensible à la casse
```



## Metacharacters

### Répétition

- <*> : Elément précédent, 0 ou plusieurs fois

- <+> : élément précédent, un ou plusieurs fois
- <?> : Elément précédent, zéro ou une fois

#### Exemples

- `/pommes*/` sélectionne "pomme", "pommes" et "pommesssss"
- `/pommes+/` sélectionne "pommes" et "pommessss" mais pas "pomme" car le caractère s doit être présent
- `/couleu?r/` sélectionne "couleur" et "couler"

 

### Quantificateur

- <{min, max}>

Les accolades permettent d'exprimer le nombre minimum ou maximum de l'élément précédent, max n'est pas obligatoire et équivaut à l'infini si omis.

### Exemple

- `/d{3, 6}/` sélectionne les nombres constitués de 3 à 8 chiffres
- `/d{3}/` sélectionne les nombres ayant exactement un chiffre
- `/d{3,}/` sélectionne les nombres avec 3 ou plus de chiffres

## En javascript

La fonction test permet de vérifier si une string vérifie un pattern donné grâce à une regex

### Exemple

Voici une regex qui vérifie les conditions suivantes

 * Qui commence par une majuscule ;
 * Qui peut comporter des '-' ou des espaces suivis d'une majuscule (Ex. Truc-Machin-Chose);
 * Qui ne doit contenir que des lettres.

```javascript
function name(value) {
  if (!isString(value)) {
    throw new InvalidArgumentError('error', value);
  }

  if (/^[A-Z]([A-Za-z]*)([- ]?[A-Z][a-zA-Z]*)*$/gm.test(value)){
    return true;
  }
  throw new ValidationError();
}
```



## Sources 

- Cours de Technologie Web (TWEB) enseigné à l'HEIG-VD en 2021
- Cours Linkedin *Learning Regular Expressions* enseigné par K.Skoglund.



