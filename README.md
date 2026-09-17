# Secura OS

> **A Debian-based cybersecurity education and authorized-testing operating system designed for safety, stability, transparency, and architectural rigor.**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Base Distribution](https://img.shields.io/badge/Base-Debian%2012%20(Bookworm)-D70A53.svg)](https://www.debian.org)
[![Desktop](https://img.shields.io/badge/Desktop-XFCE%204.18-1793D1.svg)](https://www.xfce.org)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg)](https://www.python.org)
[![Status](https://img.shields.io/badge/Status-Milestone%201%20Foundation-orange.svg)](#roadmap)

---

## 1. Project Vision

**Secura** is an open-source, curated Linux distribution built on Debian Stable. It provides a structured, guided, and safe environment for:

* Cybersecurity students & learners
* Junior security analysts & SOC engineers
* Security researchers & ethical penetration testing students
* Network administration & Linux learners
* University labs, training academies, and workshops
* Authorized defensive and offensive security professionals

### How Secura Differs from Kali Linux
Unlike distributions that preload thousands of disparate, unvetted tools without context or guardrails:
* **Curated Tooling**: Only verified, high-value defensive, audit, and educational security tools are integrated.
* **Integrated Scope Management**: Tools require an active, validated assessment scope before execution.
* **Audit Trail**: Every security operation is automatically recorded into a structured, redacted JSONL audit log.
* **Safe Local Laboratories**: Isolated, containerized environments (powered by rootless Podman) let learners practice techniques without network risk.
* **Beginner-Friendly Experience**: Every tool and lab provides context, methodology, safe usage examples, and risk ratings.

> [!WARNING]
> **Important Safety Notice**:  
> Having a tool installed does not mean you are authorized to use it against every target.  
> **Scope validation is a safety control, not legal authorization.**  
> Always obtain explicit, written permission from verified system owners before conducting any testing. See [ACCEPTABLE_USE.md](ACCEPTABLE_USE.md).

---

## 2. System Architecture

Secura adopts a unified core architecture where the graphical interface (**Secura Center**) and the command-line interface (`secura`) share identical business logic:

```text
               ┌───────────────────────────┐
               │    Secura Center (GUI)    │  (PySide6 Desktop Application)
               │    - Dashboard & Metrics  │
               │    - Scope Manager        │
               │    - Tool Catalog         │
               │    - Lab Launcher         │
               │    - Report Viewer        │
               └─────────────┬─────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      Secura Core Engine                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Scope Manager (Target validation, CIDR, RFC1918 check)│  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ Audit Logger (JSONL structured logs + regex redactor) │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ Safe Runner (shell=False, argument arrays, timeouts)  │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ Tool Catalog (Metadata schema, risk levels, guidance) │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ Lab Manager (Isolated rootless Podman lab containers) │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ Report Engine (Markdown & HTML reporting)             │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ System Info & Hardware Inspector                      │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             ▲
                             │
               ┌─────────────┴─────────────┐
               │        Secura CLI         │  (Typer / Rich Command Line)
               │   `secura status`         │
               │   `secura scope add/list` │
               │   `secura tools list`     │
               │   `secura logs`           │
               └───────────────────────────┘
                             │
                             ▼
         ┌───────────────────────────────────────┐
         │     Debian 12 Base Linux System       │
         │  (Kernel, systemd, NetworkManager,    │
         │   XFCE, Polkit, Podman, Calamares)    │
         └───────────────────────────────────────┘
```

---

## 3. Repository Organization

```text
secura-os/
├── README.md                          # Project overview, vision, and quickstart
├── LICENSE                            # Apache 2.0 open-source license
├── SECURITY.md                        # Vulnerability reporting process and invariants
├── CONTRIBUTING.md                    # Developer standards, branching, and testing
├── CODE_OF_CONDUCT.md                 # Contributor Covenant v2.1
├── ACCEPTABLE_USE.md                  # Ethical boundaries and legal disclaimer
├── pyproject.toml                     # Modern PEP 621 Python packaging
├── ruff.toml                          # Formatting & linting configuration
│
├── docs/                              # Technical documentation
│   ├── hardware-compatibility.md      # x86_64, UEFI, legacy BIOS, RAM/CPU requirements
│   ├── mac-compatibility.md           # Intel Mac vs Apple Silicon (UTM / QEMU virtualization)
│   ├── virtualization.md              # QEMU/KVM, UTM, VirtualBox, VMware setup guide
│   ├── installation.md                # Live USB, Calamares installer, dd/Rufus/Etcher guide
│   ├── security-model.md              # Least privilege, safe subprocesses, audit architecture
│   ├── tools.md                       # Curated tool catalog, metadata schema, and risk levels
│   ├── labs.md                        # Built-in local cybersecurity training laboratories
│   └── troubleshooting.md             # Common boot, display, networking, and VM issues
│
├── build/                             # OS distribution generation scaffolding
│   ├── live-build/                    # Debian live-build configs (auto/, package-lists)
│   ├── packages/                      # Debian packaging rules for secura-core
│   ├── includes.chroot/               # Live system overlay (etc/skel, systemd, polkit)
│   └── scripts/                       # build-iso.sh, test-vm.sh
│
├── packaging/
│   └── calamares/                     # Calamares graphical OS installer configuration
│
├── src/
│   └── secura/                        # Core Python architecture
│       ├── config/                    # Config manager & Pydantic schemas
│       ├── logging/                   # Audit logger (JSONL) & credential redactor
│       ├── core/                      # System info inspector & safe subprocess runner
│       ├── scope/                     # Scope target validator & persistent manager
│       ├── tools/                     # Tool catalog loader & metadata schema
│       ├── labs/                      # Local containerized lab abstraction
│       ├── reports/                   # Security report data models & generators
│       ├── security/                  # Privilege checks & unprivileged enforcement
│       ├── cli/                       # Typer CLI application (`secura`)
│       └── gui/                       # PySide6 GUI entry point (`secura-center`)
│
├── tests/                             # Comprehensive automated pytest test suite
│
└── .github/
    └── workflows/                     # Automated CI/CD (lint, test, build)
```

---

## 4. Hardware & Platform Compatibility

Secura is engineered for x86_64 PCs and laptops from the past 8–10 years:

* **Primary CPU**: 64-bit x86_64 (Intel Core i3/i5/i7/i9/Xeon, AMD Ryzen/Athlon/FX).
* **RAM**: 4 GB minimum recommended; 2 GB minimum bare boot.
* **Storage**: 25 GB free disk space for full OS installation.
* **Firmware**: UEFI (with GPT) and Legacy BIOS (with MBR).
* **Mac Support**:
  * *Intel Macs*: Bootable via standard x86_64 ISO.
  * *Apple Silicon Macs (M1/M2/M3/M4)*: Virtualization via **UTM** or **QEMU** with documented acceleration. (Native bare-metal ARM64 is planned on the roadmap).
* **Virtual Machines**: First-class support for **QEMU/KVM**, **UTM**, **VirtualBox**, and **VMware**.

See [docs/hardware-compatibility.md](docs/hardware-compatibility.md) and [docs/mac-compatibility.md](docs/mac-compatibility.md) for full details.

---

## 5. Development Roadmap

- [x] **Milestone 1 — Foundation**: Repository structure, packaging, core configuration, audit logging with redaction, scope validation engine, CLI skeleton, docs, live-build scaffolding, and unit test suite.
- [ ] **Milestone 2 — CLI Expansion**: Complete interactive CLI workflows (`secura status`, `secura scope`, `secura tools`, `secura logs`, `secura report`).
- [ ] **Milestone 3 — Secura Center (GUI)**: PySide6-based control center with dark/light theme, system dashboard, scope wizard, interactive catalog, and log viewer.
- [ ] **Milestone 4 — Tool Integration**: Integration of curated defensive/auditing tools with parameter builders and scope safety locks.
- [ ] **Milestone 5 — Safe Labs**: Rootless Podman containerized laboratories (Network Discovery, Web Security, Linux Hardening).
- [ ] **Milestone 6 — Reporting**: Markdown and HTML vulnerability report generator with audit evidence linkage.
- [ ] **Milestone 7 — Bootable ISO**: Live Debian 12 ISO generation via `live-build`, Calamares installer, UEFI/BIOS boot test.
- [ ] **Milestone 8 — Hardware Testing & Release v1.0**: Validation on physical hardware matrix, VM verification, and public release.

---

## 6. Getting Started (Developer Quickstart)

```bash
# Clone the repository
git clone https://github.com/secura-os/secura.git
cd secura

# Install dependencies
python -m pip install -e ".[dev]"

# Run status check
python -m secura.cli.main status

# Run the test suite
python -m pytest tests/ -v
```

---

## 7. License

Secura is open-source software licensed under the [Apache License 2.0](LICENSE).
Third-party Linux tools, kernels, and upstream Debian packages retain their respective open-source licenses (GPL, BSD, MIT).
