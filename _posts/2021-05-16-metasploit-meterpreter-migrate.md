---
layout: post
title:  "Metasploit - Elévation de privilège avec migrate"
date:   2021-05-16 
categories: securite
tags: metasploit meterpreter keylogger migrate
description: Cet article présente la commande Meterpreter migrate du logiciel  Metasploit. Celle-ci permet à un attaquant d'élever ses privilèges sur la machine après qu'il ait pu obtenir dessus une session meterpreter.
image: \assets\article\outil-securite\metasploit\migrate.png
---

Cet article présente une des fonctionnalités du logiciel [Metasploit](https://www.metasploit.com) : la commande Meterpreter *migrate*. Celle-ci permet à un attaquant d'élever ses privilèges sur la machine après qu'il ait pu obtenir dessus une session *meterpreter*. Cette opération peut lui permettre par exemple d'utiliser un keylogger.



>  Attention : Cet article est publié à titre informatif, il a été réalisé dans un **réseau en local à l'aide de machine virtuelle.** 



## Migrate

Une fois que l'attaquant a une commande meterpreter sur la machine "cible", il est capable de migrer dans un processus afin :

- D'avoir des droits supplémentaires
- De pouvoir persister sur la machine cible au-delà de la session meterpreter et éviter la détection

1) Il lui faut d'abord lister tous les processus :

```
 ps -a
```

Ensuite, il peut choisir le processus en fonction de ce qu'il a envie de réaliser.

- Par exemple, le processus svchost.exe tourne régulièrement en arrière-plan et est par conséquent discret
- Pour un maximum de privilège, il peut prendre un processus de l'utilisateur NT AUTHORITY\SYSTEM, qui aura alors les droits systèmes.

Pour l'exercice, j'ai choisi internet explorer afin de pouvoir montrer comment il est possible de récupérer les entrées de l'utilisateur (Key logger)

![migrate]({{site.url_complet}}\assets\article\outil-securite\metasploit\processus.png)



La commande *migrate* va permet de migrer le processus :

```bash
migrate PID
```

les commandes getpid et getuid permettent d'afficher le pid courant ainsi que l'utilisateur. On peut les utiliser pour vérifier le résultat de la commande *migrate*.

```bash
getpid
getuid
```

![migrate]({{site.url_complet}}\assets\article\outil-securite\metasploit\migrate.png)



## KeyLogger

Cette élévation de privilège lui permet de lancer de nouvelles attaques. Par exemple, il peut lancer un keylogger avec la commande  keyscan_start qui va sniffer les entrées du clavier.

![keyscan_start]({{site.url_complet}}\assets\article\outil-securite\metasploit\keyscan_start.JPG)

Puis  afficher le résultat obtenu.

![keyscan_dump]({{site.url_complet}}\assets\article\outil-securite\metasploit\keyscan_dump.JPG)



## Sources 

- Meterpreter liste de commandes : [https://www.offensive-security.com/metasploit-unleashed/meterpreter-basics/](https://www.offensive-security.com/metasploit-unleashed/meterpreter-basics/)
- Pour les privilèges windows : [https://www.malekal.com/utilisateur-autorite-nt/](https://www.malekal.com/utilisateur-autorite-nt/)
- techniques-de-post-exploitation : [https://adminsys-dev.com/securite/pentest/techniques-de-post-exploitation](https://adminsys-dev.com/securite/pentest/techniques-de-post-exploitation)
- USING A KEYLOGGER WITH METASPLOIT  : [https://www.offensive-security.com/metasploit-unleashed/keylogging/](https://www.offensive-security.com/metasploit-unleashed/keylogging/)
- Scanner SMB auxliary Modules : [https://www.offensive-security.com/metasploit-unleashed/scanner-smb-auxiliary-modules/](https://www.offensive-security.com/metasploit-unleashed/scanner-smb-auxiliary-modules/)
- Cours SOS enseigné à l'HEIG-VD en 2021
