# Secura Installation Guide

Secura can be booted directly as a **Live Operating System** from a USB flash drive without touching your computer's internal storage, or installed permanently onto a drive using the **Calamares Graphical Installer**.

---

## 1. Preparing the Installation Media

### Prerequisites
* A Secura ISO image file (e.g., `secura-1.0.0-amd64.iso`)
* The corresponding SHA256 checksum file (`secura-1.0.0-amd64.iso.sha256`)
* A USB flash drive with at least **8 GB** capacity.

### Step 1: Verify ISO Integrity
Always verify the cryptographic integrity of your downloaded ISO before flashing:

```bash
# On Linux / macOS:
sha256sum -c secura-1.0.0-amd64.iso.sha256

# On Windows (PowerShell):
Get-FileHash secura-1.0.0-amd64.iso -Algorithm SHA256
```
Ensure the printed hash matches the official published SHA-256 release digest.

---

## 2. Writing the ISO to a USB Drive

> [!CAUTION]
> **CRITICAL DATA LOSS WARNING**:  
> Writing an ISO image to a USB flash drive will **PERMANENTLY ERASE ALL EXISTING DATA** on that target device.  
> Double-check and triple-check that you have selected the correct USB drive letter or device path before proceeding!

### Method A: Balena Etcher (Windows, macOS, Linux — Recommended for Beginners)
1. Download and install [Balena Etcher](https://etcher.balena.io/).
2. Insert your USB flash drive.
3. Open Etcher and click **Flash from file**; select the Secura ISO.
4. Click **Select target** and carefully choose your USB drive (verify by drive size).
5. Click **Flash!** and wait for the verification process to finish.

### Method B: Rufus (Windows)
1. Download [Rufus](https://rufus.ie/).
2. Insert your USB flash drive.
3. Select your USB drive under **Device**.
4. Click **SELECT** and choose `secura-1.0.0-amd64.iso`.
5. Under **Partition scheme**:
   * Choose **GPT** for modern UEFI PCs.
   * Choose **MBR** for older Legacy BIOS systems.
6. Click **START**. If prompted, select **Write in DD Image mode** to preserve the hybrid ISO structure.

### Method C: Linux Terminal (`dd` — Advanced)
```bash
# Identify your USB drive carefully (e.g. /dev/sdb, NOT your internal disk /dev/nvme0n1 or /dev/sda!)
lsblk

# Flash the image directly (replace /dev/sdX with your actual USB device node)
sudo dd if=secura-1.0.0-amd64.iso of=/dev/sdX bs=4M status=progress conv=fsync
```

---

## 3. Booting Secura Live

1. Insert the USB drive into your computer while powered off.
2. Power on the machine and immediately press the Boot Menu key:
   * **Dell**: `F12`
   * **HP**: `F9` or `Esc`
   * **Lenovo**: `F12` or `Enter`
   * **Asus / Acer**: `F8` or `F12`
   * **Intel Mac**: Hold the `Option` (Alt) key immediately after chime.
3. Select the UEFI or USB boot device.
4. The Secura GRUB bootloader will appear. Choose:
   * `Secura Live (Default)`: Boots into live XFCE desktop in RAM.
   * `Secura Live (Failsafe / Safe Graphics)`: For problematic GPU hardware.

---

## 4. Permanent Installation via Calamares

Once booted into the Live Desktop, you can test tools freely in RAM. To permanently install Secura:

1. Click the desktop icon labeled **Install Secura System** to launch **Calamares**.
2. **Language & Location**: Choose your language, timezone, and keyboard layout.
3. **Storage Partitioning**:
   * *Option 1 — Install Alongside*: Shrinks an existing partition to install Secura in dual-boot.
   * *Option 2 — Erase Entire Disk*: Replaces everything on the selected disk with Secura.
     > [!WARNING]
     > Selecting "Erase Entire Disk" will completely wipe all operating systems, documents, and partitions on that drive.
   * *Option 3 — Manual Partitioning*: For advanced users who want custom mount points (`/`, `/home`, `/var`).
4. **User Setup**: Create your primary username and a strong passphrase. (Secura automatically configures the primary user with password-verified `sudo` permissions).
5. **Review Summary**: Carefully review the planned disk operations on the final summary screen.
6. Click **Install Now** and wait for Calamares to complete the system deployment.
7. Reboot the computer and remove the USB drive when instructed.
