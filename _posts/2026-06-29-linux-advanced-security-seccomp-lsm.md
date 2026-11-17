---
layout: post
title: Advanced GNU/Linux Security - SECCOMP and Linux Security Modules (LSM)
date:   2026-06-29
last_modified_at: 2026-11-17
lang: en
locale: en-GB
categories: linux security
tags: linux security seccomp lsm selinux apparmor mac syscalls bpf
series: linux-sos
series_order: 2
description: How SECCOMP filters system calls and how Linux Security Modules (SELinux, AppArmor, and others) add mandatory access control on top of the base UNIX permission model.
image: /assets/article/securite/linux-advanced-security/2026-06-29-linux-advanced-security-seccomp-lsm.png
isMath: false
---

The base GNU/Linux security primitives (authentication, file permissions, ACLs, extended attributes, capabilities) all rest on the discretionary model inherited from UNIX, where the owner of a resource decides who may access it. That model has two structural gaps. First, a running program may invoke *any* system call the kernel exposes, so a process diverted from its intended behaviour has the whole kernel interface at its disposal. Second, discretionary control cannot enforce a system-wide policy that even root must obey. This article covers the two advanced primitives the Linux kernel offers to close those gaps: SECCOMP, which filters the system calls a process may issue, and Linux Security Modules (LSM), the hook framework behind mandatory access control systems such as SELinux and AppArmor.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What you need to know first

The article assumes the basics of Linux (processes, file permissions, root) and relies on these mechanisms without developing them:

- **Base security primitives.** File permissions, ACLs, extended attributes and capabilities form the discretionary layer that SECCOMP and LSM extend. [GNU/Linux Base Security Primitives]({{site.url_complet}}/2026/06/29/linux-base-security-primitives/) covers them, and this article is the second part of that series.
- **System call numbers.** The kernel identifies each system call by a number, and that numbering differs between CPU architectures. A seccomp filter matches these numbers, which is why a filter written for one architecture does not carry over to another. [System Calls, Binary Images and Processes]({{site.url_complet}}/2026/09/16/system-calls-binary-image-process/) explains how a call enters the kernel.
- **BPF (Berkeley Packet Filter).** A small virtual machine inside the kernel, first used to filter network packets for tools such as `tcpdump`. seccomp-bpf reuses it to run a filter program on each system call.
- **Inodes, paths and hard links.** A file's data and metadata live in an inode, and a path is a directory entry that points to it. Several hard links can name the same inode. SELinux puts its labels on inodes and AppArmor writes its rules on paths, and most differences between the two follow from that choice.
- **Extended attributes.** Name-value pairs stored with an inode by the filesystem. SELinux keeps each file's security context in one of them.
- **Capabilities.** Root's privileges split into separate units such as `CAP_NET_ADMIN` or `CAP_SETUID`, which a process can hold individually. AppArmor profiles list the capabilities a confined program may use.
- **ptrace.** The system call that lets one process inspect and control another, used by debuggers and by `strace`. The Yama module restricts it.

## How Programs Talk to the Kernel

A user program does not touch hardware directly. When a shell runs `echo 'hello world'`, the text reaches the screen only because the program asks the kernel to perform the privileged operation on its behalf. There are two channels for that conversation:

1. **System calls (syscalls):** synchronous requests from a process into the kernel (documented under `man syscalls`). A `printf("hello world\n")` in C compiles down to a `write` syscall once the binary runs. The tool `strace ./hello` reveals the full sequence of syscalls a program makes.
2. **Signals:** asynchronous notifications defined by POSIX (`man 7 signal`), such as `SIGKILL` (terminate) or `SIGSEGV` (invalid memory access).

The compilation and execution chain is therefore: source code, compiled to a binary, which at run time issues syscalls to the kernel. This syscall boundary is the attack surface SECCOMP addresses.

### The Security Problem

A process has access to *every* system call the kernel provides, and some of those require superuser rights. This breadth conflicts with the second UNIX rule, "do one thing and do it well": a program that should only read and write a file has no legitimate need for `socket`, `ptrace`, or `mount`. The adversary model makes the risk concrete: a program's execution is not fixed. It can be redirected at run time by exploiting little-known options (the classic `vi` shell escape) or by injecting code through a buffer overflow. Once redirected, the attacker inherits the program's full syscall reach.

