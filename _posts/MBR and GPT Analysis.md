https://tryhackme.com/room/mbrandgptanalysis

# MBR and GPT Analysis

https://tryhackme.com/room/mbrandgptanalysis

**MBR** (Master Boot Record) and **GPT** (GUID Partition Table) are different partitioning schemes that act as a map for all of the partitions used in the disk. 

They are like a blueprint of the building (disk) containing all the rooms (partitions). Both partitioning schemes differ in structure and properties, and choosing between them depends on multiple factors, including the disk size, hardware compatibility, and much more. 

The MBR/GPT is located in the very first sector of the disk and contains information about the structure and partitions of the disk. It also plays a key role during the boot process of a system. Due to this, the MBR/GPT has become an attractive target for attackers to manipulate the boot process by embedding their malware, often known as **Bootkits**, or tampering with them to make the system un-bootable.

In this room, you will learn the boot process of a system and the role of the MBR/GPT partitioning schemes during this process. You will also explore some attacks on both partitioning schemes and solve practical scenarios to identify and resolve these attacks.

## Power-On the System

The first step of the boot process starts with pushing the power button, which sends electrical signals to the motherboard and initializes all the components. The CPU is the first component to get the electrical signals and needs some instructions to move further. The CPU fetches and executes these instructions from a chipset deployed on the motherboard. This chipset is known as BIOS/UEFI, and it contains instructions on how to get the boot process going.

**BIOS** (Basic Input/Output System) and **UEFI** (Unified Extensible Firmware Interface) are responsible for verifying whether all the hardware components work properly. A system can either use BIOS or UEFI firmware. The difference between them lies in their capabilities and features.

- **BIOS** has been used for decades and is still used in some hardware. It runs in the basic 16-bit mode and supports only up to 2 terabytes of disks. The most important thing to note is that BIOS supports the MBR partitioning scheme, which we will discuss later in the task.
- **UEFI** came as a replacement for BIOS, offering 32-bit and 64-bit modes with up to 9 zettabytes of disks. UEFI offers a secure boot feature to ensure integrity during the system boot process. It also offers redundancy, allowing us to recover from the backup even if the boot code is corrupted. UEFI uses a GPT partitioning scheme, unlike the MBR partitioning scheme used by BIOS.

There are several ways to check if your system uses BIOS or UEFI firmware. The process can be different depending on the operating system you use. For the Windows OS, first open the Run dialog box by pressing `Windows+R` . Type `msinfo32` in this dialog box and press enter. This will show you the system summary. If it is running BIOS, the field named **BIOS Mode** would be shown as the **Legacy**. Otherwise, it would be **UEFI**.

## Power-On-Self-Test (POST)

The system is now powered on, and the CPU has executed instructions from the firmware (BIOS/UEFI) installed. The BIOS/UEFI then starts a Power-On-Self-Test to ensure all the system’s hardware components are working fine. You may hear a single or multiple beeps during this process in your system; this is how the BIOS/UEFI communicates any errors in the hardware components and displays the error message on the screen, e.g., keyboard not found.

## Locate the Bootable Device

After the BIOS/UEFI has performed the POST check, it is time for the BIOS/UEFI to locate bootable devices, such as SSDs, HDDs, or USBs, with the operating system installed. Once the bootable device is located, it starts reading this device. Now, here comes the role of the **MBR/****GPT**. The very first sector of the device would either contain the MBR (Master Boot Record) or the GPT (GUID Partition Table). The MBR/GPT would be taking control of the boot process from here. In the upcoming tasks, we will see how the boot process propagates from here if the MBR partitioning scheme is used and what happens if it is GPT instead.

**Note:** The method of checking your disk's partitioning scheme will differ for different operating systems. For the Windows OS, you can type `Get-Disk` in your PowerShell terminal, and it will show the partitioning schemes of the disks on your system.

The first 3 steps of the boot process that we discussed in this task were the initial steps to find the bootable disk on which the OS resides. From the first task, we imagined this disk as a building where all our data is stored, and there are multiple rooms (partitions) in this building. The next step of the boot process would be to get the map of this building. This map would be either MBR or GPT. 

bootforensics@001

## What if MBR ?

In the previous task, we learned about the boot process, from when the computer powers on till the bootable device is located. 

In this task, we will assume that the bootable device found uses the MBR partitioning scheme. MBR has been used for decades and is now replaced by the GPT in modern systems. However, it is important to learn the MBR as it is still used in some systems.

The bootable device, which was located in the 3rd step of the boot process, would be in the form of a disk. A disk is divided into multiple sectors, each with a standard size of 512 bytes. The first sector of this disk would contain the MBR. A disk's MBR can be viewed by taking the system's disk image and opening it in a hexadecimal editor.

We will be using the **HxD tool**, a hexadecimal editor available in the taskbar of the attached machine. Open the HxD tool, click the File button in the options tab, and select Open from the options. Now, you have to input the file's location to be opened. We have extracted the MBR portion from a disk image and saved it at `C:\Analysis\MBR`. You can select this file to examine the MBR for this task.



This will open it in hexadecimal format. It is to be noted that the MBR provided to you in the attached machine is different from the one presented in the screenshots.





The Master Boot Record (MBR) takes up 512 bytes of space at the very first sector of the disk. Now, we know that it starts from the very first sector. We can easily analyze the MBR code by starting from the first line, but how do we know where this MBR code ends? The answer to this question is straightforward. Every two digits coupled in hexadecimal represents 1 byte, and once the first 512 bytes of the disk completes, the MBR has been ended. So, in the hexadecimal editor we are using, 16 bytes are present in each row, meaning that the first 32 rows of the disk would be the whole MBR. Another way to spot the end is by looking at the MBR signature. The MBR signature is represented by `55 AA`, which marks the end of the MBR code. You can look for these hexadecimal digits to identify where the MBR ends.

The screenshot below shows the MBR portion (first 512 bytes) of a disk when opened into the hex editor. You can see that these are the first 32 rows (16 bytes for each row) and ending at 55 AA (MBR Signature). The first highlighted portion represents the bytes offset, the second represents the actual hexadecimal bytes, and the third represents the ASCII-converted text of the hexadecimal bytes. We would focus on the second portion, the hexadecimal bytes. In this task, we will analyze this whole MBR by decoding the meaning of these hexadecimal digits. 





Before we start analyzing the bytes, it's important to understand that together, every two hexadecimal digits present a single byte. These 512 bytes of the MBR are further divided into three portions. The following screenshot highlights each of the three portions of the MBR with different colors.

Before we start analyzing the bytes, it's important to understand that together, every two hexadecimal digits present a single byte. These 512 bytes of the MBR are further divided into three portions. The following screenshot highlights each of the three portions of the MBR with different colors.

Let's dissect each of the three portions of the MBR.

## Bootloader Code (Bytes 0-446)

The first component of the MBR is the Bootloader code. They cover 446 out of the total 512 bytes of the MBR, as shown in the screenshot below: 