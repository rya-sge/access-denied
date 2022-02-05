---
layout: post
title:  "Lecture de fichier JSON avec Node.JS"
date:   2022-01-01
last-update: 
categories: programmation
tags: nodejs Node.JS fs json
description: Résumé des différentes possibilités pour lire un fichier JSON avec Node.JS.
image: 
---



Cet article présente les différentes possibilités pour lire un fichier JSON avec **Node.JS**.

L'ensemble du code est disponible sur mon github : [github.com/rya-sge/AD-ressources - nodeJS/json](https://github.com/rya-sge/AD-ressources/tree/master/programmation/nodeJS/json)

## Avec le module expérimental

Depuis [Node v8.5.0](https://nodejs.org/en/blog/release/v8.5.0/), Il est possible d'importer un fichier JSON avec la directive `import`pour ensuite l'utiliser dans votre application, par exemple pour créer une map à partir de son contenu. 

Cela permet de simplifier la lecture des fichiers json.

Les sources disponibles sont les suivantes : 

- [https://nodejs.org/api/esm.html](https://nodejs.org/api/esm.html)

- [https://nodejs.org/api/esm.html#json-modules](https://nodejs.org/api/esm.html#json-modules)

### Lancement

La fonctionnalité est encore au stade expérimentale, il faut lancer node js avec le flag `--experimental-json-modules`

- En ligne de commande :

```bash
node --experimental-modules --experimental-json-modules app.js
```



- Avec `npm start`

II faut ajouter la commande dans la partie `scripts` du fichier `package.json` .

Ensuite, il suffira d'exécuter la commande `npm start` pour que `node` soit lancé avec les bons flags.

```json
"scripts": {
    "start": "node --experimental-modules --experimental-json-modules app.js"
  },
```

### Exemple de code

```javascript
import ANIMES_LIST from "./anime.json"
mapAnimes = ANIMES_LIST.reduce((map, anime) => map.set(anime.id, anime), new Map())
console.log("**Converto to map**")
console.log(mapAnimes)
```



### Erreur possible

Si vous ne mettez pas le flag `experimental`, vous aurez  une `triggerUncaughtExceptionexception` qui sera lancée car l'extension du fichier ne sera pas reconnue

```bash
internal/process/esm_loader.js:74
    internalBinding('errors').triggerUncaughtException(                              ^
TypeError [ERR_UNKNOWN_FILE_EXTENSION]: Unknown file extension ".json" for test.json

```

## Avec le module fs

### 1) Synchrone 

Avec la fonction readIleSync, la lecture du fichier sera synchrone (bloquant)

```javascript
let rawdata = fs.readFileSync(FILE_PATH);
let persons = JSON.parse(rawdata)
let mapPersons = persons.reduce((map, person) => map.set(person.id, person), new Map())
```

Source principale : [stackabuse.com - Reading and Writing JSON Files with Node.js](https://stackabuse.com/reading-and-writing-json-files-with-node-js/)

### 2) Asynchrone

En utilisant `readFile`, la lecture sera asynchrone (non bloquant)

```javascript
async function loadJson() {
    return fs.readFile(FILE_PATH, "utf8", (err, response) => {
        if (err) {
            console.error(err);
            return;
        }
        // your JSON file content as object
        let data = JSON.parse(response);
        console.log("****Read JSON with fs & ReadFile****")
        mapPersons = data.reduce((map, person) => map.set(person.id, person), new Map())
        console.log(mapPersons)
        return mapPersons;
    });

}
```



Source principale : [sebhastian.com - How to read JSON file using NodeJS](https://sebhastian.com/node-read-json-file/)

## Source 

### Global

Documentation officiel Node.js v17.3.0 : [https://nodejs.org/api/esm.html](https://nodejs.org/api/esm.html)

- [json-modules](https://nodejs.org/api/esm.html#json-modules)
- [builtin-modules](https://nodejs.org/api/esm.html#builtin-modules)

Cours de Technologie Web (TWEB) enseigné à l’HEIG-VD en 2021-2022

### Module expérimental

- [https://nodejs.org/api/esm.html](https://nodejs.org/api/esm.html)
- [https://nodejs.org/api/esm.html#json-modules](https://nodejs.org/api/esm.html#json-modules)

### Module fs

- [sebhastian.com - How to read JSON file using NodeJS](https://sebhastian.com/node-read-json-file/)
- [https://stackoverflow.com/ - How to read file with async/await properly?](https://stackoverflow.com/questions/46867517/how-to-read-file-with-async-await-properly)

- [blog.logrocket.com - Reading and writing JSON files in Node.js: A complete tutorial]( https://blog.logrocket.com/reading-writing-json-files-nodejs-complete-tutorial/)
- [stackabuse.com - Reading and Writing JSON Files with Node.js](https://stackabuse.com/reading-and-writing-json-files-with-node-js/)
- [www.geeksforgeeks.org - Node.js fs.readFileSync() Method](https://www.geeksforgeeks.org/node-js-fs-readfilesync-method/)
