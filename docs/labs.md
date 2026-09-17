# Secura Safe Cybersecurity Laboratories

Secura integrates local, self-contained laboratories designed to teach hands-on defensive and authorized testing skills without risking production networks or violating acceptable use policies.

---

## 1. Laboratory Architecture

All active labs are containerized using **rootless Podman**:

```text
┌─────────────────────────────────────────────────────────────┐
│                       Secura Host OS                        │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │            Podman Isolated Lab Network              │   │
│   │            Subnet: 10.88.10.0/24 (No WAN)           │   │
│   │                                                     │   │
│   │   ┌───────────────────┐     ┌───────────────────┐   │   │
│   │   │ Target Container  │     │ Vulnerable Service│   │   │
│   │   │ 10.88.10.20       │     │ 10.88.10.30       │   │   │
│   │   └───────────────────┘     └───────────────────┘   │   │
│   └─────────────────────────────────────────────────────┘   │
│                             ▲                               │
│                             │ Controlled Interface          │
│                ┌────────────┴───────────┐                   │
│                │   Secura Scope Lock    │                   │
│                │  Target: 10.88.10.0/24 │                   │
│                └────────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

* **Zero Leakage**: Lab networks bind to local host interfaces and do NOT route outbound traffic across public Wi-Fi or Ethernet interfaces.
* **Instant Reset**: Every lab can be reset to pristine state with a single command or GUI click.
* **Pre-configured Scope**: Starting a lab automatically registers its internal subnet into the Secura Scope Manager.

---

## 2. Standard Laboratory Modules

### Lab 1 — Network Discovery & Port Scanning
* **Objective**: Learn how port scanners identify open ports, service banners, and OS fingerprints.
* **Environment**: A multi-service local container running mock SSH, HTTP, FTP, and DNS services.
* **Tools Used**: `nmap`, `netcat`, `curl`.
* **Learning Outcomes**: TCP SYN vs Full Connect scans, banner grabbing, service enumeration.

### Lab 2 — Web Application Security Basics
* **Objective**: Understand common web flaws (OWASP Top 10) such as SQL injection, broken authentication, and directory traversal.
* **Environment**: Lightweight Python/Flask deliberately vulnerable web application bound strictly to `127.0.0.1:8080`.
* **Tools Used**: Web browser, `curl`, `nikto`.
* **Learning Outcomes**: HTTP request structure, parameter tampering, secure input validation.

### Lab 3 — Linux System Security & Hardening
* **Objective**: Audit and secure a Linux environment.
* **Environment**: Local sandbox containing misconfigured file permissions, SUID binaries, open firewall rules, and excessive user privileges.
* **Tools Used**: `lynis`, `find`, `chmod`, `ufw`, `systemctl`.
* **Learning Outcomes**: Principle of least privilege, SUID remediation, firewall rule definitions, auth log auditing.

### Lab 4 — Network Traffic Analysis
* **Objective**: Analyze real-world packet captures to detect malicious or anomalous traffic.
* **Environment**: Pre-packaged offline `.pcap` files containing simulated network attacks, port scans, and cleartext credential leaks.
* **Tools Used**: `wireshark`, `tshark`.
* **Learning Outcomes**: Display filters, TCP stream reassembly, protocol dissection, identifying anomalous beacons.

### Lab 5 — Secure Code Review
* **Objective**: Detect code-level security vulnerabilities before deployment.
* **Environment**: Sample repositories with hardcoded secrets, unsafe deserialization, SQL injection, and command injection patterns.
* **Tools Used**: `bandit`, static linters.
* **Learning Outcomes**: Static application security testing (SAST), remediation patches.
