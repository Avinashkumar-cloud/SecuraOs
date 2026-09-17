"""Secura command-line interface (CLI) implemented with Typer and Rich."""

import json
import os
import shutil
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from secura import DISCLAIMER, __version__
from secura.core.sysinfo import get_system_info
from secura.logging.audit import AuditLogger
from secura.reports.generator import ReportGenerator
from secura.reports.models import AssessmentReport
from secura.scope.manager import ScopeManager
from secura.tools.catalog import ToolCatalog

app = typer.Typer(
    name="secura",
    help="Secura OS - Curated Cybersecurity & Education Operating System CLI",
    add_completion=False,
)
scope_app = typer.Typer(help="Manage authorized assessment targets and scopes")
tools_app = typer.Typer(help="Explore curated cybersecurity tool catalog")
report_app = typer.Typer(help="Generate and manage security assessment reports")

app.add_typer(scope_app, name="scope")
app.add_typer(tools_app, name="tools")
app.add_typer(report_app, name="report")

console = Console()

# Global state for machine-readable JSON output
cli_state = {"json": False}


def is_json_mode(local_json: bool = False) -> bool:
    """Check if machine-readable JSON output was requested globally or locally."""
    return local_json or cli_state["json"] or any(arg in sys.argv for arg in ["--json", "-j"])


@app.callback(invoke_without_command=True)
def main_callback(
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Output raw machine-readable JSON format",
    ),
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Show distribution version and exit",
    ),
):
    cli_state["json"] = json_output

    if version:
        if json_output:
            print(json.dumps({"version": __version__, "disclaimer": DISCLAIMER}))
        else:
            console.print(
                f"[bold cyan]Secura OS Core CLI[/bold cyan] version [bold green]{__version__}[/bold green]"
            )
            console.print(f"[dim]{DISCLAIMER}[/dim]")
        raise typer.Exit()


@app.command(name="status")
def status_cmd(
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output raw machine-readable JSON format"
    ),
):
    """Display system status, resources, hypervisor environment, and scope summary."""
    sysinfo = get_system_info()
    scope_mgr = ScopeManager()
    active_scopes = scope_mgr.list_targets(active_only=True)
    audit_logger = AuditLogger()
    recent_events = audit_logger.query(limit=5)
    tool_catalog = ToolCatalog()
    all_tools = tool_catalog.list_tools()

    if is_json_mode(json_output):
        data = {
            "version": __version__,
            "system": sysinfo.model_dump(mode="json"),
            "active_scopes_count": len(active_scopes),
            "total_tools_count": len(all_tools),
            "recent_audit_count": len(recent_events),
            "disclaimer": DISCLAIMER,
        }
        print(json.dumps(data, indent=2))
        return

    console.print(
        Panel(
            f"[bold cyan]Secura OS Core Platform v{__version__}[/bold cyan]\n"
            f"[yellow]Notice:[/yellow] [italic]{DISCLAIMER}[/italic]",
            border_style="cyan",
        )
    )

    table = Table(title="System Status", show_header=True, header_style="bold blue")
    table.add_column("Property", style="bold")
    table.add_column("Status / Value")

    table.add_row("Operating System", f"{sysinfo.os_name} {sysinfo.os_release}")
    table.add_row("Kernel", sysinfo.kernel_version)
    table.add_row("Architecture", sysinfo.architecture)
    table.add_row(
        "Virtual Machine",
        f"[green]Yes ({sysinfo.hypervisor_name})[/green]"
        if sysinfo.is_virtual_machine
        else "[blue]Bare Metal[/blue]",
    )
    table.add_row("CPU Cores", str(sysinfo.cpu_count))
    table.add_row("Memory (RAM)", f"{sysinfo.memory.used_mb} MB / {sysinfo.memory.total_mb} MB")
    table.add_row(
        "Root Storage",
        f"{sysinfo.disk.used_gb} GB / {sysinfo.disk.total_gb} GB ({sysinfo.disk.percent_used}% used)",
    )
    table.add_row(
        "Active Scopes", f"[bold green]{len(active_scopes)}[/bold green] targets in scope"
    )
    table.add_row("Tool Catalog", f"{len(all_tools)} curated tools registered")

    console.print(table)


