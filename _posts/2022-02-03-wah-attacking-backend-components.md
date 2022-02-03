---
layout: post
title:  "WAH - Attacking Back-End Components"
date:   2022-02-03
categories: securite reseau web
tags: web backend component lfi rfi hpi hpp smtp
description: Questions & Réponses du chapitre 10 du livre The Web Application Hacker's Handbook
image: 
---

> Cet article contient mes réponses personnelles aux questions présentes dans le chapitre 10, *Attacking Back-End Components* du livre *The Web Application Hacker's Handbook*.
>
> L'article a pour objectif de sensibiliser le lecteur aux différentes vulnérabilités existantes afin qu'il puisse s'en prémunir.

Le chapitre  traite des attaques suivantes :

- Injection de commande OS / *Injecting OS Commands* (p.358)
- *Path Traversal Vulnerabilities* (p.368)
- Inclusion de fichier / *File Inclusion Vulnerabilities* (LFI & RFI) (p.381)
- *Injecting XML External Entities* (p.384)
- *Injecting into SOAP Services*  (p.386)
- Injecting into Back-end HTTP Requests (p.426)
  - Redirection HTTP côté serveur / *Server-side HTTP Redirection* (p.390)
  - *HTTP Parameter Injection* (HPI) (p.393)
  - *HTTP Parameter Pollution* (HPP) (p.394)
- Injection dans les services mails (p.397)
  - Injection de commandes SMTP (*SMTP Command Injection*) (p.399)

A la fin du chapitre, une liste de questions permet de mieux comprendre les différentes attaques présentées.

### Question  1

*A network device provides a web-based interface for performing device*
*configuration. Why is this kind of functionality often vulnerable to OS*
*command injection attacks?*



**Solution** 

Il arrive que ces interfaces implémentent ces fonctionnalités sous la forme d'une entrée utilisateur qui sera reprise pour exécuter une commande. On peut dès lors y injecter des commandes malveillantes.



### Question 2

*You are testing the following URL:
http://wahh-app.com/home/statsmgr.aspx?country=US
Changing the value of the country parameter to foo results in this error
message:
Could not open file: D:\app\default\home\logs\foo.log (invalid file).
What steps could you take to attack the application?*



**Solution** 

Le fonctionnement côté serveur lorsqu'il traite la requête est vraisemblablement le suivant :

1) Extraction de la valeur du paramètre *country* de la *query string*

2) Ajouter la valeur du préfix à l'entrée utilisateur pour créer le chemin : Exemple : `D:\app\default\home\logs\` + `foo.log`

3) Ouvrir le fichier se trouvant au chemin crée au point 2.

4) Lire le fichier et retourner le contenu au client

Attaque :

On peut dès lors effectuer une attaque de type "Path Transversal". Cela consiste à parcourir l'arborescence en ajoutant `..\`(“dot-dot-slash) pour aller chercher des fichiers de configuration, mot de passes, etc.

Ex : `D:\app\default\home\logs\\..\\\..\\..\secret.txt`

 Pour contourner l'ajout de l'extension ".log", on peut terminer le nom du fichier en utilisant un `NULL byte`



**Source** 

