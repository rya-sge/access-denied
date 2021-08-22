---
layout: post
title:  "Les wrappers de fonctions en C++ avec std::function"
date:   2021-08-13
categories: programmation
tags: c++ wrapper std::function généricité dictionnaire
description: Cet article introduit l'utilisation des wrappers de fonctions en c++, apparu avec C++11. Le concept sera vu à travers l'implémentation d'un dictionnaire et le wrapper std::function.
image: 
---

Cet article illustre l'utilisation des **wrappers de fonctions** en c++, apparu avec C++11.

Lors d'un laboratoire effectué dans le cadre d'un cours à l'HEIG, il était demandé d'implémenter un dictionnaire et de pouvoir effectuer des opérations sur celui-ci comme retrouver un mot, insérer un nouveau mot ou en supprimer. Finalement, le but final était d'implémenter un correcteur orthographique en **C++**.

Dans le cas présent, le code a été édulcoré pour se concentrer uniquement sur les *wrappers* de fonctions à travers la classe *DictionaryContainer* qui représente un dictionnaire et les opérations qu'on peut effectuer sur celui-ci. Plutôt que de déterminer un conteneur fixe pour le dictionnaire comme *vector*, l'objectif était de laisser libre le choix à l'utilisateur de la classe de choisir le conteneur. C'est là qu'entre en matière les **wrappers de fonctions**.





## Etape 1 - Classe conteneur

La classe **DictionaryContainer** est notre classe *wrapper*. 

- Le type de donnée contenu dans le dictionnaire est définit par le *template* T. On peut dès lors avoir aussi bien des entiers , des strings que des objets dans notre dictionnaire. 
- Une entrée dans le dictionnaire est représenté par le terme *key*. 

### Fonctions publiques

Les trois opérations que la classe va fournir publiquement sont :

- *contains* pour savoir si la clé est présente dans le dictionnaire

  ```c++
  bool contains(const T &key) const
  ```

- *insert* pour insérer la clé dans le dictionnaire

```c++
void insert(const T &key) const
```

- *erase* pour supprimer la clé du dictionnaire

  ```c++
   void erase(const T &key) const
       
  ```



Ce qui donne :


```c++
public:
  
    bool contains(const T &key) const {  // A compléter // 
    }

    void insert(const T &key) const { // A compléter // 
    }
   
    void erase(constT &key) const {// A compléter // 
    }
};
```

Ces trois opérations vont appeler les fonctions correspondante du conteneur choisi. Par exemple, pour un conteneur *vector*, la fonction *insert* va appeler *push_back*.  Le paragraphe suivant décrit cette implémentation

### Fonctions privées

Pour implémenter les fonctions privées, on aura besoin du wrapper *std::function*. Les fonctions privées seront appelées par les fonctions publiques de la classe et ne seront pas visible à l'extérieur de la classe.

Vu que chaque fonction publique appelle une fonction privée, il y aura aussi 3 fonctions privées

- *contains_inside* pour savoir si la clé est présente dans le dictionnaire
- *insert_inside* pour insérer la clé dans le dictionnaire
- *erase_inside* pour supprimer la clé du dictionnaire



Pour définir une fonction renvoyant un booléean et prenant en paramètre une clé de type *T*

```c++
std::function<bool(const T &key)>;
```

Si elle ne renvoie aucune valeur de retour, le type de la fonction est *void*

```c++
std::function<void(const T &key)>;
```



Ce qui donne :

```c++
template<typename T>
class DictionaryContainer {

    using boolFunction =  std::function<bool(const T &key)>;
    using voidFunction =  std::function<void(const T &key)>;

    const boolFunction contains_inside;
    const voidFunction insert_inside;
    const voidFunction erase_inside;
```



Si on reprend le code plus haut,  la fonction publique *contains* va être complété comme suit :

```c++
 bool contains(const T &key) const {
        return contains_inside(key);
 }
```



### Constructeur

Le constructeur prend 3 fonctions en paramètre afin d'initialiser les 3 fonctions privées :

- contaisFunction
- insertFunction
- eraseFunction

```c++
 DictionaryContainer(const boolFunction &containsFunction, const voidFunction &insertFunction,
                        const voidFunction &eraseFunction)
            : contains_inside(containsFunction), insert_inside(insertFunction), erase_inside(eraseFunction) {}
```





### Code de la classe

Ci-dessous, le code complet de la classe *DictionaryContainer*.

```c++
template<typename T>
class DictionaryContainer {

    using boolFunction =  std::function<bool(const T &key)>;
    using voidFunction =  std::function<void(const T &key)>;

    const boolFunction contains_inside;
    const voidFunction insert_inside;
    const voidFunction erase_inside;

public:

    DictionaryContainer(
        const boolFunction &containsFunction, 
        const voidFunction &insertFunction,
        const voidFunction &eraseFunction) : contains_inside(containsFunction), insert_inside(insertFunction), erase_inside(eraseFunction) {}

  
    bool contains(const T &key) const {
        return contains_inside(key);
    }

    /**
     * @brief Appelle la fonction d'insertion avec la clé donnée
     * @param key
     */
    void insert(const T &key) const {
        insert_inside(key);
    }

    /**
     * @brief Delete a key from the dictionary
     * @param key
     */
    void erase(const T &key) const {
        erase_inside(key);
    }
};
```

## Etape 2 - fonction de test

Pour créer un objet de la classe, il suffit de le créer en lui passant en paramètre les fonctions correspondantes au conteneur choisi.

### unordered_set

Avec unordered_set, les fonctions de recherche, insertion et de suppression sont *find*, *insert* et *erase*

```c++
void testUnordered(){

    // Creation
    unordered_set<string> test;
    DictionaryContainer<string> dc([&test](const string &KEY) { return test.find(KEY) != test.end(); },
                                   [&test](const string &KEY) { test.insert(KEY); },
                                   [&test](const string &KEY) { test.erase(KEY); });
    dc.insert("Test");
    dc.insert("Alfred");
    dc.insert("Gimmove");
    assert(dc.contains("Gimmove") == true);
    dc.erase("Gimmove");
    assert(dc.contains("Gimmove") == false);
}
```



### vector

```c++
	// Creation
    vector<string> test;
    DictionaryContainer<string> dc([&test](const string &KEY) { return binary_search(test.begin(), test.end(), KEY); },
                                   [&test](const string &KEY) { test.push_back(KEY); },
                                   [&test](const string &KEY) { test.erase(lower_bound(test.begin(), test.end(), KEY)); });

    dc.insert("Test");
    dc.insert("Alfred");
    dc.insert("Gimmove");
    sort(test.begin(), test.end());
    assert(dc.contains("Gimmove") == true);
    dc.erase("Gimmove");
    assert(dc.contains("Gimmove") == false);
```

Avec *vector*, les fonctions de recherche, d'insertion et de suppression sont *binary_search*, *push_back* et *erase*.

A noter que l'utilisation de *binary_search* et *lower_bound* est conditionné au fait que le *vector* est trié, par exemple en appliquant *sort.*

## Source 

- Cours d'Algorithmes et structures de données 2 enseigné à l'HEIG-VD en 2020.

- [www.cplusplus.com - std::function](https://www.cplusplus.com/reference/functional/function/)