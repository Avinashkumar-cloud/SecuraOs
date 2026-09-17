#!/usr/bin/env bash
# ==============================================================================
# Secura OS — Test Generated ISO in QEMU / KVM
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ISO_PATH="${1:-${PROJECT_ROOT}/dist/secura-1.0.0-alpha-amd64.iso}"

if [ ! -f "${ISO_PATH}" ]; then
    echo "[-] Error: ISO image not found at: ${ISO_PATH}" >&2
    echo "    Build the ISO first with: sudo bash build/scripts/build-iso.sh" >&2
    exit 1
fi

command -v qemu-system-x86_64 >/dev/null 2>&1 || {
    echo "[-] Error: 'qemu-system-x86_64' is not installed." >&2
    echo "    Install with: sudo apt-get install -y qemu-system-x86 ovmf" >&2
    exit 1
}

# Determine KVM acceleration
KVM_FLAG=""
if [ -w /dev/kvm ]; then
    KVM_FLAG="-enable-kvm"
    echo "[+] KVM hardware acceleration enabled."
else
    echo "[!] Warning: /dev/kvm not writable, running in pure emulation (slower)."
fi

echo "[+] Starting Secura OS Live VM testing session..."
qemu-system-x86_64 \
    ${KVM_FLAG} \
    -m 4096 \
    -smp 4 \
    -cpu host \
    -vga virtio \
    -display gtk,gl=on \
    -cdrom "${ISO_PATH}" \
    -boot d \
    -net nic,model=virtio \
    -net user \
    -name "Secura OS Live Test"
