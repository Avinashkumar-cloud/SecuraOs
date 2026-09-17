# Secura Hardware Compatibility Guide

Secura is engineered to run reliably on consumer, enterprise, and educational PC hardware manufactured within the last 8–10 years.

---

## 1. System Requirements

| Specification | Minimum (Bare Boot) | Recommended (Comfortable Lab Operation) | Ideal (Multi-Container Labs) |
| :--- | :--- | :--- | :--- |
| **Processor (CPU)** | 64-bit Dual-Core x86_64 (1.8 GHz) | 64-bit Quad-Core x86_64 (2.5 GHz+) | Modern 6+ Core AMD Ryzen or Intel Core i5/i7/i9 |
| **System Memory (RAM)**| 2 GB RAM (text/minimal XFCE) | 4 GB RAM | 8 GB – 16 GB RAM |
| **Storage (Disk)** | 16 GB free disk space | 25 GB free disk space (SSD) | 50 GB+ NVMe SSD |
| **Graphics** | 1024x768 display resolution | 1920x1080 (FHD) with hardware acceleration | 1080p or multi-monitor |
| **Network** | 100 Mbps Ethernet adapter | Gigabit Ethernet + 802.11ac Wi-Fi | Gigabit Ethernet + Wi-Fi with monitor mode |
| **Firmware** | Legacy BIOS or 64-bit UEFI | 64-bit UEFI with GPT partitioning | 64-bit UEFI |

---

## 2. Supported Architectures

### Primary: `x86_64` (`amd64`)
* Intel Core 2 Duo (later 64-bit revisions), Core i3/i5/i7/i9, Xeon.
* AMD Athlon 64 X2, Phenom, FX, A-Series, Ryzen, EPYC.
* Broad support for Intel HD/UHD integrated graphics, AMD Radeon, and standard Linux open-source drivers (Mesa).

### Stretch / Future: `arm64` (`aarch64`)
* Native bare-metal ARM64 (e.g., Raspberry Pi 4/5, Pinebook) is in the Secura roadmap for subsequent milestones.
* For Apple Silicon (M-Series Macs), see [docs/mac-compatibility.md](mac-compatibility.md).

---

## 3. Boot Modes & Firmware Support

### UEFI (Unified Extensible Firmware Interface)
* Secura provides standard 64-bit UEFI boot support via GRUB 2 EFI.
* Formatted using GUID Partition Table (GPT).
* **Secure Boot Status**: During early pre-release / alpha phases, Secure Boot must be disabled in UEFI BIOS settings. Signed shim bootloader integration is planned for Milestone 7.

### Legacy BIOS (CSM / MBR)
* Secura includes syslinux/isolinux fallback for legacy BIOS systems.
* Supports older PC laptops and desktops lacking modern UEFI firmware.

---

## 4. Peripherals & Networking

* **Keyboards & Mice**: Standard USB HID devices, PS/2 interfaces, and standard laptop trackpads (Synaptics, ELAN, Libinput).
* **Ethernet**: Broad support for Realtek (`r8169`), Intel (`e1000e`, `igb`), and Broadcom adapters.
* **Wi-Fi**: Includes standard open-source wireless firmware (Intel Wi-Fi `iwlwifi`, Atheros `ath9k`/`ath10k`, Realtek `rtw88`). Proprietary non-free firmware packages can be included in live-build configurations as permitted by Debian package guidelines.

---

## 5. Hardware Verification Test Matrix

The following matrix records verified testing targets across physical systems and hypervisors:

| Platform / Device | CPU & Specs | Firmware | Boot Result | Installation | Network / Wi-Fi | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Intel ThinkPad T480** | Intel Core i5-8350U, 16GB RAM | UEFI | Untested (Planned M8) | Untested | Untested | Primary reference physical laptop |
| **AMD Ryzen Desktop** | Ryzen 5 3600, 16GB RAM | UEFI | Untested (Planned M8) | Untested | Untested | Primary reference physical desktop |
| **Intel Mac (2015-2019)**| Core i5/i7 x86_64 | Apple EFI | Untested (Planned M8) | Untested | Untested | See Mac guide |
| **QEMU / KVM (Linux)** | Virtualized x86_64, 4GB RAM | SeaBIOS / OVMF | Pending M7 ISO | Pending M7 | VirtIO OK | Primary development hypervisor |
| **VirtualBox 7.x** | Virtualized x86_64, 4GB RAM | BIOS / EFI | Pending M7 ISO | Pending M7 | Intel PRO/1000 OK| Cross-platform testing |
| **VMware Workstation** | Virtualized x86_64, 4GB RAM | BIOS / EFI | Pending M7 ISO | Pending M7 | VMXNET3 OK | Enterprise lab testing |
| **Apple Silicon (UTM)**| Apple M1/M2/M3 via UTM | Emulated x86_64 / Native ARM64 | Pending M7 ISO | Pending M7 | Slirp/Bridged | See Mac guide |

> [!NOTE]
> Per Secura development rules, compatibility status is strictly marked as **Untested** until verified against physical ISO builds.
