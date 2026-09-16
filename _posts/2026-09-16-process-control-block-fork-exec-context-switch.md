---
layout: post
title: "The Process Control Block, fork/exec/waitpid/exit and the Context Switch"
date:   2026-09-16
lang: en
locale: en-GB
categories: linux programmation
tags: linux syscalls process fork exec context-switch pcb scheduling operating-system
series: sye
series_order: 2
description: "What a Process Control Block holds, how fork(), exec(), waitpid() and exit() create, replace and reap processes, and what a context switch costs the kernel."
image: /assets/article/linux/sye-process-context-switch/2026-09-16-process-control-block-fork-exec-context-switch.png
isMath: false
---

The [previous article in this series]({{site.url_complet}}/2026/09/16/system-calls-binary-image-process/) defined a process as an execution context, a memory context and a set of kernel-held resources. This one looks at the kernel's side of that definition: the data structure in which the kernel records a process, the **Process Control Block** (PCB), and the four system calls through which a process is created, given a new program, terminated and reaped, namely `fork()`, `exec()`, `exit()` and `waitpid()`.

The PCB is also what makes multitasking possible. When the kernel suspends one process to run another, it saves the outgoing process's registers, stack pointer and memory configuration in its PCB and restores the incoming process's state from its own. That operation, the **context switch**, is examined in the last part: when it happens, what it has to save and restore, and why the scheduler tries to keep it rare.

> **Source and currency note.** This article is based on the lecture *SYE - S4 Processus, appels systèmes et changement de contexte* (DR, FG, MZ, HEIG-VD, 2020), including its speaker notes. The material targets the SO3 teaching kernel on 32-bit ARM, and its description of `fork()` as a full copy of the parent is the textbook model. Where Linux differs in mechanism (copy-on-write, `clone()`, `posix_spawn()`, the measured cost of a context switch), the difference is stated in place.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The Process Control Block

### Definition

Every process is described by exactly one **Process Control Block**, and every PCB belongs to exactly one process. The lecture calls it the process's *identity card*: a data structure that the kernel allocates when the process is created, updates during its life, and frees after it terminates. It holds all the system-level information the kernel needs about the process, and it lives in kernel memory, where user-space code cannot read or write it.

Its main use is the context switch. When the kernel decides to suspend the running process and give the processor to another, it saves the state of the outgoing process in that process's PCB and loads the state of the incoming process from its PCB. The PCB is therefore the place where a process exists while it is not running.

### Contents

The lecture lists the fields a PCB contains. They fall into four groups:

- **Identity and scheduling state.** The process state (ready, running, blocked, terminated), its identifier (PID), its parent, and its scheduling priority.
- **Execution context(s).** For each thread of the process: the saved program counter, the saved stack pointer, the data registers, and the state of the execution context itself. The main thread's context is what a single-threaded process saves and restores on every switch.
- **Memory context.** A descriptor of the address space (on a system with an MMU, a pointer to the page tables), the current heap pointer, and the stack region.
- **Resources and lineage.** The table of open file descriptors, references to the child processes, and the **exit code** the process will leave behind when it terminates.

