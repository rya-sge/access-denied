---
layout: post
title:  "Fuzzing avec AFL"
date:   2021-06-05 
categories: security
tags: fuzzing afl
description: Présentation de l'outil de Fuzzing AFL (American Fuzzy Lop)
image: /assets/article/outil-securite/afl-fuzzing/result-print.png
---
*AFL*  de Google est un outil de fuzzing (*fuzzer*), disponible sur le github de google : [https://github.com/google/AFL](https://github.com/google/AFL)

Il a pour objectif de tester les entrées d'un programme en y injectant des données. Celles-ci sont au départ aléatoire puis *AFL* va ensuite adapter les inputs aux résultats obtenus.

### Mise en place

- Adapter le programme à *AFL* 

Si vous voulez déterminer quel input mène à un endroit du code particulier, il faut ajouter la fonction suivante dans votre code, ici en C :   

```c
  abort();
```

Ainsi lorsqu'AFL atteindra cette portion du code, cela va générer une erreur qui sera ensuite accessible dans les résultats.



- Générer le 1er test cases

Avant de pouvoir lancer AFL, il faut créer le 1er test arbitraire. AFL va ensuite dérivé cette input pour produire d'autres inputs.

Ici, il est crée avec la commande *echo* sur un terminal *bash*

```bash
mkdir test
echo "hello" > test/test1
```



### List de commandes utiles

- Compiler le code pour AFL:


```bash
/bin/afl-clang-fast -fno-inline program.c -o program
```

Cela va instrumenter le code pour l'adapter à *AFL*



- Exécuter afl sur un programme.

*test* correspond à votre dossier où vous avez crée les tests.

```bash
afl-fuzz -i test -o output ./programme
```

Sur kali Linux, si vous n'ajoutez pas le *./* devant programme, *AFL* vous renverra l'erreur suivante : *Program  not found or not executable* 



### Voir les résultats

#### Fenêtre en temps réel

Une fois lancé, une fenêtre s'ouvre avec les résultats en temps réel.

![result-print]({{site.url_complet}}/assets/article/outil-securite/afl-fuzzing/result-print.png)

##### Overall results 

Situé en haut à droite

| Nom           | Description                                                  |
| ------------- | ------------------------------------------------------------ |
| total paths   | Nombre de chemins explorés. Ici AFL a exploré 8 chemins      |
| uniq crashes  | Nombre de crashs ayant menés à un chemin unique. Si 2 mêmes inputs font crachés le programme au même endroit, il n'y aura qu'un seul crash de comptabilité |
| total crashes | Nombre de crash total (unique ou non)                        |
| uniq hangs    | Nombre de timeout sur des chemins uniques                    |

##### Stage progress

| Nom         | Description                                   |
| ----------- | --------------------------------------------- |
| total execs | Nombre de fois que le programme a été exécuté |
| exec speed  | Vitesse d'exécution du programme              |



Plus d'informations est disponible sur le *github* de *AFL* à l'adresse suivante : [https://github.com/google/AFL/blob/master/docs/status_screen.txt](https://github.com/google/AFL/blob/master/docs/status_screen.txt)



#### Voir les inputs

Dans le dossier output/crashes, afficher les fichiers ayant généré un crash avec par exemple la commande *cat*. Petites remarques, les noms de fichiers sont plutôt longs.

![result]({{site.url_complet}}\assets\article\outil-securite\afl-fuzzing\result.PNG)



### Astuces

Il est possible de lancer plusieurs instances d'AFL. Pour cela il faut d'abord lancer le master puis les autres avec l'option -S

Ex :

![instances]({{site.url_complet}}\assets\article\outil-securite\afl-fuzzing\instances.png)



et dans un autre terminal :

![instances2]({{site.url_complet}}\assets\article\outil-securite\afl-fuzzing\instances2.png)

Voir cet article pour plus d'informations :

[https://github.com/google/AFL/blob/master/docs/parallel_fuzzing.txt](https://github.com/google/AFL/blob/master/docs/parallel_fuzzing.txt)

### Sources

- Ce tutoriel est très bien expliqué et complet :

[http://spencerwuwu-blog.logdown.com/posts/1366733-a-simple-guide-of-afl-fuzzer](http://spencerwuwu-blog.logdown.com/posts/1366733-a-simple-guide-of-afl-fuzzer)

- Cours de sécurité logicielle enseigné à l'HEIG-VD en 2021