The security primitive is to filter system calls like a firewall, allowing only those a program needs, in keeping with least privilege.

## SECCOMP (Secure Computing)

SECCOMP was created in 2005 by Andrea Arcangeli. Its first form, **mode 1 (strict mode)**, was aimed at selling spare CPU cycles for grid computing: an untrusted process was confined to just four system calls, `exit()`, `sigreturn()`, `read()`, and `write()`, and the last two only on file descriptors already open. Anything else terminated the process. This is safe but far too restrictive for general programs.

**Mode 2**, [seccomp-bpf](https://www.kernel.org/doc/html/latest/userspace-api/seccomp_filter.html), generalizes the idea using the Berkeley Packet Filter (BPF) virtual machine to express which syscalls are permitted. Instead of a fixed list of four, a developer writes a filter program that the kernel runs on every system call. Adoption followed once this flexibility existed:

- 2009: Linus Torvalds questions whether SECCOMP is used in practice.
- 2012: Chrome (`chrome://sandbox`) and Firefox (`cat /proc/PID/status | grep Seccomp`) adopt it.
- 2013: OpenSSH adds support.
- 2017: qemu adopts it.

### How seccomp-bpf Works

The filter is usually installed by the program itself, but filters are inherited across `fork`, `clone` and `execve`, so a launcher, a service manager or a container runtime can also install one before starting an unmodified program. Before installing a filter, the task must set `PR_SET_NO_NEW_PRIVS` or hold `CAP_SYS_ADMIN` in its namespace, which stops a filter from being applied to a child process with more privileges than the task that installed it.

A BPF program works as a whitelist of system calls to allow, a blacklist of calls to refuse, or a mix of both, and the kernel evaluates it on each syscall. Every rule returns one of eight verdicts: allow the call, log and then allow it, fail it with an error code, raise a `SIGSYS` signal, pass it to a `ptrace` tracer, forward it to a userspace supervisor, or kill the calling thread or the whole process.

![seccomp-bpf filtering a system call]({{site.url_complet}}/assets/article/securite/linux-advanced-security/seccomp-bpf-filter-workflow.png)

A minimal C program installs the filter before doing its real work:

```c
#include <stdio.h>
#include <linux/unistd.h>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/seccomp.h>

/* ... */

int main(void) {
    if (install_syscall_filter())
        return 1;

    printf("hello world\n");
    return 0;
}
```

The filter itself is an array of BPF rules. Allowed syscalls fall through to execution; anything not matched hits the terminal `KILL_PROCESS` rule:

```c
static int install_syscall_filter(void)
{
    struct sock_filter filter[] = {
        /* ... */
        ALLOW_SYSCALL(rt_sigreturn),
        ALLOW_SYSCALL(exit_group),
        ALLOW_SYSCALL(exit),
        ALLOW_SYSCALL(read),
        ALLOW_SYSCALL(write),
        KILL_PROCESS,
        /* add your syscalls here */
        ALLOW_SYSCALL(WHAT-YOU-WANT),
    };
    /* ... */
}
```

**Trade-offs.** SECCOMP answers a long-standing risk, unrestricted access to all syscalls. It reuses the BPF virtual machine and can be retrofitted to an existing binary with modest effort. The costs are significant:

- the developer must determine the exact allow/deny list;
- some programs legitimately need many syscalls, which is in tension with the do-one-thing rule;
- an update to a program can change its syscall set and break the filter;
- the program must be modified to install its own filter, unless a launcher installs one for it;
- the filter is CPU-architecture-dependent because syscall numbers differ across architectures;
- the protection is barely visible from outside the process: `cat /proc/*/status | grep Seccomp`;
- in practice it remains little used.

## Linux Security Modules (LSM)

SECCOMP narrows the syscall interface but does not express an access-control *policy*. For that, Linux needed **mandatory access control (MAC)**. The vocabulary comes from the [Trusted Computer System Evaluation Criteria (TCSEC)](https://csrc.nist.gov/csrc/media/publications/conference-paper/1998/10/08/proceedings-of-the-21st-nissc-1998/documents/early-cs-papers/dod85.pdf), published in 1983 and known as the "Orange Book".

### DAC versus MAC

- **Discretionary Access Control (DAC):** access is limited based on the identity of subjects or the groups they belong to. It is *discretionary* because a subject holding a permission can pass that permission to any other subject. This is the standard UNIX permission model.
- **Mandatory Access Control (MAC):** used when the security policy requires that protection decisions are *not* made by the owner of the objects. The system associates and manages security attributes on files and processes according to a central policy, and even the owner (including root) cannot override it.

The kernel implements MAC through hooks. **LSM places hooks on kernel functions**, the code paths behind syscalls, signals and similar operations, so that a security module can be consulted before the operation proceeds. A generic interface named Linux Security Modules was developed in 2002 specifically so the kernel would not privilege any single MAC project.

The history explains the design: the NSA had been developing Security-Enhanced Linux (SELinux) since the late 1990s and proposed integrating it into the kernel in 2001; rather than merge one vendor's system, the kernel community built LSM as a neutral hook layer that any module could use.

![LSM hooks, DAC first then mandatory access control]({{site.url_complet}}/assets/article/securite/linux-advanced-security/lsm-hook-architecture-concept.png)

The checks run in a fixed order: the standard DAC check runs first, and only if it permits the operation does the LSM hook consult the active module(s). Access is granted only when DAC *and* every consulted module agree. Many modules build on LSM: SELinux, SMACK, AppArmor, TOMOYO, Yama, LoadPin, SafeSetID, and Lockdown.

## SELinux

[SELinux](https://github.com/SELinuxProject) was created by the NSA, satisfies the TCSEC requirements, and implements multi-level security (MLS) derived from MULTICS. It stores its security context in the **extended attributes** of the filesystem, so every file and process carries a label:

```text
$ ls -lZ /etc/passwd
-rw-r--r--. 1 root root system_u:object_r:etc_t:s0 1337 Mar 6 06:08 /etc/passwd

system_u = user   (a virtual SELinux user, not a login account)
object_r = role   (subject / object / domain)
etc_t    = type   (domain / security context)
s0       = range  (level, MLS)

$ ps axZ
system_u:system_r:sshd_t:s0-s0:c0.c1023 1932 ? S 0:00 sshd: alice@pts/1
```

### Type Enforcement

The heart of SELinux is **type enforcement**: access is decided by the *type* labels of subject and object, not by the UID. A type is a label assigned to a resource; for example, `/bin/passwd` is labelled `passwd_exec_t`. A domain is a security state identified by the rights it holds, such as `passwd_t`. Running the labelled executable triggers a domain transition, and a policy rule then permits or refuses the access regardless of who the calling user is.

![SELinux type enforcement, access decided by labels not UID]({{site.url_complet}}/assets/article/securite/linux-advanced-security/selinux-type-enforcement-concept.png)

The label has four components:

- **user**: a group of roles, distinct from a login account; no one can log in directly as an SELinux user.
- **role**: governs which subjects can enter which domains.
- **type/domain**: the type is the label on a resource, the domain is the runtime security state of a subject.
- **range**: the MLS level.

### Configuration

SELinux is configured under `/etc/selinux/` and runs in one of three modes: **Disabled**; **Permissive**, which only monitors and logs what it would block; and **Enforcing**, which blocks. Three policy types exist: `default` for the targeted policy, `mls` for Multi-Level Security, and `src` for a custom policy. Useful commands:

```text
sestatus ; getenforce ; setenforce        # status and mode control

getsebool ssh_sysadm_login                 # booleans simplify common tweaks
setsebool ssh_sysadm_login on

chcon unconfined_u:object_r:user_home_t:s0 alice-file.txt   # change context
restorecon alice-file.txt                  # restore the policy-defined context
```

Booleans exist precisely because writing raw policy is hard; they toggle common behaviours without editing rules.

**Trade-offs.** SELinux is the most complete LSM, a US standard, used mainly by RHEL/CentOS, offers incomparable granularity, ships with many default rules, and has improvements (booleans) that ease its use. Against that, it brings back the complexity of MULTICS:

- immense technical and administrative overhead;
- a steep learning curve;
- difficulty writing rules for a specific threat model;
- deactivation by some distributions, which may need a kernel recompile to change;
- reliance on filesystem extended attributes;
- rights that depend on how a file is handled: `mv` preserves the context, `cp` can reset it.

## AppArmor

[AppArmor](https://apparmor.net/), short for Application Armor, was created by the company Immunix under the name SubDomain, then developed by Novell for SUSE and Canonical for Ubuntu, and integrated into the Linux kernel in 2010. It is a deliberate counter-project to SELinux: simpler, and built on path-based identification.

The key design difference is the identifier. **SELinux labels inodes; AppArmor uses paths.** A profile constrains a program identified by the path to its executable, and confines it at the level of process rights. Those rights cover capabilities, file operations such as read, write, append, execute, lock and link, and sockets, ports and I/O.

Because it does not label objects, there is no `ls -lZ` output and no `.` appended to the mode string; the configuration lives in per-program text files. AppArmor is enabled by default on several distributions and supports two modes that can coexist for different processes: **enforce**, and **complain**, which only logs.

### Profiles

Profiles are text files in `/etc/apparmor.d/`, named after the executable path with `/` replaced by `.`. A profile lists several rule types, notably file paths and capabilities:

```text
# profile excerpt (file paths the process may touch)
/etc/passwd  r,
/dev/pts/*   rw,

# capabilities the confined process is allowed
capability net_admin,
capability setuid,
```

Management uses the boot option `apparmor=1 security=apparmor`, plus:

```text
apparmor_status                              # list enforce/complain profiles
aa-complain /etc/apparmor.d/bin.ping         # put a profile in complain mode
aa-enforce  /etc/apparmor.d/bin.ping         # put a profile in enforce mode
apparmor_parser                              # load/unload a profile in the kernel
service apparmor start                       # load all profiles in /etc/apparmor.d
```

**Trade-offs.** AppArmor is a simplified MAC keyed on program paths: generates profiles dynamically, manages capabilities, needs no labels on objects (avoiding filesystem-attribute incompatibilities), supports enforce and complain at once, ships by default on many distributions, and comes with many default rules. Its limits: it is an *incomplete* MAC by TCSEC standards and does not replace SELinux; identifiers are programs rather than files, so moving a file out of a protected path leaves it unprotected, granularity is coarse (fewer access choices), and a hard-link attack can be possible because two paths may point to the same inode.

## Other LSMs and Stacking

Beyond the two main MAC systems, several focused modules exist:

- **SMACK** (Simplified Mandatory Access Control): attribute-based, aimed at embedded systems.
- **TOMOYO:** path-based, embedded systems, builds a profile of process interactions.
- **LoadPin:** ensures that every file the kernel loads (modules, firmware) comes from the same filesystem, expected to be read-only, for embedded systems.
- **Yama:** restricts `ptrace()`, an improved DAC.
- **SafeSetID:** hardens UID/GID management.
- **Lockdown:** protects kernel integrity.

These modules can be **stacked**, with a notion of major and minor modules, so a system can run one comprehensive MAC, such as SELinux or AppArmor, alongside targeted modules such as Yama and LoadPin. Solutions also exist outside LSM, such as the paid grsecurity and RSBAC.

Defining a single adversary model for the LSM family is hard because the options are so numerous. A reasonable division: SELinux, AppArmor, SMACK, and TOMOYO target general mandatory access control, while Yama, LoadPin, SafeSetID, and Lockdown provide targeted protection against specific attacks.

## Conclusion

When defenses are organized around many distinct adversary models, each addressing a specific attack, the security toolkit becomes a complex suite to describe and operate. 

- SECCOMP filters the syscall interface but must be compiled in and maintained per architecture; 
- LSM-based MAC systems enforce policies the owner cannot override, with SELinux offering the most complete and most demanding option and AppArmor trading completeness for a simpler path-based model. 

The cost is that no single tool gives a global view of risk, even though each answers a real need, and the overall technical complexity (entropy) grows quickly. 

This is the MULTICS syndrome: the simplicity that made UNIX practical is gradually traded back for protection. The castle model of perimeter defense no longer suffices on its own, which is why least privilege leads toward defense in depth, and from there to process isolation and virtualization.

![Advanced GNU/Linux security mindmap]({{site.url_complet}}/assets/article/securite/linux-advanced-security/2026-06-29-linux-advanced-security-seccomp-lsm.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **System call (syscall)** | A synchronous request from a process into the kernel to perform a privileged operation, such as `write`. |
| **Signal** | An asynchronous POSIX notification delivered to a process, such as `SIGKILL` or `SIGSEGV`. |
| **SECCOMP strict mode (mode 1)** | The original SECCOMP, which confines a process to `exit`, `sigreturn`, `read` and `write` on already-open descriptors and kills it on any other call. |
| **seccomp-bpf (mode 2)** | SECCOMP with a BPF filter program, written by the developer, that the kernel runs on each system call to choose a verdict. |
| **SIGSYS** | The signal a seccomp filter can raise instead of letting a refused system call run. |
| **Discretionary Access Control (DAC)** | Access decided by the identity of subjects and groups, where a holder of a permission can pass it on; the standard UNIX model. |
| **Mandatory Access Control (MAC)** | Access decided by a central policy on security attributes of files and processes, which the owner, root included, cannot override. |
| **TCSEC (Orange Book)** | The 1983 US Department of Defense criteria that define the DAC and MAC vocabulary. |
| **Linux Security Modules (LSM)** | The kernel's neutral hook framework, consulted after the DAC check, on which MAC modules such as SELinux and AppArmor are built. |
| **LSM stacking** | Running one comprehensive MAC module alongside targeted modules such as Yama or LoadPin. |
| **Security context** | The SELinux label `user:role:type:range` attached to every file and process, shown by `ls -Z` and `ps -Z`. |
| **Type enforcement** | The SELinux rule that decides access from the type of the object and the domain of the subject, not from the UID. |
| **Domain transition** | The change of a process to a new SELinux domain when it runs an executable with a given type, such as `passwd_exec_t` to `passwd_t`. |
| **Multi-level security (MLS)** | The SELinux policy type that adds sensitivity levels, the `range` field of the context. |
| **SELinux boolean** | A named switch that turns a common policy behaviour on or off without editing rules, set with `setsebool`. |
| **Permissive / complain mode** | A mode in which SELinux (permissive) or an AppArmor profile (complain) logs what it would block without blocking it. |
| **AppArmor profile** | A text file in `/etc/apparmor.d/` that lists the paths, capabilities and network access one program may use, identified by the program's path. |

## Frequently Asked Questions

**Q: What are the two channels a program uses to communicate with the kernel, and how do they differ?**

System calls and signals. System calls are synchronous requests a process makes into the kernel to perform privileged operations (a C `printf` becomes a `write` syscall), and the process waits for the result. Signals are asynchronous notifications defined by POSIX, such as `SIGKILL` or `SIGSEGV`, that can reach a process at any time independent of what it is doing. SECCOMP filters the first channel.

**Q: Why was SECCOMP strict mode (mode 1) too limited, and what did mode 2 change?**

Strict mode allowed only four system calls: `exit`, `sigreturn`, `read` and `write`, the last two only on already-open descriptors. That suited an untrusted grid-computing workload but is unusable for ordinary programs that need to open files, allocate memory, or use the network.

Mode 2, seccomp-bpf, replaced the fixed list with a BPF filter program that the developer writes. Each application can then permit exactly the syscalls it needs and choose the verdict for the rest, for example allow, log, error, SIGSYS or kill.

**Q: What is the difference between discretionary and mandatory access control?**

Under DAC, access is decided by the identity of subjects and groups, and a subject holding a permission can pass it on to others, which is the standard UNIX model where the file owner sets the bits. 

Under MAC, a central policy decides, security attributes are attached to files and processes, and the owner (root included) cannot override the policy. LSM is the kernel hook framework that lets MAC modules enforce such policies.

**Q: In SELinux type enforcement, why can an access be refused even when the UNIX permissions and the UID would allow it?**

Because SELinux decides on the *type labels* of the subject domain and the object, not on the UID. After the DAC check passes, the LSM hook consults SELinux, which looks for an `allow` rule matching the subject's domain and the object's type, for example `passwd_t` and `shadow_t`. 

If no such rule exists, the access is denied regardless of ownership, so even root is bound by the policy. 

This label-based decision, derived from MULTICS MLS, is what makes it mandatory rather than discretionary.

**Q: SELinux and AppArmor are both MAC systems. What is the core design difference, and what practical consequence follows from it?**

SELinux identifies objects by labelling their inodes (stored in filesystem extended attributes), while AppArmor identifies a confined program by the path to its executable and constrains it by path-based rules. 

The practical consequence is that AppArmor's protection follows the path rather than the data: moving or copying a file out of a protected path leaves it unconfined, and because different paths can point to the same inode, a hard-link attack is possible. 

SELinux's inode labels travel with the file under `mv`, though `cp` can reset them. This gives stronger but more complex guarantees, which is why AppArmor is considered an incomplete MAC by TCSEC standards yet easier to operate.

**Q: Combining SECCOMP and LSM with the earlier base primitives, why does the lecture conclude that the castle model is no longer enough?**

Each primitive answers a different, narrowly stated adversary model: 

- SECCOMP for an attacker who hijacks a process to abuse syscalls, 
- MAC for an attacker who would otherwise rely on the owner's discretion, capabilities for the all-or-nothing root problem. 

Stacking these produces a powerful but complex toolkit with no single global view of risk, and the technical entropy keeps rising (the MULTICS syndrome). Because attackers increasingly start from *inside* a compromised process rather than at the perimeter, defending only the walls (the castle model) leaves the interior exposed. 

The logical next step is least privilege applied in depth, then isolating processes from one another through namespaces, containers, and virtualization, which is the subject that follows this lecture.

## Gaps

The article follows a 2021 lecture. These points were not checked against current kernel sources or rest on the lecture alone, and should be verified before relying on them.

| Gap | Why it matters | What to read or verify |
|-----|----------------|------------------------|
| Landlock and the BPF LSM, added after the lecture's material, are not covered. | Landlock lets an unprivileged process sandbox itself, which changes the comparison with seccomp. | The [Landlock documentation](https://docs.kernel.org/userspace-api/landlock.html) and the [LSM documentation](https://www.kernel.org/doc/html/latest/admin-guide/LSM/index.html). |
| The stacking rules (one major module plus minor ones) come from the lecture and may be out of date. | Newer kernels have extended which modules can be stacked together. | The [LSM documentation](https://www.kernel.org/doc/html/latest/admin-guide/LSM/index.html) and `/sys/kernel/security/lsm` on the target host. |
| The dates (SECCOMP 2005, adoption by Chrome, OpenSSH and qemu, LSM 2002, AppArmor merged in 2010) and the MULTICS origin of SELinux MLS come from the lecture slides. | They were not checked against kernel history or project changelogs. | The kernel changelogs and each project's history, and the [TCSEC](https://csrc.nist.gov/csrc/media/publications/conference-paper/1998/10/08/proceedings-of-the-21st-nissc-1998/documents/early-cs-papers/dod85.pdf) for the MLS vocabulary. |

## References

- HEIG-VD -  "Sécurité des systèmes d'exploitation" 
- [seccomp_filter — Linux kernel documentation](https://www.kernel.org/doc/html/latest/userspace-api/seccomp_filter.html)
- [LoadPin — Linux kernel documentation](https://docs.kernel.org/admin-guide/LSM/LoadPin.html)
- [Linux Security Modules — kernel documentation](https://www.kernel.org/doc/html/latest/admin-guide/LSM/index.html)
- [SELinux Project](https://github.com/SELinuxProject)
- [AppArmor](https://apparmor.net/)
- [TCSEC (Orange Book), DoD 5200.28-STD](https://csrc.nist.gov/csrc/media/publications/conference-paper/1998/10/08/proceedings-of-the-21st-nissc-1998/documents/early-cs-papers/dod85.pdf)
- [Claude Code](https://claude.com/product/claude-code)

### Related articles

- [How Fail2Ban Works — Architecture, Privilege Model and Residual Risk]({{site.url_complet}}/2026/09/03/fail2ban-architecture-privilege-model/)
- [System Calls, Binary Images and Processes - How a Program Reaches the Kernel]({{site.url_complet}}/2026/09/16/system-calls-binary-image-process/)
- [The Process Control Block, fork/exec/waitpid/exit and the Context Switch]({{site.url_complet}}/2026/09/16/process-control-block-fork-exec-context-switch/)
- [AppArmor on Ubuntu, User Namespace Restrictions, and Why sol2uml Cannot Export a PNG]({{site.url_complet}}/2026/10/15/apparmor-ubuntu-user-namespaces-sol2uml/)
