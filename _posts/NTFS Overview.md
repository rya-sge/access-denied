## NTFS Overview

https://tryhackme.com/room/ntfsanalysis

As already covered, NTFS, or New Technology File System, is a file system developed by Microsoft. It's been the default file system for Windows operating systems since Windows NT 3.1, way back in 1993. A file system is the way our computer organizes and stores files on a drive. 

It is trivial to understand that NTFS can also be classified as a Journaling file system because it is designed to maintain the file system's consistency by recording or writing down the changes within the file system in a journal (log) before applying them to the main file system structures. 

From an OS point of view, this is useful when recovering the OS from unexpected system crashes, power failures, etc. 

Some of the key features of NTFS are:

- **Advanced Metadata:** NTFS maintains detailed metadata, including file creation, modification, and access times, which is invaluable for forensic investigations.
- **Journaling:** NTFS uses a journaling feature to keep track of changes. This feature helps recover data after crashes and provides a trail of file system activities. This can also be helpful for forensics investigations.
- **Security Features:** NTFS supports advanced security features like encryption (EFS) and permissions, which can be analyzed to understand access patterns and security breaches.
- **Large Volume Support:** NTFS can handle large volumes and files, making it suitable for modern storage needs.
- **Resilience:** NTFS is more resilient to corruption compared to older file systems like FAT32, thanks to its robust structure and recovery mechanisms.
- **Compatibility:** While primarily for Windows, NTFS can be read (and sometimes written) on Linux and macOS with third-party tools.
- **Compression:** It includes built-in file compression to save space.



[TOC]



## Comparison with other filesystem

| Feature                  | NTFS                                                  | FAT32                                | exFAT                                                  |
| ------------------------ | ----------------------------------------------------- | ------------------------------------ | ------------------------------------------------------ |
| **Max Drive Size**       | 256 TB                                                | 2 TB                                 | 128 PB                                                 |
| **Max File Size**        | 256 TB                                                | 4 GB                                 | 16 EB                                                  |
| **Crash Recovery**       | Yes (keeps track of all changes)                      | No                                   | No                                                     |
| **Encryption**           | Yes (built-in encryption)                             | No                                   | No                                                     |
| **Compression**          | Yes                                                   | No                                   | No                                                     |
| **File Permissions**     | Yes (you can control who accesses what)               | No                                   | No                                                     |
| **Reliability**          | High (less likely to corrupt)                         | Low (older and more prone to issues) | Moderate (better than FAT32 but not as robust as NTFS) |
| **Works Across Devices** | Mostly Windows (limited compatibility with Mac/Linux) | Universal (works on almost anything) | Universal (great for flash drives and SD cards)        |
| **Best For**             | Modern Windows systems                                | Older systems or small USB drives    | Flash drives, SD cards, and external drives            |





Below is a detailed explanation of the NTFS disk structure, its components, and their forensic significance.

## Partition Boot Sector (PBS)

The Partition Boot Sector is the first sector of an NTFS volume and plays a vital role in the booting process. It contains the necessary information to locate and load the operating system. It also includes the `BIOS Parameter Block (BPB)`, which defines the disk layout. 

It maintains critical file system parameters such as sectors per cluster and the location of the Master File Table.

**Key Contents**

Some of the key components of PBS are:

- Jump instruction to bootstrap code.
- File system type indicator (e.g., NTFS).
- Location of the MFT and the MFT Mirror.
- End-of-sector marker (**0x55AA**).

**Forensics Value**
Looking at the PBS from the forensics perspective can reveal information about the boot process and disk configuration. This sector can be analyzed to determine whether it has been tampered with (e.g., by malware or rootkits) or to validate the integrity of the boot code and the BIOS Parameter Block (BPB).

## Master File Table (MFT)

One of the key components/sectors of the NTFS disk is the Master File Table (MFT). This is considered the backbone of NTFS, acting as a database that contains metadata about every file and directory. It provides a comprehensive structure for the local file data and can be used to track all the files and directories on the disk, including the user data and the system files. We will explore this in the later task.

