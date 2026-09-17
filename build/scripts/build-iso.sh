#!/usr/bin/env bash
# ==============================================================================
# Secura OS — Reproducible Debian 12 (Bookworm) Live ISO Build Script
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
BUILD_DIR="${PROJECT_ROOT}/build/live-build"
OUTPUT_DIR="${PROJECT_ROOT}/dist"
ISO_NAME="secura-1.0.0-alpha-amd64.iso"

echo "================================================================="
echo "   Secura OS — Live Distribution ISO Build Pipeline"
echo "================================================================="
echo "Project Root: ${PROJECT_ROOT}"
echo "Build Dir:    ${BUILD_DIR}"
echo "Target ISO:   ${OUTPUT_DIR}/${ISO_NAME}"
echo "================================================================="

# 1. Environment and Privilege Checks
if [[ $EUID -ne 0 ]]; then
   echo "[-] Error: Building a Debian Live ISO requires root privileges." >&2
   echo "    Please run: sudo bash $0" >&2
   exit 1
fi

command -v lb >/dev/null 2>&1 || {
    echo "[-] Error: 'live-build' (lb) is not installed." >&2
    echo "    On Debian/Ubuntu: sudo apt-get update && sudo apt-get install -y live-build xorriso isolinux grub-efi-amd64-bin" >&2
    exit 1
}

# 2. Prepare Directories
mkdir -p "${BUILD_DIR}"
mkdir -p "${OUTPUT_DIR}"
cd "${BUILD_DIR}"

# 3. Clean previous build artifacts
echo "[+] Cleaning previous build artifacts..."
lb clean --purge || true

# 4. Configure live-build
echo "[+] Configuring live-build for Debian 12 Bookworm (amd64)..."
lb config \
    --mode debian \
    --system live \
    --distribution bookworm \
    --architectures amd64 \
    --archive-areas "main contrib non-free non-free-firmware" \
    --image-name "secura-live" \
    --iso-application "Secura Cybersecurity OS" \
    --iso-publisher "Secura Project (https://github.com/secura-os)" \
    --iso-volume "SECURA_LIVE" \
    --binary-images iso-hybrid \
    --bootloader grub-efi \
    --memtest memtest86+ \
    --win32-loader false \
    --apt-recommends false \
    --security true \
    --updates true

# 5. Populate Package Lists
mkdir -p config/package-lists
cp -r "${PROJECT_ROOT}/build/live-build/config/package-lists/"* config/package-lists/ 2>/dev/null || true

# 6. Copy Chroot Overlays (system files, desktop settings, Secura binaries)
mkdir -p config/includes.chroot
if [ -d "${PROJECT_ROOT}/build/includes.chroot" ]; then
    echo "[+] Syncing rootfs overlays from build/includes.chroot..."
    cp -r "${PROJECT_ROOT}/build/includes.chroot/"* config/includes.chroot/
fi

# 7. Install Secura Python package into Chroot
echo "[+] Preparing Secura core package for chroot installation..."
mkdir -p config/includes.chroot/opt/secura
cp -r "${PROJECT_ROOT}/src" config/includes.chroot/opt/secura/
cp "${PROJECT_ROOT}/pyproject.toml" config/includes.chroot/opt/secura/

# 8. Execute Build
echo "[+] Executing 'lb build' (this will take several minutes)..."
lb build

# 9. Verify and Checksum Output
if [ -f "live-image-amd64.hybrid.iso" ]; then
    mv "live-image-amd64.hybrid.iso" "${OUTPUT_DIR}/${ISO_NAME}"
    echo "[+] ISO successfully generated: ${OUTPUT_DIR}/${ISO_NAME}"

    cd "${OUTPUT_DIR}"
    sha256sum "${ISO_NAME}" > "${ISO_NAME}.sha256"
    echo "[+] SHA256 digest generated:"
    cat "${ISO_NAME}.sha256"
else
    echo "[-] Error: ISO was not produced by live-build." >&2
    exit 1
fi

echo "================================================================="
echo "   Secura OS Build Complete!"
echo "================================================================="
