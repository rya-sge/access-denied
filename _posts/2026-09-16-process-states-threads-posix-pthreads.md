---
layout: post
title: "Process States, Threads and the POSIX Threads Library"
date:   2026-09-16
lang: en
locale: en-GB
categories: linux programmation
tags: linux process threads pthread posix scheduling concurrency race-condition operating-system
series: sye
series_order: 3
description: "The five process states and their transitions, what a thread owns and shares, the TCB, pthread_create/join/exit, and why two threads on a counter lose updates."
image: /assets/article/linux/sye-states-threads/2026-09-16-process-states-threads-posix-pthreads.png
isMath: false
---

The [previous article in this series]({{site.url_complet}}/2026/09/16/process-control-block-fork-exec-context-switch/) described the Process Control Block and the context switch that saves and restores it. A context switch is triggered when a process terminates, blocks, or is preempted, and each of those events moves the process from one **state** to another. The first part of this article names those states, New, Ready, Running, Waiting and Zombie, and the transitions between them, then shows how the kernel keeps one list of processes per state.

The second part refines the definition of a process. A process may contain several **execution contexts**, each with its own registers, program counter and stack, all sharing the same code, data and heap. Such a context is a **thread**, described by its own Thread Control Block. The last part introduces the POSIX threads API, `pthread_create()`, `pthread_join()` and `pthread_exit()`, through the lecture's example program, and ends on what that example is designed to show: two threads incrementing the same global counter do not produce the expected total, which is the problem the synchronisation lectures set out to solve.

> **Source and currency note.** This article is based on the lecture *SYE - S5 États et threads* (DR, FG, MZ, HEIG-VD, 2020). The state model and the POSIX threads API are unchanged. Two points are updated in place: the lecture's remark that Windows supports POSIX threads through its POSIX subsystem refers to the Subsystem for UNIX-based Applications, removed after Windows 8.1 and Server 2012 R2; and the explanation of the lecture's non-deterministic counter, which the slides leave as a question, is given here in terms of the C memory model and the instruction sequence behind `count++`.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## States and transitions

### The five states

At any moment a process is in exactly one state, recorded in its PCB. The lecture uses five:

| State | Meaning |
|-------|---------|
| **New** | The process has been created by `fork()` and is being initialised; its PCB exists but it cannot be scheduled yet. |
| **Ready** | The process has everything it needs to run except a processor. It waits in the scheduler's ready queue. |
| **Running** | The process is executing on a processor. On a machine with X processors, at most X processes are in this state. |
| **Waiting** | The process is blocked on an event it cannot make progress without: an I/O completion, a resource held by someone else, a `waitpid()` on a child that has not exited. |
| **Zombie** | The process has terminated; its memory is released, but its PCB is kept until the parent collects its exit status with `waitpid()`. |

### The transitions

![State machine of a process: fork() creates it in New, it becomes Ready once initialised, the scheduler elects it to Running, preemption sends it back to Ready, an I/O request or wait sends it to Waiting, the event completion returns it to Ready, exit() moves it to Zombie and waitpid() reaps it]({{site.url_complet}}/assets/article/linux/sye-states-threads/process-state-machine-concept.png)

Each arrow in the state diagram corresponds to one of the events discussed in the previous article:

- **New → Ready.** Initialisation is complete: the PCB is filled in, the address space is set up, and the process is placed in the ready queue.
- **Ready → Running.** The scheduler elects the process and the context switch loads its state into a processor.
- **Running → Ready.** The scheduler **preempts** the process, typically because its time slice is used up. The process could still run; it has only lost the processor.
- **Running → Waiting.** The process **suspends itself** by asking for something that is not available: it issues a `read()` that has to reach a disk, waits on a lock, or calls `waitpid()` on a live child. The kernel marks it as blocked and schedules another process.
- **Waiting → Ready.** The event the process was waiting for occurs: the I/O completes, the resource is released, the child exits. The kernel **wakes** the process by moving it back to the ready queue. It does not run immediately; it competes with the other ready processes.
- **Running → Zombie.** The process calls `exit()`, or returns from `main()`, or is killed. Its status is stored in its PCB and its parent is notified.

