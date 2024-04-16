---
layout: post
title:  "La sécurité du protocole Telnet"
date:   2022-02-05
last-update: 
categories: security
tags: telnet pentesting 
image: /assets/article/pentest/telnet/telnet-cov.PNG
description: Cet article présente un test d'intrusion sur le protocole telnet afin de sensibiliser le lecteur aux différentes vulnérabilités possibles pour qu'il s'en prémunisse.
---



> Cet article présente un test d'intrusion sur le protocole telnet afin de sensibiliser le lecteur aux différentes vulnérabilités possibles pour qu'il s'en prémunisse.
>
> Le protocole telnet est connu pour être moins sécurisé que son remplaçant, le protocole SSH, qui lui est préférable.
>
> Tous les exemples montrés sur cet article l'ont été sur des machines de laboratoires.

### Phase de reconnaissance

La phase de reconnaissance permet de trouver un certains nombre de ports ouverts sur la machine

```
nmap -O <IP>
```

![recon]({{site.url_complet}}/assets/article/pentest/telnet/recon.PNG)



Intéressons-nous au port telnet...

### telnet

Pour se connecter au port

```
telnet <IP machine> 23
```

Une interface *metasploit* apparait. Après quelques essais, le nom d'utilisateur `user` avec le mot de passe `user` permet de se connecter.

![telnet]({{site.url_complet}}/assets/article/pentest/telnet/telnet.PNG)



Une fois connecté, on peut se balader dans l'arborescence pour y trouver des fichiers sensibles

![telnet]({{site.url_complet}}/assets/article/pentest/telnet/arborescence.PNG)

## Conclusion

Dans le cas présent, une interface *metasploit* était accessible à travers le protocole telnet permettant ensuite d'accéder à l'arborescence. A la place de **telnet**, il aurait été préférable d'utiliser le protocole **SSH** qui aurait alors protégé cette interface grâce aux mécanismes d'authentification qu'il implémente.

## Source

[adminsys-dev.com - Test de pénétration part 2 L'exploitation](https://adminsys-dev.com/securite/pentest/test-de-penetration-part-2-lexploitation)