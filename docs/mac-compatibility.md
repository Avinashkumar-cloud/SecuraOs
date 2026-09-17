# Secura Apple Mac Compatibility Guide

Secura supports Mac users through both bare-metal installation (on Intel Macs) and virtualization (on Apple Silicon and Intel Macs).

---

## 1. Important Distinction: Intel vs. Apple Silicon Macs

| Feature | Intel-Based Macs (2006 – 2020) | Apple Silicon Macs (M1, M2, M3, M4, Pro/Max/Ultra) |
| :--- | :--- | :--- |
| **CPU Architecture** | 64-bit `x86_64` | 64-bit `ARM64` (`aarch64`) |
| **Bare-Metal Boot** | Supported via Apple EFI (Option/Alt key boot) | **NOT natively supported bare-metal.** Do not attempt direct install. |
| **Primary Deployment**| Live USB, dual-boot, or VM | **Virtualization via UTM, Parallels, or QEMU** |
| **ARM64 Roadmap** | N/A | Native ARM64 live-build planned for Milestone 8+ |

> [!CAUTION]
> **Do NOT attempt to flash a Secura x86_64 ISO directly onto an Apple Silicon Mac's internal storage.** Apple Silicon hardware uses a custom boot architecture (iBoot/Apple Silicon firmware) that does not boot standard PC x86_64 EFI binaries.

---

## 2. Running Secura on Apple Silicon via UTM (Recommended)

**UTM** is the recommended open-source hypervisor for macOS:

### Option A: Emulated x86_64 (Direct ISO usage)
1. Download and install [UTM](https://mac.getutm.app/).
2. Click **Create a New Virtual Machine** -> **Emulate** -> **Linux**.
3. Select the Secura x86_64 ISO image.
4. **Hardware Configuration**:
   * **Memory**: Minimum 4096 MB (4 GB).
   * **CPU Cores**: 4 vCPUs.
   * **Disk Size**: 25 GB or larger.
   * **Display**: Choose `virtio-gpu-gl` or `virtio-ramfb` for smooth desktop rendering.
5. In Network settings, choose **Shared Network (NAT)**.

### Option B: Native ARM64 (Future Release)
When Secura releases its official `arm64` ISO, UTM's **Virtualize** engine will provide near-native performance with Apple Hypervisor acceleration.

---

## 3. Recommended VM Settings for macOS Hypervisors

| Hypervisor | Recommended vCPUs | Recommended RAM | Display Adapter | Audio |
| :--- | :--- | :--- | :--- | :--- |
| **UTM** | 4 Cores | 4096 MB – 8192 MB | VirtIO-GPU GL | Intel AC97 / HDA |
| **Parallels Desktop** | 4 Cores | 4096 MB | Parallels Video (3D enabled) | CoreAudio |
| **VMware Fusion** | 4 Cores | 4096 MB | VMware SVGA 3D | Intel HDA |

---

## 4. Networking Modes for macOS Virtual Machines

1. **Shared Network (NAT)**:
   * *Best for*: General web browsing, downloading security updates, isolated research.
   * *Limitation*: The host machine cannot directly connect to services inside the VM without explicit port forwarding.
2. **Bridged Network**:
   * *Best for*: Network scanning laboratories, interacting with other physical lab hardware, Wireshark packet capture.
   * *Configuration*: VM obtains an IP address directly from your local Wi-Fi / Ethernet router.
3. **Host-Only Network**:
   * *Best for*: Safe exploit analysis, malware dissection labs, preventing any traffic from escaping into the internet.

---

## 5. VM Best Practices on macOS

* **Snapshots**: Always create a clean snapshot named `Base-Clean-Install` immediately after booting or installing Secura. If an assessment or lab causes system instability, restore the snapshot in seconds.
* **Shared Folders**: In UTM or Parallels, configure a host shared directory (e.g., `~/SecuraShared`) to export audit logs and generated security reports to macOS without network file transfers.
* **USB Device Passthrough**: To use an external Wi-Fi dongle (e.g., Alfa AWUS036ACH for monitor mode) or USB drive, enable USB device sharing in UTM settings.
