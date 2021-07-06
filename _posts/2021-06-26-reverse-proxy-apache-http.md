---
layout: post
title:  Configurer un reverse proxy avec HTTP Apache
date:   2021-06-26 
categories: reseau
tags: apache proxy load-balancing reverse-proxy
description: Cet article présente la configuration d'un reverse proxy avec HTTP Apache, avec notammment le load balancing et les sticky sessions.
Auteur: rya-sge
image: /assets/article/reseau/reverse-proxy/schema-reverse-proxy.png
---



Cet article présente la configuration d'un *reverse proxy* avec *HTTP Apache*.

Il peut être intéressant d'en installer un pour les raisons suivantes:

- Sécurité : le *reverse proxy* peut cacher les serveurs backend aux yeux de l'utilisateur
- Performance : il est possible de répartir la charge entre différence serveur backend avec du *load balancing*
- scalabilité : il est plus facile d'ajouter de nouveaux serveurs backend à infrastructure.

### Schéma

Un *reverse proxy* se situe du côté du serveur. Voici un schéma pour mieux illustrer cela :

![schema-reverse-proxy]({{site.url_complet}}/assets/article/reseau/reverse-proxy/schema-reverse-proxy.png)

### Configuration de base

| Directive            | Explication                                                  |
| -------------------- | ------------------------------------------------------------ |
| ServerName           | Permet identifier un serveur, correspondant au nom de domaine voulue.[Lien doc apache](https://httpd.apache.org/docs/2.4/fr/mod/core.html#servername) |
| ProxyPreserveHost On | Va transmettre l0en host de la requête entrante, plutôt que d'utiliser celle fournit par ProxyPass [Lien doc apache](https://httpd.apache.org/docs/2.4/mod/mod_proxy.html#proxypreservehost) |
| ProxyPass            | Permet de rediriger les requête entrantes ers un serveur en backend ou vers cluster de server appelé Balancer. |
| ProxyPassReverse     | A normalement la même configuration que le proxyPass. Cette directive va réecrire les en-têtes des réponses envoyés par le serveur en backend. Cela permet de rendre le serveur backend anonyme auprès du client. |

Exemple :

```bash
<VirtualHost *:80>
	ServerName incroyable.ch
	
	ProxyPass "/api/animals" "http://172.17.0.3:3000/"
	ProxyPassReverse "/api/animals" "http:/172.17.0.3:3000"
	
	ProxyPass "/" "http://172.17.0.2:80/"
	ProxyPassReverse "/" "http:/172.17.0.2:80"
</VirtualHost>
```

Une explication plus détaillée, avec  des conteneurs Docker se trouve sur mon repo github à l'adresse suivante : [https://github.com/rya-sge/http-infra/tree/fb-apache-reverse-proxy](https://github.com/rya-sge/http-infra/tree/fb-apache-reverse-proxy)

**Load Balancing**

Le *load balancing* permet de redirigés les requêtes en direction de plusieurs serveurs en backend. cela permet d'ajouter de la redondance au proxy.

Par défaut la répartition des charges est du Round Robin Les requêtes sont répartis en fonction du nombre de requête traités par chacun des serveurs backend afin de répartir les requête

Ex :

```bash
<Proxy balancer://dynamic>
		BalancerMember 'http://<?php print "$DYNAMIC_APP_1"?>' 

		BalancerMember 'http://<?php print "$DYNAMIC_APP_2"?>' 			

</Proxy>

ProxyPreserveHost On

ProxyPass '/api/animals' "balancer://dynamic/"

ProxyPassReverse '/api/animals' "balancer://dynamic/"

ProxyPass '/' "balancer://static/"
ProxyPassReverse '/' "balancer://static/"
```

Une explication plus détaillée, avec  des conteneurs Docker se trouve sur mon repo github à l'adresse suivante : [http-infra/tree/load-balancing-multiple-server-nodes](https://github.com/rya-sge/http-infra/tree/load-balancing-multiple-server-nodes)

### Sticky Session / Round Robin

Les **sticky session** permettent d'assigner un serveur particulier à un client lors de sa 1ère requête. Cela permet de ne pas repartir à  zéro, au niveau des données, à chaque requête du client, par exemple dans le cas d'un panier d'achat ou d'une authentification.

Directive  :

```bash
ProxySet stickysession=ROUTEID
```

Une explication plus détaillée, avec  des conteneurs Docker se trouve sur mon repo github à l'adresse suivante : [http-infra/tree/fb-load-balancer-sticky-session](https://github.com/rya-sge/http-infra/tree/fb-load-balancer-sticky-session)



### Sources 

#### Documentation apache 

- Réaliser un reverse proxy : https://httpd.apache.org/docs/2.4/fr/howto/reverse_proxy.html
- proxy balancer : https://httpd.apache.org/docs/2.4/fr/mod/mod_proxy_balancer.html


#### Autres sources

- Définition, exemple avec apache httpd : [https://www.ionos.fr/digitalguide/serveur/know-how/quest-ce-quun-reverse-proxy-le-serveur-reverse-proxy/]( https://www.ionos.fr/digitalguide/serveur/know-how/quest-ce-quun-reverse-proxy-le-serveur-reverse-proxy/)


- Article très complet en anglais : [https://www.digitalocean.com/community/tutorials/how-to-use-apache-as-a-reverse-proxy-with-mod_proxy-on-ubuntu-16-04](https://www.digitalocean.com/community/tutorials/how-to-use-apache-as-a-reverse-proxy-with-mod_proxy-on-ubuntu-16-04)


- Cours de Réseaux(RES) enseigné à l'HEIG-VD en 2021

