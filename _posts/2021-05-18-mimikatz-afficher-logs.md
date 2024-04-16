---
layout: post
title:  "Mimikatz - afficher les logs"
date:   2021-05-18 
categories: security
tags: mimikatz log 
Auteur: rya-sge
description: Afficher les logs de Mimikatz sur Windows grâce à l'event viewer
image: /assets/article/outil-securite/mimikatz/windows-policiy-kernel_1.JPG
---

Cet exercice a été réalisé sur une machine windows dans une VM.

La 1ère étape montre comment installer mimikatz sous windows pour réaliser les tests

La 2ème étape montre comment afficher les logs générés par mimikatz.

### 1) Installation de mimikatz sous Windows

Depuis votre machine hôte, aller dans release et prend mimikatz_trunk (pas les source code)

Lien : [https://github.com/gentilkiwi/mimikatz/releases/tag/2.2.0-20210512](https://github.com/gentilkiwi/mimikatz/releases/tag/2.2.0-20210512)

--

![wndows-version]({{site.url_complet}}/assets/article/outil-securite/mimikatz/wndows-version.JPG)

2) Activer un dossier partagé sur votre VM et y déposer le dossier mimikatz_trunk

![shared-folder]({{site.url_complet}}/assets/article/outil-securite/mimikatz/shared-folder.JPG)

3) Dans votre VM, exécuter mimikatz x64 en tant qu**'administrateur**

![mimikatz-launch]({{site.url_complet}}/assets/article/outil-securite/mimikatz/mimikatz-launch.JPG)



4) Configurer mimikatz avec le privilège debug  et dumper les hashs avec sekurlsa

Attention : il faut écrire sekurlsa avec un k

![mimikatz-config]({{site.url_complet}}/assets/article/outil-securite/mimikatz/mimikatz-config.JPG)



Remarques : Pour activer le privilège debug, il faut avoir exécuter mimikatz en tant qu'administrateur lors du point précédent



5) Résultat :

Voici une partie des résultats obtenus

![mimikatz-logon-passwords]({{site.url_complet}}/assets/article/outil-securite/mimikatz/mimikatz-logon-passwords.JPG)



### **Activer les logs sur mimikatz**

1) Mettre secpol.msc dans  la barre de recherche et le lancer

![secpol.msc]({{site.url_complet}}/assets/article/outil-securite/mimikatz/secpol.msc.JPG)

2)  Aller dans Advanced Audit Policy, sous Object Access, cliquer sur Audit kernel Object![windows-policiy-kernel_1]({{site.url_complet}}/assets/article/outil-securite/mimikatz/windows-policiy-kernel_1.JPG)



3) Cocher success

![windows-policy-kernel-2]({{site.url_complet}}/assets/article/outil-securite/mimikatz/windows-policy-kernel-2.JPG)

4) Exécuter à nouveau mimikatz en tant qu'administrateur, remettez le privilège debug et lancer sekurlsa afin de générer des logs.

5) Aller dans l'*event viewer*, éventuellement faites un *refresh*.

![event-viewer-refresh]({{site.url_complet}}/assets/article/outil-securite/mimikatz/event-viewer-refresh.JPG)

6) Toujours dans l'*event viewer*, aller sur les événements avec la catégorie Kernel Object

![windows-logs-kernel]({{site.url_complet}}/assets/article/outil-securite/mimikatz/windows-logs-kernel.JPG)



6) Sélectionner et afficher

- Ici on peut voir que le log indique également  sous Process Name le nom de l'exécutable, ici mimikatz.exe 
- On peut également voir le nom de l'objet Lsass.exe

![windows-event-mimikatz]({{site.url_complet}}/assets/article/outil-securite/mimikatz/windows-event-mimikatz.JPG)

### Désavantage 

-En activant les logs sur les *kernels objects*, Il y a aussi des logs générés lorsqu'on se connecte normalement à la session....

### Sources

- Cours SOS enseigné à l'HEIG-VD en 2021