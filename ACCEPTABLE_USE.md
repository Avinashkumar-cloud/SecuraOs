# Secura Acceptable Use Policy (AUP)

**Effective Date:** September 2026  
**Version:** 1.0.0

---

## 1. Core Principle & Ethical Mandate

Secura is a specialized Linux distribution created strictly for **cybersecurity education**, **defensive security analysis**, **authorized security auditing**, **Linux administration**, and **safe laboratory training**.

> ### ⚠️ Crucial Safety Notice
> **Having a tool available does not mean the user is authorized to use it against every target.**
>
> **Scope validation is a safety control, not legal authorization.**

The inclusion of security assessment tools in Secura does not grant permission to perform unauthorized testing, scanning, enumeration, or exploitation against any system, network, organization, or individual.

---

## 2. Authorized Use Cases

Secura is intended solely for:

1. **Explicitly Authorized Security Auditing**: Conducting tests against networks, applications, or infrastructure where you have received written, formal, explicit authorization from the verified system owner.
2. **Personal Systems & Owned Hardware**: Testing systems, routers, virtual machines, and hardware devices that you personally own and operate.
3. **Local & Isolated Laboratories**: Engaging with Secura's built-in containerized labs, isolated cyber-ranges, CTF environments, or virtual machine target networks that do not leak traffic into production networks.
4. **Academic & Classroom Environments**: University cybersecurity courses, certified training programs, and supervised academic research.
5. **Defensive Analysis & Incident Response**: Forensic examination, log inspection, defensive rule evaluation (e.g., firewall, IDS/IPS), and software code auditing.

---

## 3. Prohibited Activities

Users of Secura must **never**:

* Scan, probe, test, or attack any system, network, host, or service without explicit prior written authorization from the owner.
* Conduct denial-of-service (DoS/DDoS) attacks against any target.
* Attempt unauthorized access, credential theft, privilege escalation, or lateral movement on unauthorized networks.
* Deploy malware, ransomware, botnets, cryptominers, or destructive payloads.
* Bypass, disable, or tamper with Secura's scope enforcement or audit logging mechanisms to conceal unauthorized activity.
* Distribute modified versions of Secura designed to facilitate malicious, destructive, or unauthorized cyber attacks.

---

## 4. Scope Management & Legal Reality

Secura integrates a mandatory **Scope Management Engine** (`secura scope`). 

* The scope engine is designed to prevent accidental targeting of unintended IP addresses, public subnets, and critical infrastructure.
* **Adding a target to Secura's Scope Manager does NOT grant or imply legal permission.** Legal authorization can only be granted by the legal owner of the target infrastructure via formal agreements (such as a signed Rules of Engagement / RoE document).
* You are solely and personally responsible for complying with all applicable local, state, national, and international laws (such as the US Computer Fraud and Abuse Act (CFAA), UK Computer Misuse Act, and equivalents worldwide).

---

## 5. Disclaimer of Liability

The developers, contributors, and maintainers of Secura assume no liability and are not responsible for any misuse, damage, data loss, legal consequences, or operational disruptions caused by the use or misuse of this operating system or the tools bundled within it.