- L'explication de la solution se trouve à la page 369 du livre.
- Laboratoire PortSwigger : [https://portswigger.net/web-security/file-path-traversal/lab-validate-file-extension-null-byte-bypass](https://portswigger.net/web-security/file-path-traversal/lab-validate-file-extension-null-byte-bypass)

### Question 3

3. *You are testing an AJAX application that sends data in XML format within*
*POST requests. What kind of vulnerability might enable you to read*
*arbitrary files from the server’s filesystem? What prerequisites must be*
*in place for your attack to succeed?*

**Solution**

L'application pourrait être vulnérable à l'attaque par injection  XXE pour `XML external entity`

Cela consiste pour un attaquant à soumettre une requête définissant une entité XML externe qui référence un fichier sur le système de fichier du serveur.

Exemple issu du livre page 365

```
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM “file:///windows/win.ini” > ]>
<Search><SearchTerm>&xxe;</SearchTerm></Search>
```

Les pré-requis sont les suivants :

- L'interpréteur XML de l'application supporte les entités externes
- La fonctionnalité de base prévoyait que l'application réponde au contenu XML de la requête par le contenu XML correspondant.

### Question 4

*You make the following request to an application that is running on the
ASP.NET platform:
POST /home.aspx?p=urlparam1&p=urlparam2 HTTP/1.1
Host: wahh-app.com
Cookie: p=cookieparam
Content-Type: application/x-www-form-urlencoded
Content-Length: 15
p=bodyparam
The application executes the following code:
String param = Request.Params[“p”];
What value does the param variable have?*

**Solution**

La valeur de la variable `param` correspond à toutes les fois où le paramètre "p" apparait. C'est-à-dire dans la *query* de l'url (urlparam1, urlparm2), dans les cookies ainsi que dans le body de la requête. On a par conséquent les valeurs suivantes : urlparam1, urlparam2, cookieparam et bodyparam

### Question 5

*Is HPP a prerequisite for HPI, or vice versa?*



**Solution**

HPI pour `HTTP parameter injection`  arrive quand un attaquant peut injecter des paramètres dans une requête qui seront ensuite exécuter par le serveur.

Une attaque HPP consiste à utiliser dans la même requête plusieurs fois le même paramètre.

Aucune des 2 attaques n'est un pré-requis pour l'autre même si une attaque HPI implique souvent une attaque HPP. Il existe de nombreux cas d'attaques HPP n'impliquant pas HPI.

**Réponse**

Solution : page 394 du livre

Autre sources : [owasp.org - Testing for HTTP Parameter Pollution](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/04-Testing_for_HTTP_Parameter_Pollution)

### Question 6

*An application contains a function that proxies requests to external domains
and returns the responses from those requests. To prevent server-side
redirection attacks from retrieving protected resources on the application’s
own web server, the application blocks requests targeting localhost or 127.0.0.1. How might you circumvent this defense to access resources
on the server?*

**Solution**

Il peut varier la représentation de l'adresse locale du serveur, par exemple :

- 127.1
- 127.000.0.1
- Une autre adresse du sous-réseau de classe A : 127.0.0.0
- Utiliser la représentation binaire ou octale de l'adresse locale.

### Question 7

*An application contains a function for user feedback. This allows the user*
*to supply their e-mail address, a message subject, and detailed comments.*
*The application sends an email to feedback@wahh-app.com, addressed*
*from the user’s email address, with the user-supplied subject line and*
*comments in the message body. Which of the following is a valid defense*
*against mail injection attacks?*
*(a) Disable mail relaying on the mail server.*
*(b) Hardcode the RCPT TO field with feedback@wahh-app.com.*
*(c) Validate that the user-supplied inputs do not contain any newlines or*
*other SMTP metacharacters.*

**Solution**

La meilleur solution est de vérifier l'entrée utilisateur, c'est par conséquent la réponse C

La réponse A n'empêche pas les `mail injection attacks`.

Pour la réponse B, elle est insuffisante car les autres champs du formulaire pourraient permettre d'injecter un second destinataire en ajoutant une seconde ligne RCPT TO

## Sources 

- STUTTARD, Dafydd, PINTO Marcus , 2018. *The Web Application Hacker's Handbook: Finding and Exploiting Security Flaws*. 2e édition. Wiley Publishing
- Obtenir le livre en ligne : [https://www.oreilly.com/library/view/the-oracle-hackers/9780470080221/](https://www.oreilly.com/library/view/the-oracle-hackers/9780470080221/)
- Github avec les réponses aux questions : [https://github.com/six2dez/wahh_extras/blob/master/answers.md](https://github.com/six2dez/wahh_extras/blob/master/answers.md)