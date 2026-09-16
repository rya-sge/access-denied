---
layout: post
title: "File Descriptors, the IPC Subsystem and Pipes - Named, Anonymous and Shell Pipelines"
date:   2026-09-16
lang: en
locale: en-GB
categories: linux programmation
tags: linux syscalls ipc pipes file-descriptor dup2 fifo shell posix operating-system
series: sye
series_order: 4
description: "How descriptor tables point into the kernel open-file table, what dup2() redirects, the IPC families, and how pipe(), fork() and exec() build ls | more."
image: /assets/article/linux/sye-ipc-pipes/2026-09-16-file-descriptors-ipc-pipes.png
isMath: false
---

Every resource a UNIX process reads or writes is reached through a **file descriptor**, a small integer that indexes a table owned by the process and pointing into a table of open files owned by the kernel. That two-level structure is what lets a descriptor be duplicated, redirected with `dup2()`, inherited across `fork()` and kept across `exec()`, and it is the foundation on which the shell builds redirections and pipelines without the redirected programs knowing.

The [previous articles in this series]({{site.url_complet}}/2026/09/16/process-control-block-fork-exec-context-switch/) described processes as isolated address spaces. Isolation is only useful if it can be selectively broken, and that is the job of the **Inter-Process Communication** (IPC) subsystem: shared memory and mapped files for exchanging data, locks, semaphores and signals for synchronising, and two mechanisms that do both at once, pipes and sockets. This article follows the sixth SYE lecture through the descriptor model, the map of IPC mechanisms, and then the pipe in detail: its FIFO semantics, its two descriptors, its named form created by `mkfifo()` and its anonymous form created by `pipe()`, ending with the dozen lines of C by which a shell turns `ls | more` into two processes joined by a kernel buffer.

> **Source and currency note.** This article is based on the lecture *SYE - S6 IPC et tubes* (DR, FG, MZ, HEIG-VD, 2020). The descriptor model, the `dup2()` semantics and the pipe API are unchanged. The lecture's "about 4 KB" pipe capacity reflects historical UNIX and the SO3 teaching kernel; Linux has used a 64 KB default since kernel 2.6.11, and 4 KB (`PIPE_BUF`) survives there as the size below which a write is atomic. Where Linux adds a level of indirection or a rule the lecture's simplified model leaves out (the `struct file` layer, `SIGPIPE`, the blocking `open()` on a FIFO), it is stated in place.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## File descriptors

### A per-process table pointing into a kernel table

A **file descriptor** is an integer that identifies, uniquely within one process, an open resource of the file kind: a regular file, a console, a device, and, as this article will show, a pipe or a socket. The lecture's model has two tables:

- **One descriptor table per process**, in the process's PCB. Its index is the descriptor number and each entry is a pointer.
- **One table of open files** in kernel space, shared by all processes. Each entry describes an open resource: what it is, how it was opened, and the current position in it.

By convention the first three entries of every process are pre-opened: **0** is standard input, **1** standard output, **2** standard error. `open()` returns the lowest free index, which is why a program that opens one file after start-up gets descriptor 3.

The lecture's figure shows two processes and the kernel table side by side. Process Pa has descriptors 0 and 1 pointing at the console entries for reading and writing, and descriptor 3 pointing at a read-only file. Process Pb has descriptors 0 and 1 pointing at the **same** console entries: two processes can share an open-file entry, and this is how children inherit their parent's terminal. 

Two facts follow from the split. Descriptor numbers are meaningful only inside a process, since Pa's 3 and Pb's 3 may point anywhere; and a resource can be reached through several descriptors, in one process or in several, all of which see the same open-file entry, including its offset.

