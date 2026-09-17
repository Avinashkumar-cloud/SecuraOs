#!/usr/bin/env python3
"""Cross-platform Debian package (.deb) generator for secura-core.

Builds a standard Debian package (ar archive containing debian-binary,
control.tar.gz, and data.tar.gz) without requiring dpkg-deb.
"""

import gzip
import io
import os
import tarfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src" / "secura"
OUTPUT_DIR = PROJECT_ROOT / "dist"
VERSION = "0.1.0-alpha"
PACKAGE_NAME = "secura-core"


def create_ar_archive(filename: Path, members: list[tuple[str, bytes]]) -> None:
    """Create a standard Unix ar archive (.deb file)."""
    with open(filename, "wb") as f:
        # AR magic
        f.write(b"!<arch>\n")
        for name, data in members:
            # AR header: 16b name, 12b mtime, 6b uid, 6b gid, 8b mode, 10b size, 2b magic (`\n)
            name_field = f"{name:<16}".encode("ascii")[:16]
            mtime = f"{1726500000:<12}".encode("ascii")[:12]
            uid = f"{0:<6}".encode("ascii")[:6]
            gid = f"{0:<6}".encode("ascii")[:6]
            mode = f"{100644:<8o}".encode("ascii")[:8]
            size = f"{len(data):<10}".encode("ascii")[:10]
            header = name_field + mtime + uid + gid + mode + size + b"`\n"
            f.write(header)
            f.write(data)
            # 2-byte alignment padding
            if len(data) % 2 != 0:
                f.write(b"\n")


def build_deb_package(output_path: Path) -> Path:
    """Construct a clean, valid secura-core .deb package."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. debian-binary
    debian_binary = b"2.0\n"

    # 2. control.tar.gz
    control_content = f"""Package: {PACKAGE_NAME}
Version: {VERSION}
Architecture: all
Maintainer: Secura OS Project Maintainers <maintainers@secura-project.org>
Depends: python3, python3-pydantic, python3-yaml, python3-rich, python3-typer, python3-platformdirs
Section: admin
Priority: optional
Homepage: https://github.com/secura-os
Description: Secura OS Core Runtime, Scope Management, and CLI Architecture
 Secura is a curated, Debian-based cybersecurity education and authorized-testing
 operating system. This package supplies the unified Secura Python core, scope
 validation engine, structured audit logging with secret redaction, and the
 'secura' command line utility.
""".encode()

    control_tar_io = io.BytesIO()
    with gzip.GzipFile(fileobj=control_tar_io, mode="wb", mtime=1726500000) as gz:
        with tarfile.open(fileobj=gz, mode="w:") as tar:
            ti = tarfile.TarInfo(name="./control")
            ti.size = len(control_content)
            ti.mode = 0o644
            ti.mtime = 1726500000
            tar.addfile(ti, io.BytesIO(control_content))

    control_tar_gz = control_tar_io.getvalue()

    # 3. data.tar.gz
    data_tar_io = io.BytesIO()
    with gzip.GzipFile(fileobj=data_tar_io, mode="wb", mtime=1726500000) as gz:
        with tarfile.open(fileobj=gz, mode="w:") as tar:
            # Install python package under /usr/lib/python3/dist-packages/secura/
            for root, _, files in os.walk(SRC_DIR):
                for file in files:
                    if file.endswith((".py", ".yaml", ".json")):
                        full_p = Path(root) / file
                        rel_p = full_p.relative_to(PROJECT_ROOT / "src")
                        target_name = f"./usr/lib/python3/dist-packages/{rel_p.as_posix()}"

                        data = full_p.read_bytes()
                        ti = tarfile.TarInfo(name=target_name)
                        ti.size = len(data)
                        ti.mode = 0o644
                        ti.mtime = 1726500000
                        tar.addfile(ti, io.BytesIO(data))

            # Add CLI binary wrapper: /usr/bin/secura
            cli_wrapper = b"""#!/usr/bin/python3
from secura.cli.main import app
if __name__ == '__main__':
    app()
"""
            ti_cli = tarfile.TarInfo(name="./usr/bin/secura")
            ti_cli.size = len(cli_wrapper)
            ti_cli.mode = 0o755
            ti_cli.mtime = 1726500000
            tar.addfile(ti_cli, io.BytesIO(cli_wrapper))

            # Add GUI launcher: /usr/bin/secura-center
            gui_wrapper = b"""#!/usr/bin/python3
from secura.gui.main import main
if __name__ == '__main__':
    main()
"""
            ti_gui = tarfile.TarInfo(name="./usr/bin/secura-center")
            ti_gui.size = len(gui_wrapper)
            ti_gui.mode = 0o755
            ti_gui.mtime = 1726500000
            tar.addfile(ti_gui, io.BytesIO(gui_wrapper))

    data_tar_gz = data_tar_io.getvalue()

    # 4. Assemble ar archive
    members = [
        ("debian-binary", debian_binary),
        ("control.tar.gz", control_tar_gz),
        ("data.tar.gz", data_tar_gz),
    ]

    create_ar_archive(output_path, members)
    return output_path


def main():
    out_file = OUTPUT_DIR / f"{PACKAGE_NAME}_{VERSION}_all.deb"
    print(f"[+] Generating Debian package: {out_file}...")
    build_deb_package(out_file)
    print(f"[+] Package generated successfully! Size: {out_file.stat().st_size:,} bytes")
    print(f"[+] To install on Debian/Ubuntu: sudo dpkg -i {out_file.name}")


if __name__ == "__main__":
    main()
