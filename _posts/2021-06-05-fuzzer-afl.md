---
layout: post
title:  "Fuzzing avec AFL"
date:   2021-06-05 
categories: sécurité
tags: fuzzing afl
---
AFL est un outil de fuzzing c'est-à-dire qu'il injecte des données dans le programme. Celles-ci sont au départ aléatoire puis AFL va ensuite adapter les inputs aux résultats obtenus.

### List de commandes utiles

Compiler le code pour AFL:

```bash
/bin/afl-clang-fast -fno-inline program.c -o program
```

http://spencerwuwu-blog.logdown.com/posts/1366733-a-simple-guide-of-afl-fuzzer

Exécuter afl sur un programme

```bash
afl-fuzz -i input -o output ./programme
```

Sur kali Linux, si vous n'ajouter pas le *./* devant programme, AFL vous renverra l'erreur suivante : *Program ' not found or not executable* 



### Voir les résultats

Dans le dossier output/crashes, afficher les fichiers ayant généré un crash avec par exemple la commande cat. Petites remarques, les noms de fichiers sont plutôt longs.

![result](C:\Users\super\switchdrive\HEIG\divers\mywebsite\accessDenied\assets\article\outil-securite\afl-fuzzing\result.PNG)



### Astuces

Il est possible de lancer plusieurs instances d'AFL. Pour cela il faut d'abord lancer le master puis ensuite les autres avec l'option -S

Ex :

![instances](C:\Users\super\switchdrive\HEIG\divers\mywebsite\accessDenied\assets\article\outil-securite\afl-fuzzing\instances.png)



et dans un autre terminal :

![instances2](C:\Users\super\switchdrive\HEIG\divers\mywebsite\accessDenied\assets\article\outil-securite\afl-fuzzing\instances2.png)

Voir cet articule pour plus d'informations :

[https://github.com/google/AFL/blob/master/docs/parallel_fuzzing.txt](https://github.com/google/AFL/blob/master/docs/parallel_fuzzing.txt)

### Sources

- Ce tutoriel est très bien expliqué et complet :

[](http://spencerwuwu-blog.logdown.com/posts/1366733-a-simple-guide-of-afl-fuzzer)

- Cours de sécurité logicielle enseigné à l'HEIG-VD(M.Bost)