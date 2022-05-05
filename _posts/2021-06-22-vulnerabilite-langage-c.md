---
layout: post
title:  "Vulnérabilités avec le langage C"
date:   2021-06-22
categories: programmation securite
tags: c vulnérabilité strcpy scanf printf malloc sanitizer
description: Cet article présente une liste de vulnérabilités (CWE 121, CWE 122, etc.) et menaces potentielles avec le langage C afin de sensibiliser les programmeurs.
image: /assets/article/securite/cover/c-vulnerabilite.PNG
---



Cet article présente une liste de vulnérabilités et menaces potentielles avec le langage C.

Il a pour objectif de sensibiliser les programmeurs aux différents points sensibles de la programmation en C. Certaines de ces vulnérabilités sont également présentes dans le langage C++.

Cet article n'est pour l'instant pas complet et sera amélioré au fil du temps.



## Sécurité spatiale et temporelle

Dans cet article, je ferais souvent référence à la sécurité temporelle et la sécurité spatiale.

- La **sécurité spatiale** est obtenue lorsque les accès mémoires sont dans les bornes définies par l'objet. Par exemple avec un buffer de 12 caractères, la sécurité spatiale n'est pas présente si un utilisateur peut écrire plus de 12 caractères

- La **sécurité temporelle** est obtenue lorsque les accès mémoires sont valides au moment de leur réalisation. Par exemple, si vous accéder à un emplacement mémoire au-delà de la taille de votre tableau, alors la sécurité temporelle n'est pas présente.

  Exemple :

  ```c
  int buffer[12];
  tab[12] = 0; 
  ```

  Les index en C commencent à 0. Le programme accède à l'emplacement 12 qui est au-delà de la taille du tableau.

## Fonctions vulnérables

Voici quelques fonctions qui  représentent des vulnérabilités, soit directement par leur simple utilisation soit alors en cas de mauvaise implémentation de la part du programmeur.

### **1) strcpy**

Avec *strcpy*, on ne précise pas le nombre de caractère maximum à lire, on peut dès lors dépasser la taille du buffer qui contiendra les données. Elle est par conséquent vulnérable à des **buffer overflow**. La sécurité spatiale n'est pas garantie. 

CWE concernée : 

