---
layout: post
title:  "VirtualBox"
date:   2021-05-11
categories: Virtualisation
tags: virtualbox
---


# VirtualBox - Augmenter l'espace de stockage

## Contexte

Cet article présente mes prises de notes sur l'outil de virtualisation VirtualBox.

L'ensemble des opérations effectuées l'ont été pour augmenter l'espace de stockage d'une VM Ubuntu (Ubuntu 20.04.2 LTS) avec le logiciel de virtualisation VirtualBox. Celui-ci était installé sur Windows 10 Professional, 64 bits.

## Mise en place

Pour  effectuer cette opération, il faut avoir préalablement éteint votre espace de stockage.

De plus, pensez à sauvegarder vos fichiers de la VM sur votre disque principale car il y a un risque que l'opération puisse échouer, rendant le disque et son contenu illisible.

## Opération

### 1) Augmenter taille vdi

 Fichier -> Gestionnaire de média -> sélectionner le disque vdi que vous voulez augmenter et augmenter sa taille avec le curseur![stockage]({{site.url}}\assets\article\virtualBox\gparted_stockage.png)



## 2) Appliquer le redimensionnement 

### a) Premier essai -> pas concluant

De nombreux tutoriels proposent d'utiliser *modifyhd*. Cela n'a pas marché chez moi !!!

je mets ici les commandes que j'ai essayé à titre **indicatif**

Pour que les modifications soit prises en compte, il faut encore effectuer l'opération suivante :

![vb_resize]({{site.url}}\assets\article\virtualBox\virtualbox_resize.JPG)

C:\"Program Files"\Oracle\VirtualBox\VBoxManage.exe VBoxManage modifyhd SLO2.vdi --resize 25000.

-L'exécutable a lancé est VBoxManage.exe

-25000 correspond à la taille en MB du nouveau disque.

Source : [https://www.malekal.com/virtualbox-reduire-augmenter-la-taille-du-disque-virtuel/](https://www.malekal.com/virtualbox-reduire-augmenter-la-taille-du-disque-virtuel/)



### b) 2ème essai -> concluant

 Pour appliquer le redimensionnement à ma partition sur ubuntu, j'ai suivi ce tutoriel :

[https://linuxhint.com/increase-virtualbox-disk-size/](https://linuxhint.com/increase-virtualbox-disk-size/)

Celui-ci propose d'utiliser GNOME partition Editor : https://gparted.org/download.php

Après avoir mis démarré ma VM sur l'iso du logiciel, voici les opérations que j'ai effectuées

1) On peut voir ici que j'ai 9 GO d'espace libre, correspond à l'augmentation du disque dur

Je vais alors alloué d'abord l'espace disponible à /dev/sda2 où se situe ma partition root/principale

![gparted]({{site.url}}\assets\article\virtualBox\gparted.JPG)



2) Ensuite, je vais pouvoir alloué l'espace à /dev/sda5 qui est ma partition principale

![gparted2]({{site.url}}\assets\article\virtualBox\gparted2.JPG)



3) Il ne reste alors plus qu'à appliquer les opérations

![gp3]({{site.url}}\assets\article\virtualBox\gparted.JPG)



## 3) Vérification

On peut vérifier que l'opération a fonctionné avec l'utilitaire *lsblk*

![virtualbox_resize_verif]({{site.url}}\assets\article\virtualBox\virtualbox_resize_verif.JPG) 



# Sources

Liste des sources utilisées :

[](https://www.malekal.com/virtualbox-reduire-augmenter-la-taille-du-disque-virtuel/)

[https://linuxhint.com/increase-virtualbox-disk-size/](https://linuxhint.com/increase-virtualbox-disk-size/)





