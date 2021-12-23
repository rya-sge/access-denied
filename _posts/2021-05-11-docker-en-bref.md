---
layout: post
title:  "Docker en bref"
date:   2021-05-11
last-update: 2021-13-10 
categories: virtualisation 
tags: docker 
description: Liste des principales commandes de Docker
image: /assets/article/docker/docker-horizontal-monochromatic-white.png
---

Présentation et explications des principales commandes de Docker

### Opérations sur les images

#### Obtenir une image

##### Pull

```bash
docker pull <nom image>
```

##### Build

```bash
build  <Path | url>
```

Construire une image à partir d'un *dockerfile*. 

On peut construire l'image avec un tag choisi à l'avance avec l'option -t

```bash
docker build --tag exemple/test .
```

Lorsqu'on lancera la commande, celle-ci affichera à la fin si tout s'est bien passée

*Successfully tagged exemple/test:latest*

Erreurs possible :

> COPY failed: forbidden path outside the build context: ../../src ()*

Source intéressante si vous avez cette erreur : [https://stackoverflow.com/questions/27068596/how-to-include-files-outside-of-dockers-build-context](https://stackoverflow.com/questions/27068596/how-to-include-files-outside-of-dockers-build-context)

#### Affichage et suppression

Les images disponibles peuvent être listées avec :

```bash
docker images
```

Il est aussi possible de supprimer une image :

```bash
docker image rm <nom image ou ID >
```

Il est important de régulièrement supprimer les images non utilisées car celles-ci prennent vite beaucoup de place sur le système hôte.

### Exécuter un container (run | exec)

#### run

```bash
docker run <image>
```

Permet d'exécuter un container à partir d'une image. Si on exécute plusieurs fois la commande run, il y aura alors plusieurs containeurs de crées, tous avec le même état initial.

- Lors de la création du Dockerfile, on peut préciser ce que doit exécuter le container avec CMD

```dockerfile
CMD ["java", "-jar", "/opt/app/monProgramme.jar"]
```

Ici lorsque l'utilisateur fait run, cela exécutera la commande *java -jar opt/app/monProgramme.jar* et par conséquent le programme.

- On peut exécuter un container en arrière-plan avec le flag -d



```bash
docker run -it <image> /bin/bash
```

 Permet de démarrer un container en obtenant une  invite de commande dessus.

#### exec

```bash
docker exec -it le_container /bin/bash
```

Exécuter une commande  à l 'intérieur d'un containeur déjà en exécution.

Ici, on ouvre un shell



### Opérations sur les containeurs

#### Obtenir l'IP d'un conteneur 

```bash
docker ps
```

Ensuite son ip 

```bash
docker inspect <nom conteneur> | grep IPAddress
```

#### Port mapping

Il est aussi possible de faire du port mapping.

Par exemple, ici le port 80 du conteneur sera redirigé sur le port 9090 de localhost.

Ainsi, il sera possible d'accéder au serveur depuis l'hôte avec l'adresse : 127.0.0.1:9090

```bash
docker run -p 9090:80 serveur/apache_php
```

#### Copier des fichiers

Pour copier des fichiers de votre hôte vers le conteneur, vous pouvez utiliser la commande cp.

```bash
docker cp  dossier ece6be770055:/home/test
```

où 

- dossier correspond au path de votre dossier. Ici le dossier se trouvait à l'endroit où la commande était lancée.
- ece6be770055 correspond à l'id ou le nom de votre conteneur
- /home/test correspond au path dans le conteneur



#### Créer un volume

Les volumes, option -v,  permettent de connecter un dossier de la machine hôte au docker.

Exemple :

```bash
docker run -ti -v "$PWD/site":/usr/share/nginx/ -d -p 8080:80 --name
projet-docker --hostname <hostname>
```



#### Définir des variables d'environnement

On peut définir des variables d'environnements au moment du run avec le flag -e.

On peut ainsi transmettre dynamiquement des informations au conteneur



#### Faire le ménage

```
docker container kill $(docker ps -q)
```

Permet de tuer tous les containers en cours d'exécution



```bash
docker system prune
```

Permet de supprimer les conteneurs qui ne sont pas listés. Typiquement ceux qui apparaissent quand vous faite *ps -a* mais qui ne s'affichent pas avec la commande ps simple

### Sources

- Tutoriel sur docker : [https://nouslesdevs.com/docker/](https://nouslesdevs.com/docker/)
- Documentation officielle de Docker : [https://docs.docker.com/reference/](https://docs.docker.com/reference/)
- Cours RES enseigné à l'HEIG-VD
- Article listant une liste de commande Docker utile : [https://towardsdatascience.com/15-docker-commands-you-should-know-970ea5203421](https://towardsdatascience.com/15-docker-commands-you-should-know-970ea5203421)
