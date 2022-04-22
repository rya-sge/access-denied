---
layout: post
title:  "Conversions entre format de données en python(byte, string, int)"
date:   2021-08-05
categories: programmation
tags: python
description: Cet article décrit différentes façons de convertir des données représentées dans des formats différents en python, par exemple des bytes en int
image:
---



Cet article décrit différentes façons de convertir des données représentées dans des formats différents en python : byte à entier, string à byte, hexa string à byte, etc.

Lors des CTF(Capture the flags), il m'arrivait souvent de perdre du temps dans les conversion et de me mélanger les pinceaux, d'où cet article pour faciliter la compréhension.

## Conversion int <->Bytes

### Nativement

#### int -> bytes

Python3 possède la fonction `int.``to_bytes`(*length*, *byteorder*, ***, *signed=False*) qui permet de convertir un entier en bytes. Elle est intéressante si on souhaite s'assurer de la taille en byte de la chaîne résultante.

- `length`: Longueur de la chaîne de byte résultante
- `byteorder` : Il faut pour cela spécifier si l'ordre est big ou little endian.

Exemple 

Le code suivant :

```python
integer = 2000
print("big : ", (integer).to_bytes(2, byteorder='big'))
print("little : ", (integer).to_bytes(2, byteorder='little'))
```

produira la sortie suivante :

> big :  b'\x07\xd0' 
>
> little :  b'\xd0\x07'

Sources :

