---
layout: post
title:  L'analyse de données avec pandas
date:   2022-03-07
last-update: 
categories: programmation ai
tags: machine-learning panda python
image: /assets/article/programmation/python/pandas/pandas-head.PNG
description: Pandas est une librairie python permettant de faire de l'analyse de donnée. Elle est beaucoup utilisée pour traiter les données dans le cadre du Machine Learning.
---



**Pandas** est une librairie python permettant de faire de analyse de donnée. Elle est beaucoup utilisée pour traiter les données dans le cadre du *Machine Learning*.

Cet article présente les principales fonctions de bases de cette librairie. Les exemples sont basées sur le cours Linkedin `pandas Essential Training` de *Jonathan Fernandes*

Site web de l'éditeur : [https://pandas.pydata.org](https://pandas.pydata.org)

Les exemples proviennent de la manipulation du fichier *Olympics.csv*  mis à disposition par le journal *theguardian.com* : [theguardian.com - olympic medal winner](https://www.theguardian.com/sport/datablog/2012/jun/25/olympic-medal-winner-list-data#data)

Le fichier n'était plus disponible, vous pouvez le retrouver sur mon github :  [https://github.com - file/olympics.csv](https://github.com/rya-sge/AD-ressources/blob/master/programmation/machine-learning/python/file/olympics.csv)

## Vocabulaire

Cette partie présente quelques termes à connaitre pour utiliser **panda**

`Dataframe ` : séquence d'une série qui partage le même index

La 1ère colonne correspond à l'index et les autres colonnes correspondent aux *Series*.

`Series` : tableau d'une dimension d'une donnée indexée

## Configuration

Cette partie présente les fonctions pour la mise en place de l'environnement de travail.

### Mise en place

- Importer

```python
import pandas as pd
```

- Afficher la version ainsi que les dépendances

```python
pd.show_versions()
```

- Afficher la version : `pd.__version__`

### Lecture de fichiers

- Importer un fichier CSV

Dans le code ci-dessous, on skipp de l'importation les 4 premières lignes du fichier avec  l'attribut `skiprows=4`

```python
data = pd.read_csv('data/olympics.csv', skiprows=4)
data.head()
```

La sortie sera la suivante :

![pandas-head]({{site.url_complet}}/assets/article/programmation/python/pandas/pandas-head.PNG)

- Autres types de fichiers

```python
read_excel()
read_json()
read_sql_table()
```



## Récupération d'information

- Obtenir les dimensions d'une *dataframe* (appelée data)

```python
data.shape
```

Sortie : (29216, 10)

Il est possible d'accéder à chaque élément du tuple de manière individualisé en précisant l'index. Ainsi :

```python
data.shape[0]
```

Sortie : 29216

```python
data.shape[1]
```

Sortie : 10

- Type d'une variable

Exemple 1 : avec une *dataframe*

```python
type(data)
```

Sortie : `pandas.core.frame.DataFrame`

Exemple 2 : avec une série

```python
type(data['City'])
```

Sortie : `pandas.core.series.Series`

- Afficher le contenu de la variable data

```python
data
```

- Afficher les informations

```python
data.info()
```

Sortie : 

![pandas-info]({{site.url_complet}}/assets/article/programmation/python/pandas/pandas-info.PNG)

- Afficher le contenu de la colonne *City* :  `data['City']`

- Affichage à partir du début
  
  - Les 4 premières lignes (par défaut)
  
  ```python
  data.head()
  ```
  
  - Les 3 premières lignes
  
  ```python
  data.head(3)
  ```

  - Afficher les 3 dernières lignes

```python
data.tail()
```

## Opération de base

### value_counts

Retourne un objet contenant le nombre de valeurs uniques

Sur une *dataframe* : [pandas.pydata.org - DataFrame.value_counts.html](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.value_counts.html)

Sur une série : [pandas.pydata.org - Series.value_counts.html](https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html)

Exemple

- Le nombre de médailles par Edition

```
data.Edition.value_counts()
```

Sortie :

```
2008    2042
2000    2015
2004    1998
1996    1859
[...]
Name: Edition, dtype: int64
```

- Le nombre de médailles en fonction du genre

  ```
  data.Gender.value_counts()
  ```

  Résultat :

  ```
  Men      21721
  Women     7495
  Name: Gender, dtype: int64
  ```

### Trier les valeurs

 `sort_values()` permet de tirer les valeurs

- D'une série

Documentation officielle de pandas : [pandas.pydata.org - sort_values.html](https://pandas.pydata.org/docs/reference/api/pandas.Series.sort_values.html)

- D'un *dataFrame*

Documentation officielle de pandas : [pandas.pydata.org - sort_values.html](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html)

Remarques : Il est nécessaire de déclarer une variable pour récupérer la valeur de retour

Exemple :

- Trier les entrées en fonction du nom de l'athlète

```
ath = data.Athlete.sort_values()
```

- Trier les entrée en fonction de l'Edition, puis ensuite du nom de Athlète.

```
data.sort_values(by=['Edition', 'Athlete'])
```



## Sources

- FERNANDES Jonathan, 2017. *pandas Essential Training* [en ligne].  Linkedin Learning. [Consulté en mars 2022]. Disponible à l'adresse [https://www.linkedin.com/learning/pandas-essential-training/](https://www.linkedin.com/learning/pandas-essential-training/)
- Documentation pandas : [https://pandas.pydata.org/docs/index.html](https://pandas.pydata.org/docs/index.html)