---
layout: post
title:  "Android Studio - Récupérer le résultat d'une activité"
date:   2021-11-14
last-update: 
categories: programmation
tags: android kotlin activity
image:
description: Lancer une nouvelle activité et récupérer son résultat
---

Cet article décrit comment lancer une nouvelle activité puis récupérer son résultat dans **Android**.

Le lange de programmation utilisé est **Kotlin**

Le code dans son ensemble est disponible sur mon github : [rya-sge/AD-ressources - programmation/android/android-getActivityResult](https://github.com/rya-sge/AD-ressources/tree/master/programmation/android/android-getActivityResult)

## MainActivity

Lorsque l'utilisateur clique sur le bouton, on crée un nouvel `intent` sur *SecondActivity*. Les **intent**, comme leur nom l'indique, permettent de décrire une intension, une action que le système va réaliser. Ils permettent de communiquer entre deux activités distinctes.

```kotlin
val intent = Intent(this, SecondActivity::class.java)
```



Ensuite, pour exécuter *l'intent*, on appelle la fonction `getResult.launch` lorsque l'utilisateur clique sur le bouton. La seconde activité va alors exécuter son code et renvoyer le code résultant. Quant à la fonction`getResult`, celle-ci permet de récupérer le résultat de l'activité appelée et doit être déclarée dans la classe.

- Code pour écouter les événements sur le bouton

```kotlin
 button?.setOnClickListener()
        {
            val intent = Intent(this, SecondActivity::class.java)
            getResult.launch(intent)
        }
```

- Récupérer le résultat de *SecondActivity*


```kotlin
private val getResult =
        registerForActivityResult(
            ActivityResultContracts.StartActivityForResult()
        ) {
            //Execute when SecondActivity is finished
        }
```



## SecondActivity

```kotlin
val result: Int = Random.nextInt(0, 100)
val resultIntent = Intent()
resultIntent.putExtra("result", result.toString())
setResult(RESULT_OK, resultIntent)
finish()
```

La seconde activité génère un nombre aléatoire et le stocker dans la variable locale `result`.

Le programme créer un nouvel *intent* `resultIntent` afin de pouvoir renvoyer le nombre calculé à *MainActivity*. La fonction `putExtra` stocke sa valeur dans un Extra, appelé ici *result*.

le code résultat de l'activité est définit sur `RESULT_OK` en appelant la fonction `setResult`

## MainActivity

*SecondActivity* étant terminé, *MainActiviy* exécute la fonction `getResult`.

Celle-ci contient une condition permettant d'exécuter du code uniquement si le résultat de *SecondActivity* est OK. Dans le cas présent, cela consiste à afficher le nombre renvoyé par *SecondActivity* et le stocké dans la variable locale `value`. Comme dit dans le paragraphe plus haut, ce nombre est stocké dans l'extra " ". Pour récupérer sa valeur, on appelle la fonction `getStringExtra` en lui passant le nom de l'extra définit dans les *compagnion object*

```kotlin
if (it.resultCode == Activity.RESULT_OK) {
    val value = it.data?.getStringExtra(ExtraSecondActivity)
    val text: TextView = findViewById(R.id.textViewResult)
    text.setText(value)
}
```



## Sources 

- Documentation officielle : [developer.android.com - kotlin/Intent](https://developer.android.com/reference/kotlin/android/content/Intent)
- [stackoverflow.com - How to manage startActivityForResult on Android](https://stackoverflow.com/questions/10407159/how-to-manage-startactivityforresult-on-android)
- [stackoverflow.com - OnActivityResult method is deprecated, what is the alternative?](https://stackoverflow.com/questions/62671106/onactivityresult-method-is-deprecated-what-is-the-alternative)

