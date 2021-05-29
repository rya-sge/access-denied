---
layout: post
title:  "Docker en bref"
date:   2021-05-11
categories: Virtualisation docker
tags: docker virtualisation
---

Présentation et explications des principales commandes de Docker

### Opérations sur les images

#### Obtenir une image

##### Pull

```
docker pull <nom image>
```

Vous pouvez ensuite afficher les images disponible avec :

```
docker images
```

##### build

```
build  <Path | url>
```

Construire une image à partir d'un dockerfile. 

On peut construire l'image avec un tag choisi à l'avance avec l'option -t

```
docker build --tag exemple/test .
```

Lorsqu'on lancera la commande, celle-ci affichera à la fin si tout c'est bien passée

*Successfully tagged exemple/test:latest*

#### Affichage et suppression

La liste des images disponibles peuvent être obtenues avec :

```bash
docker images
```

Il est aussi possible de supprimer une image :

```
docker image rm <nom image ou ID >
```

Il est important de régulièrement supprimer les images non utilisées car celles-ci prennent vite beaucoup de place sur le système hôte.

### Exécuter un container (run | exec)

#### run

```
docker run <image>
```

Permet d'exécuter un container à partir d'une image. Si on exécute plusieurs fois la commande run, il y aura alors plusieurs containeurs de crées, tous avec le même état initial.

- Lors de la création du Dockerfile, on peut préciser ce que doit exécuter le container avec CMD

```dockerfile
CMD ["java", "-jar", "/opt/app/monProgramme.jar"]
```

Ici lorsque l'utilisateur fait run, cela exécutera la commande *java -jar opt/app/monProgramme.jar* et par conséquent le programme.

- On peut exécuter un container en arrière-plan avec le flag -d



```
docker run -it <image> /bin/bash
```

 Permet de démarrer un container en obtenant une  invite de commande dessus.

#### exec

```
docker exec -it le_container /bin/bash
```

Exécuter une commande  à l 'intérieur d'un containeur déjà en exécution.

Ici, on ouvre un shell



### Opérations sur les containeurs

#### Obtenir l'IP d'un conteneur 

```
docker ps
```

Ensuite son ip 

```
docker inspect <nom conteneur> | grep IPAddress
```

#### Port mapping

Il est aussi possible de faire du port mapping.

Par exemple, ici le port 80 du conteneur sera redirigé sur le port 9090 de localhost.

Ainsi, il sera possible d'accéder au serveur depuis l'hôte avec l'adresse : 127.0.0.1:9090

```
sudo docker run -p 9090:80 serveur/apache_php
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

#### Définir des variables d'environnement

On peut définir des variables d'environnements au moment du run avec le flag -e.

On peut ainsi transmettre dynamiquement des informations au conteneur



#### Faire le ménage

```
docker system prune
```

Permet de supprimer les conteneurs, images, volumes, etc, qui ne sont plus utilisés

### Sources

- Tutoriel sur docker : [https://nouslesdevs.com/docker/](https://nouslesdevs.com/docker/)
- Documentation officielle de Docker : [https://docs.docker.com/reference/](https://docs.docker.com/reference/)
- Cours de RES de l'HEIG(M.Liechti)