**Characteristics**

Some of the key characteristics of MFT are:

- Divided into fixed-size records (typically 1 KB).
- Each file and directory gets an MFT entry.
- File attributes such as timestamps, permissions, and data location are stored as metadata.

**Forensics Value**

Some of the key forensics values provided by MFT are:

- Deleted file records may still exist in the MFT, aiding data recovery.
- It is essential for timeline analysis, as it contains timestamps for creation, modification, and last access.
- Useful in detecting unauthorized changes to File metadata.

### $MFTMirr

As the name suggests, the MFT Mirror is a duplicate copy of the first few records of the Master File Table, designed to ensure redundancy. Its main purpose is to provide a backup copy to recover data in case the primary MFT becomes corrupted. It also ensures file system stability and reliability. It is typically located in a separate part of the disk.

**Forensics Value**

From a forensics point of view, it can be used to cross-verify the integrity of the MFT. If the primary MFT is damaged or tempered, it can be used to get useful metadata.

## System Files

System files in NTFS are reserved files that manage the internal operations of the file system. Some of the key examples of system files are:

- `$MFT`: Master File Table.
- `$MFTMirr`: MFT Mirror.
- `$LogFile`: A transactional log for consistency.
- `$Bitmap`: Tracks allocated and free clusters.
- `$Boot`: Stores the boot sector information.
- `$BadClus`: Tracks bad sectors.
- `$UpCase`: Stores uppercase character mapping for case-insensitive comparisons.

**Forensics Value**

From the forensics perspective, some of the files mentioned below are important:

- System files `$LogFile` can reveal a history of file system operations.
- `$Bitmap` It can help identify recent cluster allocations and deletions.
- `$BadClus` It might expose sectors marked badly to hide data intentionally.

## File Data Area

The area where user and system file content is stored, either within the **MFT** (resident) or in separate **clusters** (non-resident). 

- It stores the actual content of files and directories. 
- It provides flexibility by storing small files directly in the MFT.

**Forensics Value**

This is the primary source for recovering the user data. It can be analyzed for file fragments and slack space, which may contain the residual data.

## Alternate Data Stream

Alternate Data Streams (ADS) are a feature of NTFS that allows multiple data streams to be associated with a single file or directory. 

While the primary data stream contains the main content of a file, ADS can store additional metadata or hidden content without altering the size or appearance of the main file.

## Identifying the Artifacts

To extract and examine the NTFS disk and its components, we will use the powerful forensics tool called FTK Imager, which can be found on the taskbar.





The Master File Table (MFT) Record is considered the most important file for the forensics investigator because the MFT handles any file created/modified/deleted on the file system. The Windows OS creates an entry for each individual file or folder within the MFT record.
Let's start our investigation by exploring the MFT record, a very important component of NTFS.

## Master File Table

The MFT record is a core component of the NTFS, which serves as the database that tracks all files and directories. Each file or directory on the disk has a corresponding MFT record, which acts as a detailed metadata repository for that object.

**Contents of an MFT Record**

The MFT contains very important information about the records related to the files. Each MFT record contains attributes describing the file or the directory. The Hex representation of a particular record within the MFT File is shown below:



From an OS perspective, MFT File manages the files and directories within the disk. It is used to locate and interpret the files' metadata, such as timestamps, security permissions, attributes, etc. The OS also uses MFT File to effectively access/find the files by storing pointers to the file or data.

**Forensics Value**

MFT records play a vital role in investigations, as they are considered an invaluable source of evidence because they provide a comprehensive map of the file system activity and the timeline. Some of the key aspects of MFT records, from the forensics point of view, are:

- It provides evidence of the presence of a certain file on the disk, even if the file is deleted.
- It can also provide evidence of file modification, which could be useful in certain forensics use cases.

## Examining the MFT Record

