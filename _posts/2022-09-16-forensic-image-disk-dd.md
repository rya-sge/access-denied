---
layout: post
title: Forensic analysis on a disk image (dd)
date:   2022-09-16
locale: en-GB
lang: en
last-update: 
categories: security
tags: forensic mount dd
description: Presentation of a list of tools to perform a forensic analysis on a disk image (minfo, fls, mount, photorec, ...).
isMath: false
image: 
---

If you have a disk image file (dd file), here is a presentation of some tools to perform a forensic analysis. You can find more information about this extension here [[WhatIsFileExtension](https://www.whatisfileextension.com/dd/)].

## Retrieve information

- file

Determine file type

Documentation : [linux.die.net/man/1/file](https://linux.die.net/man/1/file)

```bash
 file <filename>.dd
```

- minfo

Print the parameters of a MSDOS filesystem

Documentation : [linux.die.net/man/1/minfo](https://linux.die.net/man/1/minfo)

```bash
minfo -i  <filename>.dd
```

- fstat

Get file status

Documentation : [linux.die.net/man/3/fstat](https://linux.die.net/man/3/fstat)

```bash
fstat <filename>.dd
```

Reference : [[Azad 2020b](https://linuxhint.com/usb_forensics/)]

### List files - Fls

With the fls command you can list the files contained in the disk image

Manpage : [sleuthkit.org/sleuthkit/man/fls.html](http://www.sleuthkit.org/sleuthkit/man/fls.html)

- fat32


```bash
fls -rp -f fat32 <filename>.dd
```

- NTFS


```bash
fls -rp -f ntfs <filename>.dd
```

If the files is preceded by an *, it is a deleted files

Reference : [[Azad 2020b](https://linuxhint.com/usb_forensics/)]

## Mount the dd image

You can mount the image with the command `mount`.

Documentation : [linux.die.net/man/8/mount](https://linux.die.net/man/8/mount)

```bash
mkdir /mnt/image
sudo mount -o loop <filename>.dd /mnt/image
```

Warning: do not mount the image on an existing directory containing files, they will be deleted!!!

Reference : [[Mohan 2016](https://technewskb.com/mount-dd-image-linux-using-terminal-commands/)]

## Recover Files - Photorec

Photorec is a utility to recover files from a disk image. The interest of photorec is that it also recovers deleted files. You can find a presentation of the tool here :  [cgsecurity.org - PhotoRec](https://www.cgsecurity.org/wiki/PhotoRec)

```bash
photorec <filename>.dd
```

Reference : [[Sharma 2021]([https://www.tomshardware.com/how-to/recover-deleted-files-from-any-drive-in-linux](https://www.tomshardware.com/how-to/recover-deleted-files-from-any-drive-in-linux))]



## Reference 

1. AZAD, Usama, 2020a. How to Use Kali Linux Forensics Mode. *LinuxHint*. Online. 2020. [Accessed 16 September 2022]. Retrieved from: [https://linuxhint.com/kali_linux_forensics_mode/](https://linuxhint.com/kali_linux_forensics_mode/)
2. AZAD, Usama, 2020b. USB Forensics. *LinuxHint*. Online. 2020. [Accessed 16 September 2022]. Retrieved from: [https://linuxhint.com/usb_forensics/](https://linuxhint.com/usb_forensics/)
3. MOHAN, Shini, 2016. Solution To Mount DD Image In Linux OS. *TechNewsKB*. Online. 8 December 2016. [Accessed 16 September 2022]. Retrieved from: [https://technewskb.com/mount-dd-image-linux-using-terminal-commands/](https://technewskb.com/mount-dd-image-linux-using-terminal-commands/)
4. SHARMA, Shashank, 2021. How To Recover Deleted Files From Any Drive in Linux. *tom’sHardware*. Online. 21 August 2021. [Accessed 16 September 2022]. Retrieved from: [https://www.tomshardware.com/how-to/recover-deleted-files-from-any-drive-in-linux](https://www.tomshardware.com/how-to/recover-deleted-files-from-any-drive-in-linux)
5. WHATISFILEEXTENSION, no date. What is DD File Extension? Understanding Forensic DD Image. *WhatIsFileExtension*. Online. [Accessed 16 September 2022]. Retrieved from: [https://www.whatisfileextension.com/dd/](https://www.whatisfileextension.com/dd/)