---
layout: post
title:  "Les outils de base pour l'analyse réseau"
date:   2021-11-14
last-update: 
categories: programmation
tags: javascript node.js  websockets
image:
description: Cet article présente une liste d'outils de base dans l'analyse de réseau : ping, traceroute, whois, dig, etc.
---

Outils de réseaux - netowkr tools



Pour réaliser une analyser réseau, quelques outils sont essentiels :



## Active

Dans la partie Active, il s'agit d'outils laissant des traces dans les logs.

### Ping

La commande ping permet de savoir si un hôte est atteignable ou non. Il permet également de connaitre l'adresse IP associé à un site web

Quelques options :

- On peut préciser si on souhaite utiliser ipv4 (flag `-4`) ou IPv6 (flag `-6`)
- On peut définir un temps d'intervalle entre chaque paquet avec le flag `-i interval`
- On peut obtenir plus d'information en ajoutant le flag `-v`

Exemple :

On peut voir l'adresse IP associée au site web `rya-sge.github.io`

![ping](../../../assets_2/outil-securite/tryHackMe/network-tool/ping.PNG)



### Traceroute

A partir d'une adresse IP donnée, cette commande détermine le chemin emprunté jusqu'à l'adresse IP de destination. Pour ce faire, elle utilise le protocole ICMP (comme pour ping). Elle nécessite d'avoir les droits de super-utilisateurs.
La commande traceroute fournit en sortie :
• Numéro d'ordre (1,2,.etc.)
• Noms et adresses IP des routeurs successifs (gateway)
• Temps de réponse minimum, moyen et maximum :Permet de tracet le chemin entre sa machine et une cible (IP ou nom de domaine).

Par défaut, traceroute s'exécute sur la couche Internet du modèle TCP/IP

Commande :

```
traceroute <destination>
```

Quelques options

- On peut préciser l'interface à partir duquel envoyer les paquets avec le flag `-i`

- On peut demander à traceroute utiliser des requêtes TCP/SYN en ajoutant le flag `-T`

  

#### Exemple

![traceroute](../../../assets_2/outil-securite/tryHackMe/network-tool/traceroute.PNG)

### TRACEPATH

Elle trace le chemin jusqu'à une destination et détermine les différents MTU (Maximum Transmission Unit) et PMTU (Path Maximum Transmission Unit).
La dernière colonne affiche le RTT, similaire au RTT de ping. Il s'agit du temps d'aller-retour entre le délai entre l'envoi du paquet et la réponse obtenue.



#### Exemple

![tracepath](../../../assets_2/outil-securite/tryHackMe/network-tool/tracepath.PNG)



## Passive

Les outils passifs laissent moins de trace car ils utilisent des données disponible publiquement, sans directement atteindre le réseau que l'on souhaite analyser.

### dig

Cet outil permet de faire des requêtes récusrives aux serveurs DNS sur un domaine choisi

![dig](../../../assets_2/outil-securite/tryHackMe/network-tool/dig.PNG)

## nslookup

Permet de faire des requête à des serveurs DNS (comme dig)

Quelques options :

nslookup OPTIONS DOMAIN_NAME SERVER

- `option`: correspondent au type de requête montré dans le tableau ci-dessous
- `DOMAIN_NAME` : le nom de domaine sur lequel on souhaite effectuer des recherches
- `server` : Serveur DNS que l'on veut interroger

Quelques types de requêtes

| Query type | Résultat           |
| ---------- | ------------------ |
| A          | Adresse IPV4       |
| AAA        | Adresse IPv6       |
| CNAME      | Nom canonique      |
| MX         | Serveurs mail      |
| SOA        | Start of Authority |
| TXT        | Enregistrement TXT |

![nslookup](../../../assets_2/outil-securite/tryHackMe/network-tool/nslookup.PNG)

### WHOIS

Un client WHOIS permet d'interroger un server WHOIS  dans le but d'obtenir des informations  sur nom de domaine ou une adresse IP passé en paramètre, notamment le propriétaire, adresse email de contact, date d'enregistrement, etc. Pour pouvoir répondre, le serveur WHOIS va récupérer les informations contenues dans les registres auxquels il a accès/maintient.



Au sein de l'UE, ces informations ne sont plus librement accessibles en raison du RGPD

Le protocole WHOIS est décrit par la RFC 3912 disponibles à l'adresse suivante : [https://datatracker.ietf.org/doc/html/rfc3912](https://datatracker.ietf.org/doc/html/rfc3912)

Autres sources :

- https://www.computerhope.com/unix/uwhois.htm
- [www.commentcamarche.net - whois](https://www.commentcamarche.net/contents/717-whois)
- [ICANN : urgence d’une mise en conformité du WHOIS au RGPD](https://www.alain-bensoussan.com/avocats/icann-mise-en-conformite-du-whois-au-rgpd/2018/05/25/)

Exemple

![whois](../../../assets_2/outil-securite/tryHackMe/network-tool/whois.PNG)