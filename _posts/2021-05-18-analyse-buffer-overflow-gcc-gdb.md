---

layout: post
title:  "Analyse de buffer overflow avec GCC et GDB"
date:   2021-05-18 
categories: sécurité reverse 
tags: gcc gdb buffer-overflow reverse shellcode
description: Compilation avec gcc et commandes de base de GDB
---
Création de l'exécutable à tester avec **GCC** puis présentation des principales commandes de **GDB** pour analyser des buffer overflows

## Configuration

Attention : Les manipulations suivants sont à faire dans un environnement dédié, par exemple une machine virtuelle. Elles rendent votre machine vulnérable à de potentielles attaques.

Désactiver l'ASLR : 

```bash
sudo bash -c "echo 0 > /proc/sys/kernel/randomize_va_space"
```

Le bash -c permet de conserver les droits sudo durant l'exécution de la commande.

### Compilation avec GCC

Désactiver les protections sur la pile au moment de la compilation de votre programme c

```bash
gcc -m32 −fno−stack−protector -no-pie −z execstack −o prg prg.c

```

Le flag -m32 nécessite, sur Ubuntu d'avoir installer gcc multilib

```bash
sudo apt-get install gcc-multilib
```

Source :  [https://askubuntu.com/questions/453681/gcc-wont-link-with-m32]( https://askubuntu.com/questions/453681/gcc-wont-link-with-m32)



Explications des flags

| Flags gcc            | Explication                                                  |
| -------------------- | ------------------------------------------------------------ |
| -fno-stack-protector | Désactiver la protection sur la pile                         |
| execstack            | Autoriser l'exécution de la pile                             |
| -no-pie              | Ne pas produire de lien dynamique indépendant de l'exécutable |
| -m32                 | Pour compiler en 32 bits                                     |

Dans gdb, si vous voulez utiliser des shellcodes, il faut l'autoriser à ouvrir un processus fils.

```
(gdb) set follow-fork-mode parent
```

**Vérification :**

```bash
readelf -l nom_programme
```

Puis sous GNU_STACK, vérifier que le flag est mis à RWE.

## GBD - Liste de commandes

### Commande de base

Voici les commandes utiles pour une analyse pas à pas

Les parties entre crochet [] doivent être remplacé par le contenu souhaité

| Commandes              | Explication                                                  |      |
| ---------------------- | ------------------------------------------------------------ | ---- |
| gdb ./buffer           | Lancer gdb avec le binaire                                   |      |
| b main                 | Mettre un breakpoint sur la fonction main                    |      |
| b *0xFFFF8765          | Breakpoint à une adresse. Ne pas oublier de mettre *         |      |
| r [args] Ex : r aabbbb | Lancer le programme dans gdb avec les arguments args         |      |
| disas                  | Désassembler le programme                                    |      |
| c                      | Continuer le programme après s'être arrêté à un breakpoint   |      |
| finish                 | Continuer l'exécution jusqu'à après le retour de la fonction en cours. Utilise si vous voulez vous retrouver juste après un call |      |
| quit                   | quitter gdb                                                  |      |
| kill                   | stopper l'exécution du programme                             |      |

### Commandes pour une analyse avancée

| CMD                   | Explication                                                  |
| --------------------- | ------------------------------------------------------------ |
| x/-10bs $ebp          | Afficher les 10 1ers bytes de la pile                        |
| x/s [adr]             | Affiche en string le contenu situé à l'adresse               |
| x/x [adr]             | Afficher le byte situé à l'adresse en hexa                   |
| p/x $ebp              | Obtenir l'adresse de ebp. Utilise pour ensuite écraser la valeur de eip, situé 4 byte plus loin(si adresse 32 bits) |
| p/s 0x804b048         | Afficher la string située à l'adresse 0x804b048. Utile pour print des inputs/buffers |
| x/w [adr]             | Affiche 8 bytes du contenu de adr                            |
| info symbol 0x804a1e0 | Obtenir le symbole correspondant à l'adresse. C'est pratique si on a par exemple des movl avec des pointeurs de fonctions et qu'on voudrait savoir quel est le nom de la fonction correspondante |

Analyse du programme

| CMD            |                                               |
| -------------- | --------------------------------------------- |
| info frame     | Afficher infos sur la pile                    |
| info functions | Afficher toutes les fonctions et leur adresse |
|                |                                               |



## Astuces

Il est possible de passer du code python en argument dans gdb. Ici cela aura pour résulta tde passer AAAAAAAAAA en argument du programme

```
run `python2 -c 'print("A" * 10)'`
```



Si vous souhaitez avoir la notation assembleur d'intel, vous pouvez configurer cela avec la commande suivante :

```
set disassembly-flavor intel
```



## Sources 

- Manuel GCC : [https://gcc.gnu.org/onlinedocs/gcc/Link-Options.html]( https://gcc.gnu.org/onlinedocs/gcc/Link-Options.html)
- Désactiver l'ASLR sur Ubuntu : [https://superuser.com/questions/127238/how-to-turn-off-aslr-in-ubuntu-9-10](https://superuser.com/questions/127238/how-to-turn-off-aslr-in-ubuntu-9-10)
- Articles sur les désactivation des protections du compilateur : [https://ubuntuplace.info/questions/316138/disable-stack-protection-on-ubuntu-for-buffer-overflow-without-c-compiler-flags]( https://ubuntuplace.info/questions/316138/disable-stack-protection-on-ubuntu-for-buffer-overflow-without-c-compiler-flags)
- [HACKING] 01. Tuto exploitation d'un Buffer Overflow : [https://www.youtube.com/watch?v=V7Gdc32XRhA](https://www.youtube.com/watch?v=V7Gdc32XRhA)
- Cours de sécurité logicielle enseigné à l'HEIG-VD en 2021
