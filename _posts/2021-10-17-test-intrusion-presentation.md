---
layout: post
title:  "Les tests d'intrusion (pentesting)"
date:   2021-10-17
categories: securite
tags: intrusion pentesting
description: Cet article introduit le concept de test d'intrusion (pentesting)
image: 
---



## Présentation

Un test d'intrusion (*pentesting*) est le processus pour trouver et exploiter des vulnérabilités dans des systèmes d'informations qu'un hacker malveillant pourrait exploiter.

## Pourquoi un test d'intrusion

A l'heure où les attaques informatiques se multiplient, il est devenu urgent de s'en prémunir. Une des solutions possibles est de réaliser un test d'intrusion. Celui-ci :

- Permet à l'organisation où se déroule le test de mieux comprendre un risque donné
- Trouver des vulnérabilités avant les *bad guys*
- Exploiter des failles afin d'estimer les probabilités qu'une vulnérabilité donnée puisse être exploitée, notamment en prenant compte :

  - Les compétences des hackers éthiques
  - Le temps disponible

Cela permet alors de quantifier la probabilité que cela arrive et son impact. Ce qu'on appelle le risque.

Le risque peut se calculer comme suit :
`Risque = P(menace + Vulnerabilité) * impact`

### Type de tests d'intrusion

Il existe plusieurs types de tests d'intrusion, en voici une liste :

- Services réseaux (*network services*) : chercher des vulnérabilités sur le système cible à travers  le réseau et les exploiter. Les systèmes peuvent être accessible au public ou situés dans les locaux de la cible (réseaux internes)
- Côté client (*Client-side*) : trouver et exploiter des vulnérabilités sur le logiciel côté client (navigateurs, lecteurs de médias)
- Application web (*Web application*) : chercher et exploiter des vulnérabilités dans des applications webs
- Application mobile (*Mobile application*) : chercher et exploiter des vulnérabilités sur des plateformes mobiles (IOS/Android)
- Sécurité sans-fil (*Wireless security*): Chercher pour des  points d'accès(AP) sans-fils non autorisé ou des AP avec des vulnérabilités.
- Ingénierie sociale (*Social engineering*) : forcer les utilisateurs à révéler des informations sensibles
- Equipement volés (*Stolen equipment*) : implique d'obtenir un équipement de la cible (ordinateur d'entreprise) et d'essayer d'extraire des informations de celui-ci
- Cryptanalyse attaque (*Cryptanalysis attack)* : contourner ou casser les systèmes de chiffrement sur les systèmes locaux ou au travers  le réseau. Cela implique aussi l'évaluation des solutions de gestion des droits numériques (GDN /DRM)
- Sécurité du produit (*Product security*) : chercher pour des failles de sécurités dans des produits logiciels, exploier des *buffer overflows*, élévation de privilèges, expositions d'information sensible non chiffrée, etc.)

### Guide

Quelques guides expliquent comment réaliser un test d'intrusion

- PTES : [www.pentest-standard.org/index.php/Main_Page](http://www.pentest-standard.org/index.php/Main_Page)
- OSSTMM  : [www.isecom.org/OSSTMM.3.pdf](https://www.isecom.org/OSSTMM.3.pdf)
- OWASP testing guide : [owasp.org/www-project-web-security-testing-guide/](https://owasp.org/www-project-web-security-testing-guide/)
- NIST framework : [www.nist.gov/cyberframework](https://www.nist.gov/cyberframework)
- Penetration Testing Framework 0.59 : [http://www.vulnerabilityassessment.co.uk/Penetration%20Test.html](http://www.vulnerabilityassessment.co.uk/Penetration%20Test.html)



## Limitation d'un test d'intrusion

Un test d'intrusion ne peut pas trouver toutes les vulnérabilités sur un environnement ciblé.

### Sur le projet

- Limite du scope

- Limite de temps

- Les accès : a quoi a -t-on accès pour réaliser le test ?

- La méthode

  - Par exemple : on ne peut pas faire du Déni du service pour réaliser une distraction

### Autres facteurs

- Compétences
- Imagination
- Exploits connus
  - On n'a pas forcément le temps d'écrire nos propres exploits pour écrire un exploit pour une faille spécifique trouvée dans un environnement spécifique. En principe, le client ne va pas payer pour que le pentester écrive ses exploits.

## Source

Cours **Projet d'audit de sécurité technique** enseigné à l'HEIG-VD en 2021