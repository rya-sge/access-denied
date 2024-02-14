---
layout: post
title:  "Introduction aux Flexbox"
date:   2021-10-03
categories: web
tags: flexbox css 
description: Cet article présente le concept de flexbox en css. Les flexbox permettent  de gérer le positionnement des éléments sur une page. 
image: /assets/article/web/css/level-10.PNG
---



Cet article présente le concept de **flexbox** en css. Les flexbox permettent  de gérer le positionnement des éléments sur une page. 

Une partie du contenu provient du jeux en ligne *Flexbox froggy* permettant de s'entrainer sur ce concept. Il est vraiment bien fait et je vous conseille d'aller l'essayer : [https://flexboxfroggy.com/#fr](https://flexboxfroggy.com/#fr)



## Définition

Il est possible de définir une flexbox avec la propriété **display: flex**. Une flex box :

- Se comporte comme un élément de block. Il commence une nouvelle ligne
- Définit l'affichage interne type qui dicte comment les éléments doivent s'afficher

Exemple de code

```css
.container {
 display: flex;
 flex-direction: row;
 justify-content: center;
}
```



### Propriété du container 

- flex-direction
- flex-wrap
  - `nowrap` : Tous les éléments sont sont sur une seule ligne.
  - `wrap` : Les éléments peuvent être sur plusieurs lignes au besoin.
  - `wrap-reverse` : Les éléments se placent sur plusieurs lignes en séquence inversé.
- flex-flow
  - permet de combiner les propriété de flex-direction et flex-wrap
  - Ex : flex-flow: row wrap
- justify-content
- align-items
- align-content
  - `flex-start` : Les lignes sont placés en haut du conteneur.
  - `flex-end`: Les lignes sont placées dans le bas du conteneur.
  - `center` : Les lignes sont placées dans le centre vertical du conteneur.
  - `space-between` : Les lignes s'affichent avec un espace égal entre eux.
  - `space-around` : Les lignes s'affichent avec un espace égal autour d'eux.
  - `stretch` : Les lignes sont étirées pour s'adapter au conteneur.

### Propriété des enfants 

- flex
- flex-grow
- flex-shrink
- flex-basis
- order
- align-self
  -  Accepte les mêmes valeurs que align-items mais s'applique seulement à l'élément ciblé.

## Propriété du container 

###  justify-content

Cette propriété permet d'aligner les éléments

- `flex-start` : aligner les éléments sur le côté gauche
- `flex-end` : aligner les éléments sur le côté droit
- `center` : aligner les éléments au cœur du conteneur
- `space-between` : les élément s'affiche en respectant un espace égal entre eux.
- `space-around`: les éléments s'affichent avec un espacement égale autour d'eux

La principale différence entre `space-around` et `space-between` réside que le côté droit du 1er élément et le côté gauche du dernière élément auront un espace avec le `space-around`.

Remarques :

Quand la direction est en colonne (flex-direction: row), `justify-content` change pour la verticale et `align-items` pour l'horizontale.

Source : [developer.mozilla.org - justify-content](https://developer.mozilla.org/fr/docs/Web/CSS/justify-content)

### Exemple

- flex-center

```css
.container{
	display: flex;
	justify-content: center;
}
```

Code disponible sur mon gihtub : [rya-sge/AD-ressources - css/flexbox/1-center](https://github.com/rya-sge/AD-ressources/tree/master/web/css/flexbox/1-center)

**Résultat**

![flex-center]({{site.url_complet}}/assets/article/web/css/flex-center.PNG)

- space-between

```
.container{
	display: flex;
	justify-content: space-between;
}
```

Code disponible sur mon github : [rya-sge/AD-ressources - css/flexbox/2-space-between](https://github.com/rya-sge/AD-ressources/tree/master/web/css/flexbox/2-space-between)

**Résultat**

![space-between]({{site.url_complet}}/assets/article/web/css/space-between.PNG)

- Avec flex-direction: column

```css
flex-direction: column;
justify-content: flex-end;
```



### align-items

Cette propriété permet d'aligner les éléments verticalement

- `flex-start` : Les éléments s'alignent au haut du conteneur.
- `flex-end` : Les éléments s'alignent au bas du conteneur.
- `center` : Les éléments s'alignent au centre vertical du conteneur.
- `baseline` : Les éléments s'alignent à la ligne de base du conteneur.
- `stretch` : Les éléments sont étirés pour s'adapter au conteneur.



#### Exemple

Le code suivant va aligner les boîtes vers le bas. Vous pourrez constater l'ajout de la priopriété height à 100% afin que la hauteur de la boite principale corresponde à la hauteur de la page.

```css
.container{
	display: flex;
	align-items: flex-end;
	height: 100%;
}
```

Code disponible sur mon github : [(rya-sge/AD-ressources - css/flexbox/3-flex-end](https://github.com/rya-sge/AD-ressources/tree/master/web/css/flexbox/3-flex-end)

**Résultat**

![3-align-item-flex-end]({{site.url_complet}}/assets/article/web/css/3-align-item-flex-end.PNG)

### flex-direction

Cette propriété définit la direction des éléments placés dans le conteneur

- `row` : Les éléments sont disposés dans la même direction que le texte.
- `row-reverse` : Les éléments sont disposés dans la direction opposée au texte.
- `column` : Les éléments sont disposés de haut en bas.
- `column-reverse` : Les éléments sont disposés de bas en haut.

Une propriété intéressante de ces flex-direction est de pouvoir inverser le c

#### Exemple

Dans ce niveau, il fallait retourner le sens des grenouilles pour que chaque grenouille soit sur sa couleur

![level-10-init]({{site.url_complet}}/assets/article/web/css/level-10-init.PNG)

En mettant uniquement row-reverse, on inversait bien les grenouilles mais celles-ci se mettaient tout à droite. Nous faisions une rotation

```css
#ponds{
	display: flex;
	flex-direction: row-reverse;
}
```

**Résultat**

![level-10-rotation]({{site.url_complet}}/assets/article/web/css/level-10-rotation.PNG)



La solution résidait dans l'ajout de la propriété `justify-content: flex-end`. Celle-ci va coller à droite les grenouilles, qui seront alors inversés du bon côté par `flex-direction`.

```css
#ponds{
	display: flex;
    justify-content: flex-end;
	flex-direction: row-reverse;
}
```

**Résultat**

![level-10]({{site.url_complet}}/assets/article/web/css/level-10.PNG)



## Sources

- [https://flexboxfroggy.com/#fr](https://flexboxfroggy.com/#fr)
- [developer.mozilla.org - justify-content](https://developer.mozilla.org/fr/docs/Web/CSS/justify-content)
- Cours de Technologie Web(TWEB) enseigné à l'HEIG-VD en 2021