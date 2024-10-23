---
layout: post
title:  "WPA en bref"
date:   2021-06-15 
categories: security network
tags: wpa wifi
description: Cet article résume les principaux points du protocole WPA, notamment la génération des clés, le contrôle d'intégrité avec MIC et la confidentialité avec TKIP
image: /assets/article/reseau/wpa/wpa-schema.png
---

Cet article résume les principaux points du protocole WPA.

Le **WPA** (Wi-Fi Protected Access) est un protocole de sécurité destiné aux réseaux sans fil (Wi-Fi). 

Introduit en 2003 par la Wi-Fi Alliance, il avait pour objectif de corriger les failles du protocole précédent, le WEP (Wired Equivalent Privacy), qui contenait de nombreuses vulnérabilités, notamment liées à son protocole de chiffrement [RC4](https://fr.wikipedia.org/wiki/RC4).  Pour plus de détail, voir mon [article](https://rya-sge.github.io/access-denied/2022/04/28/protocole-wep/) sur les vulnérabilités dans WEP.

WPA apporte des améliorations significatives en termes de cryptographie et de gestion des clés, renforçant ainsi la sécurité des réseaux sans fil. 

Il a été suivi par **WPA2** qui remplace l'algorithme TKIP par [CCMP](https://fr.wikipedia.org/wiki/Counter-Mode/CBC-Mac_protocol) et ensuite WPA3.

## Résumé

- Nouveau contrôle intégrité *Message Integrity Code*
- Utilise l'algorithme *TKIP*
- Double la taille de l'IV, par rapport à **WEP**, qui passe à 48 bits



## Schéma

### Protocole WPA

Représentation simplifiée du protocole **WPA** pour mes messages unicast

Le premier cadre rouge représente la partie qui protège l'intégrité, grâce au *MIC*

Le 2ème cadre rouge concerne la partie qui assure la confidentialité grâce à l'algorithme *TKIP*.



![wpa-schema]({{site.url_complet}}/assets/article/reseau/wpa/wpa-schema.png)

### Génération des clés

Ce schéma représente la génération des clés

![wpa-generation-cle]({{site.url_complet}}/assets/article/reseau/wpa/wpa-generation-cle.png)



## Détails

### MIC - Intégrité

- Comment est généré le *MIC* ?

Il est généré à partir d'une clé MIC, du bloc de données data et des informations permettant d'authentifiés les émetteurs et les récepteurs. Ceux-ci  sont authentifiés par leur adresse MAC respectives. Pour la priorité, celle-ci vaut toujours 0 en pratique.



- Conséquence : 

1) Si un attaquant intercepte le message,  il lui ne sera pas possible de lui faire croire que le message provient de l'attaquant et non de l'émetteur originale

2) Un message protégé par un MIC ne peut être rendu qu'au destinataire qu'on avait choisi au début.

3) Le récepteur ne va jamais croire que le message provient de quelqu'un d'autres que l'émetteur



### TKIP - Confidentialité

Dans WEP, on utilise RC4 directement

Avec WPA, on utilise TKIP et c'est cet algorithme qui va appeler RC4 afin de générer un *keystream*. TKIP aura pour rôle de rattraper les vulnérabilités présentes dans RC4. 

Le *keystream* sera différent à chaque fois. 



#### Les clés

Il existe 3 groupes de clés différentes :

**Pairwise / Unicast**

Pour envoyer une trame protégée avec WPA en unicast, il faut 2 clés :

- La clé TK (*Temporal Key*) permet de garantir le chiffrement et est utilisé pour l'algorithme TKIP.
- La clé MICK (*Message Integrity Control*) permet de garantir l'intégrité.

Chaque clé est unique pour chaque client.

**Groupe**

Ces clés sont pour les messages en broadcast.

- La clé GTK (*Group Master Key*) permet le chiffrement ;
- La clé GMIC (*Group Master Key*) permet de garantir l'intégrité..

Les stations n'ont pas le droit d'envoyer elle-même des messages en *broadcast*. Elles doivent envoyer leur message à l'AP, qui lui s'occupera ensuite d'émettre le message en *broadcast*.



**Transmission des clés**

- La clé KEK  (*Key Encryption Key*)  permet le chiffrement
- La clé KCK (*Key Confirmation Key*) permet de garantir l'intégrité





### Sources 

- Cours de Sécurité des Réseaux (SRX) enseigné à la HEIG-VD en 2021.
- [Wikipedia - Wi-Fi Protected Access](https://en.wikipedia.org/wiki/Wi-Fi_Protected_Access)
- ChatGTP avec l'entrée "Ecris moi un article, en français sur WPA. Parle de la sécurité, cryptographie, etc."
