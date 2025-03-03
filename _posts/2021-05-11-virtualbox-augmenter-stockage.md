---
layout: post
title:  VirtualBox - augmenter l'espace de stockage
date:   2021-05-11
last-update: 2021-13-10
categories: programmation
tags: virtualbox virtualisation
description: Cet article est un tutoriel pour augmenter l'espace de stockage d'une machine virtuelle avec le logiciel de virtualisation VirtualBox. 
image: /assets/article/virtualBox/gparted.JPG
---

Cet article est un tutoriel pour augmenter l'espace de stockage d'une machine virtuelle avec le logiciel de virtualisation **VirtualBox**. 

- L'ensemble des opérations effectuées concernent une VM Ubuntu (Ubuntu 20.04.2 LTS).  
- VirtualBox était installé sur le système d'exploitation Windows 10 Professional, 64 bits.

### Mise en place

Pour  effectuer cette opération, il faut avoir préalablement éteint votre espace de stockage.

De plus, pensez à sauvegarder vos fichiers de la VM sur votre disque principal car il y a un risque que l'opération puisse échouer, rendant le disque et son contenu illisible.

### Opération

#### 1) Augmenter taille vdi

 Fichier -> Gestionnaire de média -> sélectionner le disque vdi que vous voulez augmenter et augmenter sa taille avec le curseur![stockage]({{site.url_complet}}/assets/article/virtualBox/gparted_stockage.png)



### 2) Appliquer le redimensionnement 

#### a) Premier essai -> pas concluant

De nombreux tutoriels proposent d'utiliser l'utilitaire VBoxManage.exe avec la commande *modifyhd*. Cela n'a pas marché chez moi !!!

je mets ici les commandes que j'ai essayé à titre **indicatif**

![vb_resize]({{site.url_complet}}/assets/article/virtualBox/virtualbox_resize.JPG)

C:\"Program Files"\Oracle\VirtualBox\VBoxManage.exe VBoxManage modifyhd SLO2.vdi --resize 25000.

-L'exécutable lancé est VBoxManage.exe

-25000 correspond à la taille en MB du nouveau disque.

Source : [https://www.malekal.com/virtualbox-reduire-augmenter-la-taille-du-disque-virtuel/](https://www.malekal.com/virtualbox-reduire-augmenter-la-taille-du-disque-virtuel/)



#### b) 2ème essai -> concluant

 Pour appliquer le redimensionnement à ma partition sur ubuntu, j'ai suivi ce tutoriel :

[https://linuxhint.com/increase-virtualbox-disk-size/](https://linuxhint.com/increase-virtualbox-disk-size/)

Celui-ci propose d'utiliser GNOME partition Editor : [https://gparted.org/download.php](https://gparted.org/download.php)

Il faut ajouter l'ISO comme lecteur optique dans les paramètres de la VM :

![gparted-add]({{site.url_complet}}/assets/article/virtualBox/gparted-add.PNG)

Après avoir démarré ma VM sur l'iso du logiciel, voici les opérations que j'ai effectuées :



1) On peut voir ici que j'ai 9 GO d'espace libre, correspond à l'augmentation du disque dur

Je vais alors allouer d'abord l'espace disponible à /dev/sda2 où se situe ma partition root/principale

![gparted]({{site.url_complet}}/assets/article/virtualBox/gparted.JPG)





2) Ensuite, je vais pouvoir allouer l'espace à /dev/sda5 qui est ma partition principale.

![gparted2]({{site.url_complet}}/assets/article/virtualBox/gparted2.JPG)





3) Il ne reste alors plus qu'à appliquer les opérations.

![gp3]({{site.url_complet}}/assets/article/virtualBox/gparted0.JPG)



### 3) Vérification

On peut vérifier que l'opération a fonctionné avec l'utilitaire *lsblk*

![virtualbox_resize_verif]({{site.url_complet}}/assets/article/virtualBox/virtualbox_resize_verif.JPG) 



## 4) Avec Kali

Avec Kali, j'ai eu comme problème que sda2 se trouvait entre sda1, la partition que je voulais agrandir et mon espace libre.

![gparted-kali1]({{site.url_complet}}/assets/article/virtualBox/gparted-kali1.PNG)

Comme solution, il faut supprimer sda2, agrandir sda1 et refaire sda2(partition de swap)

Source _: [https://qastack.fr/ubuntu/175174/why-cant-i-increase-the-size-of-sda1-using-gparted](https://qastack.fr/ubuntu/175174/why-cant-i-increase-the-size-of-sda1-using-gparted)

### Sources

- [https://www.malekal.com/virtualbox-reduire-augmenter-la-taille-du-disque-virtuel/](https://www.malekal.com/virtualbox-reduire-augmenter-la-taille-du-disque-virtuel/)
- [https://linuxhint.com/increase-virtualbox-disk-size/](https://linuxhint.com/increase-virtualbox-disk-size/)
- [https://qastack.fr/ubuntu/175174/why-cant-i-increase-the-size-of-sda1-using-gparted](https://qastack.fr/ubuntu/175174/why-cant-i-increase-the-size-of-sda1-using-gparted)