- [https://docs.python.org/fr/3.7/library/stdtypes.html](https://docs.python.org/fr/3.7/library/stdtypes.html)

#### bytes -> int

>  `int.``from_bytes`(*bytes*, *byteorder*, ***, *signed=False*)

Dans le sens inverse, on peut aussi convertir des bytes en int.

```python
byteString = b"test"
print("big :", int.from_bytes(b'\x00\x10', byteorder='big'))
print("little :", int.from_bytes(b'\x00\x10', byteorder='little'))
print("big : ", int.from_bytes(byteString, byteorder='big'))
```

produira la sortie suivante :

> big : 16
>
> little : 4096
>
> big :  1952805748

### Avec la librairie Crypto

La librairie *Crypto.Util.number* permet d'effectuer des conversions (long en bytes et inversement) sans devoir indiquer le nombre de bytes résultant.

- Installation : [pycryptodome](https://pypi.org/project/pycryptodome/)
- Importation de la librairie

```python
from Crypto.Util.number import long_to_bytes, bytes_to_long
```

- Exemple

> ```python
> byteString = b"test"
> integer = 2000
> print("Byte -> int : ", byteString, "->", bytes_to_long(byteString))
> print("int -> Byte : ", integer, "->",long_to_bytes(integer))
> ```

produira la sortie suivante :

> Byte -> int :  b'test' -> 1952805748
>
> int -> Byte :  2000 -> b'\x07\xd0'



### Misc 

Appliqués la fonctions *bytes* sur un entier va simplement construire un byte avec le nombre d'octets spécifiés par le nombre. Elle ne va pas convertir le nombre en bytes.

```python
a = 0x10
b = bytes(a)
print("a = ", a, "b = ", b)
```

produira la sortie suivante :

```python
a =  16 b = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
```



## int <-> string

Pour ce faire, python3 implémente déjà nativement des fonctions :

- string -> int : *str(...)*
- int -> string : *int(...)*

```python
integer = 2000
str_integer = "2000"
print("int -> string", integer,  "->",str(integer))
print("string -> int : ", int(str_integer))
```

produira la sortie suivante :

> int -> string 2000 -> 2000
> string -> int :  2000

Avertissement :

Il faut que la string représente un nombre entier. Par exemple, le code suivant :

```python
Astring = "A_String"
print(int(Astring ))
```

produira l'erreur suivante :

> ValueError: invalid literal for int() with base 10: 'A_String'



## int <-> hex

Pour convertir des nombres hexadécimaux sous forme de string en  int et inversement, il existe les fonctions suivantes :

- int(...)
  - Il est nécessaire de préciser la base utilisée pour la conversion, avec des hexa, il s'agit ici de la base 16

Ressources complémentaires : [stackoverflow.com - Convert hex string to int in Python](https://stackoverflow.com/questions/209513/convert-hex-string-to-int-in-python)

- hex(...)

Le code suivant :

```python
integer = 2000
str_hex = "0x20"
print("string hexa -> int : ", str_hex, "->" , int(str_hex, 16))
print("int -> string hexa : ", integer, "->" , hex(integer))
```

produira la sortie suivante :

> string hexa -> int :  0x20 -> 32
>
> int -> string hexa :  2000 -> 0x7d0

## hexa string <-> bytes



### hexa string -> bytes

#### bytes.fromhex(string)

Il s'agit d'une fonction native fournie par python permettant de convertir un nombre hexa sous forme de string en byte.

Par exemple, le code suivant :

```python
str_hex = "0x20"
StringHexa = "0x42"
StringHexa2 = "42"

print("hex string -> bytes : ", str_hex[2:], "->", bytes.fromhex(str_hex[2:]))
print("hex string -> bytes : ", str_hex[2:], "->", bytes.fromhex(str_hex[2:]))
print("hex string -> bytes : ", StringHexa[2:], "->",bytes.fromhex(StringHexa[2:]))
print("hex string -> bytes : ", StringHexa[2:], "->", bytes.fromhex(StringHexa2))

```

Produit la sortie suivante :

> hex string -> bytes :  20 -> b' '
>
> hex string -> bytes :  20 -> b' '
>
> hex string -> bytes :  42 -> b'B'
>
> hex string -> bytes :  42 -> b'B'



On peut constater que la transformation de 0x20 en byte ne donne rien car cette valeur n'a aucun sens en ascii.

Au contraire de 0x42 qui donne B

Avertissement :

Le nombre hexa, qui est sous format string, ne doit pas contenir le "0x" sinon cela provoquera l'erreur suivante :

> ValueError: non-hexadecimal number found in fromhex() arg at position 1

Dans le code d'exemple ci-dessus, j'ai ajouté [2:] pour ne  pas prendre le "0x"



Ressources complémentaires :

- Documentation python : [https://docs.python.org/fr/3.7/library/stdtypes.html](https://docs.python.org/fr/3.7/library/stdtypes.html)

- [Convertir hexadécimal en octet en Python](https://www.delftstack.com/fr/howto/python/python-convert-hex-to-byte/)
- [https://200ok.ch - hexlify() and unhexlify()](https://200ok.ch/posts/2018-12-09_unhexlify.html)

## byte hexa string <-> bytes

### binascii

La librairie binascii, comme son nom l'indique permet des conversions ascii <-> bytes avec les fonctions *unhexlify* et *hexlify*. Par exemple, le code suivant :

```python
print("Hexa number -> byte string :", binascii.unhexlify(byteStringHexa))
print("byte string -> hexa number :", binascii.hexlify(byteString))
```

produira la sortie suivante :

> hex string -> byte : b'42' -> b'B'
>
> byte string -> hexa number : b'test' -> b'74657374'



Sources : [https://docs.python.org/3/library/binascii.html]( https://docs.python.org/3/library/binascii.html)

## Sources

- Documentation officielle de python :[https://docs.python.org/fr/3.7/library/stdtypes.html](https://docs.python.org/fr/3.7/library/stdtypes.html)
- [stackoverflow.com - Convert hex string to int in Python](https://stackoverflow.com/questions/209513/convert-hex-string-to-int-in-python)
- https://docs.python.org/fr/3.7/library/stdtypes.html)

- [Convertir hexadécimal en octet en Python](https://www.delftstack.com/fr/howto/python/python-convert-hex-to-byte/)
- [https://200ok.ch - hexlify() and unhexlify()](https://200ok.ch/posts/2018-12-09_unhexlify.html)
- [https://docs.python.org/3/library/binascii.html]( https://docs.python.org/3/library/binascii.html)