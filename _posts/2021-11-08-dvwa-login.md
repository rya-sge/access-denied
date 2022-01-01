---
layout: post
title:  "DVWA - Login & Hydra"
date:   2021-11-13
last-update: 
categories: securite
tags: hydra pentesting login dbwa
image: /assets/article/pentest/dvwa/brute-force/login-page.PNG
description: Pourquoi est-il important d'employer des mots de passes forts ? Illustration à travers l'exemple de 
l'application vulnérable DVWA.
---

> Cet article a pour objectif de sensibiliser le lecteur à l'importance des mots de passes fort pour protéger l'accès aux applications. 
>
> L'exemple été réalisé sur l'application web vulnérable DVWA en local.  Il consiste en un write-up d'une attaque par brute-force sur une page web de login en employant le logiciel **Hydra**



## Installation DVWA

Vous pouvez récupérer une image docker de DVWA à l'adresse suivante :

[https://hub.docker.com/r/vulnerables/web-dvwa](https://hub.docker.com/r/vulnerables/web-dvwa)

- Pour la lancer :

```bash
docker run --rm -it -p 80:80 vulnerables/web-dvwa
```

- Credentials par défaut :
  - Username: admin
  - Password: password

## Phase de reconnaissance

### Page de login

![login-page]({{site.url_complet}}/assets/article/pentest/dvwa/brute-force/login-page.PNG)



### Passage des paramètres 

En regardant le code source la page, on peut voir que les paramètres sont passés par GET, ce qui nous sera utile pour configurer Hydra ainsi que les noms des champs : `username` et `password`



![form-code-source]({{site.url_complet}}/assets/article/pentest/dvwa/brute-force/form-code-source.PNG)

### Récupérer le cookie de session

DVWA nécessite d'être connecté pour pouvoir être utilisé. Il faut alors récupérer le cookie de session, que l'on trouve dans la partie Storage/Cookies du navigateur.

On peut également observer la présence d'un second cookie indiquant le niveau de sécurité de l'application, ici `low`

![cookie-session]({{site.url_complet}}/assets/article/pentest/dvwa/brute-force/cookie-session.PNG)



## Attaque

Maintenant, nous avons toutes les informations permettant de lancer une attaque par brute-force.

```bash
hydra 0.0.0.0 -l admin -P rockyou.txt http-get-form "/vulnerabilities/brute/:username=^USER^&password=^PASS^&Login=Login:F=Username and/or password incorrect.:H=Cookie:security=low; PHPSESSID=1bnn5p1207ll8vphurqbel9r97"
```

### Explication

- -l admin

On part du principe que l'utilisateur cible est admin, mais on pourrait aussi faire du brute-force dessus.

- -P rockyou.txt

Indique le dictionnaire à utiliser pour cracker le mot de passe

- http-get-form

Inique la méthode de transmission des paramètres. Comme vu durant la phase de reconnaissance, les paramètres sont passés par GET

- Pour la string
  - ^USER^ indique à Hydra qu'il doit remplacer par le user, ici admin
  - ^PASS^ indique à Hydra qu'il doit remplacer par le password. Vu que nous avons indiqué un dictionnaire, Hydra va remplacer par les mots du dictionnaire
  - `F=Username and/or password incorrect.`message qui sera affiché par la page en cas de login incorrect. 
  - `H=Cookie:security=low; PHPSESSID=1bnn5p1207ll8vphurqbel9r97"`permet d'indiquer des headers.



### Résultats

![hydra-result]({{site.url_complet}}/assets/article/pentest/dvwa/brute-force/hydra-result.PNG)

Le mot de passe trouvé est `password`

## Sources

- Installation docker : [https://hub.docker.com/r/vulnerables/web-dvwa](https://hub.docker.com/r/vulnerables/web-dvwa)
- Tutoriels Kali sur Hydra : [https://www.kali-linux.fr/hacking/tutohydrabruteforce](https://www.kali-linux.fr/hacking/tutohydrabruteforce)
- Autres write-up :
  -  [https://securitytutorials.co.uk/brute-forcing-web-logins-with-dvwa/](https://securitytutorials.co.uk/brute-forcing-web-logins-with-dvwa/)

