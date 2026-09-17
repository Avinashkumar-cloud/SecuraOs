# Secura Curated Tool Catalog

Unlike operating systems that dump thousands of uncurated and potentially hazardous security utilities onto the desktop, Secura uses a **metadata-driven, curated catalog**.

---

## 1. Tool Selection Criteria

Tools included in Secura must satisfy the following principles:

1. **Defensive, Educational, or Audit Relevance**: Must assist with security education, vulnerability identification, traffic inspection, or system hardening.
2. **Deterministic & Inspectable**: Must have well-documented command-line interfaces and verifiable behaviors.
3. **No Destructive Capabilities**: The default catalog explicitly excludes:
   * Ransomware, wipers, or destructive exploit payloads
   * Botnet/C2 (Command & Control) agents
   * Credential harvesting/theft malware
   * Automated unconstrained attack scripts
   * Persistence rootkits or backdoor injectors

---

## 2. Tool Metadata Schema

Every tool in Secura is registered with a structured metadata specification:

```yaml
name: nmap
category: network-security
description: Network exploration tool and security/port scanner
purpose: Discover live hosts, open TCP/UDP ports, operating systems, and service versions.
risk_level: medium
authorization_required: true
binary: /usr/bin/nmap
package: nmap
enabled_by_default: true
documentation_url: https://nmap.org/book/man.html
safe_examples:
  - description: Ping scan on local lab subnet
    command: ["nmap", "-sn", "192.168.1.0/24"]
  - description: Service version detection on single target
    command: ["nmap", "-sV", "-p", "22,80,443", "{target}"]
```

---

## 3. Risk Levels

Secura classifies tools into three risk tiers:

| Risk Level | Description | Scope Requirement | Default State |
| :--- | :--- | :--- | :--- |
| **Low** | Passive analysis, offline inspection, code scanning, or forensics. No network traffic generated. | No target scope required (operates on local files). | Enabled |
| **Medium** | Active network enumeration, port scanning, benign banner grabbing. | Active, verified ScopeTarget required. | Enabled |
| **High** | Active web vulnerability probing, aggressive fuzzing, or deep protocol testing. | Active, verified ScopeTarget + explicit confirmation dialog required. | Disabled by default / Confirmation required |

---

## 4. Initial Core Catalog Tools

### Network Security & Packet Analysis
* **Nmap**: Network discovery and security auditing (`risk_level: medium`).
* **Wireshark**: Interactive graphical network protocol analyzer (`risk_level: low`).
* **TShark**: Terminal-based packet capture and protocol analysis engine (`risk_level: low`).

### Web Application Auditing
* **Nikto**: Web server vulnerability scanner for outdated software, configuration issues, and dangerous files (`risk_level: high`).
* **Curl / HTTPie**: Diagnostic HTTP client for inspecting headers, SSL handshakes, and API endpoints (`risk_level: low`).

### Defensive Analysis & Code Auditing
* **Bandit**: Static code analysis tool designed to find common security issues in Python code (`risk_level: low`).
* **ExifTool**: Forensic metadata reader and editor for image, PDF, and media files (`risk_level: low`).
* **Lynis**: Comprehensive Linux system security auditing and compliance benchmarking tool (`risk_level: low`).
