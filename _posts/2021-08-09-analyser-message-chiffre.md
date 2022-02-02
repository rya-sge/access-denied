---
layout: post
title:  "Analyser un message chiffré [transposition/substitution]"
date:   2021-08-09
categories: cryptographie
tags: transposition substitution railfence vigenère césar bifid ractf
description: Cet article présente les manières d'analyser un message dont on ne connait pas la méthode de chiffrement employé. Il se concentre  sur les chiffrements classiques ":" substitution mono-alphabétique (César, Vigenère) et la transposition comme le chiffre de RailFence.
image: /assets/article/cryptographie/analyse-chiffrement/01-dcode-2.PNG
---



Cet article présente les manières d'analyser un message dont on ne connait pas la méthode de chiffrement employé. Il se concentre  sur les chiffrements classiques : substitution mono-alphabétique (César, Vigenère) et la transposition comme le chiffre de RailFence.



## Introduction

###  Traiter le texte 

Parfois il est nécessaire de traiter le message chiffré, boxentriq.com propose de nombreux outils pour cela, comme un qui supprime automatique les espaces.

Supprimer les espaces : [www.boxentriq.com - remove-spaces](https://www.boxentriq.com/code-breaking/remove-spaces)

Page avec tous les outils proposée : [www.boxentriq.com/code-breaking](https://www.boxentriq.com/code-breaking)



### Outils de résolutions (solver)

Ces différents sites ou logiciels proposent tout une gamme d'outils permettant de résoudre des messages chiffrés.

En ligne : 

- [http://www.cryptoprograms.com](http://www.cryptoprograms.com)
- [https://quipqiup.com](https://quipqiup.com)

Logiciel :

Cryptogram est à installé sur l'ordinateur : [Site web de l'éditeur]( https://sites.google.com/site/cryptocrackprogram/home?authuser=0)

Remarques :

En plus d'installer le logiciel, il faut aussi configurer les dictionnaires dans le menu Option

![05-options]({{site.url_complet}}/assets/article/cryptographie/analyse-chiffrement/05-options.PNG)

## Analyser le texte chiffré

### Avec des outils en ligne

Certains outils en ligne peuvent être utilisé pour faire une première analyse afin de connaitre quel chiffre a été utilisé. Ceux-ci ne garantissent pas toujours le résultat mais peuvent vous faire gagner du temps si elles fonctionnent.

- boxentriq.com propose un outil pour l'identification. Il ne fonctionne pas toujours mais si il trouve, cela sera un gain de temps considérable : [www.boxentriq.com - cipher-identifier](https://www.boxentriq.com/code-breaking/cipher-identifier)

- bionsgadget propose également un outil analyse, que je trouve plus efficace que boxentriq.com : [https://bionsgadgets.appspot.com](https://bionsgadgets.appspot.com/gadget_forms/refscore_extended.html)

### Manuellement

#### 1) Calculer l'indice de coïncidence

La première étape est de calculer l'indice de coïncidence. Celui-pourra indiquer si il s'agit d'une substitution ou d'une transposition, ainsi que de donner une idée sur la langue utilisée

Plus d'informations ici : [Wikipedia.org - Indice_de_coïncidence](https://fr.wikipedia.org/wiki/Indice_de_coïncidence)

On peut calculer l'indice de coïncidence avec dcode : [https://www.dcode.fr/indice-coincidence](https://www.dcode.fr/indice-coincidence)

Selon Wikipédia :

- Anglais : 0,0667
- Allemand : 0,0762
- Français :  0,0778



#### 2) Analyse de fréquence

Si l'indice de coïncidence  s'approche d'une langue connue, souvent l'anglais, alors on peut faire appel à une analyse de fréquence pour différencier un chiffre de substitution d'une transposition.

- Si vous avez la même fréquence des lettres que pour la langue d'origine du message chiffré, alors c'est probablement du chiffrement par transposition
- Sinon c'est du chiffrement par substitution

On peut calculer la fréquence des lettres avec dcode ou avec cryptage. Ce dernier propose une interface épurée; il sort les résultats pour chaque lettre et affiche également une comparaison avec le français.

- [cryptage.org - outil-crypto-frequences](https://www.cryptage.org/outil-crypto-frequences.html)

- [dcode.fr - frequency-analysis](https://www.dcode.fr/frequency-analysis)



## 2 familles de chiffrements classiques

### Substitution mono-alphabétique

Le chiffrement par substitution consiste à remplacer dans un message clair un ou plusieurs symboles par d'autres symboles, le plus souvent du même alphabet sans toucher à la structure du texte. Dans cet exemple, on a le **chiffrement de César** qui applique un chiffrement par décalage

Ces système de chiffrement conservent la **répartition** des fréquences des lettres. Par exemple, dans le français, la lettre 'e' a une grande fréquence d'apparition. Ainsi on peut supposer que le symbole ayant la plus haute fréquence correspond à la lettre 'e'.

Pour plus d'informations : [fr.wikipedia.org - Chiffrement_par_substitution](https://fr.wikipedia.org/wiki/Chiffrement_par_substitution)



Quelques outils pour décrypter le chiffrement par substitution

- **quipqiup** possède une interface épurée et clair. Le gros avantage c'est qu'il traite le texte déchiffré, on aura alors des phrases intelligibles : [https://quipqiup.com](https://quipqiup.com)

- Dcode fait aussi bien le travail. Néanmoins, il ne traite pas les espaces et le résultat ce qui peut entrainé une plus grande difficulté pour lire les résultats : [www.dcode.fr - monoalphabetic-substitution](https://www.dcode.fr/monoalphabetic-substitution)

- [cryptoprograms.com - monoalph](http://www.cryptoprograms.com/subsolve/monoalph)



#### Vigenere

Pour résoudre des messages chiffrés avec Vigenere, le site Gubulla propose un outil en ligne très efficace et en plusieurs langues : anglais, espagnol, français néerlandais et portugais.

Désavantage : Ne met pas en forme le texte, ce qui peut rendre plus difficile la compréhension du résultat.

Lien : [www.guballa.de - vigenere-solver](https://www.guballa.de/vigenere-solver)

Petite remarque : avec Vigenere, l'indice de coïncidence calculée sur le message chiffré peut être très loin de la langue d'origine. 

### Transposition

Le chiffrement par transposition consiste à **réarranger** les lettres sans pour autant remplacer les symboles par d'autres symboles comme dans le cas du chiffrement par substitution.

Par conséquent, avec un chiffrement par transposition, on garde la même fréquence des lettres que le message original et de facto, de la langue d'origine si le message était suffisamment long.

Un exemple connu de chiffre par transposition est le RailFence

Quelques sites proposent des outils pour résoudre automatiquement des chiffrements par transposition :

- [tholman.com - transposition](https://tholman.com/other/transposition/)
- [www.cryptoprograms.com - columnar](http://www.cryptoprograms.com/transsolve/columnar)



## Exemples

En 2020, le RACTF proposait 6 challenges consistant à décrypter des messages chiffrés, sans connaitre initialement la méthode de chiffrement employés.

J'ai pris comme source plusieurs write-ups écrits pour ces challenges, dont une vidéo qui résume très bien les différents moyens de résoudre les challenges : [How to Solve Classical Ciphers - RACTF Crypto 01-06 Writeup](https://www.youtube.com/watch?v=9Q5Q1Nn5Vss)



### Challenge 01

Ci-dessous, le message chiffré du challenge :

> ```
> LHFKM GMRHC FLMMJ ULXFY JOUFC
> FQFXF ZJOKP JOMMU LMRJT FFTBA
> JYFFR JZFXG AWJCB ULXFI FFKRF
> KPGKH RFWCF MTFRR LHFRI FMQFF
> KFLWU JMUFC IOMMU FYCFF KWCYB
> MFPQF CFHJG KHMJK FFPMJ PFWCY
> BMMUF TMJQJ CVJOM GZMUF CFRRJ
> TFMUG KHGAA FHLAH JGKHJ KLKPH
> FMMUF TLCCF RMFPK JCTLA YMUFW
> CYBMJ HCLBU YMFLT QJOAP PJMUG
> RIOMM UFYXF LAAPF WGPFP LMMUF
> RLTFM GTFMJ HJJKL KOLAA FLXFI
> FRMJZ AOWVL HFKMI MUFRF WCFMW
> JPFGR PJWOT FKMR
> ```



**Solution**

Le site [quipqiup.com](https://quipqiup.com) trouve immédiatement la solution 

![01-quipqiup]({{site.url_complet}}/assets/article/cryptographie/analyse-chiffrement/01-quipqiup.PNG)



Avec [dcode](https://www.dcode.fr/substitution-monoalphabetique), la solution est également trouvée, bien que je la trouve moins lisible car elle ne traite pas le résultat :

![01-dcode]({{site.url_complet}}/assets/article/cryptographie/analyse-chiffrement/01-dcode.PNG)

![01-dcode-2]({{site.url_complet}}/assets/article/cryptographie/analyse-chiffrement/01-dcode-2.PNG)



Un autre site permet aussi de trouver la solution mais supprime tous les espace ce qui rend sa compréhension plus difficile : [www.cryptoprograms.com/subsolve/monoalph](http://www.cryptoprograms.com/subsolve/monoalph)



Sources :

[https://github.com/deut-erium/WriteUps/tree/master/ractf/crypto/01](https://github.com/deut-erium/WriteUps/tree/master/ractf/crypto/01)

### Challenge 02

> ```
> KFCHT QXXKR FSAHX IEIYP GYZRX
> YXCKK OKYPG YLNIX BQRFU WFKEH
> LNYGC VBDGT NVIMF NJJLV HJEJY
> PGZFO IKQTL KBJKW TXNEH FVEHD
> PQJBG MYEYW IPLRC YNWPM YEKNV
> CEKRF SAHXI MFDVG XUTTG MRXIF
> TWUGW ZNUJZ UHEBJ FKWLV MDECT
> BTHGF VMTGP JFZUM FHFAM UNJPN
> HQQGJ AGTCV MYEVZ IPMZT NJAQY
> DOSJG DXZNL RWXXU AWTCP WZFDT
> CCKVA AFQNT SLJBM ETEAW FVIXR
> MJJBK GXPTN VVTED HTURE VTJYP
> GWVAQ DWWKJ DTSVK X
> ```



**Solution** 

Avec ce message chiffré, [quipqiup.com]( https://quipqiup.com) n'était pas capable de le casser directement.

En faisant un calcul de coïncidence, on obtient rien de tangible, là 0.04, bien éloigné de l'anglais et proche de l'aléatoire. J'ai utilisé l'outil en ligne  [planetcalc.com](https://fr.planetcalc.com/7944/) pour obtenir le résultat.

![02-planetcalc]({{site.url_complet}}/assets/article/cryptographie/analyse-chiffrement/02-planetcalc.PNG)

On ne peut pas exclure totalement le chiffrement mono-alphabétique car certains, comme Vigenere n'auront pas un indice de coïncidence proche de leur langue d'origine.

Vu qu'on n'a rien de tangible, on peut justement tester Vigenere. On teste avec [guballa.de - vigenere-solver](https://www.guballa.de/vigenere-solver ), qui arrive à casser rapidement le message et à décrypter le message en clair. Petit défaut : le texte obtenu n'est pas traité

Sources :

[https://github.com/deut-erium/WriteUps/tree/master/ractf/crypto/02](https://github.com/deut-erium/WriteUps/tree/master/ractf/crypto/02)

### Challenge 03

> GTHTI UHWSE ESLDL MUSDO RIROA SRGER TAETL VSSAT OAONT EGESN EOTNT GWPWI AFLAE OAIYA EAWTT SMENO LTOTO AIASH RKLIC EEEYO ESSUR NDBTA TNOES CMORI CEEIW GDECO HSGEN UISIY EAERE YBEHT LSRLN ADFHR SNTRM SUACU TTNRH EWDHA EEIIO RHEND PFOLT TGHSC DULWT NSNEO IHREG EWDEU IUEMC APIOI VORFT USTGP OOAOE HEOER BOEPB DHOBA BEATT ENESE WTBTK KEIED ICTIR EPOTE LLENO EEPIO IAAMC ONONY OEHEN ESIMT LFEIV CEHOR AHSET ETENL EHAPS TRRWE ISAVR HVGTL BPERI TOKER AIIPO HNIIC ONIAP BSMMF HAYST UDLYM NONPA REBTH MLOEH NRTEU ITOCY GSSIE VOEMR ODTEI IEENI CUOFS WFUMS TAHSP PCILD OOYUE ENBCE IAEVO TAEGK FSEAH DLCLE PNTIC CNPEE TNOLL AITME EOTCH RMRIT ANANH LWTOU EOECA AHUTO BTRSA UC



**Solution**

En calculant l'IC, on obtient **0.06618**, ce qui est proche de l'anglais.

On peut ensuite lancer une analyse de fréquence avec [dcode.fr - analyse-frequences]( https://www.dcode.fr/analyse-frequences) , on obtient des fréquences des lettres très semblable ce qui peut mettre sur la piste d'un chiffrement par transposition.

![03-analyse-frequence]({{site.url_complet}}/assets/article/cryptographie/analyse-chiffrement/03-analyse-frequence.PNG)



Un des chiffrements par transposition connu est le Rail Fence, il suffit alors de le tester avec un outil en ligne

Par exemple, celui-ci : [cryptoprograms.com - railfence](http://www.cryptoprograms.com/transsolve/railfence). Dcode propose aussi un outil en ligne capable de le résoudre : [dcode - chiffre-rail-fence](https://www.dcode.fr/chiffre-rail-fence)

![03-railfence]({{site.url_complet}}/assets/article/cryptographie/analyse-chiffrement/03-railfence.PNG)

Sources  :

- [https://ctftime.org/task/11924](https://ctftime.org/task/11924)

-  [https://github.com/deut-erium/WriteUps/tree/master/ractf/crypto/03](https://github.com/deut-erium/WriteUps/tree/master/ractf/crypto/03)


### Challenge 04

> IOINR EANED GTTEA INEHM ETEIS PMAON RGNHB BTTWE EEYSC YMOET PTOAL STEII DAHDE LTNUT MYSOR OTIEH WEGTN TMHAO YSYWW DNOAA EDHNG LNNHI OHDGE SSEOT YAEAD TENRY TITBO TRDHI OMALN DBTOO DEAUH EFTOR LREVO EHSMS CWEST AAADY EAIZN RRULT JNTWY SLAOO ATTHK UTYED GOOMY FOSEF SASDO NSNAH OSSIO EIBPS ALCCR NDTNO EMEHA STNEL TIHIE AABED PYTMP SOOED IUWHS LACEE TSORS NUICY RASMU TEEMR NSTME EYUXG STAOU OSEEY BIELR YNLEW CUTID THNES PGMKE YOYNE YEVYE UTSTY NOSEY RIAER NDSEC OLCRX XOYCE X
>
> The flag is the 2nd and 3rd 9 letter words concatenated together



**Solution :**

Ce challenge consistait en un chiffrement par transposition.

Malheureusement, je n'ai pas pu trouvé de résolveur en ligne.

Dans le write-up du challenge, ils utilisaient cet outil pour visualiser les différentes permutations :

[tholman.com - transposition](https://tholman.com/other/transposition/)

J'ai tenté cet outil, mais celui-ci ne trouvait pas la solution : [cryptoprograms.com - columnar](http://www.cryptoprograms.com/transsolve/columnar)

Sources :

[deut-erium - ractf/crypto/04](https://github.com/deut-erium/WriteUps/tree/master/ractf/crypto/04)

[medium.com/@Nicholaz99/ractf-2020-writeup](https://medium.com/@Nicholaz99/ractf-2020-writeup-1b567ddcb9ca#2839)

### Challenge 5

> DPKFC LISLA KWMDW ERUKW XPDID BRADA TRTMO LKKGN YUEIE LDEOC VRTUM FLCVG RBSVS DTHDK WMHOG TAECO MWEYM ITWOS SEFKF BEAWK SAEOK SRSNZ RNEOR LTHIS DWZCO RQSRA MYVSI RIRGE CZIDR MMVCR HGBYE WSLSO CWMBU LGKDA DELQU BWKLF CMWGQ RYSPA EZBDA PIRGW SQSFA CLUMA RVERU ILKBA ATNOF CKWWA TCKKI IUSWD EIAPK SWSGO HCFYM SDODS MUORA TDEKU NRRSG NETHD WPHRG AEODL LOEFH BEOWC QWNAO BRUWW CCHOS OLUAC CXPWA BEAWA ROHAR O 
>
> The flag ***\*is\**** the name ***\*of\**** the person mentioned ***\*in\**** the message



**Solution**

Le calcul de L'IC donne 0.04764, ce qui donne rien de tangible. On est plus proche de l'aléatoire que de l'anglais

Avec [boxentriq.com](https://www.boxentriq.com/code-breaking/cipher-identifier) suivant, on obtient une liste de chiffre possible

- [Vigenere Cipher](https://www.boxentriq.com/code-breaking/cipher-identifier#vigenere-cipher) (64 votes)
- [Beaufort Cipher](https://www.boxentriq.com/code-breaking/cipher-identifier#beaufort-cipher) (7 votes)
- [Columnar Transposition Cipher](https://www.boxentriq.com/code-breaking/cipher-identifier#columnar-transposition-cipher) (7 votes)
- etc.

On teste le beaufort, Vigenere et la transposition par colonne

 Pour le beaufort, on peut utiliser cet outil en ligne :  [www.boxentriq.com - beaufort-cipher](https://www.boxentriq.com/code-breaking/beaufort-cipher)

Aucun des trois ne donnent de résultat probant, je lance alors une analyse avec [bionsgadgets](  https://bionsgadgets.appspot.com/gadget_forms/refscore_extended.html), qui lui propose le chiffre de bifide.

- Bifid6 3
- Bifid7 4
- Seriatedpfair 5
- Cmbifid 5

Pour celui-ci je n'ai pas tout de suite trouvé de résolveur en ligne. En allant alors lire le [write-up](https://github.com/deut-erium/WriteUps/tree/master/ractf/crypto/05), j'ai pu voir qu'ils proposaient Cryptocrack, un logiciel à installer sur l'ordinateur : [cryptocrack - site web](https://sites.google.com/site/cryptocrackprogram/home?authuser=0)

Après l'installation, je lance le programme d'abord avec 4 puis ensuite 5. Là miracle j'obtient une solution ;)

Une autre possibilité, que j'ai découvert plus tard, est d'utiliser l'outil en ligne cryptoprogram, qui ne nécessite aucune installation :[www.cryptoprograms.com - bifid](http://www.cryptoprograms.com/othersolve/bifid)



Sources :

[https://github.com/deut-erium/WriteUps/tree/master/ractf/crypto/05](https://github.com/deut-erium/WriteUps/tree/master/ractf/crypto/05)

### Challenge 6

> It looks like someone already tried to crack ***\*this\**** message, but they destroyed all their work. They used a naff shredder though, and we were able to recover the number 143526. 
>
> BFPNU DXTEA IDDTK VDSSY NJCYC HETNS YDWVP ZWHBA FCMAN CDWOV IZJOB VTNLT NFPKM XIODY UMCJR XDPAZ QZFRB UXZLZ ZTLVD JJVAK EYMRT YTMHW XAMPX TWEKC WNSYH REYBG AZFRQ SMJNN XRBJM UVDZI CUFJX YIQSH JMXCV ABIDY SMQLN OPZGJ JFLUC SPPKS AYZMX OQYOS SNJLD CNJAM BLXYN BFLXC UAKOH HCBER IAWXE VXCGL BQONI LXWYA TYHMH GSOMF LEZMG EFCRQ TKWMF VWNGH XZZPX RWYWN NATZT GYAKV BKGLF BYBCZ IWOTK BEQJI LXONL TCYET BUDGJ FBTHT EVKCH XVEDX XPBXE NZEYG INKNM KYWXT XNEMO AOCRG XBGXQ XYWHQ IYXBO BEVDG ADNXT DFDYD GCFZN KGHHD WQKXY CFJII GSDJV FREIW QMNYP MXMKZ IZRBO BHDRB EASHY NXZXS GEHPE PMVLK WXEUU KAOMW OWJFD LBKHE

**Solution**

Avec l'outil  [bionsgadgets](  https://bionsgadgets.appspot.com/gadget_forms/refscore_extended.html), on obtient la liste des chiffres suivant:

- RunningKey 4
- Gromark 5
- Vigautokey 5
- Periodic gromark 5
- Nicodemus 6
- Progkey beaufort 6

La consigne fournit le nombre 143526 qu'on peut alors tester comme clé avec CryptoCrack pour le chiffre de Gromark, périodique. Le gromak simple n'ayant pas donné de résultat.

![06-crypto-crack]({{site.url_complet}}/assets/article/cryptographie/analyse-chiffrement/06-crypto-crack.PNG)

## Sources 

Outils :

- [www.boxentriq.com - cipher-identifier](https://www.boxentriq.com/code-breaking/cipher-identifier)
- [http://www.cryptoprograms.com](http://www.cryptoprograms.com)
- [https://quipqiup.com](https://quipqiup.com)
- [cryptocrack - site web](https://sites.google.com/site/cryptocrackprogram/home?authuser=0)

RACTF :

- [CTFTIME - RACTF](https://ctftime.org/event/1051/tasks/)
- [How to Solve Classical Ciphers - RACTF Crypto 01-06 Writeup](https://www.youtube.com/watch?v=9Q5Q1Nn5Vss)

Théorie :

- VERGNAUD, Damien, 2018.  *Exercices et problèmes de cryptographie*. 3e édition. Malakoff : DUNOD. ISBN 978-2-10-078461-5