@scope_app.command(name="list")
def scope_list_cmd(
    all_targets: bool = typer.Option(
        False, "--all", "-a", help="Include expired and revoked targets"
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output raw machine-readable JSON format"
    ),
):
    """List registered assessment targets and their authorization status."""
    scope_mgr = ScopeManager()
    targets = scope_mgr.list_targets(active_only=not all_targets)

    if is_json_mode(json_output):
        print(json.dumps([t.model_dump(mode="json") for t in targets], indent=2))
        return

    if not targets:
        console.print("[yellow]No assessment targets currently registered in scope.[/yellow]")
        console.print("Add a target with: [bold]secura scope add <target>[/bold]")
        return

    table = Table(title="Secura Authorized Assessment Scope", header_style="bold blue")
    table.add_column("ID", style="dim", no_wrap=True)
    table.add_column("Target", style="bold", no_wrap=True)
    table.add_column("Type")
    table.add_column("Scope")
    table.add_column("Status")
    table.add_column("Expires At")
    table.add_column("Warning / Note")

    for t in targets:
        priv_str = "[green]Private[/green]" if t.is_private else "[bold red]Public[/bold red]"
        status_str = (
            f"[green]{t.status.value}[/green]"
            if t.is_currently_active()
            else f"[red]{t.status.value}[/red]"
        )
        warn_str = f"[yellow]{t.warning}[/yellow]" if t.warning else (t.description or "-")
        table.add_row(
            t.id,
            t.target,
            t.target_type.value,
            priv_str,
            status_str,
            t.expires_at or "Never",
            warn_str,
        )

    console.print(table)
    console.print(f"[dim italic]{DISCLAIMER}[/dim italic]\n")


@scope_app.command(name="add")
def scope_add_cmd(
    target: str = typer.Argument(..., help="Target IP, CIDR subnet, domain, or lab target"),
    description: str = typer.Option("", "--description", "-d", help="Description of target system"),
    owner_note: str = typer.Option(
        "", "--owner-note", "-o", help="Authorization / owner reference"
    ),
    hours: int = typer.Option(
        24, "--hours", "-h", help="Duration in hours until scope expires (0 for no expiration)"
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output raw machine-readable JSON format"
    ),
):
    """Register an authorized assessment target into the scope manager."""
    scope_mgr = ScopeManager()
    new_target, val_res = scope_mgr.add_target(
        target_str=target,
        description=description,
        owner_note=owner_note,
        duration_hours=hours if hours > 0 else None,
    )

    if not val_res.is_valid:
        if is_json_mode(json_output):
            print(json.dumps({"error": val_res.error, "is_valid": False}))
        else:
            console.print(f"[bold red]Error:[/bold red] {val_res.error}")
        raise typer.Exit(code=1)

    if is_json_mode(json_output):
        print(json.dumps(new_target.model_dump(mode="json") if new_target else {}, indent=2))
        return

    console.print(
        f"[bold green][+] Successfully added target to authorized scope:[/bold green] [bold]{new_target.target}[/bold]"
    )
    console.print(f"  - Type: {new_target.target_type.value}")
    console.print(
        f"  - Classification: {'Private IP/Subnet' if new_target.is_private else '[bold red]Public IP / Internet Target[/bold red]'}"
    )
    console.print(f"  - Expires: {new_target.expires_at or 'Never'}")

    if new_target.warning:
        console.print(f"  [bold yellow][!] WARNING:[/bold yellow] {new_target.warning}")

    console.print(f"\n[dim italic]{DISCLAIMER}[/dim italic]")


@scope_app.command(name="remove")
def scope_remove_cmd(
    target_or_id: str = typer.Argument(..., help="Target ID or canonical target string to remove"),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output raw machine-readable JSON format"
    ),
):
    """Remove a target from the authorized scope."""
    scope_mgr = ScopeManager()
    removed = scope_mgr.remove_target(target_or_id)

    if is_json_mode(json_output):
        print(json.dumps({"target": target_or_id, "removed": removed}))
        return

    if removed:
        console.print(f"[bold green][+] Removed target:[/bold green] {target_or_id}")
    else:
        console.print(f"[bold red]Target not found:[/bold red] {target_or_id}")
        raise typer.Exit(code=1)


