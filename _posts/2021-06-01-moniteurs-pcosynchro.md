---
layout: post
title:  Les moniteurs avec PcoSynchro
date:   2021-06-01 
categories: programmation
tags: programmation concurrence pcosynchro hoare mesa 
description: Cet article présente les moniteurs de Hoare et de Mesa, ainsi que leur utilisation avec la librairie PcoSyncro. Les moniteurs permettent de synchroniser des ressources mises en concurrence entre plusieurs threads qui veulent y accéder.
---



Les moniteurs permettent de synchroniser des ressources mises en concurrence entre plusieurs threads qui veulent y accéder.

Dans cet article, deux types de moniteurs seront présentés : Mesa et Hoare ainsi que leur utilisation avec la librairie PcoSynchro. Il s'agit d'une librairie développée par l'institut REDS de l'HEIG, disponible publiquement sur gitlab : [https://gitlab.com/reds-public/pco-synchro](https://gitlab.com/reds-public/pco-synchro).

Elle s'utilise avec le logiciel QT : [https://www.qt.io/product/development-tools.](https://www.qt.io/product/development-tools).

Les exemples ci-dessous sont en **c++**



## Différence entre Mesa et Hoare

### Réveille

Avec un moniteur de **Mesa**, le thread qui est libéré par la variable de condition est en concurrence avec les autres threads pour acquérir le verrou.

Il est par conséquent important de revérifier la condition ayant entrainé la mise en attente du thread avant d'accéder à la section critique. Par exemple dans une boucle *while(condition)*



Avec un moniteur de **Hoare**, le thread réveillé acquière directement le mutex, on peut par conséquent le laisser accéder à la section critique sans risque. Une fois sa tâche terminée, il redonne la main au thread qui l'a réveillé.

### Réveille multiple

#### Avec Mesa

Une autre différence entre Hoare et Mesa c'est qu'il est possible d'effectuer un réveille multiple, c'est-à-dire de réveiller plusieurs threads, avec Mesa en appelant la fonction *notifyAll*.

#### Avec Hoare

Avec Hoare, la fonction signal ne va réveiller qu'un seul thread. Il faut alors effectuer des réveils en cascade ou avec une boucle. C'est deux façons de procéder sont détaillés dans la partie dédiée à Hoare.



## Moniteur de Hoare

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



### Réveiller tous les threads

#### Méthode 1 : boucle

Ce code permet de réveiller tous les threads en attente sur la variable de condition.

On a besoin d'un compteur *nbWaitingThreads* pour déterminer le nombre de threads effectivement en attente.

```c++
for(unsigned i = 0; i < nbWaitingThreads; ++i){
	signal(cond);
}
```

Quel est cependant le danger ici ?

Le thread qui effectue le signal va perdre le thread au profit du thread réveillé (Contrairement à Mesa).

Il faut faire attention que la variable *nbWaitingThreads* ne soit pas modifié par le thread réveillé.



#### Méthode 2 - réveil en cascade

Une autre solution est le réveille en cascade. Le programme réveille le 1er thread et c'est le thread réveillé qui va effectuer un nouveau signal et ainsi de suite

```c++
signal(cond);
```

- Code bloquant l'exécution du thread

```c++
monitorIn();
if (votreCondition) {
      wait(condA);
      signal(condA); //Réveille en cascade
 }
//Votre code
monitorOut();
```

- Code réveillant le 1er thread

```c++
monitorIn();
//Votre code
if (votreCondition) {
    signal(condA); //Réveiller un seul thread
}
monitorOut();
```



L'avantage de cette approche en cascade c'est qu'on ne fait pas du ping pong entre le 1er thread et les autres threads.

## Moniteur de Mesa

### Header à inclure

```c++
// Pour les threads

#include <pcosyncrho/pcothread.h>

// Pour les variables de conditions

#include <pcosynchro/pcoconditionvariable.h>

// Pour les sémaphores

#include <pcosynchro/pcosemaphore.h>
```



### Déclaration

Déclarer un mutex pour protéger la variable partagée :

```c++
PcoMutex mutex;
```

Déclarer une variable de condition

```c++
PcoConditionVariable cond;
```



Déclarer un tableau de condition.

```c++
PcoConditionVariable tabCond[2];
```

Ou un pointeur :

C'est intéressant de déclarer un pointeur si vous ne connaissez pas la taille en avance mais que votre tableau aura une taille fixe, par exemple si la taille est spécifiée dans le constructeur de la classe.

```c++
PcoConditionVariable* tabCond = new PcoConditionVariable[size];
```



### Résumé des fonctions

- nofityOne()  :  Réveiller un thread en attente sur la variable de conditions 
- notifyAll()  :  Réveiller tous les threads en attente sur la variable de condition
- wait(&mutex)  : Mise en attente d'un thread sur la variable de condition

Remarques :

Il n'y a pas de garantie que notifyOne ou notifyAll réveille dans l'ordre les threads.

Ainsi le 1er thread mis en attente ne sera pas forcément réveillé en 1er.



Exemple de code :

```c++
mutex.lock();

while(votreCondition){
	++nbWaiting; //Si vous voulez savoir le nombre de thread en attentes
	cond.wait(&mutex);
    //Ici, le thread doit se "battre" pour récupérer le mutex
}

//Zone protégée

mutex.unlock();
```



### Assurer un ordre

Il est possible d'assurer un ordre dans lequel on va réveiller les threads en attente sur les variables de condition en utilisant une *queue*.

Déclaration :

```c++
std::queue<std::PcoConditionVariable*> conditionsList
```

Puis

```c++
if(VotreCondition){
    ++nbWaiting;
    PcoConditionVariable * cond = new PcoConditionVariable();
    conditionsList.push(cond);
    cond->wait(&mutex);
    delete cond;
}
```

Il est important  de supprimer le pointeur de condition avec *delete* après que le thread ait été réveillé.

A l'appel :

```c++
if(nbWaiting){
	PcoConditionVariable* cond = queue.front();
    condLists.pop();
    --nbWaitingThreads;
    cond->notifyOne(); //Réveiller un thread en attente
}
```



## Sources

- [gitlab.com/reds-public/pco-synchro](https://gitlab.com/reds-public/pco-synchro)
- Cours de Programmation concurrente(PCO) enseigné à l'HEIG-VD en 2021