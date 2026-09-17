# Secura Security Architecture & Model

Secura is engineered around defense-in-depth, explicit scope validation, least privilege, and tamper-resistant audit trails.

---

## 1. Core Principles

```text
       ┌────────────────────────────────────────────────────────┐
       │                 Core Security Tenets                   │
       ├────────────────────────────────────────────────────────┤
       │ 1. Least Privilege       → Never run GUI/apps as root  │
       │ 2. Explicit Scope        → No testing without target   │
       │ 3. Defense in Depth      → Multi-layered isolation     │
       │ 4. Auditability          → JSONL trail with redaction  │
       │ 5. Safe Execution        → Array args, shell=False     │
       │ 6. Container Isolation   → Rootless Podman labs        │
       └────────────────────────────────────────────────────────┘
```

---

## 2. Privilege Model

Secura strictly rejects the insecure pattern of running desktop environments, file managers, or GUI applications as `root`:

* **Secura Center (GUI)** runs under standard, unprivileged user permissions (`$UID >= 1000`).
* **Sub-operations requiring privilege** (such as raw packet capture with Wireshark/tcpdump or firewall configuration) request granular elevation using **Polkit** (`pkexec`) or configured Linux capabilities (`setcap cap_net_raw,cap_net_admin=eip`).
* No persistent root daemon processes are maintained by Secura.
* SUID root binaries are actively minimized across the live filesystem.

---

## 3. Safe Subprocess Execution Layer

Security tools invoked via Secura CLI or Secura Center must pass through the **Safe Subprocess Engine** (`secura.core.runner`):

```text
User Request / GUI Action
       │
       ▼
1. Scope Validation Check (secura.scope)
   - Is the target active, unexpired, and properly authorized?
   - Is it private/RFC1918 or public? (Require explicit confirmation if public)
       │
       ▼
2. Tool Metadata & Schema Verification (secura.tools)
   - Verify tool flags against permitted parameter schema
       │
       ▼
3. Safe Argument Construction
   - STRICTLY array format: `["/usr/bin/nmap", "-sV", target_ip]`
   - `shell=False` hard-enforced. No string concatenation into `/bin/sh` or `/bin/bash`.
       │
       ▼
4. Privilege Check
   - Verify if elevated capabilities are required and use Polkit if necessary
       │
       ▼
5. Execution with Monitored Timeout
   - Process runs with configured timeout to prevent hanging or deadlocks
       │
       ▼
6. Stream Sanitization & Redaction (secura.logging.redactor)
   - Scrub credentials, private keys, authorization headers
       │
       ▼
7. Audit Log Persistence (audit.jsonl) & Result Presentation
```

---

## 4. Audit Logging & Sensitive Data Redaction

Every tool execution, scope alteration, laboratory launch, and report generation is logged to:
`~/.config/secura/logs/audit.jsonl`

### Data Redaction
The logging system applies a multi-pattern regex redaction filter to scrub:
* Command-line password flags (`-p <secret>`, `--password=<secret>`, `-u user:pass`)
* HTTP Authorization headers (`Bearer <token>`, `Basic <hash>`)
* API Keys (Stripe, AWS `AKIA...`, GitHub `ghp_...`, Generic `Bearer ey...`)
* Cryptographic private keys (`-----BEGIN RSA PRIVATE KEY-----`)

Example sanitized audit entry:
```json
{
  "timestamp": "2026-09-17T16:30:00.123456Z",
  "user": "secura",
  "action": "tool_execution",
  "tool": "nmap",
  "target": "192.168.1.15",
  "scope_id": "scope-8f12a4",
  "command": ["nmap", "-sV", "-p", "80,443", "192.168.1.15"],
  "result": "success",
  "exit_code": 0
}
```

---

## 5. Containerized Lab Isolation (Podman)

Secura leverages **rootless Podman** for cybersecurity laboratories:
* Labs execute inside isolated container namespaces without root privileges on the host OS.
* Lab networks default to isolated bridge networks (`10.88.0.0/16`) that do NOT route out to physical LAN adapters unless explicitly configured.
* Containers are ephemeral: resetting a lab immediately destroys container layers and restores pristine configurations.