@tools_app.command(name="list")
def tools_list_cmd(
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output raw machine-readable JSON format"
    ),
):
    """List tools in the curated security catalog."""
    catalog = ToolCatalog()
    tools = catalog.list_tools()

    if is_json_mode(json_output):
        print(json.dumps([t.model_dump(mode="json") for t in tools], indent=2))
        return

    table = Table(title="Secura Curated Tool Catalog", header_style="bold blue")
    table.add_column("Tool", style="bold")
    table.add_column("Category")
    table.add_column("Risk Level")
    table.add_column("Scope Required")
    table.add_column("Installed")
    table.add_column("Purpose")

    for t in tools:
        installed = catalog.is_installed(t)
        inst_str = "[green]Yes[/green]" if installed else "[dim]No[/dim]"
        risk_style = {
            "low": "[green]Low[/green]",
            "medium": "[yellow]Medium[/yellow]",
            "high": "[bold red]High[/bold red]",
        }.get(t.risk_level.value, t.risk_level.value)

        auth_req = "[yellow]Yes[/yellow]" if t.authorization_required else "[green]No[/green]"
        table.add_row(t.name, t.category.value, risk_style, auth_req, inst_str, t.purpose)

    console.print(table)


@app.command(name="logs")
def logs_cmd(
    limit: int = typer.Option(20, "--limit", "-l", help="Number of recent log events to display"),
    tool: str | None = typer.Option(None, "--tool", "-t", help="Filter by tool name"),
    action: str | None = typer.Option(None, "--action", "-a", help="Filter by action name"),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output raw machine-readable JSON format"
    ),
):
    """View recent structured audit log events."""
    audit_logger = AuditLogger()
    events = audit_logger.query(limit=limit, tool=tool, action=action)

    if is_json_mode(json_output):
        print(json.dumps([e.model_dump(mode="json") for e in events], indent=2))
        return

    if not events:
        console.print("[yellow]No audit events found matching query.[/yellow]")
        return

    table = Table(title=f"Recent Audit Log Trail ({len(events)} events)", header_style="bold blue")
    table.add_column("Timestamp", style="dim")
    table.add_column("User")
    table.add_column("Action", style="bold")
    table.add_column("Tool")
    table.add_column("Target")
    table.add_column("Result")

    for e in events:
        res_style = (
            "[green]completed[/green]"
            if e.result in ["completed", "success"]
            else f"[red]{e.result}[/red]"
        )
        table.add_row(e.timestamp[:19], e.user, e.action, e.tool or "-", e.target or "-", res_style)

    console.print(table)


@report_app.command(name="new")
def report_new_cmd(
    title: str = typer.Argument(..., help="Title of security assessment report"),
    assessor: str = typer.Option("Secura Analyst", "--assessor", help="Assessor name"),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output raw machine-readable JSON format"
    ),
):
    """Generate a baseline assessment report in Markdown and HTML formats."""
    scope_mgr = ScopeManager()
    active_scopes = [s.target for s in scope_mgr.list_targets(active_only=True)]
    audit_logger = AuditLogger()
    events = audit_logger.query(limit=100)

    report = AssessmentReport(
        title=title,
        assessor=assessor,
        scope_summary=active_scopes,
        audit_events_count=len(events),
    )

    generator = ReportGenerator()
    md_path, html_path = generator.save_report(report)

    if is_json_mode(json_output):
        print(
            json.dumps(
                {
                    "report_id": report.id,
                    "markdown_path": str(md_path),
                    "html_path": str(html_path),
                },
                indent=2,
            )
        )
        return

    console.print(f"[bold green][+] Created Assessment Report:[/bold green] {report.title}")
    console.print(f"  - Report ID: [bold]{report.id}[/bold]")
    console.print(f"  - Markdown: {md_path}")
    console.print(f"  - HTML: {html_path}")


