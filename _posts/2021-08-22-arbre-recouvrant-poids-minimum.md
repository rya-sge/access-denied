> layout: post
> title:  "Arbre couvrant de poids minimum (MST / ACM)"
> date:   2021-08-22
> categories: programmation
> tags:  acm mst minimum-spanning-tree kruskal boruvka prim
> description: Cet article résume les principales notions et algorithmes utilisés permettant de calculer l'arbre couvrant de poids minimum (ACM ) ou  Minimum Spanning Tree (MST) en anglais.  
> image: 

Cet article résume les principales notions et algorithmes utilisés permettant de calculer l'arbre couvrant de poids minimum (ACM ) ou  *Minimum Spanning Tree* (MST) en anglais.  

Dans un graphe, un arbre couvrant de poids minimum :

- Contient tous les sommets du graphe
- La somme des poids des arêtes qui le constitue  est minimal. Pour rappel, une arête relie deux sommets du graphe entre eux.

## Définition

Avant d'aller plus loin, voici quelques définition et notion de la théorie des graphes 

### Arbre

Un arbre est un graphe connexe, tous les sommets sont reliés entre eux, et sans cycle. Sur l'image ci-dessous, on peut constater que tous les sommets sont reliés entre eux et qu'aucun sommet n'est relié à lui-même.

![arbre]({{site.url_complet}}/assets/algorithme/mst/arbre.PNG)



### Forêt

- Lorsqu'on parle d'une forêt, il s'agit d'un graphe sans cycles simples.  
- Les composantes connexes d'une forêt sont des arbres. 

Dans le graphe ci-dessous, la forêt est constituée de 2 arbres.

![forêt]({{site.url_complet}}/assets/algorithme/mst/forêt.PNG)



Les forêts tous comme les arbres sont des graphes simples





## Algorithme 

### Glouton

Un algorithme glouton consiste à faire étape par étape un choix optimum locale.

Il y a trois grands algorithmes ayant une stratégie gloutonne permettant de calculer l'ACM/MST :

- Algorithme de Kruskal

- Algorithme de Prim : Version stricte et paresseuse
- Algorithme de Boruvka 



### Algorithme de Kruskal

- Le point de départ est une forêt vide ne contenant que les sommets du graphe. 

- On examine par poids croissants chaque arrête du graphe (stratégie gloutonne)

- Si cette arrête ne crée pas un cycle, c'est-à-dire qu'elle permet d'ajouter un nouveau sommet au MST, alors on la sélectionne et on l'ajoute à notre forêt MST. Cela va diminuer petit à petit le nombre de composantes connexes de la forêt.

- Une fois qu'on a sélectionné V-1 arrête, on a le MST et on peut s'arrêter

- Il y a plusieurs façons d'implémenter l'algorithme de Kruskal. Une des possibilités est d'utilisé une structure **Union-Find** avec des arbres. Le représentant d'un sommet est la racine de l'arbre auquel il appartient. Une telle structure implémente trois opérations. Pour un sommet u :
  - MakeSet(u) va créer un sous-ensemble ne contenant que u. Le représentant de cet ensemble sera alors u et se sera la racine de l'arbre.
  - Find(u) pour retrouver la classe d'équivalence (le représentant) contenant  u
  - Union(u, v) va fusionner les arbres auxquels appartiennent u et v en rattachant la racine de l'un à l'autre, en général le plus petit arbre est rattaché au plus grand.
  
  #### Exemple 
  
  Le graphe suivant est sans cycle et convexe. Chaque arrête possède un poids.

![kruskal-graphe]({{site.url_complet}}/assets/algorithme/mst/kruskal-graphe.jpg)



Avec *union-find*, on va d'abord réaliser une queue de priorité où chaque arrête sera mise en fonction de son poids, C'est la fonction *make-set* qui s'en occupe.

![kruskal-initialisation]({{site.url_complet}}/assets/algorithme/mst/kruskal-initialisation.PNG)

Pour chaque arête, numéroté de a à i, on va appelé *Find(u)* afin de déterminer à quelle classe apparient le sommet et par ricochet savoir aussi si les 2 sommets sont déjà connectés entre eux. Si c'est le cas, l'arrête n'a pas besoin d'être ajoutée au MST.

a) 1-3 => Classe d'équivalente différente => pas connecté => appelle de Union (1, 3)

b) 2-3 => pas connecté => union (2,3)

c) 4-6 => pas connecté => union (4,6)

d) 1-2 => déjà connecté à travers le sommet 3 et les arrêtes 1-3 et 2-3

e) 2-4 =>pas connecté => union (2,4)

f) 5-6 => pas connecté => union (5,6)