Two transitions are absent from the diagram, and their absence says as much as the arrows. A process never goes from Waiting straight to Running: being woken only makes it eligible, and the scheduler still has to pick it. And a process never goes from Ready to Waiting: only a running process can issue the request that blocks it.

### One list per state

The lecture's second slide on the subject shows how the kernel organises processes by state: for each state, a linked list of PCBs. New processes P0 to PN sit in one list, ready processes PN+1 to PM in another, and so on. The Running list is special: it has one entry per processor, so on a machine with X CPUs it holds PM+1 on CPU#1, PM+2 on CPU#2, up to PM+X on CPU#X. Every other list can be arbitrarily long.

```text
New      : P0 -> P1 -> ... -> PN
Ready    : PN+1 -> PN+2 -> ... -> PM          (the run queue)
Running  : PM+1 (CPU#1), PM+2 (CPU#2), ..., PM+X (CPU#X)
Waiting  : PX+1 -> PX+2 -> ... -> PY          (one per event in practice)
Zombie   : PY+1 -> PY+2 -> ... -> PZ
```

The state transitions above are then list operations: preemption unlinks a PCB from a Running slot and appends it to Ready; blocking moves it from Running to Waiting; a wake-up moves it from Waiting to Ready.

In a real kernel the Waiting list is not one list but many, one **wait queue** per event or resource, so that an I/O completion wakes exactly the processes waiting on that device rather than scanning every blocked process.