Now that we have understood the importance of the MFT record, it is time to extract the juicy information from the MFT File we extracted in the previous task and validate all the key findings that we discussed earlier.

To extract the information from the MFT records, we will use the `MFTECmd.exe` tool, which is placed in the EZ Tools directory on the Desktop. Open the terminal and run the following command to check the available options, as shown below:

## Important Columns in the MFT Record

If we examine the output, we can see that various columns contain important information. Let's break down these columns to better understand the output.

- **Entry Number**
- - **Description:** A unique identifier for the MFT record.
  - **Importance:** Helps map the record to its specific file or directory and reuse track records.
- Parent Entry Number
  - **Description:** The entry number of the parent directory.
  - **Importance:** Shows the file or directory location in the file system hierarchy, aiding in reconstructing directory structures.

- **Sequence Number**
  - **Description:** A counter incremented when the MFT record is reused.
  - **Importance:** Helps identify reused records and differentiate between old and new files occupying the same entry.
- **File Name**
  - **Description:** The name of the file or directory.
  - **Importance:** Essential for identifying the file and matching it with user activities or processes.
- **Timestamps**
  - **Creation Time:** When the file or directory was created.
  - **Modification Time:** When the content of the file was last modified.
  - **Access Time:** When the file was last accessed.
  - **MFT record Modification Time:** When the metadata was last updated.
  - **Importance:** Crucial for **timeline analysis**, helping to reconstruct the sequence of events involving the file.
- **Flags**
  - **Description:** Indicates whether the record represents a file, directory, or unused record.
  - **Importance:** Determines the type of object and its activity status (e.g., deleted or active).
- **Entry Flags**
  - **Description:** Flags like `Read-only`, `Hidden`, `System`, etc.
  - **Importance:** Useful for identifying hidden or system files often used by malware.
- **In Use**
  - **Description**: Indicates whether the current record is associated with the active file or directory.
  - **Importance**: It can indicate which files are present on the disk and which are deleted or no longer in use. MFT File still maintains the record even after the deletion.
- **Logical Size**
  - **Description:** The size of the file's actual data.
  - **Importance:** Provides insights into the file's content size, useful for verifying anomalies (e.g., files marked empty but containing data).
- **Physical Size**
  - **Description:** The amount of disk space allocated to the file.
  - **Importance:** Helps identify slack space or fragmented files.

Now that we understand what these columns mean and what key values they provide, explore the MFT record and see if you can find footprints of any suspicious file or the tool.

## MACB Time

In the records, we see different timestamps associated with each record. What are they, and how are they different from each other? Well, they are classified as MACB time. **MACB** refers to the timestamps associated with file system metadata, which provide crucial information about a file's history. These timestamps are:

- **M - Modified**: The time when the file's content was last changed.
- **A - Accessed**: The time when the file was last read or opened.
- **C - Changed (Metadata)**: The time when the file's metadata (e.g., permissions, ownership) was last altered.
- **B - Birth (Creation)**: The time when the file was first created (available in NTFS and other advanced file systems).

NTFS includes a very important feature called file system journaling. This technology allows the OS to maintain a transactional record of all changes made to a volume, so in the event of a crash or power failure, the system can roll back the changes or continue where it left off.

The goal is to maintain file system integrity and to prevent catastrophic events from occurring. Some of the key features of NTFS Journaling are:

- **File system Integrity**: NTFS journaling ensures that the file system can recover even after crashes, minimizing data loss and corruption risks. This is essential for both performance and reliability.
- **Deleted Files**: The ability to track when files were deleted through the USN journal allows forensic experts to establish timelines critical in investigations.
- **USN vs. Log File**: Understanding the difference between the USN journal (file changes) and the log file (MFT metadata changes) is vital for accurate forensic analysis, as they provide different insights.
- **Historical Data Access**: Volume shadow copies provide a way to retrieve older versions of journals, allowing forensic teams to analyze data from different points in time, which might reveal crucial evidence.

