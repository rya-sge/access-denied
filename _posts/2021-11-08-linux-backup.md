---
layout: post
title:  "Réaliser un backup sous Linux"
date:   2021-11-05
last-update: 
categories: linux
tags: backup parted
description: Cet article présente la réalisation d'un backup "fait maison" sous le système d'exploitation
image: /assets/linux/sauvegarde/8-df.png
---

Cet article présente la réalisation d'un système de backup "fait maison" sur une machine virtuelle vmware tournant sur le système d'exploitation *Ubuntu* 18.04.6 *LTS* 



## Etat du système

1) Tout d'abord on peut afficher la liste des disques et partitions avec la commande  find dev/sd*

- Les disques sont représentés par des lettres (a, b...)
- Les partitions sont représentés par des numéros(1, 2, 3....)
- sd pour  disque SCSI (selon l'ID SCSI) 
- hd pour  les disques sur le contrôleur IDE primaire 

![1-find]({{site.url_complet}}/assets/linux/sauvegarde/1-find.PNG)



Source : https://www.debian.org/releases/wheezy/amd64/apcs04.html.fr

2) Pour obtenir plus d'informations, on peut :

- afficher la liste des partitions visible et leurs informations  : lsblk -o

  ![2-lsblk]({{site.url_complet}}/assets/linux/sauvegarde/2-lsblk.PNG)

-  afficher la liste des partitions montés on peut utiliser la commande mount

![2-b-mount]({{site.url_complet}}/assets/sauvegarde/2-b-mount.PNG)

### Installer le back-up

1) On peut plugger un nouveau disque avec vmware :

2) On peut alors constater l'apparition d'un nouveau disque /dev/sdb avec la commande vue précédemment : `find /dev/sd*`

![4-find-sdb]({{site.url_complet}}/assets/linux/sauvegarde/4-find-sdb.png)

3) avec `parted`

- sudo parted sdb
  - `print` pour afficher les partitions existantes

  - Création d'une table de partition, de type msdos(Master Boot Record) : `mklabel msdos`

  - `print free` pour afficher la table de partition

- Affichage lsblk

  ![6-b-lsblk]({{site.url_complet}}/assets/linux/sauvegarde/6-b-lsblk.png)

- Commande `mkpart` pour créer les partitions

  - start : début
  - end : fin

```bash
mkpart [part-type name fs-type] start end
```

Résultat avec 2 partitions créées :

![6-print-free]({{site.url_complet}}/assets/linux/sauvegarde/6-print-free.PNG)

4) Après formatage, on montage les partitions sur /mnt/backup1 et /nt/backup2

```
sudo mount /dev/sdb1 /mnt/backup1
sudo mount /dev/sdb2 /mnt/backup2
```

![7-mount]({{site.url_complet}}/assets/linux/sauvegarde/7-mount.png)

5) On obtient ensuite la quantité d'espace libre sur chacun des filestyme avec la commande `df -h`

![8-df]({{site.url_complet}}/assets/linux/sauvegarde/8-df.png)



## Source 

- [www.tecmint.com - 8 Linux ‘Parted’ Commands to Create, Resize and Rescue Disk Partitions](https://www.tecmint.com/parted-command-to-create-resize-rescue-linux-disk-partitions/)

Les ressources suivantes permettent d'accéder au MAN en ligne et ont été utilisée pour le labo.

- Manuel tar en ligne : [http://manpagesfr.free.fr/man/man1/tar.1.html]( http://manpagesfr.free.fr/man/man1/tar.1.html)
- Manuel zip en ligne : [http://www.delafond.org/traducmanfr/man/man1/zip.1.html](http://www.delafond.org/traducmanfr/man/man1/zip.1.html)
- Manuel unzip : [https://linux.die.net/man/1                                    /unzip](https://linux.die.net/man/1/unzip)

