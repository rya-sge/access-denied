# Windows Registry

https://tryhackme.com/room/windowsforensics1

**Windows Registry:**

The Windows Registry is a collection of databases that contains the system's configuration data. This configuration data can be about the hardware, the software, or the user's information. It also includes data about the recently used files, programs used, or devices connected to the system. As you can understand, this data is beneficial from a forensics standpoint. Throughout this room, we will learn ways to read this data to identify the required information about the system. You can view the registry using regedit.exe, a built-in Windows utility to view and edit the registry. We'll explore other tools to learn about the registry in the upcoming tasks.

The Windows registry consists of Keys and Values. 

- When you open the `regedit.exe` utility to view the registry, the folders you see are Registry Keys. 
- Registry Values are the data stored in these Registry Keys.
-  A [Registry Hive ](https://docs.microsoft.com/en-us/windows/win32/sysinfo/registry-hives#:~:text=Registry Hives. A hive is a logical group,with a separate file for the user profile.)is a group of Keys, subkeys, and values stored in a single file on the disk.

**Structure of the Registry:**

The registry on any Windows system contains the following five root keys:

1. HKEY_CURRENT_USER
2. HKEY_USERS
3. HKEY_LOCAL_MACHINE
4. HKEY_CLASSES_ROOT
5. HKEY_CURRENT_CONFIG

You can view these keys when you open the `regedit.exe `utility. To open the registry editor, press the Windows key and the R key simultaneously. It will open a `run `prompt that looks like this:

![img](https://tryhackme-images.s3.amazonaws.com/user-uploads/61306d87a330ed00419e22e7/room-content/9d33389f2fd0445a63e75dce3f6d7a88.png)

In this prompt, type `regedit.exe `, and you will be greeted with the registry editor window. It will look something like this:

![img](https://tryhackme-images.s3.amazonaws.com/user-uploads/61306d87a330ed00419e22e7/room-content/e14ef3193fce1f4b35c37a96862d71da.png)

Here you can see the root keys in the left pane in a tree view that shows the included registry keys, and the values in the selected key are shown in the right pane. You can right-click on the value shown in the right pane and select properties to view the properties of this value.

Here is how Microsoft defines each of these root keys. For more detail and information about the following Windows registry keys, please visit [Microsoft's documentation ](https://docs.microsoft.com/en-US/troubleshoot/windows-server/performance/windows-registry-advanced-users).



| Folder/predefined key   | Description                                                  |
| ----------------------- | ------------------------------------------------------------ |
| **HKEY_CURRENT_USER**   | Contains the root of the configuration information for the user who is currently logged on. The user's folders, screen colors, and Control Panel settings are stored here. This information is associated with the user's profile. This key is sometimes abbreviated as HKCU. |
| **HKEY_USERS**          | Contains all the actively loaded user profiles on the computer. HKEY_CURRENT_USER is a subkey of HKEY_USERS. HKEY_USERS is sometimes abbreviated as HKU. |
| **HKEY_LOCAL_MACHINE**  | Contains configuration information particular to the computer (for any user). This key is sometimes abbreviated as HKLM. |
| **HKEY_CLASSES_ROOT**   | Is a subkey of `HKEY_LOCAL_MACHINE\Software `. The information that is stored here makes sure that the correct program opens when you open a file by using Windows Explorer. This key is sometimes abbreviated as HKCR.<br />This information is stored under both the HKEY_LOCAL_MACHINE and HKEY_CURRENT_USER keys. <br />- The `HKEY_LOCAL_MACHINE\Software\Classes `key contains default settings that can apply to all users on the local computer. <br />- The `HKEY_CURRENT_USER\Software\Classes `key has settings that override the default settings and apply only to the interactive user.<br />- The HKEY_CLASSES_ROOT key provides a view of the registry that merges the information from these two sources. <br />- HKEY_CLASSES_ROOT also provides this merged view for programs that are designed for earlier versions of Windows. <br />To change the settings for the interactive user, changes must be made under `HKEY_CURRENT_USER\Software\Classes `instead of under HKEY_CLASSES_ROOT.<br />To change the default settings, changes must be made under `HKEY_LOCAL_MACHINE\Software\Classes ` .If you write keys to a key under HKEY_CLASSES_ROOT, the system stores the information under `HKEY_LOCAL_MACHINE\Software\Classes `.<br />If you write values to a key under HKEY_CLASSES_ROOT, and the key already exists under `HKEY_CURRENT_USER\Software\Classes `, the system will store the information there instead of under `HKEY_LOCAL_MACHINE\Software\Classes `. |
| **HKEY_CURRENT_CONFIG** | -                                                            |

FAQ

What is the short form for HKEY_LOCAL_MACHINE?



> HKLM

If you are accessing a live system, you will be able to access the registry using regedit.exe, and you will be greeted with all of the standard root keys we learned about in the previous task. However, if you only have access to a disk image, you must know where the registry hives are located on the disk. The majority of these hives are located in the `C:\Windows\System32\Config` directory and are:

1. **DEFAULT** (mounted on `HKEY_USERS\DEFAULT`)
2. **SAM** (mounted on `HKEY_LOCAL_MACHINE\SAM`)
3. **SECURITY** (mounted on `HKEY_LOCAL_MACHINE\Security`)
4. **SOFTWARE** (mounted on `HKEY_LOCAL_MACHINE\Software`)
5. **SYSTEM** (mounted on `HKEY_LOCAL_MACHINE\System`)

**Hives containing user information:**

Apart from these hives, two other hives containing user information can be found in the User profile directory. For Windows 7 and above, a user’s profile directory is located in `C:\Users\<username>\` where the hives are:

1. **NTUSER.DAT** (mounted on HKEY_CURRENT_USER when a user logs in)
2. **USRCLASS.DAT** (mounted on HKEY_CURRENT_USER\Software\CLASSES)

The USRCLASS.DAT hive is located in the directory `C:\Users\<username>\AppData\Local\Microsoft\Windows`. 

![img](https://tryhackme-images.s3.amazonaws.com/user-uploads/61306d87a330ed00419e22e7/room-content/3ffadf20ebe241040d659958db115c2f.png)

The NTUSER.DAT hive is located in the directory `C:\Users\<username>\`.

![img](https://tryhackme-images.s3.amazonaws.com/user-uploads/61306d87a330ed00419e22e7/room-content/f3091f38f680b418f89cf79128d1933c.png)

Remember that NTUSER.DAT and USRCLASS.DAT are hidden files.**
**

**The Amcache Hive:**

Apart from these files, there is another very important hive called the AmCache hive. This hive is located in `C:\Windows\AppCompat\Programs\Amcache.hve`. Windows creates this hive to save information on programs that were recently run on the system.

**Transaction Logs and Backups:**

Some other very vital sources of forensic data are the registry transaction logs and backups. The transaction logs can be considered as the journal of the changelog of the registry hive. Windows often uses transaction logs when writing data to registry hives. This means that the transaction logs can often have the latest changes in the registry that haven't made their way to the registry hives themselves. The transaction log for each hive is stored as a .LOG file in the same directory as the hive itself. It has the same name as the registry hive, but the extension is .LOG. For example, the transaction log for the SAM hive will be located in `C:\Windows\System32\Config` in the filename SAM.LOG. Sometimes there can be multiple transaction logs as well. In that case, they will have .LOG1, .LOG2 etc., as their extension. It is prudent to look at the transaction logs as well when performing registry forensics.

Registry backups are the opposite of Transaction logs. These are the backups of the registry hives located in the `C:\Windows\System32\Config` directory. These hives are copied to the `C:\Windows\System32\Config\RegBack` directory every ten days. It might be an excellent place to look if you suspect that some registry keys might have been deleted/modified recently.