Linux exposes the state of each process in the `State` field of `/proc/<pid>/status` and in the `STAT` column of `ps`: `R` for running or runnable (the lecture's Ready and Running), `S` and `D` for the two flavours of Waiting (interruptible and uninterruptible sleep), `Z` for zombie.

## Definition of a thread

### One process, several execution contexts

The earlier articles defined a process as an execution context plus a memory context. The lecture now relaxes the first half: a process contains **one or more** execution contexts, and each such context is called a **thread**. The lecture's Process Explorer screenshot shows a `chrome.exe` process with several threads, each with its own thread ID, its own state, its own CPU time and its own stack of return addresses, all inside one process.

Two rules follow:

- **A thread is created from another thread.** There is no thread without a creator, except the first one.
- **Every process has at least one thread**, the **main thread** (T0), which the kernel starts once the binary image has been loaded and which runs `main()`. All the other threads of the process descend from it.

The lecture's figure shows a process P0 with one thread T0, and a process P1 with five threads T0 to T4. The threads of P1 are execution contexts of the same program: they run its code, read and write its data, and allocate from its heap.

### What a thread owns and what it shares

The distinction between execution context and memory context determines what is per-thread and what is per-process:

| Per thread (execution context) | Per process (memory context and resources) |
|--------------------------------|--------------------------------------------|
| Program counter | Code |
| Data registers | Data and BSS (global and static variables) |
| Stack pointer and **its own stack** | Heap |
| State (ready, running, waiting) | Open file descriptors |
| Priority | Address space, PID, parent, children, exit code |

The memory layout of a multithreaded process therefore contains several stacks, one per thread, and one copy of everything else. The lecture's figure places Stack T0, Stack T1, ..., Stack Tn at the top of the address space, then the free region, then the heap, BSS, data and code shared by all of them.

![Memory layout of a multithreaded process: the PCB in kernel space points to one TCB per thread, each TCB's stack pointer points to that thread's private stack in the address space, and the heap, BSS, data and code regions are shared by all threads]({{site.url_complet}}/assets/article/linux/sye-states-threads/thread-memory-pcb-tcb-concept.png)

The per-thread stack is what makes a thread's function calls independent of the other threads': each thread has its own frames, its own local variables and its own return addresses. The shared heap, data and BSS are what make threads useful and dangerous at the same time. A pointer to a heap block or a global variable is valid in every thread, so threads exchange data at the cost of a memory write; but nothing prevents two threads from writing the same location at the same time, which is the subject of the last section.

### The Thread Control Block

Just as a process is described by its PCB, a thread is described by a **Thread Control Block** (TCB), the thread's identity card. The lecture lists its contents:

- the **instruction pointer** (saved program counter);
- the **data registers**;
- the **stack pointer**;
- a **state**;
- a **priority**.

These are exactly the fields that the previous article listed under "execution context" in the PCB. In a multithreaded kernel they move out of the PCB into one TCB per thread, and the PCB keeps a **list of its threads**. The remaining PCB fields, the heap, the open files, the children, the address space and the exit code, stay in the PCB because they belong to the process as a whole.

A context switch between two threads of the same process saves and restores TCBs but does not have to reconfigure the MMU, since the address space does not change; this is why switching between threads is cheaper than switching between processes.

On Linux the distinction is flattened: the kernel schedules **tasks**, each described by a `task_struct`, and a "process" is a group of tasks sharing the same `mm_struct`, `files_struct` and thread-group ID. What the lecture calls the TCB is the per-task part of `task_struct`; what it calls the PCB is the part shared through pointers.

### Hardware threads

The lecture's slide carries a Pentium 4 badge with the **Hyper-Threading** logo, a reminder that the word *thread* is also used for a hardware feature. A hyper-threaded core presents itself to the operating system as two logical processors, each with its own register set, sharing the core's execution units and caches. To the scheduler these are two CPUs, so two software threads can be in the Running state on one physical core.

Hardware threads are a way of filling execution units that a single instruction stream leaves idle; software threads are the execution contexts the operating system schedules. The two meet only in the sense that the scheduler counts logical processors, not cores, when it fills the Running list.

## The POSIX threads library

### POSIX and IEEE 1003.1c

[POSIX](https://pubs.opengroup.org/onlinepubs/9799919799/), the *Portable Operating System Interface*, is the family of IEEE standards that defines a common programming interface for UNIX-like systems; the lecture glosses the final X as *uniX, linuX, macosX*. Its threads part, originally published as **IEEE Std 1003.1c-1995** and since merged into the base specification, defines the API known as **pthreads**. It covers three areas, which the lecture lists:

- **creation and termination** of threads;
- **synchronisation** between threads: join, mutexes, condition variables;
- **concurrent access** to shared data, through the mutex and read-write lock primitives that solve the problem shown in the last section.

The API is implemented on Linux by glibc (the NPTL implementation, on top of `clone()`), on macOS and the BSDs natively, and on Windows historically through the POSIX subsystem the lecture mentions. That subsystem, later called the Subsystem for UNIX-based Applications, was dropped after Windows 8.1 and Server 2012 R2; a Windows program that needs pthreads today uses a compatibility library such as pthreads-win32, the Windows Subsystem for Linux, or the native Win32 thread API.

### Creating a thread

A thread is created with [`pthread_create()`](https://man7.org/linux/man-pages/man3/pthread_create.3.html):

```c
#include <pthread.h>

int pthread_create(pthread_t *thread, const pthread_attr_t *attr,
                   void *(*start_routine)(void *), void *arg);
```

Its four parameters are the thread's identifier, its attributes, its code and its argument:

- **`thread`** receives the identifier of the new thread, of type `pthread_t`, which is what the creator later passes to `pthread_join()`.
- **`attr`** points to attributes (stack size, detached state, scheduling policy); `NULL` selects the defaults.
- **`start_routine`** is the function the new thread executes. Its prototype is fixed: it takes one `void *` and returns one `void *`. This is the *threaded function*.
- **`arg`** is the single argument passed to `start_routine`. Anything more elaborate than one pointer is passed by pointing at a structure.

The function returns `0` on success and an error number on failure. Unlike most system calls it does **not** set `errno`; the error code is the return value itself. The new thread starts executing `start_routine(arg)` immediately and concurrently with its creator; nothing in the API says which of the two runs first.

### Waiting for a thread and terminating one

[`pthread_join()`](https://man7.org/linux/man-pages/man3/pthread_join.3.html) is the thread-level counterpart of `waitpid()`:

```c
int pthread_join(pthread_t thread, void **retval);
```

The calling thread blocks until `thread` terminates, and the value that thread returned is stored through `retval` if it is not `NULL`. Joining also releases the terminated thread's resources, exactly as `waitpid()` releases a zombie's PCB; a thread that is never joined (and was not created detached) keeps its TCB and stack allocated until the process exits.

A thread terminates in one of two ways. It can **return from its start routine**, which the lecture notes is the normal case when there is no particular value to hand back; the return value of the function becomes the value delivered by `pthread_join()`. Or it can call [`pthread_exit()`](https://man7.org/linux/man-pages/man3/pthread_exit.3.html) from any depth of its call stack:

```c
void pthread_exit(void *retval);
```

`pthread_exit()` ends the calling thread only. The process continues as long as other threads are running; and conversely, `exit()` called by any thread terminates the whole process, including threads that are still in the middle of their work. In the main thread, returning from `main()` calls `exit()` and therefore kills the other threads, which is why a `main()` that spawns workers must join them, or call `pthread_exit()` itself, before returning.

## Running threads

### The example program

The lecture's example creates a thread that prints a greeting and increments a global counter one hundred thousand times. In its first version, `main()` creates one thread, joins it, and prints the counter. The threaded function and the creation call are the two parts to look at:

```c
#include <string.h>
#include <pthread.h>
#include <stdio.h>

int count = 0;

void *printHello(void *args) {
  char *th_name;
  int i;

  th_name = (char *) args;

  printf("Hello! It's me, I am thread %s.\n", th_name);

  for (i = 0; i < 100000; i++)
    count++;

  return NULL;
}
```

`printHello()` has the mandatory prototype, `void *(void *)`, and recovers its real argument, a string, by casting `args` back to `char *`. `count` is a global, so it lives in the process's data segment and is visible to every thread. The function returns `NULL` because there is nothing to hand back.

In `main()`, the thread is created and joined as follows; the error path shows the return-value convention of `pthread_create()`:

```c
  pthread_t hello_thread;
  int ret;
  char th_name[20];

  strcpy(th_name, "Thread SYE");

  ret = pthread_create(&hello_thread, NULL, printHello, (void *) th_name);
  if (ret) {
    printf("ERROR; return code from pthread_create() is %d\n", ret);
    exit(-1);
  }

  pthread_join(hello_thread, NULL);

  printf("count = %d\n", count);
  exit(0);
```

`th_name` is a local array of `main()`, so it lives on the main thread's stack. Passing its address to another thread is safe here only because `main()` joins the thread before returning; if `main()` returned first, the worker would be reading a dead stack frame.

### Two threads and a sequence diagram

The second version creates two threads, `hello_thread1` and `hello_thread2`, with two names, and joins both before printing the counter. The lecture draws the resulting sequence diagram: T0 enters `main()`, calls `pthread_create()` twice, and blocks in `pthread_join(T1)`; T1 and T2 run concurrently and each returns when its loop is done; T0 resumes after T1's return, blocks again in `pthread_join(T2)` if T2 is still running, and finishes after T2's return.

![Sequence diagram of the lecture's two-thread program: the main thread T0 creates T1 and T2 with pthread_create, both run the counting loop on the shared variable count, T0 blocks in pthread_join until T1 returns and again until T2 returns, then prints count and exits]({{site.url_complet}}/assets/article/linux/sye-states-threads/pthread-create-join-sequence-workflow.png)

The order of the two `pthread_join()` calls does not matter for correctness: if T2 finishes before T1, the second join returns immediately. What matters is that both are joined before `count` is read.

### What happens: the counter is wrong

Each thread adds one hundred thousand to `count`, so the expected output is `count = 200000`. The lecture's terminal capture of ten successive runs shows otherwise:

```text
$ ./app
Hello! It's me, I am thread Thread SYE 1.
Hello! It's me, I am thread Thread SYE 2.
count = 123001
$ ./app
...
count = 200000
$ ./app
...
count = 149549
$ ./app
...
count = 123501
$ ./app
...
count = 108533
```

Some runs print `200000`; others print `123001`, `149549`, `123501` or `108533`. The result is never larger than `200000`, it varies from run to run, and it is wrong more often than not. The slide leaves the question open ("but what happens?"); the answer is the entry point of the synchronisation lectures, and it is short enough to give here.

`count++` is one statement in C but three operations for the processor: **load** the current value of `count` from memory into a register, **add** one to the register, **store** the register back to memory. On ARM:

```text
ldr   r3, [r2]        @ load  count into r3
add   r3, r3, #1      @ add   1
str   r3, [r2]        @ store r3 back to count
```

The two threads run this sequence concurrently, on two processors or interleaved by preemption on one. Nothing prevents the following interleaving:

| Step | Thread T1 | Thread T2 | `count` in memory |
|------|-----------|-----------|-------------------|
| 1 | `ldr r3 ← 41` | | 41 |
| 2 | | `ldr r3 ← 41` | 41 |
| 3 | `add r3 = 42` | | 41 |
| 4 | | `add r3 = 42` | 41 |
| 5 | `str 42` | | 42 |
| 6 | | `str 42` | 42 |

Two increments were executed and `count` grew by one: the update of T1 was **lost**, overwritten by T2's store of a stale value. Every time the scheduler or the hardware interleaves the two threads inside the load-add-store window, one increment disappears, which is why the total is always at most `200000` and usually below it. The runs that print `200000` are those in which the interleaving happened to fall between complete increments every time, or in which one thread ran its whole loop before the other started.

This is a **data race**: two threads access the same memory location without synchronisation, and at least one access is a write. In C11 and later a program containing a data race has undefined behaviour, so the compiler is even allowed to keep `count` in a register for the whole loop and store it once at the end, which would make the outcome worse still.

The fix is to make the read-modify-write **atomic** with respect to the other thread, either by protecting it with a mutex (`pthread_mutex_lock()` / `pthread_mutex_unlock()` around the increment) or by declaring `count` as a C11 `_Atomic int` so that the increment compiles to an atomic instruction. Both belong to the "concurrent access" part of the pthreads API and are the subject of the next lectures.

## Conclusion

A process moves through five states. It is created in New, waits for a processor in Ready, executes in Running, blocks in Waiting when it asks for something unavailable, and ends in Zombie until its parent reaps it. Preemption returns it from Running to Ready, a wake-up from Waiting to Ready, and only the scheduler moves it into Running. The kernel maintains one list of PCBs per state, with as many Running entries as processors.

A thread is one execution context of a process: its own program counter, registers, stack and state, recorded in a Thread Control Block, sharing the process's code, data, heap and open files. Every process starts with one thread that runs `main()`; the others are created from it. The POSIX threads API creates a thread with `pthread_create()` around a `void *(void *)` function, waits for it with `pthread_join()`, and ends it by returning from that function or calling `pthread_exit()`.

The lecture's closing example shows two threads incrementing one global counter and printing totals between 108533 and 200000 across runs. The cause is that `count++` is a load, an add and a store, and an interleaving of two threads inside that window loses an update. Shared memory is what makes threads convenient; unsynchronised writes to it are a data race, and removing them is the subject of the lectures that follow.

![Mindmap of the lecture covering process states and transitions, the definition of a thread and its TCB, the POSIX threads API (pthread_create, pthread_join, pthread_exit) and the two-thread counter example that loses updates]({{site.url_complet}}/assets/article/linux/sye-states-threads/2026-09-16-process-states-threads-posix-pthreads.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Ready** | The state of a process that could run but has no processor; such processes wait in the scheduler's run queue. |
| **Waiting** | The state of a process blocked on an event (I/O completion, resource, child exit); it leaves this state only when the event occurs, and then goes to Ready, not Running. |
| **Preemption** | The transition from Running to Ready imposed by the scheduler on a process that has used up its time slice. |
| **Zombie** | A terminated process whose PCB is retained until its parent reads its exit status. |
| **Thread** | One execution context of a process: its own program counter, registers, stack and state, sharing the process's memory context and resources. |
| **Main thread** | The first thread of a process, started by the kernel after the binary image is loaded, which executes `main()`. |
| **Thread Control Block (TCB)** | The kernel structure describing one thread: instruction pointer, data registers, stack pointer, state and priority. The PCB keeps a list of its TCBs. |
| **pthreads** | The POSIX threads API (IEEE 1003.1c), covering thread creation and termination, synchronisation and concurrent access. |
| **`pthread_join()`** | The call by which one thread blocks until another terminates and collects its return value, releasing its resources; the thread-level analogue of `waitpid()`. |
| **Data race** | Two threads accessing the same memory location without synchronisation, at least one of them writing; the cause of the lost increments in the lecture's counter example. |

## Frequently Asked Questions

**Q: Why is there no transition from Waiting directly to Running?**

Because the event a process waits for only makes it eligible to run again; it does not give it a processor. When the I/O completes or the resource is released, the kernel moves the process to Ready, where it competes with every other ready process. The scheduler then decides, according to its policy and priorities, which ready process gets the next free processor.

Waking a process and scheduling it are two separate decisions taken by two different parts of the kernel.

**Q: How many processes can be in the Running state at once?**

At most one per processor as seen by the scheduler. On a machine with X logical CPUs the Running list has X slots. With Hyper-Threading, each physical core exposes two logical processors, so a four-core hyper-threaded machine can have eight processes (or threads) Running at once.

**Q: What does a thread own, and what does it share with the other threads of its process?**

It owns its execution context: program counter, data registers, stack pointer and a private stack, plus a state and a priority, all recorded in its TCB.

It shares the memory context and the resources of the process: code, data and BSS, heap, open file descriptors, address space, PID and parent. A global variable or a heap block is therefore visible to every thread; a local variable of a function is on the stack of the thread executing that function.

**Q: Why must the function passed to `pthread_create()` have the prototype `void *f(void *)`?**

Because `pthread_create()` is a single library function that has to start any user function without knowing its real parameter and return types. A `void *` in and a `void *` out is the most general signature C offers: any pointer can be converted to and from `void *`. The caller packs its real arguments behind one pointer (a string in the lecture's example, a structure in general) and the thread casts it back; the value returned is delivered to whoever calls `pthread_join()`.

**Q: In the lecture's two-thread program, why is the final counter sometimes 200000 and sometimes much less, but never more?**

Each thread performs one hundred thousand increments, so 200000 is the upper bound. An increment is a load, an add and a store; when the two threads interleave inside that window, both load the same value, both add one, and both store the same result, so one of the two increments is lost. Every such collision lowers the total by one and nothing can raise it.

A run prints 200000 when no collision happened, for instance because one thread finished its loop before the other started.

**Q: What is the relationship between `pthread_join()` and `waitpid()`?**

They play the same role one level apart. `waitpid()` lets a parent process block until a child process ends, retrieve its exit status and let the kernel free its PCB. `pthread_join()` lets a thread block until another thread of the same process ends, retrieve its return value and release its TCB and stack. In both cases an object that is terminated but not yet collected keeps its control block allocated.

**Q: A worker thread is still running when `main()` returns. What happens to it, and how is that avoided?**

Returning from `main()` calls `exit()`, which terminates the whole process and every thread in it, so the worker is killed wherever it is. To let the workers finish, `main()` either calls `pthread_join()` on each of them before returning, or calls `pthread_exit()` itself, which ends the main thread only and keeps the process alive until the last thread terminates.

## References

- *SYE - S5 États et threads*, DR, FG, MZ, HEIG-VD, 2020 (source lecture)
- [SO3 - Smart Object Oriented operating system](https://github.com/smartobjectoriented/so3), the teaching kernel used by the course
- [The Open Group Base Specifications Issue 8, IEEE Std 1003.1-2024 (POSIX)](https://pubs.opengroup.org/onlinepubs/9799919799/), including the threads interfaces originally specified in IEEE Std 1003.1c-1995
- [pthreads(7) - Linux manual page](https://man7.org/linux/man-pages/man7/pthreads.7.html)
- [pthread_create(3) - Linux manual page](https://man7.org/linux/man-pages/man3/pthread_create.3.html)
- [pthread_join(3) - Linux manual page](https://man7.org/linux/man-pages/man3/pthread_join.3.html)
- [pthread_exit(3) - Linux manual page](https://man7.org/linux/man-pages/man3/pthread_exit.3.html)
- [pthread_mutex_lock(3p) - POSIX manual page](https://man7.org/linux/man-pages/man3/pthread_mutex_lock.3p.html)
- [proc_pid_status(5) - Linux manual page](https://man7.org/linux/man-pages/man5/proc_pid_status.5.html), the `State` field of a process
- [Process Explorer - Sysinternals](https://learn.microsoft.com/en-us/sysinternals/downloads/process-explorer)
- Andrew S. Tanenbaum, Herbert Bos, *Modern Operating Systems*, Pearson, 4th edition, 2014

### Related articles

- [Les moniteurs avec PcoSynchro]({{site.url_complet}}/2021/06/01/moniteurs-pcosynchro/)
