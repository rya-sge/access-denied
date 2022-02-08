---
layout: post
title:  "Introduction à Node.JS"
date:   2021-07-11
categories: reseau programmation
tags: node.js javascript serveur backend
description: Node.JS est un environnement d’exécution (runtime) en Javascript permettant d'exécuter du javascript côté serveur. Il possède un grand nombre de paquets pouvant être installés avec le gestionnaire de package npm.
---

## Introduction

Node.JS est un environnement d'exécution (*runtime*) en Javascript. 

- Il permet d'exécuter du javascript côté serveur.
- Il possède un grand nombre de paquets qui peuvent être installés avec le gestionnaire de package **npm**. Celui-ci permet de régler les dépendances et conflits, un peu comme maven *pour* Java.
- Les packages sont installés dans un dossier *nodes_modules*.  Il peut être volumineux et il est préférable de l'exclure de votre dépôt git avec un gitignore.



## Fonctionnement

Il se base sur des entrée-sorties **non bloquantes,** ce qui est plus efficace pour des applications en temps réel.

Il possède un grand nombre de packages de base

- Buffer
- HTTP et HTTPS
- Stream
- Console
- Events
- etc..

## Commande de base

- Version

```bash
node -v
npm -v
```

Ces 2 commandes permettent de vérifier la version de Node.js et de npm d'installé

- Initialisation

```bash
npm init
```

`npm init` permet d'initialiser le package npm. Cette commande créée un fichier `package.json` qui contiendra toutes les dépendances.

