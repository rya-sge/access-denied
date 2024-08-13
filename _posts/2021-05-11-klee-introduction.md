---
layout: post
title:  "Introduction à Klee"
date:   2021-05-11 
categories: security
tags: klee clang reverse sanitizer concolique analyse
description: Présentation du logiciel Klee ainsi que ses tutoriels. Klee est un outil permettant de réaliser une analyse concolique. 
image: /assets/article/outil-securite/klee/klee-tutorial2.JPG
---
Cet article présente **Klee** ainsi que ses tutoriels de prises en main. 

Il s'agit principalement d'une traduction anglais -> français complétée par mes prises des notes de la documentation proposée par l'éditeur de Klee.



## Présentation

Klee est un outil permettant de réaliser une analyse concolique. On peut exécuter le programme avec des valeurs concrètes. Il permet notamment de détecter les erreurs suivantes :

- **ptr**: Stores ou  loads  à des emplacements mémoires invalides.
- **free**: Double or invalid `free()`.
- **abort**: Appel de la fonction `abort()`.
- **assert**: Echec d'une insertion
- **div**: Division ou modulo par 0 
- **user**: Problème avec l'input ou dont la façon dont est appelé klee (ndlr : pas forcément lié à votre programme)
- **exec**: instruction inconnue, appelle à une fonction invalide ou avec de assembleur inline. 

Sauf erreur de ma part, klee n'est pas capable de détecter des  fuites de mémoire.

