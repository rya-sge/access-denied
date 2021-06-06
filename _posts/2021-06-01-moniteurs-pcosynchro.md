---
layout: post
title:  "Les moniteurs avec PcoSynchro"
date:   2021-06-01 
categories: programmation
tags: programmation concurrence pcosynchro hoare mesa 
Auteur: rya-sge
---



Les moniteurs permettent de synchroniser des ressources mises en concurrence entre plusieurs threads qui veulent y accéder.

Dans cet article, deux types de moniteurs seront présentés : Mesa et Hoare ainsi que leur utilisation avec la librairie PCoSynchro. Il s'agit d'une librairie développé par l'institut REDS de l'HEIG, disponible publiquement sur gitlab : [https://gitlab.com/reds-public/pco-synchro](https://gitlab.com/reds-public/pco-synchro).

Elle s'utilise avec le logiciel QT : [https://www.qt.io/product/development-tools.](https://www.qt.io/product/development-tools).

Les exemples ci-dessous sont en **c++**



**Quelle différence entre un moniteur de Mesa et de Hoare ?**

Avec un moniteur de Mesa, le thread qui est libéré par la variable de condition est en concurrence avec les autres threads pour acquérir le verrou.

Il est par conséquent important de ré-vérifier la condition ayant entrainé la mise en attente du thread avant d'accéder à la section critique. Par exemple dans une boucle while(condition)



Avec un moniteur de hoare, le thread réveillé acquière directement le mutex, on peut par conséquent le laisser accéder à la section critique sans risque. Une fois sa tâche terminée, il redonne la main au thread qui l'a réveillé(*Pas sûr que ça soit le cas dans toutes les implémentations*)



## PcoSynchro

### Moniteur de Hoare

Pour appeler les moniteurs dans une classe, il faut la déclarer comme sous classe de PcoHoareMonitor

```c++
nomClasse : PcoHoareMonitor
```

Déclarer une condition

```c++
Condition cond;
```

On peut ensuite utiliser les fonctions suivantes pour entrer et sortir du moniteur

- monitorIn
- monitorOut
- wait(condition) bloque le thread jusqu'à ce qu'il soit réveillé par un appel à signal
- signal(condition) : réveille UN thread en attente sur la variable de condition

Quand un thread mis en attente est réveillé, il prend directement possession du mutex.

Ensuite, il redonne la main au thread au thread qui a effectué le signal

#### Exemples

Ce code permet de réveiller tous les threads en attente sur la variable de condition.

On a besoin d'un compteur nbWaitingThreads pour déterminer le nombre de threads effectivement en attente.

```c++
for(unsigned i = 0; i < nbWaitingThreads; ++i){
	signal(cond);
}
```



### Moniteur de Mesa

##### Header à inclure

- Pour les threads

#include <pcosyncrho/pcothread.h>

- Pour les variables de conditions

#include <pcosynchro/pcoconditionvariable.h>

- Pour les sémaphores

#include <pcosynchro/pcosemaphore.h>



##### Déclaration

Déclarer un mutex pour protéger la variable partagée:

```c++
PcoMutex mutex;
```

Déclarer une variable de condition

```c++
PcoConditionVariable cond;
```



##### Résumé des fonctions

- nofityOne()  :  Réveiller un thread en attente sur la variable de conditions 
- notifyAll()  :  Réveiller tous les threads en attente sur la variable de condition
- wait(&mutex)  : Mise en attente d'un thread sur la variable de condition

Remarques :

Il n'y a pas de garantie que notifyOne ou notifyOne réveille dans l'ordre les threads.

Ainsi le 1er thread mis en attente ne sera pas forcément réveillé en 1er.



## Sources

- [https://gitlab.com/reds-public/pco-synchro](https://gitlab.com/reds-public/pco-synchro)
- Cours PCO enseigné à l'HEIG-VD en 2021