On a 6 arrêtes, on peut alors s'arrêter car on va V - 1 arrête dans le MST, V étant le nombre de sommet. 

On obtient alors la structure suivante. Les lettres correspondent aux arrêtes ayant permis de reliés le sommet au sommet racine, 1.

![kruskal-union]({{site.url_complet}}/assets/algorithme/mst/kruskal-union.jpg)

## Algorithme de Prim

- On part d'un arbre formé d'un seul sommet
- A chaque étape, on le fait croitre le plus économiquement  possible en ajoutant une nouvelle arrête et un nouveau sommet à l'arbre actuelle.
- L'arête ajouté est celle ayant le poids minimum parmi celles dont exactement 1 sommet appartient  à l'arbre courant.

#### Exemple

![prim-graphe-initial]({{site.url_complet}}/assets/algorithme/mst/prim-graphe-initial.jpg)



On sélectionne à chaque fois l'arrête de poids minimum dont un sommet appartient à l'arbre courant. On part du sommet 1.

1) 1 - 4, poids 1

2) 1 - 2, poids 2

3) 4-6, poids 2

4) 4-5, poids 3

5) 2-3, poids 4

On a 5 arrêtes, on peut alors s'arrêter car on a V - 1 arrête dans le MST, V étant le nombre de sommet. 

On obtient ainsi le MST suivant :

![prim-graphe-resultat]({{site.url_complet}}/assets/algorithme/mst/prim-graphe-resultat.jpg)





### Alogrithme de Boruvka

- Le point de départ est une forêt vide ne contenant que les sommets du graphe, comme pour *Kruskal.*
- Pour chaque sommet de la forêt actuelle, on sélectionne l'arrête du plus petit poids relié au sommet.
- On contracte ("fusionne") les composantes obtenues en un seul sommet composante. On peut alors obtenir plusieurs composantes connexes.
- On répète le processus jusqu'à n'avoir qu'une seule composante.

Remarque : chaque arrête adjacente à un sommet doit avoir un poids différent. Il est tout à fait possible de modifier le poids des arrêtes adjacentes identiques afin que tous les poids soient différents.

#### Exemple 

![boruvka-graphe-initial]({{site.url_complet}}/assets/algorithme/mst/boruvka-graphe-initial.jpg)

On peut constater que le sommet 1 a deux arrêtes (1, 2) et (1,4) de poids identiques. On modifie alors ( en rouge) le poids de l'arrête (12) pour lui attribuer un poids de 1.1. C'est par conséquent l'arrête (1-4) qui va être choisie pour le sommet 1.

![boruvka-corrige]({{site.url_complet}}/assets/algorithme/mst/boruvka-corrige.jpg)

On peut appliquer **Boruvka** pour chaque sommet, ce qui a nous donner les arrêtes suivantes :

Sommet 1) 1 - 4

Sommet 2) 1 - 2

Sommet 3) 2 - 3

Sommet 4) 1 - 4

Sommet 5) 5 - 6

Sommet 6) 5 - 6

On obtient les composantes connexes suivantes :

![boruvka-composante]({{site.url_complet}}/assets/algorithme/mst/boruvka-composante.jpg)



On refait le même processus en choisissant l'arrête (3, 5) de poids 5, poids le plus petit et on obtient le MST suivant :

![boruvka-mst]({{site.url_complet}}/assets/algorithme/mst/boruvka-mst.jpg)



## Sources

**Général**

- [wikipedia.org - Arbre couvrant de poids minimal](https://fr.wikipedia.org/wiki/Arbre_couvrant_de_poids_minimal)
- Cours de *Graphes et réseaux* (GRE) enseigné à l'HEIG-VD en 2018
- Cours d'Algorithmes et structures de données 2 (ASD 2) enseigné à l'HEIG-VD en 2020.

**Boruvka**

- [boowiki.info - algorithme-boruvka](https://boowiki.info/art/les-algorithmes-sur-les-graphes/l-algorithme-boruvka.html)
- [team.inria.fr - Algorithme de Boruvka](https://team.inria.fr/coati/seminars-and-conferences/algothe/sessions/algorithme-de-boruvka/)

**Kruskal** 

- Visualiser la résolution de MST avec kruskal : [www.cs.usfca.edu - visualization - Kruskal](https://www.cs.usfca.edu/~galles/visualization/Kruskal.html)


**Graphe **

Les graphes en début d'article ont été réalisé avec cet outil en ligne. J'ai préféré faire le reste à la main car je ne le trouvais pas très pratique, mes graphes se décomposaient régulièrement.

- [https://csacademy.com/app/graph_editor/](https://csacademy.com/app/graph_editor/)