Sources : [https://klee.github.io/tutorials/testing-regex/](https://klee.github.io/tutorials/testing-regex/)

## Installation

### Docker

Il est possible d'installer Klee dans un docker :

```
$ docker pull klee/klee:2.1
$ docker run --rm -it --ulimit='stack=-1:-1' klee/klee:2.1
```

La 1ère commande tire l'image du conteneur

La 2ème commande lance le conteneur avec un shell(option -ti) à partir de l'image précédente 

Lien : [https://klee.github.io/docker/](https://klee.github.io/docker/)

Il est possible également d'installer des outils dans le conteneur car nous y avons les droits sudo.

Par exemple pour installer nano :

```bash
sudo apt update
sudo apt-get install nano
```



Vous pouvez copier des fichiers de vote hôte dans le conteneur avec la commande *docker cp*

```bash
docker cp  dossier <nom conteneur | id>:/home/klee/klee_src/examples
```

## Utilisation dans un programme C

Il faut d'abord inclure le header de klee :

```c
#include<klee/klee.h>
```



Puis faire appel à la fonction klee_make_symbolic pour que klee génère des inputs pour la fonction donnée. Exemple avec le fichier get_sign.c du tutoriel 1 de klee.

```c
#include "klee/klee.h"

int get_sign(int x) {
} 

int main() {
  int a;
  klee_make_symbolic(&a, sizeof(a), "a");
  return get_sign(a);
} 
```



Pour repérer les input menant à un chemin particulier, un if par exemple. On peut faire un appel à la fonction klee_abort() dans le *if* afin que klee génère une erreur :

```c
klee_abort();
```



Klee générera alors des tests contenant ces erreurs qu'on pourra rejouer avec la commande suivante :

```
for f in *.abort.err;do ktest-tool ${f%.abort.err}.ktest ; done
```



## Tutoriel 1

Klee propose un tutoriel pour prendre en main l'outil : [https://klee.github.io/tutorials/testing-function/.](https://klee.github.io/tutorials/testing-function/)

Il est également possible de faire des tests en ligne : [http://klee.doc.ic.ac.uk/#](http://klee.doc.ic.ac.uk/#)

Cette partie est une version abrégée du contenu de ce tutoriel

#### 1. Compilation

Au sein du conteneur, la commande suivante permet de compiler en  LLVM bitcode 

```bash
clang -I ../../include -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone get_sign.c
```

- Le paramètre -I permet de retrouver la dépendance klee.h

- -g ajoute les informations de debug
- -c pour que le code soit compilé comme un fichier objet
- -O0 -Xclang -disable-O0-optnon permet de compiler sans optimisation

![klee-tutorial1]({{site.url_complet}}/assets/article/outil-securite/klee/klee-tutorial1.JPG)



#### 2. Run Klee

Ensuite on peut lancer klee sur le fichier bytecode 

```bash
$ klee get_sign.bc
```

Dans le code initial, il y avait 2 if et un else, ce qui donne 3 chemins(=path) possibles.

![klee-tutorial2]({{site.url_complet}}/assets/article/outil-securite/klee/klee-tutorial2.JPG)

Pour chaque chemin exploré, klee génère un test cases

#### 3. Test Cases

Les tests générées ont le format .ktest

On peut les lire avec l'outil ktest-tool :  

```bash
 ktest-tool klee-last/test000001.ktest
```

![klee-tutorial3]({{site.url_complet}}/assets/article/outil-securite/klee/klee-tutorial3.JPG)

Dans les résultats, le paramètre name fait référence au "a" passé lors de l'appel à klee_make_symbolic

![tutoriel-klee_code]({{site.url_complet}}/assets/article/outil-securite/klee/tutoriel-klee_code.png)

#### 4. Rejouer un Test Case

La *replay library*, remplace les appels à  `klee_make_symbolic` par un appel à une fonction qui remplace l'input par la valeur contenue dans le fichier `.ktest`

```bash
export LD_LIBRARY_PATH=/home/klee/klee_build/lib/:$LD_LIBRARY_PATH
```

```bash
gcc -I  ../../include -L /home/klee/klee_build/lib/ get_sign.c -lkleeRuntest
```

```bash
KTEST_FILE=klee-last/test000001.ktest ./a.out
```

```bash
echo $?
```

![klee-tutorial4]({{site.url_complet}}/assets/article/outil-securite/klee/klee-tutorial4.JPG)

La valeur 255 renvoyée par le dernier test case correspond au return -1



## Tutoriel 2

Ce tutoriel permet de test les expressions régulières

Code : [https://klee.github.io/resources/Regexp.c.html]( https://klee.github.io/resources/Regexp.c.html)

1)  Compiler le code source afin de générer un fichier object en bitecode LLVM

```bash
clang -I ../../include -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone Regexp.c
```

![klee_tutorial5]({{site.url_complet}}/assets/article/outil-securite/klee/klee-tutorial5.JPG)

2) Vérifier l'étape 1 :

```bash
llvm-nm Regexp.bc
```

3) Lancer klee :

```bash
klee --only-output-states-covering-new Regexp.bc
```

L'option --only-output-states-couvrant-new permet de limiter le nombre de tests effectués

![klee-tutorial6]({{site.url_complet}}/assets/article/outil-securite/klee/klee-tutorial6.JPG)



### Erreurs

Les fichiers d'erreurs se trouvent dans le dossier *klee-last*. On peut afficher les erreurs rencontrés en faisant :

```bash
cat test000010.ptr.err
```

![klee-tutorial7]({{site.url_complet}}/assets/article/outil-securite/klee/klee-tutorial7.JPG)

Pour afficher tous les tests ayant générés un assert abort, on peut lancer sur bash la commande suivante :

```bash
for f in *.abort.err;do ktest-tool ${f%.abort.err}.ktest ; done
```



#### Erreur générée par klee

Pour éviter que Klee génère des erreurs, il faut soit ajouter '\0' à la fin du buffer soit utiliser *klee_assume* comme ceci :

```c
klee_make_symbolic(re, sizeof re, "re");
klee_assume(re[SIZE - 1] == '\0');
```



## Astuces diverses

Ajouter cette option au lancement de klee pour obtenir tous les chemins faisant cracher un programme. Par défaut, klee ne conserve qu'un seul chemin.

```bash
–emit-all-errors 
```



## Sources

- [https://klee.github.io/tutorials/testing-function/](https://klee.github.io/tutorials/testing-function/)
- [https://klee.github.io/docker/](https://klee.github.io/docker/)
- Il a été réalisé dans le cadre du cours de sécurité logicielle donné par l'HEIG-VD en 2021.

