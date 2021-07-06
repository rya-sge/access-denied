---
layout: post
title:  "WPA en bref"
date:   2021-06-15 
categories: securite reseau
tags: wpa
description: Cet article résume les principaux points du protocole WPA, notamment la génération des clés, le contrôle d'intégrité avec MIC et la confidentialité avec TKIP
image: /assets/article/reseau/wpa/wpa-schema.png
---

Cet article résume les principaux points du protocole WPA.

### Résumé

- Nouveau contrôle intégrité *Message Integrity Code*
- Utilise l'algorithme *TKIP*
- Double la taille de l'IV, par rapport à **WEP**, qui passe à 48 bits



### Schéma

#### Protocole WPA

Représentation simplifiée du protocole **WPA**.

Le premier cadre rouge représente la partie qui protège l'intégrité, grâce au *MIC*

Le 2ème cadre rouge concerne la partie qui assure la confidentialité grâce à l'algorithme *TKIP*.



![wpa-schema]({{site.url_complet}}/assets/article/reseau/wpa/wpa-schema.png)

#### Génération des clés

Ce schéma représente la génération des clés

![wpa-generation-cle]({{site.url_complet}}/assets/article/reseau/wpa/wpa-generation-cle.png)



### Détails

#### MIC - Intégrité

- Comment est généré le *MIC* ?

Il est généré à partir d'une clé MIC, du bloc de données data et des informations permettant d'authentifiés les émetteurs et les récepteurs. Ceux-ci  sont authentifiés par leur adresse MAC respectives. Pour la priorité, celle-ci vaut toujours 0 en pratique.



- Conséquence : 

1) Si un attaquant intercepte le message,  il lui ne sera pas possible de lui faire croire que le message provient de l'attaquant et non de l'émetteur originale

2) Un message protégé par un MIC ne peut être rendu qu'au destinateur qu'on avait choisi au début.

3) Le récepteur ne va jamais croire que le message provient de quelqu'un d'autres que l'émetteur



#### TKIP - Confidentialité

Dans WEP, on utilise RC4 directement

Avec WPA, on utilise TKIP et c'est cet algorithme qui va appeler RC4 afin de générer un *keystream*. TKIP aura pour rôle de rattraper les vulnérabilités présentes dans RC4. 

Le *keystream* sera différent à chaque fois. 



#### CLES

Pour envoyer une trame protégée avec WPA (unicast), il faut 2 clés :

- Une clé pour calculer le MIC
- Une clé pour l'algorithme KTIP

Chaque clé est unique pour chaque client



### Sources 

Cours SRX enseigné à l'HEIG-VD(2021)





