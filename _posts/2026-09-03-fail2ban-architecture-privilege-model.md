---
layout: post
title: "How Fail2Ban Works — Architecture, Privilege Model and Residual Risk"
date:   2026-09-03
lang: en
locale: en-GB
categories: linux security network
tags: linux security network ssh log hardening intrusion
description: Fail2Ban reads logs and rewrites the firewall as root. Its jail architecture, the tag-escaping pipeline, and why a filter regex is a security boundary.
image: /assets/article/securite/fail2ban/fail2ban-architecture.png
isMath: false
---

Fail2Ban occupies an unusual position on a server. It is a piece of infrastructure that parses attacker-controlled text with regular expressions and, on the strength of that parse, executes shell commands as root against the packet filter. Very little else on a typical Linux host combines those three properties. Understanding it therefore means understanding two things at once: the mechanism that turns log lines into firewall rules, and the trust assumptions that mechanism rests on.

This article reads the Fail2Ban source at the current `master` revision and describes what the daemon is: a single Python process holding one filter thread and one action thread per jail, driven by a client that speaks a pickled command protocol over a UNIX socket. It then examines the privilege model (there is no privilege separation in the code), the escaping pipeline that stands between a log line and `/bin/sh`, and the class of failure that has produced most of the project's real vulnerabilities, which is not command injection but log injection.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What Fail2Ban Is For, and What It Is Not

The project README states the goal plainly and also states its limit:

> Though Fail2Ban is able to reduce the rate of incorrect authentication attempts, it cannot eliminate the risk presented by weak authentication. Set up services to use only two factor, or public/private authentication mechanisms if you really want to protect services.

That framing matters for everything that follows. Fail2Ban is a rate-limiting control, not an authentication control. It does not sit inline on the connection path, it does not inspect packets, and it does not know whether an authentication succeeded except insofar as an application wrote a line about it. It observes a side effect, after the fact, and reacts by changing a firewall.

The practical benefits follow from that: it suppresses the constant background noise of credential-stuffing bots, it keeps authentication logs readable, it reduces CPU spent on password hashing during a spray, and it can escalate ban duration for hosts that keep coming back. The practical limits follow too. A single-attempt attack against a weak password is never seen. A distributed campaign that makes three attempts from each of ten thousand addresses stays below any sensible `maxretry`. And the reaction latency is bounded below by how quickly the application flushes its log.

