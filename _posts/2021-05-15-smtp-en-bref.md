---
layout: post
title:  "SMTP en bref"
date:   2021-05-15 
categories: réseau 
tags: smtp protocole
---

Résumé en bref du protocole SMTP ainsi que la présentation de quelques outils(dig, telnet)

## Description

**SMTP** est un protocole de communication pour l'envoi et le transfert d'email. 



## Fonctionnement

### Avec état

C'est un protocole avec état car il garde la connexion active. Lors de l'envoi d'un email, on établit la connexion avec le serveur puis on envoie les informations(FROM TO, RCPT TO) puis les données.



### Ports utilisés

Le port utilisé entre 2 serveurs relais SMPT est le port25 (TCP)

Le port utilisé pour l'envoi est le port 581(TCP)

Exemple de communication avec relais



### Communication

Lors d'un échange SMTP,plusieurs acteurs entre en jeu :

- MUA (Mail User Agent) de envoyeur

Permet à l'utilisateur d'envoyer des emails, par exemple Thunderbird ou MS Outlook.

Il utilise le port TCP 587 pour envoyer l'email au MSA.

- MSA(Mail Submission Agent).

Le MSA est un intermédiaire entre le MUA et le MTA.

Il vérifie notamment que l'utilisateur est authentifié, que l'email est syntaxiquement correct puis délègue la suite au MTA

- MTA (Mail Transfert Agent) - envoyeur

Si le nom de domaine est différent de celui du MTA, il fait une requête DNS pour déterminer l'adresse IP du serveur mail. Le serveur DNS lui renvoie une liste des MX(Mail eXchanger) enregistrés.

Le MTA utilise ensuite le port 25/TCP pour transférer l'email au MTA destinataire.

- MTA destinataire

Le MTA destinataire va recevoir l'email et le stocker dans la mailbox du destinataire, 



- MUA destinataire

Le destinataire récupère l'email via son MUA avec un protocole comme IMAP ou POP3



## Commandes

Les principales commandes utilisés pour l'envoi d'un email sont :

| Commandes | Description                                                 |      |
| --------- | ----------------------------------------------------------- | ---- |
| EHLO      | Envoyé par le client pour prendre contact avec le serveur   |      |
| MAIL FROM | Spécifie l'origine de l'email                               |      |
| RCPT TO   | Spécifie le destinataire                                    |      |
| DATA      | Envoyer les données de l'email, contient notamment le sujet |      |
| QUIT      | Envoyé par le client pour mettre fin à la connexion         |      |



## Pour aller plus loin...

### Outils

Vous pouvez obtenir une liste des MX enregistrés avec la commande dig

```
dig -t any <domaine>
```

![dig-exemples]({{site.url_complet}}\assets\article\reseau\SMTP\dig-exemples.JPG)

```bash
telnet <serveur mx> 25
```

Telnet permet d'établir la connexion avec le serveur mx.

En rouge, les commandes que j'ai écrites.

## ![dig-telnet-exemple]({{site.url_complet}}\assets\article\reseau\SMTP\dig-telnet-exemple.png)

### Email forgé

Dans Data, on spécifie un destinataire. Celui-ci peut être différent du MAIL FROM pris en compte par le MTA pour le transfert.

Ainsi, il ne faut pas se fier à l'en-tête du mail que le client voit, car celui-ci ne garantir rien sur identité de l'envoyeur.



### Simuler un serveur SMTP

En java, on peut simuler un serveur SMPT, par exemple pour faire des tests avec MockMock :

[https://github.com/tweakers/MockMock](https://github.com/tweakers/MockMock).



Un exemple complet se trouve sur mon repôt git : [https://github.com/rya-sge/smtp](https://github.com/rya-sge/smtp)

## Sources 

- RFC du protocole : [https://datatracker.ietf.org/doc/html/rfc5321](https://datatracker.ietf.org/doc/html/rfc5321)
- Article très complet sur le protocole SMTP : [http://projet.eu.org/pedago/sin/ISN/8-protocole_SMTP.pdf]( http://projet.eu.org/pedago/sin/ISN/8-protocole_SMTP.pdf)
- Articles sur les protocoles avec états/sans états : [https://www.thegeeksclan.com/stateful-and-stateless-protocols/]( https://www.thegeeksclan.com/stateful-and-stateless-protocols/)
- Man page de dig : [https://linux.die.net/man/1/dig]( https://linux.die.net/man/1/dig)
- [https://www.malekal.com/comment-fonctionne-les-serveurs-de-mails-theorie/](https://www.malekal.com/comment-fonctionne-les-serveurs-de-mails-theorie/)
- Cours RES enseigné à l'HEIG-VD en 2021
