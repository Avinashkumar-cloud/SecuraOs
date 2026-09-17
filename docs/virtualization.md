# Secura Virtual Machine Deployment Guide

Virtual machines (VMs) are a **first-class deployment target** for Secura. For beginners, cybersecurity students, and risk-sensitive assessments, running Secura in an isolated VM is strongly recommended over installing directly to bare metal.

---

## 1. Why Run Secura in a Virtual Machine?

* **Risk Containment**: Vulnerability testing and lab exercises cannot compromise your host operating system.
* **Instant Rollbacks**: Take VM snapshots before running potentially breaking configurations or tests; restore in seconds.
* **Hardware Portability**: Easily transfer complete Secura lab configurations between laptops and lab desktops.
* **Multi-OS Convenience**: Run Secura alongside Windows, macOS, or your daily Linux distribution without rebooting.

---

## 2. Resource Allocation Recommendations

| Profile | vCPUs | RAM | Virtual Disk | Recommended Hypervisor |
| :--- | :--- | :--- | :--- | :--- |
| **Lightweight / Basic** | 2 vCPUs | 2048 MB (2 GB) | 20 GB (Dynamically Allocated) | VirtualBox, UTM |
| **Standard Student / Lab**| 4 vCPUs | 4096 MB (4 GB) | 30 GB (Dynamically Allocated) | VirtualBox, VMware, QEMU/KVM |
| **Heavy Lab / Multi-Pod** | 4–8 vCPUs | 8192 MB (8 GB) | 50 GB+ | QEMU/KVM, VMware Workstation Pro |

---

## 3. Supported Hypervisors & Setup

### A. QEMU / KVM (Linux Host — Maximum Performance)
QEMU with KVM kernel acceleration provides near bare-metal performance on Linux hosts:

```bash
# Recommended QEMU launch command for Secura Live ISO:
qemu-system-x86_64 \
  -enable-kvm \
  -m 4096 \
  -smp 4 \
  -cpu host \
  -vga virtio \
  -display gtk,gl=on \
  -cdrom secura-live-amd64.iso \
  -boot d \
  -net nic,model=virtio \
  -net user
```

### B. Oracle VirtualBox (Windows, Linux, Intel macOS)
1. Create a new VM with **Type: Linux**, **Version: Debian (64-bit)**.
2. Allocate **4096 MB RAM** and **4 Processors**.
3. Create a **30 GB VDI disk** (Dynamically allocated).
4. Under **Settings -> System -> Motherboard**: Enable **EFI (special OSes only)**.
5. Under **Settings -> Display**: Set Video Memory to **128 MB**, Graphics Controller to **VBoxSVGA**, and enable **3D Acceleration**.
6. Attach the Secura ISO to the Virtual Optical Drive and start the VM.

### C. VMware Workstation / Player (Windows, Linux)
1. Choose **Create a New Virtual Machine** -> **Custom (Advanced)**.
2. Select **Debian 12.x 64-bit**.
3. Firmware type: **UEFI**.
4. Memory: **4 GB**, Processors: **4 Cores**.
5. Network: **NAT** (or Bridged for external network auditing).

---

## 4. Virtual Networking Topologies

Choosing the correct network mode is vital for cybersecurity training and safety:

### 1. NAT (Network Address Translation) — Default Safe Mode
* *Behavior*: Secura shares the host's IP address. Secura can access the internet to download updates. External machines cannot scan or reach Secura.
* *Best for*: Safe web browsing, tool downloads, learning CLI commands.

### 2. Bridged Adapter — Direct LAN Access
* *Behavior*: Secura receives its own dedicated IP address from your physical router, behaving like a separate physical machine on your LAN.
* *Best for*: Scanning local lab devices, authorized network auditing, Wireshark network monitoring.
* *Warning*: Secura is directly reachable by other machines on the local network. Ensure Secura's firewall is active.

### 3. Host-Only / Internal Isolated Network — Zero Risk
* *Behavior*: Secura communicates only with the host and other VMs in the same virtual subnet. Zero internet connectivity.
* *Best for*: Intentionally vulnerable laboratory environments (e.g., Metasploitable, vulnerable web apps), ensuring vulnerable services are never exposed to your home or corporate network.

---

## 5. VM Features & Best Practices

* **Snapshots**: Always take a snapshot named `Baseline-Clean` right after setup. Use snapshots before starting new lab modules.
* **Clipboard & Drag-and-Drop**: By default, Secura disables bidirectional clipboard sharing between guest and host for security containment. If enabled in hypervisor settings, be mindful not to accidentally paste sensitive host credentials into the VM.
* **USB Passthrough**: To perform Wi-Fi auditing or inspect USB devices, connect the physical USB dongle and use the hypervisor's USB Passthrough menu to redirect the hardware directly into Secura.
