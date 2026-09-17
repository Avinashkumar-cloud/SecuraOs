# Secura Troubleshooting & Diagnostics Guide

This guide covers common issues encountered during booting, display configuration, networking, and virtual machine operation.

---

## 1. Boot Issues

### A. "Secure Boot Violation" / System refuses to boot USB
* **Cause**: In pre-release/alpha builds, custom unsigned kernel modules or bootloaders are rejected by OEM UEFI Secure Boot.
* **Solution**:
  1. Restart your PC and press the BIOS setup key (`F2`, `F10`, `Del`).
  2. Navigate to **Security** or **Boot** settings.
  3. Set **Secure Boot** to **Disabled**.
  4. Save changes and reboot.

### B. Black Screen After GRUB Boot Menu
* **Cause**: Kernel mode setting (KMS) conflict with specific dedicated GPU hardware (Nvidia or older AMD/Intel).
* **Solution**:
  1. At the GRUB menu, highlight **Secura Live (Default)** and press `e` to edit boot parameters.
  2. Locate the line starting with `linux /live/vmlinuz...`.
  3. Add `nomodeset` to the end of the line.
  4. Press `Ctrl + X` or `F10` to boot. Alternatively, select **Secura Live (Failsafe Graphics)** from the sub-menu.

---

## 2. Display & Graphical Environment Issues

### A. Screen Resolution Locked or Distorted in Virtual Machine
* **Cause**: Guest display driver not actively negotiating resolution with hypervisor.
* **Solution**:
  * **VirtualBox**: Install or verify `virtualbox-guest-utils` and `xserver-xorg-video-vmware`. Set Graphics Controller to `VBoxSVGA`.
  * **QEMU / KVM**: Use display device `virtio-vga` or `virtio-gpu-gl` with SPICE agent enabled.
  * **XFCE Resolution Adjustment**: Open **Settings -> Display** and select your native resolution.

---

## 3. Networking & Wi-Fi Diagnostics

### A. No Wi-Fi Networks Detected
* **Diagnosis**: Run `secura status` or in a terminal:
  ```bash
  ip link show
  sudo dmesg | grep -i firmware
  ```
* **Cause**: Missing non-free proprietary firmware for your wireless chipset (e.g. Broadcom BCM43xx, Realtek RTL8821CE).
* **Solution**: Connect via wired Ethernet temporarily, then install the relevant Debian firmware package:
  ```bash
  sudo apt update
  sudo apt install firmware-linux-nonfree firmware-iwlwifi firmware-realtek
  ```

### B. NetworkManager Service Not Running
* Restart the network service:
  ```bash
  sudo systemctl restart NetworkManager
  ```

---

## 4. Secura CLI & Core Diagnostics

### A. Scope Validation Blocks a Command
* If `secura` warns that a target is out of scope or blocked:
  ```bash
  # Check your active scopes:
  secura scope list
  
  # If testing a local device, explicitly add it:
  secura scope add 192.168.1.50 --description "Test router" --type ipv4
  ```

### B. View Diagnostic Audit Logs
```bash
# View recent system audit events:
secura logs --limit 20

# Inspect raw JSONL log file:
cat ~/.config/secura/logs/audit.jsonl | tail -n 10
```
