---
layout: post
title:  "Les liens avec Linux"
date:   2021-06-15 
categories: Linux
tags: bash
description: Liens symboliques et physiques avec Linux
---

Cet article présente les liens symboliques et physiques. 

Les manipulations ont été effectués sur une machine Ubuntu 20.04 *LTS*



## Petit rappel sur les fichiers  

Un fichier correspond à une entrée dans le répertoire où il se trouve. Celui-ci contient le nom du fichier ainsi que son numéro d'inode.

Que permet le numéro d'inode ?

L'inode contient les métadonnées et des pointeurs vers les blocs de contenus. C'est notamment dans l'inode que sont stockés les permissions du fichier.



## Lien physique 

On créée dans  le répertoire une nouvelle entrée qui pointe vers le **même** inode que le fichier source utilisé pour crée le lien.

Pour simplifier, on ne crée pas un nouvel inode et du contenu dans le filesystem, mais plutôt un pointeur dans le répertoire où l'on se trouve

On aura ainsi deux entrées qui pointera vers le même inode/contenu : l'entrée dans le répertoire du fichier d'origine et la nouvelle entrée qu'on a crée avec le lien physique.



Conséquence :

- Quand vous modifiez le contenu depuis le lien physique (echo, nano, vim), vous modifiez en réalité le contenu de l'inode sur lequel il pointe. Si vous affichez maintenant le fichier source du lien, il affichera alors le contenu modifié.

- Si vous supprimez le fichier source, alors cette suppression ne sera PAS reporté sur le le lien physique. En réalité, vous aurez supprimé une des entrées qui pointe vers l'inode mais sans supprimer l'inode et son contenu.

  

- ```bash
  mv unAutreFichier fichierSrc
  ```

  L'utilisation de la commande mv sur l'entrée du fichier source ne provoque  aucune modification sur le lien physique. La commande mv a  pour conséquence de modifier l'entrée dans le répertoire du fichier source(inode sur lequel il pointe) et non le contenu accessible depuis son inode d'origine.



## Lien symbolique 

Contrairement aux liens physiques, un lien symbolique a son propre inode et ses propres données fichiers. Dans les métadonnées, il y aura le chemin absolu ou relatif du fichier source

Conséquence 

- ```bash
  mv unAutreFichier fichierSrc
  ```

Ici, cette modification sera bien "prise en compte" par le lien symbolique. La raison est la suivante : le lien symbolique pointe vers le répertoire du fichier source. Cette commande aura modifié l'entrée(nom et inode) contenu dans le fichier source sur lequel pointe le lien symbolique.



- ```bash
  mv fichierSrc unAutreFichier 
  ```

Dans ce cas-là, on modifie l'entrée du répertoire du fichier source, c'est-à-dire son inode et son nom. Le lien symbolique ne pourra plus retrouver le fichier source et vous aurez un "File Not Found"



## Exemples



### 1) Affichage

Pour réaliser les exemples, on créer d'abord un

-  Un fichier source file_1
- Un lien physique file_2 à partir de  file_1
- Un lien symbolique file_3 à partir de file_1

A l'affichage, on peut remarquer que file_3 est coloré en bleu et qu'avec la commande ls, on a une petite flèche -> sur le fichier source.

![affichage-lien]({{site.url_complet}}/assets/article/linux/lien/affichage-lien.PNG)

### 2) Modification

Lorsqu'on modifie file_2(lien phyisque), on peut constater que cela modifie également file_1

On observe le même comportement avec file_1

Conclusion : Que ça soit avec un lien physique ou symbolique, bien que l'implémentation soit différente, le résultat pour l'utilisateur est le même.

![modification]({{site.url_complet}}/assets/linux/lien/modification.PNG)

### 3) Utilisation de la commande mv

On crée un nouveau fichier, file4. La commande 

```bash
mv file-4 file_1
```

va modifier l'inode de l'entrée de file_1 dans le répertoire. 

- Cette modification sera prise en compte par le lien symbolique, car celui-ci pointe sur file_1 (l'entrée).
-  Alors que le lien physique, lui il pointe toujours sur l'inode d'origine, celui auquel file_1 pointait au début.

![mv-lien]({{site.url_complet}}/assets/article/linux/lien/mv-lien.PNG)

### 4) Suppression avec rm

En supprimant file_1, on supprime en réalité l'entrée dans le répertoire de file_1, cette suppression sera reportée directement sur file_3 car celui-ci pointe sur file_1.

On peut aussi constater un affichage en rouge pour file_3 indiquant que le lien est mort.

Le lien physique ne sera pas affecté car celui-ci ne pointe pas directement sur file_1 mais avait repris l'inode sur lequel pointait file_1.

![rm-lien]({{site.url_complet}}/assets/article/linux/lien/rm-lien.PNG)



## Sources

- Cours ADS enseigné à l'HEIG-VD(2021)