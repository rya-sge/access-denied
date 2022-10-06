```
layout: post
title:  Encrypt a USB key on Windows with Bitlocker
date:   2022-10-06
last-update: 
categories: cryptographie 
tags: bitlocker aes xts-aes
description: This article details how to encrypt a USB drive on Windows with Bitlocker
image: /assets/article/windows/bitlocker/usb/bitlocker-usb-check.png
```

## Introduction

A USB key is small, it's moved (in the office, in your bag), and potentially it gets lost... By encrypting your USB key, you reduce the risk of someone accessing the data if you lose your USB key. On Windows, it is possible to encrypt a USB key with Bitlocker. On Windows 10 and later, Bitlocker uses 128-bit **XTS-AES** by default [2].

Warning  :

Bitlocker is an encryption tool offered by Windows, it will be difficult to decrypt your USB key on a Linux device. See reference for an example [3]

## Steps

### Encryption

You can encrypt with a password or to associate with a smart card and a pin if you have one.

![encryption-method]({{site.url_complet}}/assets/article/windows/bitlocker/usb/bitlocker-usb-encryption-method.PNG)

### Recovery option

Choose  your recovery option. If you have a password manager, you can store the recovery key in the password manager.

If you decide to save to a file, be aware where and how you store the file.

![recovery-key]({{site.url_complet}}/assets/article/windows/bitlocker/usb/bitlocker-usb-recovery-key.PNG)

### Choose what you want encrypt

For a better security, it is preferable to encrypt the entire drive.

![encryption-part]({{site.url_complet}}/assets/article/windows/bitlocker/usb/bitlocker-usb-encryption-part.PNG).

### Mode

The new mode of encryption (XTS-AES) is not ocmpatbiel with older version of Windows. If you encrypt a USB drive, it can be preferable to use a compatible mode.

![encryption-mode]({{site.url_complet}}/assets/article/windows/bitlocker/usb/bitlocker-usb-encryption-mode.PNG)

### Confirmation

If all is right, you can confirm the encryption.

![confirmation]({{site.url_complet}}/assets/article/windows/bitlocker/usb/bitlocker-usb-confirmation.PNG)

### End

![bitlocker-usb-end]({{site.url_complet}}/assets/article/windows/bitlocker/usb/bitlocker-usb-end.PNG)



### Check

You can then check if the device is encrypted and if you are able to unlock it.

![bitlocker-usb-check]({{site.url_complet}}/assets/article/windows/bitlocker/usb/bitlocker-usb-check.png)



## Reference

1. MICROSOFT, 2022a. BitLocker. *Microsoft | Learn*. Online. 13 July 2022. [Accessed 5 October 2022]. Retrieved from: [https://learn.microsoft.com/en-us/windows/security/information-protection/bitlocker/bitlocker-overview](https://learn.microsoft.com/en-us/windows/security/information-protection/bitlocker/bitlocker-overview)
2. MICROSOFT, 2022b. BitLocker settings reference. *Microsoft | Learn*. Online. 5 October 2022. [Accessed 5 October 2022]. Retrieved from: [https://learn.microsoft.com/en-us/mem/configmgr/protect/tech-ref/bitlocker/settings](https://learn.microsoft.com/en-us/mem/configmgr/protect/tech-ref/bitlocker/settings)
3. UNIVERSITÉ CLERMONT AUVERGNE, no date. *Déchiffrer un disque Bitlocker à l’aide de Kali-Linux*. Online. [Accessed 5 October 2022]. Retrieved from: [https://lmv.uca.fr/wp-content/uploads/2019/09/linux-dechiffrement-bitlocker.pdf](https://lmv.uca.fr/wp-content/uploads/2019/09/linux-dechiffrement-bitlocker.pdf)