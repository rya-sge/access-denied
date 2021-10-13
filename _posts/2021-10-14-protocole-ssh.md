---
layout: post
title:  "SSH - accéder à distance à un shell"
date:   2021-10-13
last-update: 
categories: Linux
tags: shell ssh linux
description: Cet article présente comment accéder à distance à un shell ainsi que la mise en place d'une connexion sécurisée entre un client et un serveur. 
image: 
---



Cet article présente comment accéder à distance à un **shell** ainsi que la mise en place d'une connexion sécurisée entre un client et un serveur. 

Pour s'authentifier, il existe 2 méthodes :

- Avec un nom d'utilisateur et un mot de passe
- En utilisant la cryptographie asymétrique

Lors de la 1ère connexion :

- Le client va s'authentifie auprès du serveur, généralement avec son nom d'utilisateur / mot de passe
- Le serveur va aussi s'authentifier auprès du client, pour éviter une attaque Man in the middle(MitM)

## Introduction

### Installation

- Serveur SSH / Ordinateur distant : 

```bash
sudo apt install openssh-server
```

- Client SSH / Ordinateur local


```bash
sudo apt install openssh-client
```



### Commande

```bash
ssh [options] [user@]host [commande]
```

- `host` - Adresse IP ou nom de domaine de la machine distante
- `user`- c'est le compte utilisateur sur la machine distante (si différent de la machine locale)
- `command` - Si rien n'est indiqué, c'est un shell qui est lancé sur la machine distance. Le paramètre command permet de spécifier l'action à exécuter. 

Quelques autres options

- -p port - permet de spécifie le port sur la machine distante, par défaut c'est le port 22. 

- -v, -vv, -vvv - pour afficher les messages générés par la commande, peut aider à résoudre des bugs.

  

### Connexion 

```
ssh username@server
```

Documentation avec Infomaniak : 

[www.infomaniak.com - se-connecter-en-ssh-et-utiliser-des-commandes-en-ligne](https://www.infomaniak.com/fr/support/faq/1941/se-connecter-en-ssh-et-utiliser-des-commandes-en-ligne)



## Cryptographie asymétrique

### Résumé des étapes

1. Générer une pair de clé SSH
2. Configurer les fichiers et les répertoires
3. Copier la clé sur le serveur distant

### Générer une pair de clé ssh

- `ssh-keygen`
  - Exemple avec RSA : `ssh-keygen -t rsa`

- Option -b pour spécifié une longueur : `ssh-keygen -b 2048 -t rsa`
- Les fichiers générés sont :
  - clé privée sans extension
  - clé publique avec l'extension **.pub**

Remarques :

- On peut choisir de protéger ou non la clé par une *passphrase*

- Par défaut, la pair de clé est stocké dans le répertoire personnel de l'utilisateur : `~/.ssh`

  

### Configuration

#### Sur le client

```bash
cd ~
mkdir .ssh
chmod go-rwx .ssh
cd .ssh
touch config
chmod go-rwx config
```

#### Sur le serveur

```bash
cd ~
mkdir .ssh
chmod go-rwx .ssh
cd .ssh
touch authorized_keys
chmod go-rwx authorized_keys
```



### Copier la clé sur le serveur distant 

#### ssh-copy-id

Sur Linux, on peut utiliser`ssh-copy-id` pour copier la clé et l'ajouter directement à
`~/.ssh/authorized_keys` 

```bash
ssh-copy-id user@hostname
```

#### Autres possibilités

- Se connecter avec SSH sur la machine distante (demande le mot de passe)
  -  taper `cat >> ~/.ssh/authorized_keys`
  - copier/coller la clé (terminer par Ctrl-D).
- Avec la commande `scp`

Celle-ci permet de transférer des fichiers de la machine locale au serveur :

```bash
scp ~/.ssh/id_rsa.pub user@host
```

Puis il faut se connecter sur la machine distante et ajouter la clé

```bash
cat ~/id_rsa.pub >> ~/.ssh/authorized_keys
```

### Création d'un alias

La création d'un alias permet d'éviter de devoir se rappeler de son utilisateur, des hosts, etc.

```
alias mon-alias = 'ssh user@host'
source ~/.bash_aliases
```

Il suffit ensuite de taper la commande `mon-alias` pour initier une connexion

Source : https://www.better.dev/how-to-create-an-ssh-shortcut

## Source 

- Cours d'Administration système enseigné à l'HEIG-VD en 2021
- Cours d'Administration IT enseigné à l'HEIG-VD en 2021
- Man ssh-keygen : [https://linux.die.net/man/1/ssh-keygen](https://linux.die.net/man/1/ssh-keygen)
- SSH shortcut client : 
  - [https://askubuntu.com/questions/754450/shortcuts-to-ssh-clients](https://askubuntu.com/questions/754450/shortcuts-to-ssh-clients)
  - [https://www.better.dev/how-to-create-an-ssh-shortcut](https://www.better.dev/how-to-create-an-ssh-shortcut)