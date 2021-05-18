---

layout: post
title:  "Analyse de buffer overflow avec gcc"
date:   2021-05-18 
categories: sécurité reverse gcc
tags: gcc buffer-overflow reverse sécurité shellcode
---
Utilisation de l'outil gcc pour analyser des buffer overflows

## Configuration

Attention : Les manipulations suivants sont à faire dans un environnement dédié, par exemple une machine virtuelle. Elles rendent votre machine vulnérable à de potentielles attaques.

Désactiver l'ASLR : 

```bash
sudo bash -c "echo 0 > /proc/sys/kernel/randomize_va_space"
```

Le bash -c permet de conserver les droits sudo durant l'exécution de la commande.



Désactiver les protections sur la pile au moment de la compilation de votre programme c

```bash
gcc −fno−stack−protector -no-pie −z execstack −o prg prg.c

```

Explications des flags

| Flags gcc            | Explication                                                  |
| -------------------- | ------------------------------------------------------------ |
| -fno-stack-protector | Désactiver la protection sur la pile                         |
| execstack            | Autoriser l'exécution de la pile                             |
| -no-pie              | Ne pas produire de lien dynamique indépendant de l'exécutable |

Dans gdb, si vous voulez utiliser des shellcodes, il faut l'autoriser à ouvrir un processus fils.

```
(gdb) set follow-fork-mode parent
```



## GDB - List de commandes utiles

Voici les commandes utiles pour une analyse pas à pas

Les parties entre crochet [] doivent être remplacé par le contenu souhaité

| Commandes              | Explication                                                  |
| ---------------------- | ------------------------------------------------------------ |
| gdb ./buffer           | Lancer gdb avec le binaire                                   |
| b main                 | Mettre un breakpoint sur la fonction main                    |
| r [args] Ex : r aabbbb | Lancer le programme dans gdb avec les arguments args         |
| disas                  | Désassembler le programme                                    |
| c                      | Continuer le programme après s'être arrêté à un breakpoint   |
| finish                 | Continuer l'exécution jusqu'à après le retour de la fonction en cours. Utilise si vous voulez vous retrouver juste après un call |
| x/-10bs $ebp           | Afficher les 10 1ers bytes de la pile                        |
| x/s [adr]              | Affiche en string le contenu situé à l'adresse               |
| x/x [adr]              | Afficher le byte situé à l'adresse en hexa                   |



## Sources :

- Manuel GCC : [https://gcc.gnu.org/onlinedocs/gcc/Link-Options.html]( https://gcc.gnu.org/onlinedocs/gcc/Link-Options.html)
- Désactiver l'ASLR sur Ubuntu : [https://superuser.com/questions/127238/how-to-turn-off-aslr-in-ubuntu-9-10](https://superuser.com/questions/127238/how-to-turn-off-aslr-in-ubuntu-9-10)
- Articles sur les désactivation des protections du compilateur : [https://ubuntuplace.info/questions/316138/disable-stack-protection-on-ubuntu-for-buffer-overflow-without-c-compiler-flags]( https://ubuntuplace.info/questions/316138/disable-stack-protection-on-ubuntu-for-buffer-overflow-without-c-compiler-flags)
- Cours de sécurité logicielle suivi à l'HEIG-VD(M.Bost)