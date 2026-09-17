# Contributing to Secura

Thank you for your interest in contributing to **Secura**! Secura is an open-source, Debian-based cybersecurity education and authorized-testing operating system.

---

## 1. Code of Conduct

All contributors and maintainers are expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Please treat everyone with respect, maintain constructive feedback, and adhere to our ethical guidelines outlined in [ACCEPTABLE_USE.md](ACCEPTABLE_USE.md).

---

## 2. Development Principles

When contributing code, documentation, or tooling to Secura:

1. **Security First**: All subprocess calls must use safe argument arrays with `shell=False`. Secrets must be redacted from logs.
2. **Never Claim False Functionality**: If a feature, ISO build, or hardware driver is not yet fully implemented or tested, mark it as `TODO`, document the limitation, and provide safe interfaces.
3. **No Malicious Tools**: Contributions containing malware, exploit frameworks, botnets, persistence agents, or destructive automation will be rejected.
4. **Clean & Lightweight**: Maintain a minimal footprint suitable for 4 GB RAM systems and low-resource environments.
5. **Separation of Concerns**: Business logic belongs in `secura.core` or its domain modules (`scope`, `logging`, `tools`, `labs`, `reports`), shared between `secura.cli` and `secura.gui`.

---

## 3. Getting Started with Local Development

### Prerequisites
* Python 3.11+
* Debian 12 (Bookworm) or a virtual machine / container for live-build ISO testing
* Git

### Local Setup
```bash
# Clone the repository
git clone https://github.com/secura-os/secura.git
cd secura

# Create a virtual environment (optional but recommended)
python -m venv .venv
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\Activate.ps1

# Install development dependencies
python -m pip install -e ".[dev]"
```

---

## 4. Running Tests & Quality Checks

Before submitting a Pull Request, ensure all tests and linters pass:

```bash
# Run pytest with coverage
python -m pytest tests/ -v

# Run Ruff linter
python -m ruff check src/ tests/

# Run Ruff format check
python -m ruff format --check src/ tests/
```

---

## 5. Branching & Commit Conventions

* Create feature branches from `main`:
  `git checkout -b feature/scope-cidr-validation` or `git checkout -b fix/redactor-jwt-pattern`
* Use conventional commits:
  * `feat: add IPv6 CIDR validation in scope manager`
  * `fix: correct audit log file permission handling`
  * `docs: update Apple Silicon virtualization guide`
  * `test: add unit tests for safe subprocess timeouts`

---

## 6. Pull Request Process

1. Provide a clear description of the problem solved and the implementation approach.
2. Ensure automated tests are added or updated to cover all new logic.
3. Verify that documentation under `docs/` reflects any user-facing changes or new configurations.
4. Maintainers will review the PR for security, architectural integrity, performance, and ethical compliance.