- CWE 121 - **Stack-based Buffer Overflow**
- Page de présentation  : [MITRE, 2022a] - [https://cwe.mitre.org/data/definitions/121.html](https://cwe.mitre.org/data/definitions/121.html)

Cet exemple est en grande partie issue de cette même CWE. J'y ais ajouté la variable locale `authOK`  afin de montrer comment on peut concrètement utiliser cet *overflow*.

```c
#define BUFSIZE 256
int main(int argc, char **argv) {
    int authOK = 0;
    char buf[BUFSIZE];
    strcpy(buf, argv[1]);
    if(auth){
        printf("Accès à la section secrète");
    }
    return 0;
}
```

Le programme alloue BUFSIZE  octets sur la pile et va ensuite copier la chaine passée en argument dans buf.

Vu qu'il ne contrôle pas la taille passée en argument, un utilisateur peut entrer une chaîne > 256, ce qui va écraser la variable authOK et va lui permettre d'accéder à la section secrète.

On pourrait aussi imaginer écraser la valeur de eip, mais vu qu'on est dans la fonction principale main, cela n'a (à mon avis) pas grande utilité.

### **2) scanf()** 

La fonction *scanf* n'est absolument pas sécurisé. Elle ne doit pas être utilisée.

Exemple 1 : 

```c
printf("Entrez votre nom d'utilisateur");
scanf("%s", buffer);
```



Dans l'exemple ci-dessus, l'utilisateur peut entrer ce qu'il veut et ainsi dépasser la taille possible de buffer. On aura alors un **buffer overwrite**. La sécurité spatiale de l'application n'est alors pas garantie

Exemple 2 :

```c
scanf("%10s", buffer)
```

Dans cet exemple, on vérifie le nombre de caractère. Parfait ? Non parce que l'utilisateur peut toujours entrer une chaine plus longue, ce qui aura pour effet que le '/0' ne sera pas copié. On aura bien seulement 127 caractère dans le buffer, mais  la chaine copiés ne contiendra pas le caractère de fin de chaine. Ainsi, en cas de lecture de celui-ci avec par exemple *printf*, alors on dépassera la taille du buffer. Nous avons alors un **buffer overread**

**Détection :** Il est possible de détecter ces vulnérabilités avec l'outil *Sanitizer en activant **AddressSanitizer**.

#### Mitigation - fgets

Il est préférable de remplacer *scanf* par la fonction *fgets*. Celle-ci permet de préciser une longueur maximale. De plus, elle ne lira qu'au plus *maxLength* - 1 caractère car elle ajoute le caractère de fin de chaîne '\0'. 

Pour récupérer la saisie de l'utilisateur, il faut spécifier *stdin* comme *stream*.

```c
char * fgets( char * string, int maxLength, FILE * stream );
```

Source : [KOOR] - [https://koor.fr/C/cstdio/fgets.wp](https://koor.fr/C/cstdio/fgets.wp)

### **3) printf**

Quel est le problème ici ?

```c
scanf("%s", buffer)
printf(buffer)
```

On ne précise par le format string avec un %s lors du printf. Un attaquant pourrait exploiter cet faille pour réaliser une attaque par format strings.

Par exemple, l'input suivant utilisé avec *pwntools* permettra d'afficher les 11 premières cases(32 bits) de la pile. On pourrait ainsi  récupérer des informations intéressante "stockées sur la pile, comme la valeur du *canary* afin de pouvoir procéder à un *buffer overflow* sans être détecté.

```python
input = ("AAAA" + "%08x." * 11 + "%x");
```

L'utilisation de *fgets* à la place de *scanf* peut rendre plus compliqué l'exploitation de la faille car l'attaquant disposera de moins de caractères pour construire son *payload*. Cependant, cela ne corrige pas la vulnérabilité.

### 4) Malloc/Calloc

Les fonctions *malloc* et *calloc* vont réserver de la mémoire dans le tas(heap) dont l'adresse du début sera retournée. Cela peut entrainer plusieurs vulnérabilités :

- Un dépassement de la mémoire allouée va entrainer un overflow sur le heap. Il s'agit de la **CWE 122** dont voici un des exemples donnés :

  ```c
  #define BUFSIZE 256
  int main(int argc, char **argv) {
  	char *buf;
  	buf = (char *)malloc(sizeof(char)*BUFSIZE);
  	strcpy(buf, argv[1]);
  }
  ```

  Le programme réserve BUFSIZE octets en mémoire. Ensuite il fait un appel à *strcpy* en copiant les octets de argv dans buf. Néanmoins, il n'y a aucune garantie que la string dans argv fasse moins de 256 bytes. Il y a par conséquent la possibilité d'effectuer un overflow sur le heap en entrant une chaine de caractères > 256.

  Lien CWE : [MITRE, 2022b] -  [https://cwe.mitre.org/data/definitions/122.html](https://cwe.mitre.org/data/definitions/122.html)

  **Détection :** 

  - Il est possible de détecter cette vulnérabilité avec
    -  l'outil **Sanitizer* en activant `AddressSanitizer(ASan)`
    - Eventuellement l'outil *klee* avec le type d'erreur *ptr* (ndlr : pas sûr à confirmer)

- Il est importer de libérer la mémoire en réalisant un *free* du pointeur, sinon il y aura une fuite de mémoire (*memory leak*). La sécurité temporelle de l'application ne sera alors pas garantie.

  **Détection :** 

  - Il est possible de détecter cette vulnérabilité avec l'outil *Sanitizer en activant `LeakSanitizer(LSan)`.
  -  Par contre, l'utilisation de l'outil Klee ne permet PAS de détecter des fuites de mémoires(sauf erreur de ma part)

## Implémentations

### Variables non initialisées

En c, les variables non initialisées ont une valeur arbitraire, ce qui peut provoquer un comportement indéterminé du programme et par conséquent entrainer des failles de sécurités

**Détection :** Il est possible de détecter ces vulnérabilités avec l'outil *Sanitizer en activant `UndefinedBehaviorSanitizer`.



### Integer overflow

La circulation des entiers peut entrainer des bugs dans l'application et de potentielles failles de sécurités



## Bibliographie

- Cours de sécurité logiciel (SLO) enseigné à la HEIG-VD en 2021
- MITRE, 2022a. CWE-121: Stack-based Buffer Overflow. In :  CWE [en ligne].  19 juillet 2006,  mis à jour le 28 avril 2022. [Consulté le 5 mai 2022]. Disponible à l’adresse : [https://cwe.mitre.org/data/definitions/121.html](https://cwe.mitre.org/data/definitions/121.html)
- MITRE, 2022b. CWE-122: Heap-based Buffer Overflow. In :  CWE [en ligne].  19 juillet 2006,  mis à jour le 28 avril 2022. [Consulté le 5 mai 2022]. Disponible à l’adresse : [https://cwe.mitre.org/data/definitions/122.html](https://cwe.mitre.org/data/definitions/122.html)
- KOOR. Fonctions *fgets* et *gets*. In :  Koor [en ligne].   [Consulté le 5 mai 2022]. Disponible à l’adresse :  [https://koor.fr/C/cstdio/fgets.wp](https://koor.fr/C/cstdio/fgets.wp)



