---
layout: post
title:  "WAH - Attacking the Application Server"
date:   2022-02-03
categories: securite reseau web
tags: application logique sql thread wah
description: Questions & Réponses du chapitre 11, Attacking Application Logic, du livre The Web Application Hacker's Handbook
image: 
---



> Cet article contient mes réponses personnelles aux questions présentes dans le chapitre 18, *Attacking the Application Server*, du livre *The Web Application Hacker's Handbook*
>
> L'article a pour objectif de sensibiliser le lecteurs aux différentes vulnérabilités existantes afin qu'il puisse s'en prémunir.

Le chapitre en question traite des points suivant :

- *credentials* par défaut (p.670)
- Les applications Oracle (p.676)
  - Oracle Application Server
  - PL/SQL *gateway*
- *Directory Listings* (p.677)
- *WebDav* (p.679)
- *The Application Server as a Proxy* (p.682)
- *VirtualHost* mal configuré (p.683)
- Faille dans les framework d'application web (p.685)
- Vulnérabilité dans la gestion de mémoire / *Memory Management Vulnerabilities* (p.687)

### Question 1

*Under what circumstances does a web server display a directory listing?*

**Réponse**

L'application ne protège pas ses répertoires, par exemple avec un fichier `.htaccess` et le répertoire peut par conséquent être listé en tapant le chemin du répertoire sur l'url.

Exemple `mon-site.com/images/` qui affichera la liste des images présentes.

**Source** 

*Directory Listings*, page 677 du livre

### Question 2

*What are WebDAV methods used for, and why might they be dangerous?*

**Réponse**

Petit rappel sur WebDAV : C'est une extension du protocole HTTP regroupant une collection de méthode HTTP. Son nom complet est *Web-based Distributed Authoring and Versioning*. WebDav ajoute de nombreuses méthodes HTTP permettant de manipuler des fichiers sur un serveur web comme en ajouter des nouveaux (PUT), les supprimer (DELETE) ou récupérer de l'information (PROPFIND)

Un attaquant pourrait par exemple utiliser la méthode PUT pour upload un fichier malveillant sur le serveur lui permettant d'avoir une backdoor dessus.

Ces méthodes peuvent être utilisées comme vecteur d'attaque pour exploiter les vulnérabilités des systèmes d'exploitation via un serveur IIS.

**Sources** 

- *WebDAV Methods*, page 679 du livre
- [kb.synology.com - WebDAV Server](https://kb.synology.com/fr-fr/DSM/help/WebDAVServer/webdav_server?version=6)

### Question 3

*How can you exploit a web server that is configured to act as a web proxy?*

**Réponse**

- SI celui-ci autorise les requêtes vers internet,  un attaquant pourrait l'utiliser pour attaquer des sites tiers où les requêtes auront comme origine le serveur web mal configuré.

- Dans le cas où les requêtes vers internet sont bloquées, on pourrait toujours tenter d'utiliser le serveur proxy pour accéder à des serveurs webs à l'intérieur du réseau qui sont inaccessible depuis l'extérieur ou pour atteindre des services web sur le serveur lui-même.

**Sources** 

- *The Application Server as a Proxy*, page 682 du livre

### Question 4

*What is the Oracle PL/SQL Exclusion List, and how can it be bypassed?*



**Réponse**

La *gateway* Pl/SQL acte comme un serveur proxy qui prend les requêtes de l'utilisateur et les passent au serveur de base de donnée où elles sont exécutées,



La `Oracle PL/SQL Exclusion List` contient une liste noir de pattern permettant de filtrer les requêtes. Elle permet notamment de bloquer  l'accès aux packages dont le nom commencerait avec certaines expressions comme `OWA` et `SYS`

On peut la contourner de plusieurs façons, en voici deux :

- en ajoutant un espace blanc (nouvelle ligne, espace ou tab) avant le nom du package

Exemple issu du livre : `https://wahh-app.com/pls/dad/%0ASYS.package.procedure`

- En entourant une expression bloquée par des guillemets double

Exemple issu du livre : `https://wahh-app.com/pls/dad/"SYS".package.procedure`

**Sources** 

- *Oracle PL/SQL Exclusion List Bypasses* , page 692 et 693 du livre
- [kennel209.gitbooks.io/owasp-testing-guide-v4 - oracle_testing.html](https://kennel209.gitbooks.io/owasp-testing-guide-v4/content/en/web_application_security_testing/oracle_testing.html)
- [https://en.wikipedia.org/wiki/PL/SQL](https://en.wikipedia.org/wiki/PL/SQL)



### Question 5

*If a web server allows access to its functionality over both HTTP and*
*HTTPS, are there any advantages to using one protocol over the other*
*when you are probing for vulnerabilities?*

**Réponse**

- Les outils de détection d'intrusion pourraient fonctionner différemment entre la version HTTP et HTTPS.
- Les attaques automatisées pourraient être plus rapide avec la version HTTP car il n'y a pas la sécurisation de la connexion.



## Sources 

- STUTTARD, Dafydd, PINTO Marcus , 2018. *The Web Application Hacker's Handbook: Finding and Exploiting Security Flaws*. 2e édition. Wiley Publishing
- Obtenir  le livre en ligne : [https://www.oreilly.com/library/view/the-oracle-hackers/9780470080221/](https://www.oreilly.com/library/view/the-oracle-hackers/9780470080221/)
- Github avec les réponses aux questions : [https://github.com/six2dez/wahh_extras/blob/master/answers.md](https://github.com/six2dez/wahh_extras/blob/master/answers.md)