## Types Of NTFS Journals

There are two journals in the NTFS which we will explore:

**$LogFile**

The $LogFile is a special metadata file in NTFS that acts as the journal. It records metadata changes such as file creation, deletion, or modification before committing them to the disk. If a system failure occurs, NTFS can replay the transactions in `$LogFile` during the recovery process to restore consistency.

This log file is located in the root directory, as shown below:

**Universal Sequence Number (USN) Journal ($USNJrnl)**

The **USN Journal**, short for **Update Sequence Number Journal**, is a feature in NTFS that records changes made to files, directories, and their attributes. It provides a historical record of file system activity, especially useful for monitoring, backup, and indexing services.

This is located in the $Extend Directory within the root directory, as shown below:

**Structure of USNJrnl**

$USNJrnl is the metadata file, which is further comprised of two components, which will be shown if we double-click on the $USNJrnl file, as shown below:

The two components are explained below:

- **$Max**: Defines the maximum size of the journal and its allocation policy.

- $J

  : Stores the actual change records. $J is the actual file we are interested in investigating.

  - $J, in fact, was implemented as an ADS (Alternative data stream) in NTFS.

Now that we have explored the two Journals, we will export and analyze `$J` in this task, as shown below:

**Extract the $J File**

Let's extract the `$J` file from the FTK Imager, as shown below:

The $I30 file is an NTFS index attribute, which can also be classified as the directory index that maintains a structured layout of files and directories within an NTFS volume. The Windows OS uses it to store and retrieve information about directory entries. As we examined the directories in FTK Imager, we observed that $I30 is present in some directories containing information about the files and folders within the directory.

Simply put, it is mainly used to store a directory's index entries and contains metadata about the files and subdirectories within it. This metadata includes filenames, timestamps, and other details about files, even those that have been deleted or modified.

## Index Allocation Attribute ($I30)

Before explaining what the $I30 file contains, let's explore the `[ROOT]/metasploit` folder within the FTK Imager. We will find the $I30 file in the directory, classified as `NTFS Index Allocation`, as shown below:

Here, we found the $I30 file, along with a few files marked with a red cross, indicating that they are no longer present, which is called the Slack Space. 

## Slack Space

Slack space in $I30 refers to files that are deleted, renamed, or moved within a directory. Even though a file entry is removed from the active index, residual data may still be present in the slack space, which may be helpful for forensics investigations when looking for deleted files.

To verify the content of this directory, we will navigate to the `C:\metasploit` directory, which shows only four directories, as shown below:

## Forensics Value

Now that we understand the $I30 file and its purpose, it's important to understand its forensics value. Some of the key forensics values we can get from this are:

- **Deleted Files:** When a file is created, its entry with attributes is stored in the $I30. However, when the files are deleted, their metadata might still be preset in the $I30, which could help track deleting files until they are overwritten.
- **Renamed / Moved File:** Actions like renaming or moving files are also reflected in the $I30, which helps track file movement.
- **Uncover Hidden Files:** File Attributes can help identify the hidden files.

## Analyzing $I30

Let's export this $I30 attribute file from the /[root]/metasploit directory using FTK Imager for the analysis. Once the $I30 index file is exported, we will use the following command to extract the information contained within the $I30 file, as shown below:

**Command:** `MFTECmd.exe -f ..\Evidence\$I30 --csv ..\Evidence\ --csvf i30.csv`

## File Attributes in the $I30

Some of the key information/metadata we can find within the $I30 about files and directories are listed below:

- Filename
- From Slack
- File Size
- Parent Directory Information
- Timestamps (MACB)
- File Attributes
  - Read Only
  - Hidden
  - Directory / File
  - Archive / Compressed / Encrypted
  - System

The output will show details about the files or directories present or present within the metasploit directory. We can apply a filter on the "From Slack" column to list down the files or directories that used to be present in this folder and are no longer present, hence being referred to in Slack Space.