@app.command(name="install")
def install_cmd(
    launch_gui: bool = typer.Option(
        True,
        "--gui/--no-gui",
        help="Attempt to launch Calamares graphical installer if desktop display is active",
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output raw machine-readable installer readiness diagnostic"
    ),
):
    """Inspect installation readiness and launch the Calamares OS installer."""
    sysinfo = get_system_info()
    is_live = Path("/run/live").exists() or Path("/lib/live/mount").exists()
    has_uefi = Path("/sys/firmware/efi").exists()
    calamares_bin = shutil.which("calamares") or shutil.which("secura-installer")
    has_display = bool(os.getenv("DISPLAY") or os.getenv("WAYLAND_DISPLAY"))

    meets_ram = sysinfo.memory.total_mb >= 3500
    meets_cpu = sysinfo.cpu_count >= 2
    meets_disk = sysinfo.disk.free_gb >= 20.0
    ready = meets_ram and meets_cpu

    disk_warning = (
        "Operating System installation modifies physical disk partitioning. "
        "Back up all important personal documents before continuing. "
        "Selecting 'Erase Entire Disk' will permanently delete all existing data."
    )

    if is_json_mode(json_output):
        data = {
            "is_live_environment": is_live,
            "meets_requirements": ready,
            "firmware": "UEFI" if has_uefi else "Legacy BIOS / Standard",
            "ram_mb": sysinfo.memory.total_mb,
            "cpu_cores": sysinfo.cpu_count,
            "disk_free_gb": sysinfo.disk.free_gb,
            "calamares_available": calamares_bin is not None,
            "has_graphical_display": has_display,
            "disk_warning": disk_warning,
        }
        print(json.dumps(data, indent=2))
        return

    console.print(
        Panel(
            "[bold cyan]Secura OS System Installer & Deployment Engine[/bold cyan]\n"
            f"[bold red][!] CRITICAL DATA SAFETY WARNING:[/bold red]\n{disk_warning}",
            border_style="red",
        )
    )

    table = Table(title="Installation Hardware Pre-flight Check", header_style="bold blue")
    table.add_column("Requirement", style="bold")
    table.add_column("Detected Value")
    table.add_column("Status")

    table.add_row(
        "Memory (RAM >= 3.5 GB)",
        f"{sysinfo.memory.total_mb} MB",
        "[green]PASS[/green]" if meets_ram else "[yellow]WARN (low RAM)[/yellow]",
    )
    table.add_row(
        "CPU Cores (>= 2 Cores)",
        f"{sysinfo.cpu_count} Cores",
        "[green]PASS[/green]" if meets_cpu else "[red]FAIL[/red]",
    )
    table.add_row(
        "Available Disk Space",
        f"{sysinfo.disk.free_gb} GB free",
        "[green]PASS[/green]" if meets_disk else "[yellow]CHECK TARGET DISK[/yellow]",
    )
    table.add_row(
        "Firmware Boot Mode",
        "64-bit UEFI (GPT)" if has_uefi else "Legacy BIOS (MBR)",
        "[green]SUPPORTED[/green]",
    )
    table.add_row(
        "Live Session Environment",
        "Active Live USB / ISO" if is_live else "Standard / Installed System",
        "[green]DETECTED[/green]" if is_live else "[blue]INFO[/blue]",
    )
    table.add_row(
        "Calamares GUI Installer",
        calamares_bin or "Not Installed",
        "[green]READY[/green]" if calamares_bin else "[yellow]UNAVAILABLE[/yellow]",
    )

    console.print(table)

    if launch_gui and calamares_bin and has_display:
        console.print("\n[bold green][+] Launching Calamares graphical installer...[/bold green]")
        import subprocess

        try:
            subprocess.run(["pkexec", calamares_bin], check=False)
        except Exception as e:
            console.print(f"[bold red]Failed to launch installer:[/bold red] {e}")
    elif not has_display:
        console.print(
            "\n[yellow][!] No graphical desktop display server found ($DISPLAY missing).[/yellow]\n"
            "To install Secura in a graphical session, boot into the XFCE live desktop and click 'Install Secura OS'.\n"
            "For automated server installations, use Debian preseed / live-installer."
        )
    elif not calamares_bin:
        console.print(
            "\n[yellow][!] Calamares installer package is not installed on this system.[/yellow]\n"
            "On Debian live systems, install with: sudo apt-get install calamares"
        )


if __name__ == "__main__":
    app()
