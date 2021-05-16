---
layout: post
title:  "Metasploit - migration avec keylogger"
date:   2021-05-16 
categories: metasploit securité keylogg
tags: smtp réseau protocole
---

Utilisation de la commande migrate sur une session meterpreter puis utilisation d'un keylogger.

Attention : Cet article est publié à titre informatif, il a été réalisé dans un réseau en local à l'aide de machine virtuelle.

## Migrate

Une fois que vous avez une commande meterpreter sur la machine "cible" vous pouvez migrer dans un processus afin :

- D'avoir des droits supplémentaires
- De pouvoir persister sur la machine cible au-delà de la session meterpreter et éviter la détection

1) Il faut d'abord lister tout les processus :

```
 ps -a
```

Ensuite, on peut choisir le processus au fonction de ce qu'on a envie de réaliser.

- Par exemple, le processus svchost.exe tourne régulièrement en arrière plan et est par conséquent discret
- Pour un maximum de privilège, vous pouvez prendre un processus de l'utilisateur NT AUTHORITY\SYSTEM, qui aura alors les droits système

Dans cet article, j'ai choisi internet explorer afin de pouvoir récupérer les entrées de l'utilisateur(Key logger)

![migrate]({{site.url}}\assets\article\outil-securite\metasploit\processus.png)



La commande migrate va permet de migrer le processus :

```
migrate PID
```

les commandes getpid et getuid permettent d'afficher le pid courant ainsi que l'utilisateur. Vous pouvez ainsi vérifier le résultat de la commande migrate

```
getpid
getuid
```

![migrate]({{site.url}}\assets\article\outil-securite\metasploit\migrate.png)



## KeyLogger

On peut ensuite lancer keyscan_start qui va sniffer les entrées du clavier.

![keyscan_start]({{site.url}}\assets\article\outil-securite\metasploit\keyscan_start.JPG)



On peut alors afficher le résultat obtenu

![keyscan_dump]({{site.url}}\assets\article\outil-securite\metasploit\keyscan_dump.JPG)



## Sources 

- Meterpreter liste de commandes : [https://www.offensive-security.com/metasploit-unleashed/meterpreter-basics/](https://www.offensive-security.com/metasploit-unleashed/meterpreter-basics/)

- Pour les privilèges windows : [https://www.malekal.com/utilisateur-autorite-nt/](https://www.malekal.com/utilisateur-autorite-nt/)

- techniques-de-post-exploitation : [https://adminsys-dev.com/securite/pentest/techniques-de-post-exploitation](https://adminsys-dev.com/securite/pentest/techniques-de-post-exploitation)

- USING A KEYLOGGER WITH METASPLOIT  : [https://www.offensive-security.com/metasploit-unleashed/keylogging/](https://www.offensive-security.com/metasploit-unleashed/keylogging/)

- Scanner SMB auxliary Modules : [https://www.offensive-security.com/metasploit-unleashed/scanner-smb-auxiliary-modules/](https://www.offensive-security.com/metasploit-unleashed/scanner-smb-auxiliary-modules/)