For [OpenSSH](https://www.openssh.com/) in particular, the honest comparison is that moving to certificate or key-only authentication removes the attack that Fail2Ban is rate-limiting, rather than throttling it.

## Process Architecture

Fail2Ban ships three executables. `fail2ban-server` is the daemon, `fail2ban-client` is the control tool, and `fail2ban-regex` is an offline tester that runs a filter against sample lines without touching the running server.

The division of labour between client and server is more asymmetric than the names suggest. **The server does not read the configuration files.** All of `config/` is parsed on the client side by `configreader.py`, `jailreader.py`, `filterreader.py` and `actionreader.py`, which flatten the whole tree of `jail.conf`, `jail.local`, `jail.d/*.conf`, `filter.d/` and `action.d/` into an ordered list of commands. Those commands are then sent to the server one by one, in exactly the same vocabulary an operator can type interactively:

```text
set sshd addfailregex ^Failed \S+ for .*? from <HOST>...
set sshd addaction iptables-multiport
set sshd action iptables-multiport actionban <iptables> -I f2b-<name> 1 -s <ip> -j <blocktype>
start sshd
```

The transport is a UNIX stream socket, by default `/var/run/fail2ban/fail2ban.sock`, and the serialization is Python `pickle` with a sentinel terminator. `fail2ban/client/csocket.py` calls `dumps(...)` on the list of arguments; `fail2ban/server/asyncserver.py` calls `loads(message)` on what arrives.

Inside the daemon, `Server` owns a `Jails` registry. Each `Jail` owns a `Filter` thread and an `Actions` thread, both subclasses of `JailThread`. A single global `ObserverThread` handles asynchronous bookkeeping (database writes and ban-time escalation) so the action path does not block on SQLite. `AsyncServer` runs the socket loop. Everything is a thread in one process; there is no per-jail process isolation.

![Fail2Ban process architecture: the client flattens the configuration and sends pickled commands over a UNIX socket to a single server process, which runs a filter thread and an action thread per jail plus a shared observer and SQLite database]({{site.url_complet}}/assets/article/securite/fail2ban/fail2ban-server-components-concept.png)

### Backends

The filter needs new log lines. `Jail._setBackend` resolves the `backend` option to one of three implementations:

- **`pyinotify`** uses the Linux inotify interface through the `pyinotify` library, watching both the file and its parent directory so that rotation is noticed.
- **`polling`** stats each watched file on a timer and compares modification time, inode and size. Rotation is recognised separately, by the file container, which keeps an MD5 of the first line so a reopened path can be identified as the same file or a new one.
- **`systemd`** reads the journal directly through the `python-systemd` bindings, filtered by `journalmatch`, and takes no `logpath` at all.

`backend = auto` tries `pyinotify` first and falls back to `polling`. The choice is per jail, which matters when some services log to files and others only to the journal.

## Anatomy of a Jail

A jail is the unit of policy: one filter, one or more actions, and the parameters that connect them. The four that decide behaviour are `findtime` (the sliding window, default 600 s), `maxretry` (failures allowed in that window, default 5), `bantime` (default 600 s) and `banaction`.

The data structure passed between the two threads is a *ticket*. A `FailTicket` records an identifier, a timestamp, an attempt count and the matched log lines. A `BanTicket` is the same object promoted once a ban has been decided. The identifier is normally an `IPAddr`, but it does not have to be: a filter that captures `<F-ID>` or `<F-USER>` instead of `<HOST>` produces tickets keyed on a username or a session identifier, which is how jails that ban by account rather than by address are built.

![From a log line to a firewall rule: date detection, ignoreregex, failregex matching, host extraction, the ignore lists, the findtime counter, then the ban and its expiry]({{site.url_complet}}/assets/article/securite/fail2ban/fail2ban-ban-lifecycle-workflow.png)

### The filter thread

Each incoming line goes through `Filter.processLine`, then `Filter.findFailure`. The order of operations is worth stating precisely, because several of the steps are security-relevant.

- **Date extraction.** `DateDetector.matchTime` locates a timestamp and splits the line into a prefix, the time text and the remainder. The date detector maintains an ordered list of templates and promotes the ones that keep matching, so a log with a stable format converges on a single template.
- **Timestamp sanity.** If the parsed date deviates from the current time by more than 60 seconds while the filter is in operation, the entry is treated as if it had just happened and a warning is emitted at most once a day. During the initial catch-up phase, entries older than `findtime` are discarded instead.
- **`ignoreregex`.** Applied before the fail regexes when there are few enough of them, and again after a match otherwise.
- **`prefregex`.** An optional pre-filter that strips the syslog prefix once and exposes the message body as `<F-CONTENT>`, so that the individual fail regexes do not each have to re-match the prefix. The `sshd` filter is built this way.
- **`failregex`.** Each expression in turn until one matches. `checkAllRegex` is false in the daemon, so matching stops at the first hit.
- **Identifier extraction.** The named groups `ip4`, `ip6`, `dns`, `fid`, `cidr` are read out of the match.
- **Ignore lists.** `ignoreip`, `ignoreself` (default true, covering the host's own addresses and names) and the external `ignorecommand`.

Only a line that survives all of that reaches `FailManager.addFailure`.

### From counter to ban

`FailManager` is a dictionary from identifier to ticket, plus a lock. Each new failure increments the ticket's retry count and slides its window. `cleanup` drops entries older than `findtime`.

The threshold check happens in two places. The periodic `toBan` sweep pulls out any ticket whose retry count has reached `maxretry`, and `processLineAndAdd` additionally calls `performBan` the moment a single line pushes an identifier over the threshold. The second path was added because a jail seeing a very high failure rate could otherwise accumulate an unbounded failure list before the sweep caught up.

The `Actions` thread drains the jail queue in `__checkBan`. For each ticket it registers the ban with `BanManager`, notifies the observer, and then calls `action.ban(aInfo)` for every configured action, in order, in the same thread. `__checkUnBan` runs on the other side of the loop and expires tickets whose `bantime` has elapsed.

Because the actions run sequentially in a single thread with a default 60 second timeout each, a slow action delays every subsequent ban in that jail. A reporting action that talks to a remote API is exactly the kind of thing that turns a ban queue into a backlog.

## Actions: Turning a Ticket into a Firewall Rule

An action is a set of command templates. `CommandAction` defines `actionstart`, `actionstop`, `actioncheck`, `actionban`, `actionunban`, `actionreban`, `actionrepair`, `actionflush` and `actionreload`, all defaulting to the empty string, plus a `timeout` of 60 seconds.

The `iptables` action shows the shape. It creates a dedicated chain per jail and jumps to it from the configured chain, so that Fail2Ban's rules are separable from everything else in the ruleset:

```text
actionstart = { <iptables> -C f2b-<name> -j <returntype> >/dev/null 2>&1; } || \
              { <iptables> -N f2b-<name> || true; <iptables> -A f2b-<name> -j <returntype>; }
              <_ipt_add_rules>

actionban   = <iptables> -I f2b-<name> 1 -s <ip> -j <blocktype>
actionunban = <iptables> -D f2b-<name> -s <ip> -j <blocktype>
```

By default `actionstart` runs lazily at the first ban rather than at server start, which avoids creating empty chains for jails that never fire.

`actioncheck` implements an invariant check. Before each ban, the action verifies that its environment is still sane (that the chain still exists and the jump is still in place). If the check fails, `_invariantCheck` attempts `actionrepair`, or a stop/start cycle, and the ban is retried once. This is what allows Fail2Ban to survive an out-of-band `iptables -F` without silently failing to ban for the rest of the day.

The repertoire is broad: 66 action files ship in `config/action.d/`, covering `iptables` and its ipset variants, `nftables`, `firewalld`, `pf`, `ipfw`, `npf`, `hosts.deny`, route blackholing, Cloudflare and Netscaler APIs, and reporting endpoints such as AbuseIPDB, blocklist.de and Apprise notifications. Actions can also be Python modules: `Actions.add` accepts a file path whose module exports an `Action` class deriving from `ActionBase`, which is then imported into the server process.

## The Privilege Model

**There is no privilege separation in the codebase.** Searching the source for `setuid`, `setgid` or any privilege-dropping call returns nothing. The server keeps whatever identity it was started with for its entire lifetime, and every thread (filter, actions, observer, socket loop) shares it.

That identity has to be sufficient for two very different jobs:

- **Reading the logs.** On a typical distribution `/var/log/auth.log` or the systemd journal's authentication units are readable only by root or by a dedicated group.
- **Rewriting the packet filter.** `iptables`, `nft` and their equivalents require `CAP_NET_ADMIN` in the relevant network namespace.

In practice that means root. A hardened deployment can narrow this (a dedicated user with `CAP_NET_ADMIN`, group-readable logs, `sudo` rules for the firewall binary), but nothing in the project does it for you, and the shipped `files/fail2ban.service.in` contains no sandboxing directives at all: no `NoNewPrivileges`, no `ProtectSystem`, no `CapabilityBoundingSet`. Distribution packages sometimes add them; upstream does not.

### The socket is the entire authorization model

The consequence is that the control socket is the security boundary, and its only protection is the filesystem.

Two mechanisms enforce that. `Server.start` calls `os.umask(0o077)` before anything else, so the socket file the daemon creates is owner-only. The systemd socket unit declares `SocketMode=0600` explicitly and places the socket under a `RuntimeDirectory`.

There is nothing else. The protocol carries no authentication, no capability tokens and no per-command authorization. Anyone who can write to that socket can issue:

```text
set sshd action iptables-multiport actionban /bin/sh -c 'id > /tmp/pwn'
```

and the next ban in that jail executes it as root. Every deployment decision about Fail2Ban reduces to keeping that socket owner-only.

The pickle protocol sits behind the same boundary. `asyncserver.py` calls `pickle.loads` on socket data, which is unsafe against untrusted input by construction, and is safe here only because untrusted parties cannot write to the socket. It is a defence-in-depth gap rather than a live vulnerability: an attacker who can send a pickle to that socket can already set `actionban` to a shell command, so deserialization buys them nothing they did not have.

![Trust boundaries around a Fail2Ban deployment: an untrusted remote client influences log lines and DNS answers, which a root-owned server parses and turns into shell commands, with the 0600 socket as the only authorization boundary]({{site.url_complet}}/assets/article/securite/fail2ban/fail2ban-trust-surface-concept.png)

### Configuration is code

Two more places treat configuration as executable, both of them root-owned by assumption:

- **`bantime.formula`** is passed to `compile(formula, '~inline-conf-expr~', 'eval')` in `Jail.setBanTimeExtra` and evaluated on every escalation. `bantime.factor` goes through a bare `eval`.
- **Python actions** are imported into the server process and run with its full privileges.

Neither is a vulnerability on a correctly permissioned system, and both are worth remembering when reviewing a host where `/etc/fail2ban` is group-writable or managed by a configuration system with a wider blast radius than the daemon itself.

## The Escaping Pipeline

Between a ticket and `/bin/sh` sits a two-stage substitution. Getting the distinction between the stages right is the whole of Fail2Ban's command-injection defence.

**Stage one, `replaceTag`,** substitutes static properties: values from the action file's `[Init]` section and from the jail configuration. This stage is recursive (a tag may expand to text containing further tags), it is cached per action, and it supports family-conditional variants such as `actionban?family=inet6`. Recursion is bounded by `MAX_TAG_REPLACE_COUNT`; exceeding it raises rather than looping, which is what stops a self-referencing definition from hanging the daemon.

**Stage two, `replaceDynamicTags`,** substitutes ticket-derived values: `<ip>`, `<failures>`, `<time>`, `<matches>`, `<F-USER>` and the rest of the filter's capture groups. The source comment states the rule for this stage directly:

> Because this tags are dynamic resp. foreign (user) input: values should be escaped (using "escape" as shell variable), no recursive substitution (no interpolation for `<a<b>>`), don't use cache.

The escaping works by relocation rather than by quoting. Any value matching

```text
[\\#&;`|*?~<>^()\[\]{}$'"\n\r]
```

is not inserted into the command text at all. It is bound to a generated shell variable named `f2bV_<sanitised tag>`, and `Utils.buildShellCmd` rewrites the command into an array whose first element is a prelude assigning those variables from positional parameters:

```text
['f2bV_matches=$0 \n<command using $f2bV_matches>', 'the actual value']
```

`subprocess.Popen` then receives that array with `shell=True`, so the shell parses the command text (which no longer contains the dangerous characters) and receives the values as arguments. Three tags are additionally escaped even in the static stage, because they carry raw log content by definition: `matches`, `ipmatches` and `ipjailmatches`.

![Assembling an action command: static tag substitution with bounded recursion, then dynamic tag substitution where any value containing a shell metacharacter is bound to a generated shell variable and passed as a positional argument]({{site.url_complet}}/assets/article/securite/fail2ban/fail2ban-action-substitution-workflow.png)

### Where this has failed

The pipeline protects the *shell*. It does not protect programs the shell invokes, and that is precisely where [CVE-2021-32749](https://github.com/fail2ban/fail2ban/security/advisories/GHSA-m985-3f3v-cwmm) landed.

The `mail-whois` action pipes the output of `whois <ip>` into `mail` as the body of a notification. GNU mailutils interprets tilde escape sequences at the start of a body line, so `~!` runs a command. An attacker who controls a `whois` record for their own address range, or who can influence the `whois` server's answer, could place such a line in it and obtain execution as the user running Fail2Ban. Nothing in `escapeTag` or `buildShellCmd` applies, because the dangerous content never passes through a shell metacharacter; it passes through `mail`'s own escape parser.

The fix was to disable that parser at the call site, and every mail action now carries it:

```text
actionban = printf %%b "..." | mail -E 'set escape' -s "..." <dest>
```

The same defensive style shows up in `helpers-common.conf`, where the log-excerpt helper greps for the banned address with `grep -wF "<ip>"`. The `-F` makes the address a fixed string rather than a pattern, so a value that reached that point could not act as a regular expression against the log.

The lesson generalises to any custom action: the value handed to you may be attacker-influenced, and it is your responsibility to know how the *downstream program* parses it.

## Log Injection: the Dominant Risk Class

Command injection into actions is well defended. The recurring vulnerability in Fail2Ban's history is a different one: the attacker frequently controls part of the log line the filter parses, and can therefore try to control which address gets banned.

The `FILTERS` file in the repository states the rule:

> When a remote user has the ability to introduce text that would match filter's failregex, while matching inserted text to the `<HOST>` part, they have the ability to deny any host they choose. So the `<HOST>` part must be anchored on text generated by the application, and not the user.

The canonical case is [CVE-2013-2178](https://vndh.net/note:fail2ban-089-denial-service). A poorly anchored Apache filter read:

```text
failregex = [[]client <HOST>[]] user .* not found
```

An attacker sends a request whose path is itself a fake log fragment:

```text
GET /[client%20192.168.0.1]%20user%20root%20not%20found HTTP/1.0
```

Apache logs the failed lookup including the requested path, and the resulting line now contains a second, forged `[client 192.168.0.1] user root not found`. The unanchored regex matches the forgery, and Fail2Ban bans an address the attacker chose. Point that at a customer's NAT gateway, a monitoring probe or a mail relay and the denial of service is complete.

The second failure mode is subtler and comes from regex greediness. Consider an SSH filter that allows a trailing remote-user field:

```text
failregex = ^Failed \S+ for .* from <HOST>( port \d*)?( ssh\d+)?(: ruser .*)?$
```

Against the line

```text
Failed password for user from 127.0.0.1 port 20000 ssh1: ruser from 1.2.3.4
```

the greedy `.*` runs to the end of the line and then backtracks to find the *last* ` from <HOST>` it can. The attacker-supplied `ruser` value wins, and `1.2.3.4` is banned instead of `127.0.0.1`. The fix is one character: `.*?` makes the leading catch-all lazy, so it settles on the first match.

Three properties reduce the risk to a manageable one:

- **Hard anchoring.** A filter anchored at both `^` and `$` leaves no room for a forged suffix. Anchoring the start matters more in practice, because far more applications log a fixed prefix than a fixed suffix.
- **Non-greedy catch-alls before `<HOST>`.** Any `.*` that precedes the host capture should be `.*?`.
- **A test that enforces both.** `fail2ban/tests/samplestestcase.py` compiles a pattern named `RE_WRONG_GREED` and asserts that no shipped filter contains a greedy catch-all before `<HOST>` that is neither hard-anchored at the end nor followed by a precise sub-expression. A filter that regresses on this fails the test suite.

That test covers the 104 filters in `config/filter.d/`. It does not cover the filter someone writes locally on a Tuesday afternoon, which is where this class of bug now lives. `fail2ban-regex` exists for exactly this: run the candidate expression against both a genuine failure line and a line containing an injected address, and confirm which one it extracts.

### Related exposures on the same path

Two smaller ones deserve mention because they share the "attacker writes the input" property.

**Regex cost.** Every line of every watched log is matched against every fail regex of the jail, and in many services the attacker controls the length and content of part of that line. A pathological expression combined with a long attacker-chosen field is a CPU sink. Fail2Ban has no per-match timeout; its only backstop is `Filter.commonError`, which counts exceptions and puts the filter thread idle after a hundred of them in a row; that counts errors, not slow matches. Anchoring and avoiding nested quantifiers is the mitigation.

**DNS trust.** `usedns` defaults to `warn`, meaning that a hostname appearing where `<HOST>` is expected will be resolved forward to addresses, with a warning logged. That makes a ban decision depend on a DNS answer, which is attacker-influenced in the general case. `usedns = no` restricts `<HOST>` to the `<ADDR>` form (literal IPv4 or IPv6 only) and removes the dependency; the cost is that filters which only ever log a name stop working.

## Persistence, Escalation and the Database

The server keeps state in SQLite at `/var/lib/fail2ban/fail2ban.sqlite3`, with tables for jails, watched logs and their read positions, bans, and per-address ban history (`bips`). Setting `dbfile = None` disables persistence entirely; `:memory:` keeps it for the process lifetime only.

The database serves three purposes.

- **Restart continuity.** `Jail.restoreCurrentBans` re-applies bans whose `bantime` has not yet expired, so a daemon restart does not release everyone. It also restores log read positions, so a restart does not re-process an entire file.
- **Ban-time escalation.** With `bantime.increment = true`, the observer looks up how many times an address has been banned before and recomputes the duration through `bantime.formula` or `bantime.multipliers`, with `bantime.factor` as a coefficient and `bantime.maxtime` as a ceiling. The default formula doubles per repeat offence up to a shift of 20.
- **Cross-jail correlation.** `bantime.overalljails` widens that lookup to every jail rather than the current one.

`bantime.rndtime` adds a random component to the computed duration. The stated reason is to stop a botnet from computing the exact moment a ban lifts and resuming at that instant.

Retention has two knobs. `dbpurgeage` (default 1 day) bounds how long expired bans are kept, and `dbmaxmatches` (default 10) bounds how many matched log lines are stored per ticket. The second one is a privacy control as much as a size control: matched lines are raw log content, and a failed authentication line routinely contains a username that was a mistyped password.

That same content flows outward through `<matches>`, `<ipmatches>` and `<ipjailmatches>` whenever a mail or reporting action is configured. Sending log excerpts to AbuseIPDB or blocklist.de is a deliberate disclosure of server logs to a third party, and it is worth treating it as one.

## Operational Risks Worth Planning For

The failure modes that cost people time are rarely the exotic ones.

- **Self-lockout.** The default `ignoreip` covers only loopback, and `ignoreself` covers the host's own addresses. Neither covers the administrator's office range or a jump host. Five failed attempts from a bastion is enough at the default `maxretry`. `fail2ban-client set <jail> unbanip <ip>` is the recovery, which requires already being on the box.
- **Shared egress.** Banning an address bans everyone behind it. Carrier-grade NAT, corporate proxies and mobile networks mean a ban can affect thousands of unrelated users, and no configuration inside Fail2Ban can distinguish them.
- **The `recidive` jail.** It watches `/var/log/fail2ban.log` and bans, for a week and on all ports, addresses that other jails have banned repeatedly. It amplifies whatever the other jails decide, including their mistakes, which makes filter correctness matter more, not less.
- **Rotation and gaps.** A log rotated while the daemon is stopped is a blind spot. The startup catch-up path explicitly discards entries older than `findtime`, which is the correct behaviour but means a restart is a small window of non-enforcement.
- **Clock and timezone.** Log timestamps without a zone are interpreted in the server's zone unless `logtimezone` says otherwise. A mismatch shows up as the "log entry N before/after the current time" warning and, during catch-up, as entries silently dropped for being too old.
- **Firewall ownership.** Fail2Ban assumes its chains persist. A configuration management run, a `firewalld` reload or a `nft flush ruleset` from elsewhere removes them. `actioncheck` detects this on the next ban and repairs, but bans placed in the interval are gone.

## Conclusion

Fail2Ban is a small program with an unusually sharp trust profile. Its architecture follows from the client/server split: the client is the configuration compiler, the server is a thread pool of filters and actions around a shared ticket queue, and the SQLite database supplies continuity and escalation.

The security properties are less obvious and worth restating. The daemon runs with the privileges needed to rewrite the packet filter and read authentication logs, and it does not reduce them; the UNIX socket is therefore a root-equivalent control channel protected by nothing but its file mode. The escaping pipeline between ticket data and the shell is carefully built, and the vulnerabilities that got through it went around it, through a downstream program's own escape syntax. And the risk that has recurred throughout the project's history is not that an attacker executes a command, but that an attacker chooses which address gets banned, by writing a plausible log line into a field the application logs verbatim.

Deploying it well is mostly a matter of respecting those three facts: keep the socket owner-only, know how any custom action's downstream program parses its arguments, and anchor every filter regex against the text the application generates rather than the text a user supplies.

![Mindmap of Fail2Ban covering its goal, the client-server architecture, the filter and action subsystems, the root privilege model, and the residual risks of log injection and regex cost]({{site.url_complet}}/assets/article/securite/fail2ban/fail2ban-architecture.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Jail** | The unit of policy: one filter, one or more actions, and the parameters (`findtime`, `maxretry`, `bantime`) that link them. |
| **Filter** | The thread that reads log lines and applies `prefregex`, `failregex` and `ignoreregex` to produce failure tickets. |
| **Action** | A set of shell command templates (`actionstart`, `actioncheck`, `actionban`, `actionunban` and others) executed when a jail bans or unbans. |
| **Ticket** | The record passed from filter to actions, carrying an identifier, a timestamp, an attempt count and the matched log lines. |
| **`<HOST>` tag** | The filter placeholder that expands to a capture group matching an IPv4 address, an IPv6 address or, when `usedns` allows it, a DNS name. |
| **`findtime` window** | The sliding interval within which `maxretry` failures must occur for a ban to be issued. |
| **Backend** | The mechanism used to obtain new log lines: `pyinotify`, `polling` or `systemd`. |
| **Log injection** | An attack in which text supplied by the attacker is written verbatim into a log line and then parsed by a filter as if the application had generated it. |
| **Tag substitution** | The two-stage process that turns an action template into a command: static properties first (recursive, cached), then ticket values (non-recursive, escaped). |
| **`bantime.increment`** | The option that consults the database for an address's previous bans and lengthens the current one according to a formula or a multiplier list. |

### Security Implementation Checklist

The properties below separate a Fail2Ban deployment (or a locally written filter or action) that is safe from one that is merely functional. They are derived from the source and from the project's own filter-security guidance, not transcribed from a standard.

#### Filter regular expressions

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The `<HOST>` capture is anchored on text the application generates, not on text a user supplies. | An attacker embeds a forged log fragment in a username, URL or header and selects the address that gets banned. |
| ☐ | Any catch-all preceding `<HOST>` is non-greedy (`.*?`, not `.*`), or the expression is hard-anchored at the end with `$`. | Backtracking matches the last host-shaped token on the line, which is the attacker-supplied one, not the connecting address. |
| ☐ | The expression is anchored at `^`, and at `$` when the application logs a fixed suffix. | An unanchored expression can match inside attacker-controlled data anywhere on the line. |
| ☐ | Both a genuine failure line and an injection attempt are tested with `fail2ban-regex` before the filter is enabled. | An untested filter is deployed on the assumption that it extracts the right address, with no evidence that it does. |
| ☐ | Quantifiers are bounded and not nested over attacker-controlled fields. | A long attacker-chosen field turns every log line into a CPU sink; there is no per-match timeout to stop it. |
| ☐ | `usedns = no` unless a monitored application logs hostnames rather than addresses. | A ban decision becomes contingent on a DNS answer the attacker can influence. |

#### Privilege and access control

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The control socket is mode 0600 and owned by the server's user, and its directory is not writable by others. | Socket write access allows setting `actionban` to an arbitrary command, which the server then runs with its own privileges. |
| ☐ | `/etc/fail2ban` and every file under `filter.d/` and `action.d/` are writable only by root. | Configuration is executable: `bantime.formula` is compiled and evaluated, and Python actions are imported into the server process. |
| ☐ | The server runs with the narrowest identity that can still read the logs and modify the firewall. | A single defect in a Python action or a dependency executes with full root instead of a bounded capability set. |
| ☐ | The service unit adds the sandboxing directives the upstream unit omits, to the extent the firewall backend permits. | The shipped unit declares no `NoNewPrivileges`, `ProtectSystem` or `CapabilityBoundingSet`, so nothing constrains the process beyond its user. |

#### Actions and data handling

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Any custom action knows how each downstream program parses its arguments, beyond shell metacharacters. | CVE-2021-32749: `whois` output reached `mail`, whose own tilde escape sequences executed a command that the shell escaping never saw. |
| ☐ | Log content used as a search term is passed as a fixed string (`grep -wF`), never as a pattern. | Attacker-influenced content is interpreted as a regular expression against the server's own logs. |
| ☐ | `<matches>` and the `ipmatches` variants are treated as raw log content wherever they are sent. | Matched lines routinely contain mistyped passwords; forwarding them to a reporting API discloses them to a third party. |
| ☐ | `dbmaxmatches` is set to the smallest value the configured actions require. | Raw log excerpts accumulate in the database for longer and in greater volume than any action requires. |
| ☐ | Reporting actions that call remote APIs are reviewed for latency and failure behaviour. | Actions run sequentially in one thread with a 60 second timeout each, so a slow endpoint delays every subsequent ban in the jail. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| A ban is issued only after `maxretry` failures from one identifier within `findtime`. | `FailManager.addFailure` sliding window plus the `toBan` threshold check. | A filter matches lines that are not authentication failures, or `maxretry` is set below the application's normal retry behaviour. |
| Dynamic tag values never introduce shell syntax into a command. | `replaceDynamicTags` relocates any value matching `ESCAPE_CRE` into a generated shell variable passed as a positional argument. | A custom action interpolates ticket data through a mechanism that bypasses the substitution path, or a downstream program has its own escape syntax. |
| Static tag substitution terminates. | Recursion in `replaceTag` is bounded by `MAX_TAG_REPLACE_COUNT`, which raises rather than looping. | Nothing in normal configuration; the bound exists precisely to make self-referencing definitions fail loudly. |
| The firewall state matches the ban list at the moment of each ban. | `actioncheck` runs before every `actionban`, with `actionrepair` or a stop/start cycle on failure and one retry. | An action defines no `actioncheck`, so out-of-band flushes go undetected until the next restart. |
| Bans survive a daemon restart for their remaining duration. | `Jail.restoreCurrentBans` replays unexpired bans from SQLite at startup. | `dbfile` is set to `None` or `:memory:`, in which case a restart releases every banned address. |
| No shipped filter contains a greedy catch-all before `<HOST>` without hard anchoring. | The `RE_WRONG_GREED` assertion in `samplestestcase.py`, run over every file in `config/filter.d/`. | A filter is written locally rather than upstream, where the test suite never sees it. |

## Frequently Asked Questions

**Q: Why does the Fail2Ban server not read its own configuration files?**

The parsing lives entirely on the client side. `fail2ban-client` walks `jail.conf`, `jail.local`, `jail.d/`, `filter.d/` and `action.d/`, resolves the interpolations and inheritance, and flattens the result into an ordered list of `set` and `start` commands that it sends over the socket.

The server implements only that command vocabulary. One practical consequence is that anything the configuration can express, an operator can also type interactively, which is what makes `fail2ban-client -i` a usable debugging tool. The security consequence is the one covered in the article: the command surface includes setting an action's `actionban` to an arbitrary string, so the socket is root-equivalent.

**Q: What is the difference between the two stages of tag substitution, and why does it matter?**

The first stage, `replaceTag`, handles static properties from the action's `[Init]` section and the jail configuration. It substitutes recursively, so a tag may expand into text containing further tags, and it caches the result per action because those values do not change between bans.

The second stage, `replaceDynamicTags`, handles ticket-derived values such as `<ip>`, `<failures>` and `<matches>`. It does not recurse, does not cache, and escapes anything containing a shell metacharacter by binding it to a generated shell variable.

The separation is the defence. Recursive substitution over attacker-influenced data would let a value expand into a tag reference and from there into other configuration content, so foreign input is confined to the stage that treats it as an opaque string.

**Q: An attacker cannot inject shell metacharacters, so why did CVE-2021-32749 happen?**

Because the escaping protects the shell, and the shell was not the parser that mattered. The `mail-whois` action piped `whois` output into GNU mailutils' `mail`, which interprets tilde escape sequences at the start of a body line, so a line beginning `~!` runs a command. That text contains no shell metacharacter, passes `escapeTag` untouched, and is executed by `mail` itself.

The fix disables mailutils' escape parser at the call site with `mail -E 'set escape'`. The general lesson is that a value which is safe for the shell is not automatically safe for everything the shell invokes.

**Q: Why is a greedy `.*` before `<HOST>` a security bug rather than a style issue?**

Because backtracking makes it select the last matching host on the line rather than the first. Given `^Failed \S+ for .* from <HOST>...$` and a line where the attacker controls a trailing field, the `.*` consumes to the end of the line and then walks backwards looking for ` from ` followed by something host-shaped. The attacker's injected `from 1.2.3.4` is found before the genuine address, and Fail2Ban bans the address the attacker chose.

Changing `.*` to `.*?` makes the catch-all settle on the first match instead, which is the genuine one. The project's test suite enforces this over every shipped filter through the `RE_WRONG_GREED` assertion, so the exposure now sits almost entirely in locally written filters.

**Q: Fail2Ban runs as root and parses attacker-controlled text. Is that not a contradiction?**

It is a real tension, and the design answer is to keep the attacker-controlled data on one side of a narrow interface. The filter's job is to turn a line into an identifier and nothing else: no configuration is read from the line, no command is built from it, and the extracted value goes through the escaping pipeline before it can reach a shell.

What that structure cannot defend is the *decision* itself. If the regex extracts the wrong identifier, every downstream stage does exactly what it was told, correctly, against the wrong address. That is why the filter regex, and not the action, is the security-critical artefact, and why hardening effort is better spent on anchoring expressions than on the command path.

**Q: If a daemon restart replays unexpired bans from SQLite, why is a restart still a gap?**

Two different windows are involved. Bans are restored, so an address that was blocked stays blocked. Log *processing* is what has a gap: the filter records its read position in the database and resumes there, but during startup catch-up it discards any entry older than `findtime`.

So a daemon that was down for longer than `findtime` will not count the failures that occurred while it was stopped, even though it can see them. That is deliberate, because replaying old failures would ban addresses for activity that has long since ended, but it does mean the restart is a small window of non-detection layered on top of continued enforcement.

## References

### Analyzed source

- [fail2ban/fail2ban](https://github.com/fail2ban/fail2ban) — analyzed at commit [`86e415a76a98ea7497ba82ed0c5412e8c7c7d8c3`](https://github.com/fail2ban/fail2ban/tree/86e415a76a98ea7497ba82ed0c5412e8c7c7d8c3) (version `1.1.2.dev1`, after release [1.1.1](https://github.com/fail2ban/fail2ban/releases/tag/1.1.1)), 2026-09-03

### Project documentation

- [Fail2Ban website](https://www.fail2ban.org/)
- [Fail2Ban wiki](https://github.com/fail2ban/fail2ban/wiki)
- [Developers documentation](https://fail2ban.readthedocs.io/)
- `FILTERS` — the "Filter Security" section of the repository, at the commit above
- `man/jail.conf.5` — the jail, filter and action option reference, at the commit above

### Vulnerabilities and advisories

- [CVE-2021-32749 / GHSA-m985-3f3v-cwmm](https://github.com/fail2ban/fail2ban/security/advisories/GHSA-m985-3f3v-cwmm) — command execution through mailutils escape sequences in the `mail-whois` action
- [CVE-2013-2178 write-up](https://vndh.net/note:fail2ban-089-denial-service) — denial of service through log injection into an unanchored Apache filter
- [fail2ban pull request #426](https://github.com/fail2ban/fail2ban/pull/426) — the greedy catch-all correction in the `sshd` filter

### Related tooling and standards

- [OpenSSH](https://www.openssh.com/)
- [netfilter project](https://www.netfilter.org/) — `iptables` and `nftables`
- [pyinotify](https://github.com/seb-m/pyinotify)
- [systemd.socket(5)](https://www.freedesktop.org/software/systemd/man/systemd.socket.html) — `SocketMode` and socket activation
- [capabilities(7) — man7.org](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [Claude Code](https://claude.com/product/claude-code)

### Related articles

- [Linux Isolation Primitives - Defense in Depth Beyond the Castle Model]({{site.url_complet}}/2026/06/29/linux-isolation-primitives-defense-in-depth/)
- [GNU/Linux Base Security Primitives - Authentication, Permissions, ACLs, Attributes, Capabilities]({{site.url_complet}}/2026/06/29/linux-base-security-primitives/)
- [Advanced GNU/Linux Security - SECCOMP and Linux Security Modules (LSM)]({{site.url_complet}}/2026/06/29/linux-advanced-security-seccomp-lsm/)
- [OpenSSH Certificates — Critical Options, Extensions and the KRL Encoding]({{site.url_complet}}/2026/08/27/openssh-certificates-critical-options-krl/)