![The PCB of a process in kernel memory, holding its state, identifiers, saved registers, address space descriptor, heap and stack pointers, open file descriptors, child references and exit code, and pointing to the page tables that map the process's user-space regions]({{site.url_complet}}/assets/article/linux/sye-process-context-switch/pcb-structure-concept.png)

On Linux the PCB is the `struct task_struct` defined in [`include/linux/sched.h`](https://elixir.bootlin.com/linux/v6.12/source/include/linux/sched.h). It is allocated per thread rather than per process, since Linux schedules threads, and the fields the lecture describes are spread across it and the structures it points to: `mm_struct` for the address space, `files_struct` for the descriptor table, `thread_struct` for the saved registers, `children` and `sibling` list heads for the lineage, `exit_code` for the status.

### Lifetime

The PCB's lifetime is bracketed by two system calls, and understanding that bracket explains the zombie state discussed below.

The PCB is **allocated by `fork()`**, in the context of the parent process that issues the call. The parent is the one paying for the new process's bookkeeping.

The PCB is **freed after the parent has collected the exit code**. When a process calls `exit()`, its status is stored in its own PCB, and the kernel informs the parent. The parent retrieves the status with `waitpid()`, and only then can the kernel release the child's PCB. Until the parent does so, the child's memory may be gone but its PCB remains: the process is a **zombie**, visible in the process table with no code left to run.

## Creating processes

### fork()

[`fork()`](https://man7.org/linux/man-pages/man2/fork.2.html) creates a new process. The new process is a **child** of the process that called `fork()`, and it starts as a complete copy of its parent: same code, same data, same heap and stack contents, same open files, and the same current position in the program. Both processes return from the `fork()` call, and both continue executing the instruction that follows it.

```text
Parent process (original)          Child process (new)
+-----------+                      +-----------+
|   Stack   |                      |   Stack   |
|   Heap    |        copy          |   Heap    |
|   Data    |   ----------------->  |   Data    |
|   Code    |                      |   Code    |
+-----------+                      +-----------+
ret = fork();                      ret = fork();
if (ret != 0) ... /* parent */     if (ret == 0) ... /* child */
```

Since the two processes run the same binary image from the same point, something must let the code tell which one it is in. That is the role of the **return value**, and it is the one thing that differs between the two copies:

| Return value of `fork()` | Meaning |
|--------------------------|---------|
| `0` | The code is running in the **child**. |
| `> 0` | The code is running in the **parent**, and the value is the **PID of the child**, to be used later with `waitpid()`. |
| `< 0` (`-1`) | The child could not be created. No new process exists, and `errno` gives the reason: `EAGAIN` when the process limit is reached, `ENOMEM` when memory is exhausted. |

The lecture's model, a full copy of the parent's memory, is how `fork()` is specified and how early UNIX implemented it. Linux implements the same semantics with **copy-on-write**: the child gets its own page tables pointing at the parent's physical pages, all marked read-only, and a page is duplicated only when one of the two processes writes to it. A `fork()` followed almost immediately by `exec()`, which is the common case, therefore copies very little. Internally, glibc's `fork()` is a wrapper around the [`clone()`](https://man7.org/linux/man-pages/man2/clone.2.html) system call, whose flags select what the child shares with the parent; a thread is created with the same call and a different set of flags.

### A fork() exercise

The lecture asks two questions about the following program: how many processes exist at most, and which outputs are possible.

```c
int main(int argc, char *argv[])
{
    int pid1, pid2;

    printf("m0\n");
    pid1 = fork();
    if (pid1)
    {
        printf("m1\n");
        pid2 = fork();
        if (pid2)
            printf("m2\n");

    } else
        printf("m3\n");
}
```

**Number of processes.** `m0` is printed once, before any `fork()`. The first `fork()` produces the original process P and a child C1. In P, `pid1` is C1's PID, so P prints `m1` and calls `fork()` again, producing a second child C2. In P, `pid2` is non-zero, so P prints `m2`. In C2, `pid2` is `0`, and the inner `if` has no `else`, so C2 prints nothing. In C1, `pid1` is `0`, so it takes the `else` branch and prints `m3`. At most **three processes** exist: P, C1 and C2.

**Possible outputs.** Each process prints its lines in program order, but the scheduler decides the interleaving between processes. The constraints are that `m0` comes first, that `m1` precedes `m2` because both are printed by P, and that `m3` (from C1) may land anywhere after `m0`. Three outputs are possible:

```text
m0 m1 m2 m3
m0 m1 m3 m2
m0 m3 m1 m2
```

Two practical remarks go beyond the exercise:

- **Error handling.** `fork()` returns `-1` on failure, which is also non-zero, so the `if (pid1)` test would treat a failed `fork()` as the parent branch. Production code tests for `-1` explicitly.
- **Buffering.** The answer assumes standard output is **line-buffered**, which is the case on a terminal: each `printf` ending in `\n` is flushed immediately. If the output is redirected to a file or a pipe, stdio switches to full buffering, `m0` is still sitting in the buffer when `fork()` copies the process, and both children inherit and eventually flush it. The file then contains `m0` three times. Calling `fflush(stdout)` before `fork()` avoids the duplication; see [`setbuf(3)`](https://man7.org/linux/man-pages/man3/setbuf.3.html) for the buffering modes.

### exit() and waitpid()

A process ends by calling [`exit()`](https://man7.org/linux/man-pages/man3/exit.3.html) with an integer status. The lecture lists its two effects: it terminates the current process, and it propagates the status to the parent. The status is stored in the terminating process's PCB, which is why the PCB cannot be freed at that moment. If a program returns from `main()` without calling `exit()`, the call is made anyway by the C runtime start-up code (the `crt` object file the linker adds to every executable), using `main()`'s return value as the status.

The parent collects that status with [`waitpid()`](https://man7.org/linux/man-pages/man2/wait.2.html), which the lecture credits with three roles:

- **Waiting.** The call blocks the parent until the designated child (or any child, with `-1` as the PID) terminates.
- **Retrieving the status.** The integer passed to `exit()` by the child is written through the `wstatus` pointer. On Linux and POSIX systems it is packed with other information (whether the child was killed by a signal, and which one), so it is decoded with the `WIFEXITED` and `WEXITSTATUS` macros rather than read directly.
- **Reaping.** Once the status has been delivered, the kernel frees the child's PCB. The zombie disappears.

The sequence of the two calls is therefore fixed: `exit()` in the child turns it into a zombie holding a status; `waitpid()` in the parent consumes the status and lets the kernel release the PCB. A parent that never calls `waitpid()` accumulates zombies, each occupying a PCB and a PID, until it terminates itself. When it does, its orphaned children (zombie or alive) are adopted by the root process, `init` or `systemd` on Linux, whose job includes calling `waitpid()` on them.

### exec()

[`exec()`](https://man7.org/linux/man-pages/man3/exec.3.html) replaces the binary image of the calling process with a new one. The lecture lists what it does:

- the code, data, BSS, heap and stack of the current image are discarded and the new image is loaded in their place;
- execution starts at the new image's **entry point**, from which the start-up code calls `main()`;
- arguments are passed to the new program, and are what `main()` receives as `argc` and `argv`.

What `exec()` does **not** change is as important: the process keeps its PID, its parent, and its open file descriptors (unless they were marked close-on-exec). This is why a shell can set up redirections with `open()` and `dup2()` before calling `exec()`, and the new program inherits them without knowing.

Strictly speaking there is no `exec()` system call. It is a **family of POSIX library functions** that differ in how they receive the program path and the arguments, and all of them end up calling the one real system call, [`execve()`](https://man7.org/linux/man-pages/man2/execve.2.html):

```c
/* man 3 exec : library functions */
int execl(const char *path, const char *arg, ... /* (char *) NULL */);
int execlp(const char *file, const char *arg, ... /* (char *) NULL */);
int execle(const char *path, const char *arg, ... /* (char *) NULL, char *const envp[] */);
int execv(const char *path, char *const argv[]);
int execvp(const char *file, char *const argv[]);
int execvpe(const char *file, char *const argv[], char *const envp[]);

/* man 2 execve : the system call */
int execve(const char *filename, char *const argv[], char *const envp[]);
```

The suffixes encode the differences: `l` takes the arguments as a NULL-terminated list of parameters, `v` takes them as an array; `p` searches the `PATH` environment variable for a bare file name; `e` lets the caller supply the new environment instead of inheriting the current one. A successful `exec()` never returns, since the code that called it no longer exists; a return value of `-1` means the new image could not be loaded and the old one is still running.

### Launching a program is fork() followed by exec()

Putting the four calls together gives the UNIX way of starting a program, which the lecture states in one sentence: the parent creates a new process with `fork()`, and the child loads and starts the binary image with `exec()`. A shell running a command does exactly this, then blocks in `waitpid()` until the command exits, and uses the collected status as the command's exit code (`$?`).

![Sequence of a shell launching a command: fork() allocates a PCB and returns twice, the parent blocks in waitpid(), the child calls execve() and runs the new image, exit() stores the status in the child's PCB and turns it into a zombie, waitpid() returns the status and the kernel frees the PCB]({{site.url_complet}}/assets/article/linux/sye-process-context-switch/fork-exec-wait-exit-sequence-workflow.png)

The split into two calls is what distinguishes UNIX from Win32, whose `CreateProcess` does both at once. It costs a copy (mitigated by copy-on-write) and buys flexibility: between `fork()` and `exec()` the child runs the parent's code with the parent's privileges and can rearrange its own environment, close descriptors, change directory, drop privileges or install a seccomp filter before the new program takes over. Systems that want to avoid even the copy-on-write cost use [`posix_spawn()`](https://man7.org/linux/man-pages/man3/posix_spawn.3.html), which combines the two steps behind an interface for the common rearrangements, or `vfork()`, which shares the parent's memory until `exec()`.

## The context switch

### When it happens

A multitasking system keeps several processes in memory, and the kernel decides which one holds the processor. The lecture identifies three situations in which the running process is replaced by another:

- **Termination.** The process calls `exit()`, explicitly or through the C runtime after `main()` returns. There is nothing left to run in it, so another process must be scheduled.
- **Blocking.** The process asks for something that is not immediately available. The lecture's example is `write()`: the call goes through the file system to the disk driver, which submits a request to the device and must wait for its completion. Rather than spin, the kernel marks the process as blocked and runs another one until the device interrupt arrives.
- **Scheduler decision.** The scheduler may take the processor away at any time, typically when the process has used up the time slice allotted to it. This is preemption, and it is what keeps one compute-bound process from monopolising the machine.

All three share a property the lecture's diagram makes explicit: a context switch happens **inside the kernel**, during a system call or an interrupt. A process running in user mode is never switched out directly; it first enters the kernel, through the trap it issued or an interrupt that arrived, and the kernel decides on the way back out whether to return to the same process or to another one.

### What it does

![Context switch sequence: process P0 enters the kernel through a system call or interrupt, the kernel saves P0's registers and FPU state into PCB0, restores P1's from PCB1, reconfigures the MMU for P1's address space, loads P1's program counter and returns to user mode in P1; later the reverse switch brings P0 back]({{site.url_complet}}/assets/article/linux/sye-process-context-switch/context-switch-sequence-workflow.png)

The lecture breaks the switch from P0 to P1 into four steps:

1. **Save the state of P0 in PCB0.** The processor registers hold P0's execution context: general-purpose registers, program counter, stack pointer, status register. They are copied into the PCB, together with the current pointers of the memory context (stack, heap) and the state of any coprocessor P0 was using, such as the floating-point unit (VFP on ARM) or a graphics or cryptographic accelerator.
2. **Restore the state of P1 from PCB1.** The same set of values, saved when P1 was last switched out, is loaded back into the registers.
3. **Reconfigure the memory.** The MMU is switched to P1's address space, that is, to P1's page tables. The caches must be made consistent, which on some architectures means writing dirty cache lines back to RAM and invalidating the TLB; this step is covered in detail in the paging lecture.
4. **Load the new program counter.** The kernel returns from the exception into P1, at the instruction where P1 was interrupted. P1 is running; P0 is not.

The next switch, from P1 back to P0, performs the same four steps with the two PCBs exchanged.

### What it costs

The lecture describes the context switch as an expensive operation, on the order of a millisecond on the teaching platform, because it involves the processor registers, the coprocessors, the MMU, the caches and the kernel's internal structures at once. On current hardware and kernels the **direct** cost is much lower: measurements on Linux put the register save and restore plus the scheduler's work in the range of one to a few microseconds.

The **indirect** cost is what remains significant. After the switch, P1 finds the caches and the TLB full of P0's data, and the misses it takes to rebuild its working set can cost far more than the switch itself; the classic measurement of this effect is the 2007 paper *Quantifying the Cost of Context Switch* by Li, Ding and Shen. Hardware features such as address-space identifiers (ASID on ARM, PCID on x86) let the TLB keep entries from several processes and avoid a full flush on every switch.

Either way the lecture's conclusion holds: the scheduling policy has a large effect on performance, and one of its goals is to keep the number of context switches as low as the workload allows. The scheduling lecture returns to this trade-off.

## Conclusion

The PCB is the kernel's record of a process: its state, identity, saved registers, address space, open files, children and exit code, in kernel memory only. It is allocated by `fork()` in the parent's context and released only after the parent has read the child's exit status with `waitpid()`, which is why a terminated but unreaped process remains as a zombie.

Four system calls cover a process's life. `fork()` duplicates the caller and returns `0` in the child and the child's PID in the parent; `exec()`, a family of library functions over `execve()`, replaces the binary image while keeping the PID and the open descriptors; `exit()` stores a status in the PCB and ends the process; `waitpid()` blocks the parent until a child ends, delivers the status and frees the PCB. Starting a program is `fork()` in the parent followed by `exec()` in the child.

A context switch happens inside the kernel when a process exits, blocks, or is preempted. It saves the outgoing process's registers and coprocessor state in its PCB, restores the incoming process's from its own, switches the MMU to the new address space, and returns to user mode at the new program counter. Its direct cost is small on current hardware; the cache and TLB misses it causes are not, which is why schedulers try to switch as rarely as the workload permits.

![Mindmap of the lecture covering the Process Control Block (contents, allocation, lifetime), process creation (fork, exec, exit, waitpid, fork plus exec) and the context switch (triggers, four steps, hardware involved, cost)]({{site.url_complet}}/assets/article/linux/sye-process-context-switch/2026-09-16-process-control-block-fork-exec-context-switch.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Process Control Block (PCB)** | The kernel data structure that records everything the kernel knows about one process: state, identifiers, saved registers, address space, open files, children and exit code. One per process, invisible to user space. |
| **`fork()`** | The system call that creates a child process as a copy of the caller; it returns `0` in the child, the child's PID in the parent, and `-1` on failure. |
| **`exec()` family** | POSIX library functions (`execl`, `execv`, `execvp`, ...) that replace the calling process's binary image with a new one, all implemented over the `execve()` system call. |
| **`execve()`** | The system call that loads a new binary image into the current process, passing it an argument vector and an environment, and starts it at its entry point. |
| **`exit()`** | The call that terminates the current process and stores an integer status in its PCB for the parent to collect. |
| **`waitpid()`** | The system call by which a parent blocks until a child terminates, retrieves the child's status and lets the kernel free the child's PCB. |
| **Zombie** | A process that has terminated but whose PCB is kept until its parent collects the exit status with `waitpid()`. |
| **Copy-on-write** | The technique by which Linux implements `fork()`: parent and child share physical pages marked read-only, and a page is copied only when one of them writes to it. |
| **Context switch** | The kernel operation that saves the running process's state in its PCB, restores another process's state from its PCB, reconfigures the MMU and resumes the second process. |
| **Preemption** | The scheduler's removal of the processor from a running process that has not blocked or exited, typically because its time slice is used up. |

## Frequently Asked Questions

**Q: Why can user-space code not read or modify its own PCB?**

The PCB lives in kernel memory, which the MMU makes inaccessible in user mode. It holds fields the process must not be able to set for itself: its scheduling priority, its identity, its open-file table, the state of other processes it references. A process learns about its PCB only through system calls (`getpid()`, `getppid()`) and, on Linux, through the kernel-generated views in `/proc/<pid>/`.

**Q: `fork()` is called once and returns twice. How does each copy know which one it is?**

By the return value, which is the only difference between the two copies at the moment they resume. The child receives `0`; the parent receives the PID of the child, a positive integer it will later pass to `waitpid()`. A negative value means no child was created and `errno` explains why.

**Q: What is a zombie process, and how is it removed?**

A zombie is a process that has called `exit()` (or been terminated) but whose parent has not yet called `waitpid()`. Its memory has been released, but its PCB is kept because it holds the exit status the parent has not read. It is removed when the parent calls `waitpid()`, which delivers the status and lets the kernel free the PCB. If the parent exits first, the zombie is reparented to `init`/`systemd`, which reaps it.

**Q: In the lecture's exercise, why can `m2` never appear before `m1`, while `m3` can appear anywhere after `m0`?**

`m1` and `m2` are both printed by the original process P, in that order, and a single process executes its instructions sequentially. `m3` is printed by the first child C1, an independent process; the scheduler may run C1 before or after P prints either line. `m0` is printed before any `fork()`, so it is first in every case. The three valid outputs are `m0 m1 m2 m3`, `m0 m1 m3 m2` and `m0 m3 m1 m2`.

**Q: Why does UNIX split program launching into `fork()` and `exec()` instead of one call?**

Between the two calls the child runs the parent's code in its own process and can prepare the environment the new program will inherit:

- redirect standard input and output with `open()` and `dup2()`;
- close descriptors that should not leak, change the working directory, set resource limits;
- drop privileges or install a system-call filter before the untrusted program starts.

`CreateProcess` on Win32 has to express every such option as a parameter. The cost of the UNIX approach is the copy of the parent, which copy-on-write reduces to page-table work; `posix_spawn()` and `vfork()` exist for the cases where even that matters.

**Q: What does a context switch have to save and restore, and why does the MMU step exist?**

The execution context of the outgoing process is saved in its PCB, and the incoming process's is restored from its PCB. That context is the general-purpose registers, the program counter, the stack pointer, the status register, and the floating-point and coprocessor state.

The MMU step exists because the two processes have different address spaces: the same virtual address means different physical memory in each, so the page tables the MMU uses must be switched, and cached translations (the TLB) that belong to the old process must be invalidated or tagged so they are not applied to the new one.

**Q: If the direct cost of a context switch is only microseconds on modern hardware, why does the scheduler still try to minimise switches?**

Because the indirect cost dominates. After a switch, the incoming process runs with caches and TLB filled by the outgoing process, and it pays a burst of misses to bring its own working set back. That penalty grows with the size of the working set and can exceed the direct switch cost by an order of magnitude.

A scheduler that switches less often lets each process amortise that warm-up over a longer run, at the price of longer response times for the processes waiting.

## References

- *SYE - S4 Processus, appels systèmes et changement de contexte*, DR, FG, MZ, HEIG-VD, 2020 (source lecture)
- [SO3 - Smart Object Oriented operating system](https://github.com/smartobjectoriented/so3), the teaching kernel used by the lecture
- [fork(2) - Linux manual page](https://man7.org/linux/man-pages/man2/fork.2.html)
- [clone(2) - Linux manual page](https://man7.org/linux/man-pages/man2/clone.2.html)
- [execve(2) - Linux manual page](https://man7.org/linux/man-pages/man2/execve.2.html)
- [exec(3) - Linux manual page](https://man7.org/linux/man-pages/man3/exec.3.html)
- [wait(2), waitpid(2) - Linux manual page](https://man7.org/linux/man-pages/man2/wait.2.html)
- [exit(3) - Linux manual page](https://man7.org/linux/man-pages/man3/exit.3.html) and [_exit(2)](https://man7.org/linux/man-pages/man2/_exit.2.html)
- [posix_spawn(3) - Linux manual page](https://man7.org/linux/man-pages/man3/posix_spawn.3.html)
- [setbuf(3) - Linux manual page](https://man7.org/linux/man-pages/man3/setbuf.3.html), stdio buffering modes
- [Linux `struct task_struct`, include/linux/sched.h (v6.12)](https://elixir.bootlin.com/linux/v6.12/source/include/linux/sched.h)
- Chuanpeng Li, Chen Ding, Kai Shen, *Quantifying the Cost of Context Switch*, ACM Workshop on Experimental Computer Science (ExpCS), 2007
- Andrew S. Tanenbaum, Herbert Bos, *Modern Operating Systems*, Pearson, 4th edition, 2014

### Related articles

- [Advanced GNU/Linux Security - SECCOMP and Linux Security Modules (LSM)]({{site.url_complet}}/2026/06/29/linux-advanced-security-seccomp-lsm/)
- [Linux Isolation Primitives - Defense in Depth Beyond the Castle Model]({{site.url_complet}}/2026/06/29/linux-isolation-primitives-defense-in-depth/)