![Two per-process descriptor tables pointing into the kernel's open-file table: both processes share the console entries for descriptors 0 and 1, and in process Pb dup2(fd, 1) has moved descriptor 1 from the console entry to the entry of the file log opened as descriptor 6]({{site.url_complet}}/assets/article/linux/sye-ipc-pipes/fd-table-open-file-table-concept.png)

### Redirection with dup2()

Because a descriptor is a pointer into the open-file table, redirecting it means changing where it points. That is what the system call [`dup2()`](https://man7.org/linux/man-pages/man2/dup.2.html) does. The lecture writes it as `dup2(int orig, int copy)`: after the call, descriptor `copy` refers to the same open-file entry as `orig`, and whatever `copy` referred to before is closed. The two descriptors are then **synonyms**: a write through either one goes to the same resource and advances the same offset.

The figure's process Pb runs the lecture's two-line example:

```c
fd = open("log", O_RDWR);   /* returns 6: the lowest free descriptor */
dup2(fd, 1);                /* stdout becomes a synonym of fd */
```

Before the call, Pb's descriptor 1 points at the console-write entry (ID 6 in the figure). After it, descriptor 1 points at the entry of the file `log` (ID 9), the same entry as descriptor 6. Anything Pb, or a program it later `exec()`s, prints on standard output now lands in `log`. The program being redirected does not know: it still writes to descriptor 1. This is the whole mechanism behind `ls > liste.txt` in a shell, which opens `liste.txt`, calls `dup2()` on the result and descriptor 1, and only then `exec()`s `ls`.

Two properties make redirection compose with process creation. A `fork()` copies the descriptor table, so the child starts with the parent's descriptors pointing at the parent's open-file entries. An `exec()` keeps the table as it is (except for descriptors marked close-on-exec), so the new program inherits whatever the process arranged before the call. Redirections are therefore set up between `fork()` and `exec()`, in the child, which is the pattern the last section uses for pipelines.

### The implementation in SO3

The lecture shows how the teaching kernel SO3 implements the model, noting that Linux is similar. Three structures are involved:

- In `process.h`, the PCB carries the per-process table as `int fd_array[FD_MAX]`, an array of indexes into the global table.
- The global open-file table is `struct fd *open_fds[MAX_FDS]`, where a `NULL` entry is free. Each `struct fd` holds the descriptor's value, its operating and access mode flags, its open flags, a type, a **reference counter** that keeps the object alive while it is greater than zero, a pointer `fops` to a table of callbacks, and a `priv` pointer to private data.
- `struct file_operations` is that table of callbacks: `open`, `close`, `read`, `write`, `lseek`, `ioctl`, `readdir`, `mkdir`, `stat`, `unlink`, `mount`, `unmount` and `clone`, each a function pointer.

The layer that ties them together is the **Virtual File System** (VFS) in `fs/vfs.c`. A `read()` system call arrives at the VFS with a descriptor; the VFS looks up `fd_array[fd]`, follows it to the `struct fd`, and calls `fops->read`. Which function runs depends on what the descriptor refers to: the FAT driver in `fs/fat/` for a file on disk, the pipe implementation in `ipc/pipe.c` for a pipe. The reference counter is what makes `dup2()` and `fork()` safe: every descriptor pointing at the entry adds one, every `close()` subtracts one, and the resource is released when the count reaches zero, not when any single descriptor is closed.

Linux uses the same design with one more level. The per-process table (`files_struct`) points to `struct file` objects, one per `open()` call, which hold the offset and the flags; those point to the inode, which is unique per file. Two descriptors produced by `dup2()` share one `struct file` and therefore one offset; two independent `open()` calls on the same file produce two `struct file` objects with separate offsets on one inode. The lecture's single open-file table merges the first two levels, which is enough for everything in this article.

## The IPC subsystem

**Inter-Process Communication** is the set of mechanisms by which processes **communicate** and **synchronise**. Each process lives in its own address space, so none of it is possible without the kernel's help, and the kernel exposes it through interfaces standardised by [POSIX](https://pubs.opengroup.org/onlinepubs/9799919799/). The lecture sorts the mechanisms by what they do:

| Purpose | Mechanisms |
|---------|------------|
| **Data exchange** | Mapped files (`mmap()` on a file shared by several processes); shared memory segments (`shm_open()`, System V `shmget()`) |
| **Synchronisation** | Locks, semaphores, monitors; signals |
| **Both** | Pipes; network sockets |

The three families differ in what crosses the process boundary:

- **Data exchange** moves bytes without any notion of ordering or arrival. Two processes mapping the same page see each other's writes immediately, and must add their own synchronisation to know when a write is complete.
- **Synchronisation** carries no data, or one bit of it: a semaphore says "go", a signal says "something happened".
- **Both** does the two in one primitive, because a byte written to a pipe or a socket is both a datum and an event. The reader receives the data, and the act of receiving it, or blocking until it arrives, is the synchronisation.

That combination is why pipes and sockets are the most used IPC mechanisms, and why the rest of the lecture is about pipes.

## Introduction to pipes

### Properties

A **pipe** (the lecture also uses the French *tube*) is a kernel buffer with a writing end and a reading end. Its properties are few and each matters:

- **Unidirectional** (generally). Bytes go in at one end and come out at the other; two-way communication needs two pipes.
- **Destructive read, FIFO order.** A byte read is removed from the pipe, and bytes come out in the order they went in. A pipe has no offset and no `lseek()`; it is a queue, not a file that can be re-read.
- **Limited capacity**, about 4 KB in the lecture's platform. When the buffer is full, a `write()` blocks until a reader has made room; when it is empty, a `read()` blocks until a writer has put something in. This is the synchronisation half of the mechanism.
- **A special file.** It is used with the ordinary `read()` and `write()` system calls, through descriptors, and dispatched by the VFS like any other file. A program written to filter standard input to standard output works unchanged whether the descriptors are files, a terminal or pipes.

On Linux the capacity is 64 KB by default and adjustable per pipe with `fcntl(F_SETPIPE_SZ)`; the historical 4 KB survives as `PIPE_BUF`, the size at or below which a `write()` is guaranteed atomic, so that several writers to one pipe do not interleave their messages. Both values are documented in [`pipe(7)`](https://man7.org/linux/man-pages/man7/pipe.7.html).

### Two descriptors for two ends

Because a pipe has two ends, it is reached through **two descriptors**: one to write into it and one to read from it. The system call [`pipe()`](https://man7.org/linux/man-pages/man2/pipe.2.html) fills a two-element array:

```c
#include <unistd.h>

int pipe_fd[2];

pipe(pipe_fd);
/* pipe_fd[0] : read end   -> read(pipe_fd[0], buf, 100); */
/* pipe_fd[1] : write end  -> write(pipe_fd[1], buf, 30); */
```

The convention is fixed by the API: index **0** is the read end, index **1** the write end, which mirrors standard input and standard output. Both descriptors point at the same pipe object in the kernel, each with its own direction.

Two rules about the ends are not on the slide but govern every program that uses a pipe. A `read()` on a pipe whose **every write descriptor is closed**, in every process, returns 0 once the buffer is drained; that is how a reader learns the stream has ended. A `write()` on a pipe whose **every read descriptor is closed** delivers the `SIGPIPE` signal to the writer, which kills it by default, or fails with `EPIPE` if the signal is ignored. Both rules count descriptors across all processes holding them, which is why the examples below are careful to close the end they do not use.

## Named and anonymous pipes

A pipe exists in one of two forms, distinguished by how processes find it.

| | Named pipe (FIFO) | Anonymous pipe |
|---|---|---|
| **Creation** | `mkfifo()`, then `open()` by each user | `pipe()` |
| **How processes find it** | By its path in the file system | By inheriting the descriptors across `fork()` |
| **Who can use it** | Any process that can open the path | The creating process and its descendants |
| **Lifetime** | Persistent: stays until `unlink()` removes it | Automatic: gone when the last descriptor is closed |

### Named pipes

A **named pipe**, or FIFO, is created with [`mkfifo()`](https://man7.org/linux/man-pages/man3/mkfifo.3.html), which gives it a path and permission bits like a file. The lecture stresses that its existence in the file system is *virtual*: the directory entry is a name for a kernel buffer, and nothing is stored on disk. Each participant then obtains a descriptor with an ordinary [`open()`](https://man7.org/linux/man-pages/man2/open.2.html), for writing on one side and reading on the other, and the FIFO **persists** after both have closed it until someone calls `unlink()`.

The lecture's example is a writer and a reader compiled as two separate programs, which is the point: they share no ancestor and find each other only through the name `essai.fifo`. The writer:

```c
const char *pipeName = "essai.fifo";
const char *str = "Bonjour";

if (mkfifo(pipeName, O_CREAT | 0644) != 0) {
  printf("Pipe creation failed.\n");
  exit(EXIT_FAILURE);
}

fd_pipe = open(pipeName, O_WRONLY);
if (fd_pipe == -1) {
  printf("Failed at open.\n");
  exit(EXIT_FAILURE);
}

write(fd_pipe, str, strlen(str) + 1);   /* +1 sends the terminating NUL */
close(fd_pipe);
```

The reader opens the same name for reading, reads into a buffer, prints it, closes, and removes the FIFO:

```c
fd_pipe = open(pipeName, O_RDONLY);
if (fd_pipe == -1) {
  printf("Failed at open.\n");
  exit(EXIT_FAILURE);
}

read(fd_pipe, str, BUFFER_SIZE);
printf("%s\n", str);

close(fd_pipe);
unlink(pipeName);
```

Three details in this code deserve attention:

- **The extra byte.** The writer sends `strlen(str) + 1` bytes so that the terminating NUL crosses the pipe and the reader's `printf("%s")` finds a proper string.
- **The `unlink()`.** It is what the "persistence" bullet requires: without it, `essai.fifo` remains in the directory after both programs exit, and the next run's `mkfifo()` fails with `EEXIST`.
- **The start order.** The example runs in either order, because `open()` on a FIFO **blocks** until the other end is opened too: whichever program starts first waits in `open()` for its partner, a rendezvous documented in [`fifo(7)`](https://man7.org/linux/man-pages/man7/fifo.7.html).

The second argument the lecture passes to `mkfifo()`, `O_CREAT | 0644`, mixes an `open()` flag into a permission mode: on Linux `O_CREAT` is octal `0100`, which as a mode is the owner-execute bit, so the FIFO is created with mode `0744` rather than `0644`. It is harmless for a FIFO, but the correct form is `mkfifo(pipeName, 0644)`.

### Anonymous pipes

An **anonymous pipe** has no name. It is created with `pipe()` by one process and can only be reached through the two descriptors that call returned, so it is used **together with process creation**: the process calls `pipe()`, then `fork()`, and the child inherits copies of both descriptors. Nothing else can ever obtain them. When the last descriptor on either end is closed in every process, the pipe disappears; there is nothing to `unlink()`.

The lecture's example has the child write a message and the parent read it:

```c
int pipe_fd[2];
char buffer[80];
int pid;

pipe(pipe_fd);                       /* pipe creation */

pid = fork();                        /* now, we fork a child */

if (!pid) {
  /* the child will send a message */
  close(pipe_fd[0]);
  write(pipe_fd[1], "Hello, I am your child\n", 24);
  close(pipe_fd[1]);

  exit(0);

} else {
  /* the parent will read something from the pipe */
  close(pipe_fd[1]);

  read(pipe_fd[0], buffer, 80);

  printf("I got from the child: %s\n", buffer);
  close(pipe_fd[0]);
  waitpid(pid, NULL, 0);
}
exit(0);
```

![Sequence of the anonymous pipe example: the parent calls pipe() and fork(), the child closes the read end and writes its message, the parent closes the write end, blocks in read() until the message arrives, prints it, and reaps the child with waitpid()]({{site.url_complet}}/assets/article/linux/sye-ipc-pipes/pipe-fork-parent-child-sequence-workflow.png)

The two `close()` calls at the top of each branch are the part learners skip and should not. After `fork()` there are **four** descriptors on this pipe: two in each process. The child closes the read end it will not use; the parent closes the write end it will not use. If the parent kept `pipe_fd[1]` open, its own `read()` could never return 0 at end of stream, because the kernel would still count one live writer, the parent itself.

In this example the parent reads exactly once and does not rely on end-of-file, so the program would still print the message; in any loop that reads "until the pipe is empty", the forgotten `close()` turns into a deadlock. The `waitpid()` at the end reaps the child, as the process-management article required.

### A pipe in the shell: ls | more

The last slide assembles everything into the mechanism a shell uses for `ls | more`: one pipe, one `fork()`, two `dup2()` and two `execve()`.

```c
int pipe_fd[2];

pipe(pipe_fd);

if (!fork()) {

    close(pipe_fd[0]);             /* end not used in this process */
    dup2(pipe_fd[1], 1);           /* stdout becomes a synonym of pipe_fd[1] */

    execve("/bin/ls", ...);        /* replacement of the binary image */

} else {

    close(pipe_fd[1]);             /* end not used in this process */
    dup2(pipe_fd[0], 0);           /* stdin becomes a synonym of pipe_fd[0] */

    execve("/bin/more", ...);      /* replacement of the binary image */

}
```

![Activity diagram of the ls | more pipeline: after pipe() and fork(), the child closes the read end, redirects its standard output into the write end with dup2() and executes ls, while the parent closes the write end, redirects its standard input to the read end with dup2() and executes more]({{site.url_complet}}/assets/article/linux/sye-ipc-pipes/shell-pipeline-ls-more-workflow.png)

Reading the two branches against the descriptor model:

- **The producer** (child) closes the read end, then makes descriptor 1 a synonym of the pipe's write end. When `execve()` replaces its image with `ls`, the new program inherits the table: its standard output is the pipe. `ls` writes its listing exactly as it would to a terminal.
- **The consumer** (parent) closes the write end, then makes descriptor 0 a synonym of the pipe's read end and becomes `more`. `more` reads its standard input exactly as it would from a file, and sees end-of-file when `ls` exits, because at that moment the last write descriptor on the pipe (the one inherited by `ls`) is closed.

The `close(pipe_fd[1])` in the consumer branch is what makes that end-of-file possible. Had the consumer kept a write descriptor, `more` would wait for input forever after `ls` finished. Neither program was written with pipes in mind, and neither needs to be: the redirection is done entirely in the descriptor table before `execve()`, which is the same trick as `ls > liste.txt` with a pipe end in place of a file.

One simplification separates the slide from a real shell. Here the parent itself becomes `more`, so the shell process is gone once the pipeline starts. An interactive shell instead forks **two** children, one per command, connects them with the pipe, closes both ends in itself, and waits for both with `waitpid()`, so that it can print the next prompt. The descriptor manipulation in each child is identical to the slide's.

## Conclusion

A file descriptor is an index into a per-process table whose entries point into the kernel's table of open files. Several descriptors, in one process or several, can point at one entry, which is what `dup2(orig, copy)` exploits: it makes `copy` a synonym of `orig`, redirecting standard output to a file or a pipe without the program's knowledge. `fork()` copies the table and `exec()` keeps it, so redirections are arranged in the child before the new program starts.

SO3 implements the model with `fd_array` in the PCB, a global `open_fds` table of reference-counted `struct fd`, and per-type `file_operations` dispatched by the VFS; Linux adds a `struct file` level between the descriptor and the inode.

The IPC subsystem provides data exchange through mapped files and shared memory, synchronisation through locks, semaphores, monitors and signals, and mechanisms that do both, pipes and sockets.

A pipe is a unidirectional kernel buffer with destructive FIFO reads, a bounded capacity that blocks writers when full and readers when empty, and two descriptors, `fd[0]` to read and `fd[1]` to write. A named pipe is created with `mkfifo()`, opened by path, and persists until `unlink()`; an anonymous pipe is created with `pipe()`, shared through `fork()`, and vanishes with its last descriptor. Closing the unused end in each process is what lets the reader see end-of-file.

A shell pipeline is a pipe, a fork, a `dup2()` per side and an `exec()` per command.

![Mindmap of the lecture covering file descriptors and dup2(), the SO3 implementation, the IPC subsystem's three families, pipe properties and descriptors, named versus anonymous pipes and the shell pipeline]({{site.url_complet}}/assets/article/linux/sye-ipc-pipes/2026-09-16-file-descriptors-ipc-pipes.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **File descriptor** | A small non-negative integer, unique within a process, indexing the process's descriptor table; 0, 1 and 2 are standard input, output and error. |
| **Open-file table** | The kernel table describing every open resource (type, mode, position); descriptor-table entries point into it, and several may point at one entry. |
| **`dup2(orig, copy)`** | The system call that makes descriptor `copy` refer to the same open-file entry as `orig`, closing whatever `copy` referred to before; the primitive behind redirection. |
| **VFS** | The Virtual File System layer that receives file system calls on a descriptor and dispatches them to the `file_operations` of the object's type (disk file, pipe, ...). |
| **IPC** | Inter-Process Communication: the kernel mechanisms by which isolated processes exchange data and synchronise, with interfaces standardised by POSIX. |
| **Pipe** | A unidirectional kernel buffer read and written through descriptors with FIFO order, destructive reads and bounded capacity. |
| **Named pipe (FIFO)** | A pipe given a path by `mkfifo()`, opened by any process through that path, and persistent until removed with `unlink()`. |
| **Anonymous pipe** | A pipe created by `pipe()` with no name, reachable only through its two descriptors and therefore shared by inheritance across `fork()`. |
| **`PIPE_BUF`** | The size (4096 bytes on Linux) at or below which a write to a pipe is atomic, so concurrent writers do not interleave. |
| **End-of-file on a pipe** | The condition, signalled by `read()` returning 0, that the pipe is empty and every write descriptor on it, in every process, has been closed. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| `read()` returns 0 only when **every** write descriptor on the pipe is closed, in every process, including the reader's own copy inherited from `fork()`. | Close the write end in the reading process right after `fork()`; a forgotten copy turns a read-until-EOF loop into a deadlock. |
| `write()` on a pipe with no reader delivers `SIGPIPE`, whose default action terminates the writer. | Ignore or handle `SIGPIPE` in long-lived writers and check `write()` for `EPIPE`, or the process dies silently when its consumer exits. |
| `open()` on a FIFO blocks until the opposite end is also opened. | Do not expect `open()` to return immediately; start the peer first, or open with `O_NONBLOCK`: a read-only open then returns at once, and a write-only open fails with `ENXIO` if no reader is present. |
| A `write()` larger than `PIPE_BUF` (4096 bytes on Linux) may be split and interleaved with other writers' data. | Keep messages at or below `PIPE_BUF` when several writers share one pipe, or add framing and a single writer. |
| `write()` blocks when the pipe is full; the default capacity is 64 KB on Linux, not the lecture's 4 KB. | Never have one process write a large payload to a pipe and only then read the reply on a second pipe; the peer may be blocked writing its reply. Read and write concurrently, or size with `F_SETPIPE_SZ`. |
| A FIFO persists after both ends close and `mkfifo()` fails with `EEXIST` if it already exists. | `unlink()` it when done, or tolerate `EEXIST` at creation. |
| `dup2(orig, copy)` closes `copy` silently if it was open, and is a no-op if `orig == copy`. | Check what `copy` currently refers to before redirecting, and close the original descriptor after `dup2()` if it is no longer needed, so the reference count can reach zero. |

## Frequently Asked Questions

**Q: Why are two tables needed, one per process and one in the kernel?**

Because the two kinds of information have different scopes. Which resources a process may reach, and under which small integers, is per process; two processes can both have a descriptor 3 pointing at unrelated things. What an open resource is, how it was opened and where the current position sits is a property of the open resource itself, and several processes or several descriptors may share it.

Splitting the tables lets a `fork()` copy the small per-process table while both processes keep pointing at the same open files, and lets `dup2()` redirect by rewriting one pointer.

**Q: After `fd = open("log", O_RDWR); dup2(fd, 1);`, what does a `printf()` do, and what happened to the terminal?**

`printf()` writes to descriptor 1, which now points at the open-file entry of `log`; the text goes to the file. The console-write entry that descriptor 1 used to point at was closed by `dup2()` as far as this descriptor is concerned. If no other descriptor points at it, the reference count drops and the kernel releases it. The program is unaware of the change.

**Q: What distinguishes the three IPC families the lecture lists?**

- **Data exchange** (mapped files, shared memory) moves bytes with no built-in notion of when they arrive; the processes must synchronise separately.
- **Synchronisation** (locks, semaphores, monitors, signals) carries an event or a permission but no payload.
- **Both** (pipes, sockets) carry bytes whose arrival is itself the event: a `read()` that returns is both data received and a signal that the writer got that far.

**Q: A process calls `pipe()` then `fork()`. How many descriptors refer to the pipe, and why does it matter?**

Four: the read and write ends in the parent, and copies of both in the child. It matters because end-of-file on the read end is detected only when the number of open write descriptors, across both processes, reaches zero. A reader that keeps its own copy of the write end can never see end-of-file. Each process therefore closes the end it does not use immediately after `fork()`.

**Q: Why does the lecture's named-pipe writer send `strlen(str) + 1` bytes rather than `strlen(str)`?**

A pipe carries bytes, not strings. If only the seven bytes of `"Bonjour"` were sent, the reader's buffer would hold them with no terminating NUL and `printf("%s")` would read past them into whatever the buffer contained before. Sending the extra byte transmits the terminator, so the reader receives a valid C string. The reader's `read()` into a `BUFFER_SIZE` buffer returns as many bytes as are available, eight in this case.

**Q: In the `ls | more` code, why must the consumer close `pipe_fd[1]` before executing `more`, given that it never writes to the pipe?**

Because `more` stops when `read()` returns 0, and `read()` returns 0 only when every write descriptor on the pipe is closed. The producer's write descriptor closes when `ls` exits. If the consumer still held its inherited copy of `pipe_fd[1]`, that copy would survive the `execve()` into `more`, the kernel would count one live writer, and `more` would block in `read()` forever after `ls` finished. Closing the unused end is what makes the pipeline terminate.

**Q: How do a named and an anonymous pipe differ in who can use them and how long they last?**

An anonymous pipe is reachable only through the descriptors `pipe()` returned, so only the creating process and the descendants that inherit those descriptors can use it, and it disappears when the last descriptor closes. A named pipe has a path, so any process with permission to open that path can use it, related or not, and it remains in the file system after every user has closed it until `unlink()` removes it.

The anonymous form suits parent-child and shell pipelines; the named form suits unrelated programs that agree on a name.

## References

- *SYE - S6 IPC et tubes*, DR, FG, MZ, HEIG-VD, 2020 (source lecture)
- [SO3 - Smart Object Oriented operating system](https://github.com/smartobjectoriented/so3), the teaching kernel whose `fd_array`, `open_fds` and `file_operations` structures the lecture shows
- [The Open Group Base Specifications Issue 8, IEEE Std 1003.1-2024 (POSIX)](https://pubs.opengroup.org/onlinepubs/9799919799/)
- [pipe(2) - Linux manual page](https://man7.org/linux/man-pages/man2/pipe.2.html)
- [pipe(7) - Linux manual page](https://man7.org/linux/man-pages/man7/pipe.7.html), capacity, `PIPE_BUF` and the end-of-file and `SIGPIPE` rules
- [fifo(7) - Linux manual page](https://man7.org/linux/man-pages/man7/fifo.7.html)
- [mkfifo(3) - Linux manual page](https://man7.org/linux/man-pages/man3/mkfifo.3.html)
- [dup(2), dup2(2) - Linux manual page](https://man7.org/linux/man-pages/man2/dup.2.html)
- [open(2) - Linux manual page](https://man7.org/linux/man-pages/man2/open.2.html)
- [signal(7) - Linux manual page](https://man7.org/linux/man-pages/man7/signal.7.html), default action of `SIGPIPE`
- [shm_overview(7)](https://man7.org/linux/man-pages/man7/shm_overview.7.html), [sem_overview(7)](https://man7.org/linux/man-pages/man7/sem_overview.7.html), [mmap(2)](https://man7.org/linux/man-pages/man2/mmap.2.html) and [unix(7)](https://man7.org/linux/man-pages/man7/unix.7.html) - Linux manual pages for the other IPC families
- Andrew S. Tanenbaum, Herbert Bos, *Modern Operating Systems*, Pearson, 4th edition, 2014

### Related articles

- [OpenSSH Connection Multiplexing — ControlMaster, the Mux Protocol and Proxy Mode]({{site.url_complet}}/2026/08/27/openssh-connection-multiplexing-controlmaster/)
- [How Fail2Ban Works — Architecture, Privilege Model and Residual Risk]({{site.url_complet}}/2026/09/03/fail2ban-architecture-privilege-model/)
