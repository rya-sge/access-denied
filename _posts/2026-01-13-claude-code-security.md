---
layout: post
title: "Security in Claude Code: Architecture, Safeguards, and Best Practices"
date:   2026-01-13
locale: en-GB
lang: en
last-update: 
categories: AI security
tags: claude security ai
description: technical overview of Claude Code’s security model, including its permission system, sandboxing architecture, identity and access management (IAM), and operational best practices.
isMath: false
image: 
---

## Introduction

As AI-assisted development becomes increasingly autonomous, security moves from being a peripheral concern to a core architectural requirement. [Claude Code](https://claude.com/product/claude-code), Anthropic’s agentic coding environment, is designed with a *security-first philosophy* that emphasizes explicit user control, least-privilege execution, and defense-in-depth. This article provides a technical overview of Claude Code’s security model, including its permission system, sandboxing architecture, identity and access management (IAM), and operational best practices.

> This article is mainly based on Claude Code documentation and written with Claude Code itself

[TOC]



------

## Security Foundations

Claude Code is developed under Anthropic’s comprehensive security program and aligns with established compliance frameworks such as **SOC 2 Type II** and **ISO/IEC 27001**. These controls govern internal development practices, infrastructure security, access management, and auditability. Details and certifications are available via the **Anthropic Trust Center**.

At a high level, Claude Code assumes a **shared responsibility model**:

- Anthropic secures the platform, tooling, and execution environment.
- Users retain responsibility for approving actions, reviewing code, and configuring permissions appropriately.

------

## Permission-Based Architecture

### Default Least-Privilege Model

Claude Code operates under a *read-only-by-default* model. Any operation with side effects—such as editing files, executing shell commands, or making network requests—requires explicit user approval.

Key design principles include:

- **Explicit consent** for all state-changing actions
- **Granular scope** (per command, per directory, per session)
- **Transparent intent**, including natural-language explanations for complex commands

### Tiered Permission System

Permissions are enforced at the tool level:

| Tool Type         | Example                  | Approval Required | Persistence |
| ----------------- | ------------------------ | ----------------- | ----------- |
| Read-only tools   | Grep, file reads         | No                | N/A         |
| Bash execution    | `npm test`, `git status` | Yes               | Per command |
| File modification | Edit/write files         | Yes               | Per session |

Advanced modes (e.g., `acceptEdits`, `plan`, `dontAsk`) allow teams to trade off autonomy and control depending on context.

------

## Built-in Security Protections

Claude Code incorporates several mitigations specifically designed for **agentic system risks**:

### Filesystem Protections

- Write access is restricted to the project directory and its subdirectories.
- Parent directories and sensitive system paths cannot be modified without explicit permission.
- Read access outside the project is allowed selectively to support dependency resolution, but edits remain constrained.

### Prompt Fatigue Mitigation

- Safe commands can be allowlisted at the user, project, or organization level.
- “Accept Edits” mode batches file changes while preserving command-level approvals.

### Command Safety

- Risky commands (e.g., `curl`, `wget`) are blocked by default.
- Suspicious commands require re-approval even if previously allowlisted.
- Unmatched commands fail closed (manual approval required).

------

## Defense Against Prompt Injection

Prompt injection attacks attempt to manipulate an AI agent into violating its intended constraints. Claude Code mitigates these risks through multiple layers:

1. **Permission enforcement** for sensitive actions
2. **Context-aware analysis** of requests
3. **Input sanitization** to prevent command injection
4. **Isolated context windows** for web fetches
5. **Command blocklists** and approval fallbacks

Even if a prompt injection succeeds at the language level, the execution environment remains constrained by permissions and sandboxing.

------

## Sandboxed Bash Execution

### Why Sandboxing Matters

Traditional approval-based security can lead to:

- Approval fatigue
- Reduced productivity
- Over-trusting repetitive prompts

Claude Code addresses this with a **sandboxed bash tool** that enforces security boundaries upfront.

### Sandbox Architecture

Sandboxing combines **filesystem isolation** and **network isolation**, enforced using OS-level primitives:

| Platform | Mechanism  |
| -------- | ---------- |
| Linux    | bubblewrap |
| macOS    | Seatbelt   |

All child processes inherit the same constraints.

### Filesystem Isolation

- Default: read/write access to the working directory
- Read-only access elsewhere (except denied paths)
- Writes outside the sandbox are blocked unless explicitly permitted

### Network Isolation

- Only approved domains are reachable
- New domains trigger permission prompts
- Optional custom proxies allow inspection and logging

### Security Benefits

- Prevents data exfiltration
- Blocks unauthorized downloads
- Limits damage from compromised dependencies or scripts
- Reduces the blast radius of successful prompt injection

------

## Identity and Access Management (IAM)

Claude Code supports multiple authentication backends:

- Claude for Teams / Enterprise (recommended)
- Claude Console (API-based)
- Cloud providers (AWS Bedrock, Google Vertex AI, Microsoft Foundry)

### Organizational Controls

Enterprise deployments gain access to:

- SSO and domain capture
- Role-based access control (RBAC)
- Managed settings enforced via policy files
- Centralized audit logging

Settings follow a strict precedence hierarchy to ensure organizational policies cannot be overridden by local configuration.

------

## Privacy and Credential Security

Claude Code includes safeguards to protect sensitive data:

- Encrypted credential storage (e.g., macOS Keychain)
- Scoped authentication tokens in cloud environments
- Limited retention of sensitive session data
- User control over training and data usage preferences

When running in the cloud, each session executes in an isolated virtual machine with restricted network access and automatic teardown.

------

## MCP and Extension Security

Claude Code supports **Model Context Protocol (MCP)** servers, which extend agent capabilities. Security considerations include:

- MCP servers are explicitly allowlisted in source control
- Permissions can be scoped per MCP tool
- Anthropic does not audit third-party MCP servers

Best practice is to use internally developed or well-audited MCP providers.

------

## Security Best Practices

### For Individual Developers

- Review all proposed commands before approval
- Avoid piping untrusted content directly into Claude
- Use sandboxing and restrictive defaults
- Regularly audit permissions with `/permissions`

### For Teams

- Enforce managed settings
- Version-control permission configurations
- Train developers on agent security risks
- Monitor usage via OpenTelemetry metrics

### For High-Risk Environments

- Use devcontainers or VMs for additional isolation
- Disable sandbox escape hatches unless strictly required
- Avoid enabling deprecated technologies such as WebDAV on Windows

------

## Reporting and Disclosure

Security vulnerabilities should be reported privately through **Anthropic’s HackerOne program**, including reproduction steps. Public disclosure should only occur after remediation.

------

## Conclusion

Claude Code demonstrates a mature approach to AI-assisted development security by combining:

- Explicit, user-controlled permissions
- OS-level sandboxing
- Defense-in-depth against prompt injection
- Enterprise-grade IAM and auditability

While no system is immune to all attacks, Claude Code significantly reduces risk when used with sound security practices and appropriate configuration.

------

## References

- [Anthropic – Claude Code Security Documentation](https://docs.anthropic.com/en/docs/claude-code/security)
- [Anthropic Trust Center – Security & Compliance Certifications](https://trust.anthropic.com)
- [Anthropic – Sandboxed Bash Tool and Agent Isolation](https://code.claude.com/docs/en/sandboxing)
- [Anthropic – Identity and Access Management (IAM) for Claude Code](https://code.claude.com/docs/en/iam)
- [OWASP Foundation – Command Injection](https://owasp.org/www-community/attacks/Command_Injection)
- [OWASP Foundation – OWASP Top 10 Web Application Security Risks](https://owasp.org/www-project-top-ten/)
- [Greshake et al. (2023) – *Not What You’ve Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection*](https://arxiv.org/abs/2302.12173)