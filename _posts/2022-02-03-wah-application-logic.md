---
layout: post
title:  "WAH11 - Application Logic"
date:   2022-02-03
categories: securite reseau web
tags: application logique sql thread wah
description: Questions & Réponses du chapitre 11, Attacking Application Logic, du livre The Web Application Hacker's Handbook
image: /assets/article/pentest/wah/wah-cover.PNG
---

> Cet article contient mes réponses personnelles aux questions présentes dans le chapitre 11, *Attacking Application Logic*, du livre *The Web Application Hacker's Handbook*
>
> L'article a pour objectif de sensibiliser le lecteurs aux différentes vulnérabilités existantes afin qu'il puisse s'en prémunir.

Le chapitre illustre les vulnérabilités présentes dans la logique applicative à travers plusieurs exemples :

1. *Asking the Oracle* (p.407)
2. *Fooling a Password Change Function* (p.409)
3. *Proceeding to Checkout* (p.410)
4. *Rolling Your Own Insurance* (p.412)
5. *Breaking the Bank* (p.414)
6. *Beating a Business Limit* (p.416)
7. *Cheating on Bulk Discounts* (p.418)
8. *Escaping from Escaping* (p.419)
9. *Invalidating Input Validation* (p.420)
10. *Abusing a Search Function* (p.422)
11. *Snarfing Debug Messages* (p.424)
12. *Racing Against the Login* (p.426)

### Question 1

*What is forced browsing, and what kinds of vulnerabilities can it be used*
*to identify?*

**Réponse**

Cette question se réfère à l'exemple 3 du livre.

Lorsqu'un utilisateur navigue sur un site (navigation in-browser), il est possible que l'application prévoit que différentes fonctionnalités ne soient accessible que durant un ordre précis. Le livre cite un processus de commande comme exemple. L'utilisateur est sensé d'abord remplir son panier, valider la commande puis payer.

La technique `forced browsing` consiste à découvrir des vulnérabilités dans ces processus et à les exploiter.

**Source** 

Exemple 3, *Proceeding to Checkout*, du livre (p.410)

### *Question 2*

*An application applies various global filters on user input, designed to*
*prevent different categories of attack. To defend against SQL injection,*
*it doubles up any single quotation marks that appear in user input. To*
*prevent buffer overflow attacks against some native code components, it*
*truncates any overlong items to a reasonable limit.*
*What might go wrong with these filters?*

**Réponse**

- Le serveur ajoute le guillemet simple  supplémentaire avant la troncation : un attaquant peut mettre à la fin son guillemet simple (*quotation mark*). Le programme va ensuite doubler le guillemet présent puis tronquer le résultat ce qui aura comme conséquence de retourner à l'entrée originale de l'utilisateur.

- Le serveur ajoute le guillemet simple après la troncation : Un attaquant peut effectuer un *buffer overflow* en ajoutant son *payload* à la fin de son entrée et en insérant suffisamment de guillemet simples avant celui-ci. En respectant la limite de taille définie, son entrée ne sera pas tronquée et c'est lorsque le serveur va ajouter les guillemets simples supplémentaires qu'il va alors dépasser la limite du buffer permettant au *payload* d'être inséré à la position voulue.



**Source** 

Exemple 9, *Invalidating Input Validation*, du livre (p.420)

### Question 3

*What steps could you take to probe a login function for fail-open conditions?*
*(Describe as many different tests as you can think of.)*

La réponse se trouve dans un autre chapitre du livre : chapitre 21, page 811.

Voici une liste non-exhaustif de tests :

- Effectuer des tests avec un compte que l'on possède et noter tous les paramètres soumises à l'application
- Soumettre une string vide comme valeur
- Supprimer la valeur du *username*
- Soumettre des courtes et très longues valeurs
- Soumettre des nombres au lieu de strings
- Soumettre le même nom de paramètre plusieurs fois avec différentes valeurs ou avec les mêmes.
- Si l'authentification se fait en plusieurs étapes, tenter d'effectuer ces différents étapes dans un ordre non-prévu par l'application.

**Source** 

Chapitre 21, *A Web Application Hacker’s Methodology*, du livre (p.811)

### Question 4

*A banking application implements a multistage login mechanism that is*
*intended to be highly robust. At the first stage, the user enters a username*
*and password. At the second stage, the user enters the changing value on*
*a physical token she possesses, and the original username is resubmitted*
*in a hidden form field.*
*What logic flaw should you immediately check for?*

Dans le cas où l'application conserve uniquement une liste de *tokens* valide, sans les associer à son utilisateur, un attaquant a deux possibilités :

- Si il possède son propre *token* physique et qu'il parvient à récupérer le mot de passe d'un autre utilisateur, il pourrait alors se logger comme celui-ci en modifiant la valeur du champ caché par le nom de l'utilisateur cible.
-  Il peut également décidé de passer la 1ère étape avec son propre compte puis ensuite utiliser son propre *token* mais en changeant le nom d'utilisateur par celui qu'il cible.

Autre point :

Lors de la 2ème étape, il est important que les messages d'erreur renvoyés ne contiennent pas d'information sur l'utilisateur. Cela provient du nom d'utilisateur dans le champ caché qui peut être modifié par un attaquant pour le remplacer par un autre utilisateur.



### Question 5

*You are probing an application for common categories of vulnerability*
*by submitting crafted input. Frequently, the application returns verbose*
*error messages containing debugging information. Occasionally, these*
*messages relate to errors generated by other users. When this happens,*
*you are unable to reproduce the behavior a second time. What logic flaw*
*might this indicate, and how should you proceed?*

Ils 'agit d'une vulnérabilité connue sous la dénomination de `race conditions` . Ces vulnérabilités apparaissent durant une brève période et sous des circonstances spécifiques. Dans le cas présent, on peut en conclure que la fonctionnalité concernant les messages d'erreurs n'est pas *thread safe*.

Pour pouvoir l'exploiter, un attaquant peut écrire un script qui lancer de multiples requêtes permettant à certaines d'entre-elles d'exploiter la fenêtre où les conditions nécessaires à la vulnérabilité sont présentes.

**Source** 

Exemple 12, *Racing Against the Login* du livre (p.426)

## Sources

- STUTTARD, Dafydd, PINTO Marcus , 2018. *The Web Application Hacker's Handbook: Finding and Exploiting Security Flaws*. 2e édition. Wiley Publishing
- Obtenir  le livre en ligne : [https://www.oreilly.com/library/view/the-oracle-hackers/9780470080221/](https://www.oreilly.com/library/view/the-oracle-hackers/9780470080221/)
- Github avec les réponses aux questions : [https://github.com/six2dez/wahh_extras/blob/master/answers.md](https://github.com/six2dez/wahh_extras/blob/master/answers.md)