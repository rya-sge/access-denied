https://medium.com/@RosanaFS/ntfs-analysis-tryhackme-walkthrough-b6ba1fc5bbf9

## Key File Paths and Details



The following table outlines the paths for crucial files within the Windows system:

| File Name    | Full Path                                                  |
| ------------ | ---------------------------------------------------------- |
| SYSTEM       | `C:\Windows\System32\config\SYSTEM`                        |
| SECURITY     | `C:\Windows\System32\config\SECURITY`                      |
| SOFTWARE     | `C:\Windows\System32\config\SOFTWARE`                      |
| SAM          | `C:\Windows\System32\config\SAM`                           |
| NTUSER.DAT   | `C:\Users\[Username]\NTUSER.DAT`                           |
| USRCLASS.DAT | `C:\Users\[Username]\AppData\Local\Microsoft\Windows\UsrC` |

https://github.com/vm32/Full-Disk-Image

https://github.com/vm32/Full-Disk-Image

https://hackmd.io/@M4shl3/ISITDTU-CTF-2024-Official-Forensics-Writeups

https://hackmd.io/@M4shl3/ISITDTU-CTF-2024-Official-Forensics-Writeups

https://yeahihaveaquestion.com/2024/05/08/day-3-of-windows-forensic-examinations-master-file-table/

https://github.com/th3c0rt3x/CyberTalents/blob/main/%5BMEDIUM%5D%20MFT.md

## Persistence

https://faresbltagy.gitbook.io/footprintinglabs/practical-windows-forensics/finding-evidence-of-persistence-mechanisms

**AutoRun keys:** They are a common persistence mechanism used by attackers to maintain access to a compromised system. They are registry entries that specify programs or scripts that are automatically executed upon system boot or user login.

- `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`
- `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce`
- `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`
- `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce`

Let's open `**SOFTWARE**` and `**NTUSER.DAT**` hives using Registry Explorer.

### WMI forensics

SU5TX1BBUlQze1dNSV9BbHdheXNfRG9lc19UaGVfSm9ifQ

INS_PART3{WMI_Always_Does_The_Job}

https://www.hackthebox.com/blog/perseverance-biz-ctf-2022-forensics-writeup

https://github.com/davidpany/WMI_Forensics#

https://github.com/mandiant/flare-wmi

### SHellbags

ShellBags is a feature in Microsoft Windows operating systems that is used to maintain and store information about how folders are displayed and customized in Windows Explorer. It helps Windows remember various settings for individual folders, such as the view mode (e.g., details view, icon view), icon positions, and other folder-specific settings.

ShellBags are stored as a highly nested and hierarchal set of subkeys in the **UsrClass.dat**

**Tool used** to solve this is **ShellBags Explorer** (from the Zimmerman Tools)

https://medium.com/@clumpstar/windows-forensics-dfir-029098add076

https://systemweakness.com/windows-forensics-analysis-analyzing-forensics-artifacts-to-uncover-system-compromise-and-rdp-b4617edfd132

### GlobalFlags image file technique was used to setup persistence

https://systemweakness.com/windows-forensics-analysis-analyzing-forensics-artifacts-to-uncover-system-compromise-and-rdp-b4617edfd132