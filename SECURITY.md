# Security Policy for Secura

Secura takes security vulnerabilities within the distribution, its core services, and packaging very seriously.

---

## 1. Supported Versions

Secura issues security patches and updates for the following release tracks:

| Version | Base OS | Status | Supported |
| :--- | :--- | :--- | :--- |
| `0.1.x` (Development) | Debian 12 (Bookworm) | Pre-Release / Alpha | Active |
| `< 0.1.0` | N/A | Unsupported | No |

---

## 2. Reporting a Security Vulnerability

If you identify a security vulnerability within Secura (including the Secura Python core, CLI, GUI, live-build recipes, Calamares configurations, or default policies):

> **Please DO NOT report security vulnerabilities through public GitHub issues or discussions.**

### Secure Reporting Channel
1. Submit a confidential report via GitHub Private Vulnerability Reporting or email the security response team at:  
   `security@secura-project.org` *(placeholder contact for official release)*
2. Include the following details in your report:
   * **Summary**: A concise overview of the vulnerability.
   * **Component Affected**: Specific module (e.g., `secura.scope`, `secura.logging`, polkit rule, Calamares module).
   * **Severity Assessment**: CVSS vector or impact evaluation (e.g., Privilege Escalation, Command Injection, Information Disclosure).
   * **Proof of Concept**: Step-by-step reproduction instructions or safe script.
   * **Remediation Suggestion**: If you have identified a potential fix, include proposed patch or mitigation.

### Response Timeline
* **Initial Acknowledgment**: Within 48 hours of receipt.
* **Triage & Validation**: Within 5 business days.
* **Fix & Coordinated Disclosure**: A patch will be prepared in a private fork, with public advisory coordinated once updates are ready.

---

## 3. Core Security Invariants

Secura adheres to strict security invariants in its architecture:

1. **Non-Root Execution**: `secura-center` (GUI) and general user tasks must NEVER run as root.
2. **Safe Subprocesses**: Subprocess execution must strictly enforce `shell=False` and use explicit argument arrays.
3. **Audit Log Integrity & Redaction**: Audit logs must redact credentials, tokens, API keys, and private keys before persistence.
4. **Scope Safety**: Security actions require explicit scope validation to prevent accidental scanning of out-of-scope or public infrastructure.
5. **Least Privilege**: Privileged system actions are isolated via fine-grained Polkit policies rather than blanket SUID permissions.
