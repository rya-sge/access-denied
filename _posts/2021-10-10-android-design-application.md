---
layout: post
title:  "Android Studio - Design d'une application"
date:   2021-10-10
categories: programmation
tags: android design mobile
description: Cet article présente les quelques astuces de bases pour configurer et modifier le design de son application Android (texte à afficher, multilingue, image, etc.)
image: /assets/article/programmation/android/design/landscape-avd.PNG
---

Cet article présente les quelques astuces de bases pour configurer et modifier le design de son application **Android**, entre autre :

- Les textes à afficher sur l'application ;
- Les langues afin que le texte puisse s'adapter en fonction de la langue de l'utilisateur ;
- L'affichage (paysage / portrait) ;
- Les types de champs dans un formulaire.



## Les ressources

Pour définir le design de notre application, Android offre la possibilités d'ajouter des ressources. Celles-ci sont les suivantes :

- Les valeurs (*values*)
- Les images (*drawables*)
- Les *layouts* (interface graphique de l'application)
- Les animations
- Les menus
- etc.

Toutes ces ressources sont situées dans des répertoires spécifiques dans le dossier `res`

## Les strings

### Définir le texte affiché

Lorsqu'on développe une application, on souhaite souvent définir du texte à afficher (*strings*). Il est possible de  les définir et de modifier ceux présent par défaut dans le fichier `res/values/strings.xml`

- Exemple pour le nom de l''application (présent par défaut) :

```xml
<string name="app_name">Mon app</string>
```

Cette string est ensuite appelé dans le fichier`AndroidManifest.XML`

```xml
android:label="@string/app_name"
```

- Exemple avec une string d'une *text view*

On définit notre string dans `strings.xml`

```
    <string name="input_text">Welcome</string>
```

Dans notre balise *TextView* qui se trouve dans le fichier xml de l'activité situé dans le layout :

```xml
<TextView
    android:id="@+id/input_text"
    android:text="@string/input_text"
```



### Application multi-langues

Une application peut être destiné à des utilisateurs de langues différentes. Il est alors important de définir des *strings* adaptés à chacune de ces langues.

Pour une présentation vidéo, je vous invite à aller regarder celle-ci qui est très bien : [YouTube - How to rotate the Android emulator display](https://www.youtube.com/watch?v=41UeSYiYsjw)

Pour définir des traductions en plusieurs langues :

- Aller dans `res/values`
- Clique droit sur `strings`
- Cliquer sur `Open Translation Editors`
- Cliquer sur le symbole terre "Add Locale"

Dans l'exemple ci-dessous, j'ai ajouté les traductions pour le français.

programmation/![strings-language]({{site.url_complet}}/assets/article/programmation/android/design/strings-language.PNG)



## Les images (Drawables)

Il existe plusieurs types de *drawables*, entre autre :

- Fichier bitmap
- Vector
- Nine-Path
- State List
- Level List

Le logo doit se trouver dans le dossier mipmap.

Android utilise le nom du fichier (sans l'extension) pour définir l'identifiant de la ressource :

`monImage.png` -> `@drawable/monImage`

## Spécifier l'affichage en mode paysage

Cette partie décrit comment créer un *layout* pour  le mode paysage pour l'activité `MainActivity`

1) Ouvrir res/layout/activity_main.xml

2) A droite, cliquer sur le symbole smartphone

![landscape-variation]({{site.url_complet}}/assets/article/programmation/android/design/landscape-variation.PNG)

3) Sélectionner `Create landscape variation`

4) Un fichier sera crée dans `layout-land/activity_main.xml`

### Pour tester

- Sélectionner votre AVD

![avd-select]({{site.url_complet}}/assets/article/programmation/android/design/avd-select.PNG)

-  puis cliquer sur "Edit"

![landscape-avd]({{site.url_complet}}/assets/article/programmation/android/design/landscape-avd.PNG)





## Formulaires - Login

Il arrive souvent qu'on souhaite créer un formulaire que l'utilisateur devra remplir, par exemple un formulaire de login. Celui-ci comprend un identifiant, ici ce sera une adresse email, ainsi que le mot de passe. Pour ce faire, ces champs ont deux contraintes :

- On ne souhaite pas que l'auto-complétion soit activée pour ces champs, car cela n'a pas de sens
- Le mot de passe doit être caché lors du remplissage, avec des points ou des astérixes. 



### Par défaut

Il est aussi possible de créer directement une activité  de login lors de la création d'un projet ou d'une activité et celle-ci aura déjà l'email et le mot de passe de configurer.

![activity-login]({{site.url_complet}}/assets/article/programmation/android/design/activity-login.PNG)

### Manuellement

Si vous souhaitez partir d'une activité basique et faire vous-même le formulaire de login, voici quelques configurations

##### Mot de passe

Pour cacher le champ de mot de passe lors de la saisie pour l'activité `MainActivity`.

- Ouvrir res/layout/**activity_main.xml**
- Aller dans la balise EditText, ajouter :
  - android:inputType="textPassword" />

Il est aussi possible de le faire avec l'interface graphique, comme pour l'email (voir ci-dessous)

##### Email

Voici comment configurer l'email. Dans `InputType`, choisir `TextEmailAdress`. Cela va ajouter le code suivante dans le layout :

```xml
  android:inputType="textEmailAddress"
```



![input-email-default]({{site.url_complet}}/assets/article/programmation/android/design/input-email-default.PNG)
