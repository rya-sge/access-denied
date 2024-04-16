---
layout: post
title:  "NodeJS - WebSockets avec Express"
date:   2021-11-14
last-update: 
categories: programmation web
tags: javascript node.js  websockets
image:
description: Présentation et implémentation de websockets avec express-ws
---

Cet article présentation l'implémentation d'un serveur et d'un client webSocket avec Node.js en utilisant la librairie **express-ws**.

Le code présenté est une version adaptée des exemples présentée sur le répertoire github de express-ws : [HenningM - express-ws](https://github.com/HenningM/express-ws)

Vous retrouverez l'ensemble du code sur mon répertoire github : [rya-sge - nodeJS/websocket](https://github.com/rya-sge/AD-ressources/tree/master/programmation/nodeJS/websocket)



## Introduction

### Fonctionnement

- Le navigateur internet ouvre une connexion et *upgrade* le protocole à *websocket*

- Une fois la connexion *websocket* ouverte, le navigateur et le serveur sont autorisées à envoyer des événements

- Le navigateur fournit une *WebScoket API* qui gère le protocole *upgrade*

  Cette méthode est caractérisé par une relative haute latence (TCP)

### Installation

Installer les modules avec npm

```bash
npm install express
npm install express-ws
```

## Server



### Mise en place

Pour obtenir le serveur, il faut d'abord créer une application express puis ensuite l'utiliser pour monter express-ws dessus.

```javascript
var express = require('express');
var app = express();
var expressWs = require('express-ws')(app);
app.listen(3000);
```



### Middleware

Une fois que nous avons mis en place une application, on peut définir une fonction *middleware* de niveau application.

Celle-ci sera exécutée à chaque fois que l'application reçoit une demande

```javascript
app.use(function (req, res, next) {
  console.log('middleware');
  req.testing = 'testing';
  return next();
});
```

Source : [expressjs.com - middleware](https://expressjs.com/fr/guide/using-middleware.html)

### Route

On peut ensuite définir des routes afin de pouvoir y accéder par le navigateur. Dans l'exemple, j'ai défini des routes GET pour la racine '/' ainsi que pour '/echo'

```javascript
//Define a rout for /
app.get('/', function(req, res, next){
  console.log('get route', req.testing);
  res.end();
});

//Define a route for echo
app.get('/echo', function(req, res, next){
  console.log('get route echo', req.testing);
  res.end();
});
```



### WebSocket

Il est ensuite possible de définir les "routes" pour les websockets. Comme plus haut, il y a une route pour la racine `/'`ainsi qu'une route pour `/echo`.

On peut ensuite définir des listeners qui attendre qu'un certains événements se produisent. Dans le cas présent, j'ai défini des listeners pour les  événements `message` et `close`



La documentation de la classe WebScoket est disponible à l'adresse suivante : [github.com - class-websocket](https://github.com/websockets/ws/blob/master/doc/ws.md#class-websocket)



```javascript
app.ws('/', function(ws, req) {
  console.log('socket', req.testing);
  ws.on('message', function(msg) {
    console.log(msg);
  });
  ws.on('close', () => {
    console.log('WebSocket was closed');
  });
});

app.ws('/echo', (ws, req) => {
  ws.on('message', msg => {
    ws.send(msg);
  });

  ws.on('close', () => {
    console.log('WebSocke echo was closed');
  });
})

```

Source :

-  [stackoverflow.com - how-to-setup-route-for-websocket-server-in-express](https://stackoverflow.com/questions/22429744/how-to-setup-route-for-websocket-server-in-express)
- [masteringjs.io/tutorials/express/websockets](https://masteringjs.io/tutorials/express/websockets)

## Client

### Mise en place

Pour déclarer un client, on importe le module `ws`et on définit un nouveau websocket sur l'adresse de notre serveur :

```javascript
const ws = require('ws');

const client = new ws('ws://localhost:3000');
```

Si on souhaite atteindre le websocket `/echo` plutôt que root il faudra alors l'indiquer dans l'url

```javascript
const client = new ws('ws://localhost:3000/echo');
```

### Evénements

On définit ensuite des *listeners* qui vont exécuter  du code dès qu'un certains événements se produits

- Ouverture de la connexion

```javascript
client.on('open', () => {
  // Causes the server to print "Hello"
  console.log("send message...")
  client.send('Hello');
});
```

- Message reçu du serveur

```javascript
client.on('message', function(msg) {
  console.log("response from server : ", msg);
});
```

- Fermeture de la connexion

```javascript
client.on('close', function(msg) {
  console.log("response from server : ", msg);
});
```

## Exemples

- Lancement du serveur 

```bash
node server.js
```

- Lancement du client

```bash
$ node client.js
send message...
Open a connection

```

- Affichage sur le serveur

```bash
middleware
socket testing
Hello
```

- Fermeture de la connexion par le client

  ```
  WebSocket was closed
  ```

  ![server-example]({{site.url_complet}}/assets/article/programmation/nodeJS/websocket/server-example.PNG)

## Sources

- Documentation officielle :
  - [HenningM - express-ws](https://github.com/HenningM/express-ws)
  - [expressjs.com - middleware](https://expressjs.com/fr/guide/using-middleware.html)
  - [github.com - class-websocket](https://github.com/websockets/ws/blob/master/doc/ws.md#class-websocket)
- Cours de Technologie Web (TWEB) enseigné à l'HEIG-VD en 2021
-  [stackoverflow.com - how-to-setup-route-for-websocket-server-in-express](https://stackoverflow.com/questions/22429744/how-to-setup-route-for-websocket-server-in-express)
- [masteringjs.io/tutorials/express/websockets](https://masteringjs.io/tutorials/express/websockets)