Documentation officielle : [https://docs.npmjs.com/cli/v7/commands/npm-init](https://docs.npmjs.com/cli/v7/commands/npm-init)

- Installer le package

```bash
npm install <nom du package>
```

Dans certaines anciennes version, l'option --save était obligatoire pour ajouter le package dans les dépendances de package.json. Cette option n'est plus nécessaire dans les nouvelles versions car fait par défaut

Documentation : [https://docs.npmjs.com/cli/v7/commands/npm-install](https://docs.npmjs.com/cli/v7/commands/npm-install)

- Exécuter le fichier index.js

```javascript
node index.js
```



## Fonctionnalités et modules

Cette partie présente plusieurs modules afin de découvrir ce qui peut être réalisé avec Node.JS

- `Chance` pour générer des données aléatoires;
- `Express`et `http` pour réaliser un serveur backend http;
- `dgram` pour envoyer et recevoir des datagrammes UDP;
- `net` pour réaliser un serveur TCP

### Chance 

Chance est un module qui permet de générer des données aléatoires afin d'effectuer des tests.

Lien du package : [https://chancejs.com/usage/node.html]( https://chancejs.com/usage/node.html)

### Serveur HTTP avec express

Le framework *express.js* permet de réaliser un backend HTTP avec *node js*.

Installer le module : 

```
npm install express
```

Installer un squelette d'application 
le -g indique que c'est une installation globale et non locale au projet

```
npm install express-generator -g
```

C'est intéressant si vous souhaitez envoyer du html, des images ou du Json

Source :  [https://expressjs.com/fr/starter/generator.html](https://expressjs.com/fr/starter/generator.html)

Exemple :

```
var express = require('express');
var app = express();

app.get('/', function(req, res){
	res.send(test());
});


app.listen(3000, function(){
  console.log("Accepte requête http sur le port 3000");
});

function test(){
	return "test";
}
```

Un exemple plus complet se trouve sur mon dépôt git :

[http-infra/blob/fb-ajax-jquery/docker-images/express-image/src/index.js](https://github.com/rya-sge/http-infra/blob/fb-ajax-jquery/docker-images/express-image/src/index.js)

### Serveur HTTP avec http

On peut se passer du framework express en utilisant http

```
const http = require("http");
```

Cet article résume bien comment s'y prendre :  [https://nodejs.org/en/docs/guides/anatomy-of-an-http-transaction/]( https://nodejs.org/en/docs/guides/anatomy-of-an-http-transaction/)

[https://developer.mozilla.org/fr/docs/Learn/Server-side/Express_Nodejs/Introduction](https://developer.mozilla.org/fr/docs/Learn/Server-side/Express_Nodejs/Introduction)



### UDP - dgram

Il est possible d'envoyer des datagrammes UDP en multicast avec le module **dgram**.

#### Emetteur UDP

Port d'envoi : 9907, utilisé par la fonction *send*

IP du groupe multicast : 239.252.10.10

Exemple :

```javascript
	const dgram = require('dgram');

    const socket = dgram.createSocket("udp4");

    //Création du message. Les données sont envoyés en JSON
    const playload = JSON.stringify(data); //data est un objet
    const message = Buffer.from(playload);

    socket.send(message, 0, message.length, 9907, '239.252.10.10', function(err, bytes) {
        if(err){
            console.log("Erreur ", err);
            socket.close();
        }
        console.log(playload + socket.address().port);
    });
```

Un exemple plus complet se trouve sur mon github : [Teaching-HEIGVD-RES-2020-Labo-Orchestra/blob/master/docker/image-musician/src/musicien.js](https://github.com/rya-sge/Teaching-HEIGVD-RES-2020-Labo-Orchestra/blob/master/docker/image-musician/src/musicien.js)



#### Récepteur UDP

Le récepteur UDP va écouter pour recevoir des datagrammes UDP

Port d'écoute : 9907, utilisé par la fonction bind

IP du groupe multicast : 239.252.10.10

```javascript
//Inclusion module
var config = require('./config.js');
const dgram = require('dgram');
const s = dgram.createSocket('udp4');
s.bind(9907, function(){
    console.log("Joining multicast group");
    s.addMembership('239.252.10.10')
});

//Récupération des messages
//ICi les datagrammes reçus contiennent des données JSON qui doivent être //parsés
s.on('message', function(msg,source){

    const json = JSON.parse(msg)
   //Votre code

});
```



Un exemple plus complet se trouve sur mon dépôt github : [Teaching-HEIGVD-RES-2020-Labo-Orchestra/blob/master/docker/image-auditor/src/auditor.js](https://github.com/rya-sge/Teaching-HEIGVD-RES-2020-Labo-Orchestra/blob/master/docker/image-auditor/src/auditor.js)



### Serveur TCP - Net

- Ports d'écoute

Le serveur TCP va écouter sur un port afin de recevoir les connexions TCP.

Dans le code ci-dessous, le port d'écoute est le port 2205.

Elle est utilisée par la fonction *listen*

- Transmission des données du serveur au client

Quant aux données envoyées par le serveur au client, celles-ci sont envoyées au format JSON en utilisant *JSON.stringify(buffer)*. Les données seront écrites dans le socket en exécutant la  fonction *write*; elles pourront ensuite être récupérées par le client.

```javascript
const Net = require('net');

//Créer un nouveau serveur tcp
tcp_server = new Net.Server();

//En attente de connexion
tcp_server.listen(2205, function() {
    console.log('Server listening for connection requests on socket localhost:${port}.');
});

//A chaque requête de connexion de la part d'un client, le serveur créer un nouveau socket dédié au client
tcp_server.on('connection', function(socket) {
    //Envoie des données en écrivant dans le socket

    var buffer = []; //Création du JSON array qui contiendra les musiciens à 
    
    //Votre code pour remplir le buffer
    
    //Ici buffer contient des objets JSON. 
    socket.write(JSON.stringify(buffer));//envoi

    //Le client demande à mettre fin à la connexion.
    //le serveur met alors fin à la connexion
    socket.on('end', function() {
        console.log('Closing connection with the client');
    });

    //On catch les erreurs
    socket.on('error', function(err) {
        console.log(`Error: ${err}`);
    });
    socket.end();
});
```



Un exemple plus complet se trouve sur mon dépôt github : [Teaching-HEIGVD-RES-2020-Labo-Orchestra/blob/master/docker/image-auditor/src/auditor.js](https://github.com/rya-sge/Teaching-HEIGVD-RES-2020-Labo-Orchestra/blob/master/docker/image-auditor/src/auditor.js)

## TIPS

### Exporter des variables

Avec *export*, on peut déclarer des variables pour qu'elles soient accessible en dehors du fichier où elles ont été créés.

Exemple :

- Fichier test.js


```javascript
export.MyVariable = 3000; //3000 => valeur de la variable
```

- Ensuite pour récupérer la valeur :


```
var testImport = require('./test.js');
testImport.MyVariable //Récupérer de la variable
```



## Sources

- Documentation officielle d'expressjs : [https://expressjs.com/fr/starter/generator.html](https://expressjs.com/fr/starter/generator.html)
- Documentation officielle de npm :  [https://docs.npmjs.com/cli/v7/commands/npm-install](https://docs.npmjs.com/cli/v7/commands/npm-install)
- Laboratoire réalisé dans le cadre du cours de Réseaux(RES) enseigné à l'HEIG-VD : [RES-Labo-Orchestra](https://github.com/rya-sge/Teaching-HEIGVD-RES-2020-Labo-Orchestra)
- Cours de Réseaux(RES) enseigné à l'HEIG-VD en 2021