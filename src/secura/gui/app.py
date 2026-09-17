"""Secura Center full multi-view graphical desktop application."""

import shutil
import subprocess
import webbrowser
from datetime import UTC, datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from secura import DISCLAIMER, __version__
from secura.core.sysinfo import get_system_info
from secura.labs.manager import LabManager
from secura.logging.audit import AuditLogger
from secura.reports.generator import ReportGenerator
from secura.reports.models import AssessmentReport
from secura.scope.manager import ScopeManager
from secura.scope.validator import TargetValidator
from secura.tools.catalog import ToolCatalog


class SecuraMainWindow(QMainWindow):
    """Main window for Secura Center cybersecurity management hub."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Secura Center — Cybersecurity OS Management Hub v{__version__}")
        self.resize(1100, 750)
        self.setMinimumSize(900, 600)

        self.scope_manager = ScopeManager()
        self.tool_catalog = ToolCatalog()
        self.lab_manager = LabManager()
        self.audit_logger = AuditLogger()
        self.report_generator = ReportGenerator()

        self._build_ui()
        self._refresh_all_views()

    def _build_ui(self):
        """Construct the multi-tab layout and status bar."""
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(10)

        # Header banner
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(
            "<span style='font-size: 20px; font-weight: bold; color: #00F0FF;'>SECURA OS</span> "
            "<span style='font-size: 16px; color: #94A3B8;'>| Cybersecurity Center</span>"
        )
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        nonroot_badge = QLabel("<b style='color: #10B981;'>[+] Non-Root User Session</b>")
        header_layout.addWidget(nonroot_badge)
        root_layout.addWidget(header_widget)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_dashboard_tab(), "Dashboard & Quick Launch")
        self.tabs.addTab(self._build_scope_tab(), "Scope Manager")
        self.tabs.addTab(self._build_tools_tab(), "Tool Catalog")
        self.tabs.addTab(self._build_labs_tab(), "Educational Labs")
        self.tabs.addTab(self._build_logs_tab(), "Audit Trail & Reports")
        root_layout.addWidget(self.tabs)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"{DISCLAIMER}")

    # =========================================================================
    # 1. Dashboard & Quick Launch Tab
    # =========================================================================
    def _build_dashboard_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        # Top System Info Card
        sys_group = QGroupBox("System Vitals & Hardware")
        sys_layout = QGridLayout(sys_group)

        self.cpu_label = QLabel("CPU: Detecting...")
        self.ram_label = QLabel("RAM: Detecting...")
        self.disk_label = QLabel("Storage: Detecting...")
        self.virt_label = QLabel("Virtualization: Detecting...")

        self.ram_bar = QProgressBar()
        self.ram_bar.setRange(0, 100)
        self.disk_bar = QProgressBar()
        self.disk_bar.setRange(0, 100)

        sys_layout.addWidget(self.cpu_label, 0, 0)
        sys_layout.addWidget(self.virt_label, 0, 1)
        sys_layout.addWidget(self.ram_label, 1, 0)
        sys_layout.addWidget(self.ram_bar, 1, 1)
        sys_layout.addWidget(self.disk_label, 2, 0)
        sys_layout.addWidget(self.disk_bar, 2, 1)

        layout.addWidget(sys_group)

        # Network Interfaces Group
        net_group = QGroupBox("Network Adapters & Connectivity")
        net_layout = QVBoxLayout(net_group)
        self.net_table = QTableWidget(0, 4)
        self.net_table.setHorizontalHeaderLabels(
            ["Interface", "IPv4 Address", "MAC Address", "Status"]
        )
        self.net_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        net_layout.addWidget(self.net_table)
        layout.addWidget(net_group)

        # Quick Launch Actions
        launch_group = QGroupBox("Everyday Applications & Media Quick Launch")
        launch_layout = QGridLayout(launch_group)

        btn_browser = QPushButton("Web Browser (Firefox)")
        btn_browser.setObjectName("primaryBtn")
        btn_browser.clicked.connect(lambda: self._launch_app("firefox-esr", "firefox", "chromium"))

        btn_vlc = QPushButton("Media Player (VLC / Movies)")
        btn_vlc.setObjectName("primaryBtn")
        btn_vlc.clicked.connect(lambda: self._launch_app("vlc", "mpv"))

        btn_terminal = QPushButton("Terminal (XFCE)")
        btn_terminal.clicked.connect(
            lambda: self._launch_app("xfce4-terminal", "x-terminal-emulator")
        )

        btn_net_settings = QPushButton("Network Settings (Wi-Fi/LAN)")
        btn_net_settings.clicked.connect(lambda: self._launch_app("nm-connection-editor"))

        btn_audio = QPushButton("Audio & Volume Mixer")
        btn_audio.clicked.connect(lambda: self._launch_app("pavucontrol"))

        btn_bluetooth = QPushButton("Bluetooth Manager")
        btn_bluetooth.clicked.connect(lambda: self._launch_app("blueman-manager"))

        btn_installer = QPushButton("Install Secura OS (Calamares)")
        btn_installer.clicked.connect(lambda: self._launch_app("secura-installer", "calamares"))

        launch_layout.addWidget(btn_browser, 0, 0)
        launch_layout.addWidget(btn_vlc, 0, 1)
        launch_layout.addWidget(btn_terminal, 0, 2)
        launch_layout.addWidget(btn_net_settings, 1, 0)
        launch_layout.addWidget(btn_audio, 1, 1)
        launch_layout.addWidget(btn_bluetooth, 1, 2)
        launch_layout.addWidget(btn_installer, 2, 0, 1, 3)

        layout.addWidget(launch_group)
        return tab

    def _launch_app(self, *binaries: str):
        """Attempt to launch an application binary."""
        for name in binaries:
            path = shutil.which(name)
            if path:
                try:
                    subprocess.Popen([path], start_new_session=True)
                    self.status_bar.showMessage(f"Launched application: {name}", 4000)
                    return
                except Exception as e:
                    QMessageBox.warning(self, "Launch Error", f"Failed to execute {name}: {e}")
                    return

        QMessageBox.information(
            self,
            "Application Not Available",
            f"Could not locate '{binaries[0]}' on this system.\n"
            f"Install it with: sudo apt-get install {binaries[0]}",
        )

    # =========================================================================
    # 2. Scope Manager Tab
    # =========================================================================
    def _build_scope_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        # Notice
        aup_label = QLabel(
            "<div style='background-color: #1E293B; padding: 10px; border-radius: 6px; border-left: 4px solid #00F0FF;'>"
            "<b>Mandatory Scope Validation:</b> Secura OS enforces target verification before executing tests. "
            "<i>Scope validation is a safety control, not legal authorization.</i>"
            "</div>"
        )
        aup_label.setTextFormat(Qt.RichText)
        layout.addWidget(aup_label)

        # Add Target Form
        form_group = QGroupBox("Register Assessment Target")
        form_layout = QGridLayout(form_group)

        self.scope_input = QLineEdit()
        self.scope_input.setPlaceholderText(
            "Enter IPv4, IPv6, CIDR subnet, or hostname (e.g., 192.168.1.100, 10.0.0.0/24)"
        )
        self.scope_input.textChanged.connect(self._on_scope_input_changed)

        self.scope_desc = QLineEdit()
        self.scope_desc.setPlaceholderText("Target description / assessment reference (optional)")

        self.scope_hours = QComboBox()
        self.scope_hours.addItems(["8 Hours", "24 Hours (Default)", "72 Hours", "7 Days"])
        self.scope_hours.setCurrentIndex(1)

        btn_add_scope = QPushButton("Add Target")
        btn_add_scope.setObjectName("primaryBtn")
        btn_add_scope.clicked.connect(self._add_scope_target)

        self.scope_feedback = QLabel("")

        form_layout.addWidget(QLabel("Target / Host:"), 0, 0)
        form_layout.addWidget(self.scope_input, 0, 1)
        form_layout.addWidget(QLabel("Duration:"), 0, 2)
        form_layout.addWidget(self.scope_hours, 0, 3)
        form_layout.addWidget(QLabel("Description:"), 1, 0)
        form_layout.addWidget(self.scope_desc, 1, 1)
        form_layout.addWidget(btn_add_scope, 1, 3)
        form_layout.addWidget(self.scope_feedback, 2, 0, 1, 4)

        layout.addWidget(form_group)

        # Table of Active Targets
        table_group = QGroupBox("Authorized Scopes")
        table_layout = QVBoxLayout(table_group)

        self.scope_table = QTableWidget(0, 5)
        self.scope_table.setHorizontalHeaderLabels(
            ["Target", "Type", "Scope Class", "Expires", "Description"]
        )
        self.scope_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table_layout.addWidget(self.scope_table)

        btn_bar = QHBoxLayout()
        btn_delete_scope = QPushButton("Remove Selected Target")
        btn_delete_scope.setObjectName("dangerBtn")
        btn_delete_scope.clicked.connect(self._delete_scope_target)

        btn_refresh_scope = QPushButton("Refresh")
        btn_refresh_scope.clicked.connect(self._refresh_scope_table)

        btn_bar.addWidget(btn_delete_scope)
        btn_bar.addStretch()
        btn_bar.addWidget(btn_refresh_scope)
        table_layout.addLayout(btn_bar)

        layout.addWidget(table_group)
        return tab

    def _on_scope_input_changed(self, text: str):
        raw = text.strip()
        if not raw:
            self.scope_feedback.setText("")
            return

        validator = TargetValidator()
        result = validator.validate(raw)
        if not result.is_valid:
            self.scope_feedback.setText(
                f"<span style='color: #EF4444;'>[!] Invalid Target: {result.error_message}</span>"
            )
            return

        if result.is_private:
            self.scope_feedback.setText(
                f"<span style='color: #10B981;'>[+] Valid Private / Local Target ({result.target_type.value})</span>"
            )
        else:
            self.scope_feedback.setText(
                f"<span style='color: #F59E0B;'>[!] WARNING: Public Target ({result.target_type.value}). "
                "Explicit written permission is legally required.</span>"
            )

    def _add_scope_target(self):
        raw = self.scope_input.text().strip()
        if not raw:
            QMessageBox.warning(self, "Input Error", "Please enter a target address or subnet.")
            return

        validator = TargetValidator()
        validation = validator.validate(raw)
        if not validation.is_valid:
            QMessageBox.critical(
                self, "Invalid Target", validation.error_message or "Target syntax is invalid."
            )
            return

        hours_map = {0: 8, 1: 24, 2: 72, 3: 168}
        hours = hours_map.get(self.scope_hours.currentIndex(), 24)
        desc = self.scope_desc.text().strip() or None

        try:
            self.scope_manager.add_target(raw, description=desc, valid_hours=hours)
            self.scope_input.clear()
            self.scope_desc.clear()
            self.scope_feedback.setText(
                "<span style='color: #10B981;'>[+] Target successfully registered.</span>"
            )
            self._refresh_scope_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to register target: {e}")

    def _delete_scope_target(self):
        row = self.scope_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Selection", "Please select a target row to remove.")
            return

        target_item = self.scope_table.item(row, 0)
        if not target_item:
            return

        target_val = target_item.text()
        confirm = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Remove '{target_val}' from authorized scopes?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            self.scope_manager.remove_target(target_val)
            self._refresh_scope_table()

    def _refresh_scope_table(self):
        targets = self.scope_manager.list_targets()
        self.scope_table.setRowCount(len(targets))
        for row, t in enumerate(targets):
            self.scope_table.setItem(row, 0, QTableWidgetItem(t.target))
            self.scope_table.setItem(row, 1, QTableWidgetItem(t.target_type.value))

            scope_class = "Private / RFC1918" if t.is_private else "Public / External"
            class_item = QTableWidgetItem(scope_class)
            if not t.is_private:
                class_item.setForeground(QColor("#F59E0B"))
            else:
                class_item.setForeground(QColor("#10B981"))
            self.scope_table.setItem(row, 2, class_item)

            exp_str = t.expires_at.strftime("%Y-%m-%d %H:%M UTC") if t.expires_at else "Permanent"
            self.scope_table.setItem(row, 3, QTableWidgetItem(exp_str))
            self.scope_table.setItem(row, 4, QTableWidgetItem(t.description or "-"))

    # =========================================================================
    # 3. Tool Catalog Tab
    # =========================================================================
    def _build_tools_tab(self) -> QWidget:
        tab = QWidget()
        layout = QHBoxLayout(tab)

        # Left Column: Search & Tools Table
        left_box = QVBoxLayout()
        search_bar = QHBoxLayout()
        self.tool_search = QLineEdit()
        self.tool_search.setPlaceholderText("Search tools by name, command, or category...")
        self.tool_search.textChanged.connect(self._filter_tools)
        search_bar.addWidget(self.tool_search)
        left_box.addLayout(search_bar)

        self.tools_table = QTableWidget(0, 4)
        self.tools_table.setHorizontalHeaderLabels(
            ["Tool", "Category", "Risk Level", "Binary Status"]
        )
        self.tools_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tools_table.itemSelectionChanged.connect(self._on_tool_selected)
        left_box.addWidget(self.tools_table)
        layout.addLayout(left_box, 3)

        # Right Column: Tool Detail Card
        right_group = QGroupBox("Tool Overview & Safe Usage")
        right_layout = QVBoxLayout(right_group)

        self.tool_name_label = QLabel("<h3>Select a Tool</h3>")
        self.tool_desc_label = QLabel(
            "Select any tool from the catalog on the left to review its purpose, risk classification, and authorized commands."
        )
        self.tool_desc_label.setWordWrap(True)

        self.tool_cmd_view = QTextEdit()
        self.tool_cmd_view.setReadOnly(True)
        self.tool_cmd_view.setPlaceholderText("Safe usage command syntax...")

        right_layout.addWidget(self.tool_name_label)
        right_layout.addWidget(self.tool_desc_label)
        right_layout.addWidget(QLabel("<b>Verified Safe Usage Commands:</b>"))
        right_layout.addWidget(self.tool_cmd_view)

        layout.addWidget(right_group, 2)
        return tab

    def _filter_tools(self):
        query = self.tool_search.text().lower()
        tools = self.tool_catalog.list_tools()
        filtered = [
            t
            for t in tools
            if query in t.name.lower()
            or query in t.category.value.lower()
            or query in t.description.lower()
        ]
        self._populate_tools_table(filtered)

    def _populate_tools_table(self, tools):
        self.tools_table.setRowCount(len(tools))
        for row, t in enumerate(tools):
            self.tools_table.setItem(row, 0, QTableWidgetItem(t.name))
            self.tools_table.setItem(row, 1, QTableWidgetItem(t.category.value))

            risk_item = QTableWidgetItem(t.risk_level.value.upper())
            if t.risk_level.value == "low":
                risk_item.setForeground(QColor("#10B981"))
            elif t.risk_level.value == "medium":
                risk_item.setForeground(QColor("#F59E0B"))
            else:
                risk_item.setForeground(QColor("#EF4444"))
            self.tools_table.setItem(row, 2, risk_item)

            installed = bool(shutil.which(t.binary_name))
            inst_item = QTableWidgetItem("Installed" if installed else "Not Found")
            inst_item.setForeground(QColor("#10B981") if installed else QColor("#94A3B8"))
            self.tools_table.setItem(row, 3, inst_item)

    def _on_tool_selected(self):
        row = self.tools_table.currentRow()
        if row < 0:
            return
        name_item = self.tools_table.item(row, 0)
        if not name_item:
            return

        tool = self.tool_catalog.get_tool(name_item.text())
        if not tool:
            return

        self.tool_name_label.setText(f"<h3>{tool.name} ({tool.binary_name})</h3>")
        self.tool_desc_label.setText(
            f"<b>Category:</b> {tool.category.value.title()}<br>"
            f"<b>Risk Tier:</b> {tool.risk_level.value.upper()}<br><br>"
            f"{tool.description}"
        )

        cmds = "\n\n".join([f"# {c.description}\n{c.command}" for c in tool.safe_commands])
        self.tool_cmd_view.setPlainText(cmds or "# No preconfigured commands")

    # =========================================================================
    # 4. Educational Labs Tab
    # =========================================================================
    def _build_labs_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        info_label = QLabel(
            "<div style='background-color: #1E293B; padding: 10px; border-radius: 6px; border-left: 4px solid #10B981;'>"
            "<b>Containerized Educational Labs:</b> Secura provides local rootless Podman containers for safe, isolated training. "
            "All targets execute strictly inside local container network boundaries."
            "</div>"
        )
        info_label.setTextFormat(Qt.RichText)
        layout.addWidget(info_label)

        self.labs_table = QTableWidget(0, 4)
        self.labs_table.setHorizontalHeaderLabels(["Lab Name", "Category", "Difficulty", "Status"])
        self.labs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.labs_table)

        btn_bar = QHBoxLayout()
        btn_start_lab = QPushButton("Start Lab")
        btn_start_lab.setObjectName("primaryBtn")
        btn_start_lab.clicked.connect(self._start_selected_lab)

        btn_stop_lab = QPushButton("Stop Lab")
        btn_stop_lab.setObjectName("dangerBtn")
        btn_stop_lab.clicked.connect(self._stop_selected_lab)

        btn_bar.addWidget(btn_start_lab)
        btn_bar.addWidget(btn_stop_lab)
        btn_bar.addStretch()
        layout.addLayout(btn_bar)

        return tab

    def _start_selected_lab(self):
        row = self.labs_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Selection", "Please select a lab from the list.")
            return

        lab_id = self.labs_table.item(row, 0).data(Qt.UserRole)
        success = self.lab_manager.start_lab(lab_id)
        if success:
            QMessageBox.information(self, "Lab Started", f"Lab '{lab_id}' initiated successfully.")
        else:
            QMessageBox.warning(
                self, "Lab Notice", f"Container runtime (Podman) required to launch lab '{lab_id}'."
            )
        self._refresh_labs_table()

    def _stop_selected_lab(self):
        row = self.labs_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Selection", "Please select a lab from the list.")
            return

        lab_id = self.labs_table.item(row, 0).data(Qt.UserRole)
        self.lab_manager.stop_lab(lab_id)
        QMessageBox.information(self, "Lab Stopped", f"Lab '{lab_id}' stopped.")
        self._refresh_labs_table()

    def _refresh_labs_table(self):
        labs = self.lab_manager.list_labs()
        self.labs_table.setRowCount(len(labs))
        for row, lab in enumerate(labs):
            name_item = QTableWidgetItem(lab.name)
            name_item.setData(Qt.UserRole, lab.id)
            self.labs_table.setItem(row, 0, name_item)
            self.labs_table.setItem(row, 1, QTableWidgetItem(lab.category))
            self.labs_table.setItem(row, 2, QTableWidgetItem(lab.difficulty))

            status_item = QTableWidgetItem(lab.status.upper())
            status_item.setForeground(
                QColor("#10B981") if lab.status == "running" else QColor("#94A3B8")
            )
            self.labs_table.setItem(row, 3, status_item)

    # =========================================================================
    # 5. Audit Trail & Reports Tab
    # =========================================================================
    def _build_logs_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        # Redaction Shield Badge
        shield_label = QLabel(
            "<div style='background-color: #1E293B; padding: 8px; border-radius: 6px; color: #00F0FF;'>"
            "🛡️ <b>Automated Secret Redaction Active:</b> All commands, tokens, private keys, and passwords are automatically scrubbed from logs."
            "</div>"
        )
        shield_label.setTextFormat(Qt.RichText)
        layout.addWidget(shield_label)

        # Audit Logs Table
        self.logs_table = QTableWidget(0, 5)
        self.logs_table.setHorizontalHeaderLabels(
            ["Timestamp (UTC)", "Actor", "Action", "Target", "Status"]
        )
        self.logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.logs_table)

        # Action Bar
        action_bar = QHBoxLayout()
        btn_report = QPushButton("Generate HTML Assessment Report")
        btn_report.setObjectName("primaryBtn")
        btn_report.clicked.connect(self._generate_report)

        btn_refresh_logs = QPushButton("Refresh Logs")
        btn_refresh_logs.clicked.connect(self._refresh_logs_table)

        action_bar.addWidget(btn_report)
        action_bar.addStretch()
        action_bar.addWidget(btn_refresh_logs)
        layout.addLayout(action_bar)

        return tab

    def _generate_report(self):
        title = f"Secura Assessment — {datetime.now(UTC).strftime('%Y-%m-%d %H:%M')}"
        active_scopes = [t.target for t in self.scope_manager.list_targets(active_only=True)]
        report = AssessmentReport(
            title=title,
            assessor="Secura Center User",
            scope_targets=active_scopes,
            summary="Automated security evaluation report generated from Secura Center.",
        )
        _, html_file = self.report_generator.generate_both(report)
        confirm = QMessageBox.question(
            self,
            "Report Created",
            f"Assessment report generated successfully:\n{html_file}\n\nWould you like to open it in your web browser?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            webbrowser.open(f"file://{html_file.resolve().as_posix()}")

    def _refresh_logs_table(self):
        events = self.audit_logger.query(limit=50)
        self.logs_table.setRowCount(len(events))
        for row, evt in enumerate(events):
            self.logs_table.setItem(
                row, 0, QTableWidgetItem(evt.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
            )
            self.logs_table.setItem(row, 1, QTableWidgetItem(evt.actor))
            self.logs_table.setItem(row, 2, QTableWidgetItem(evt.action))
            self.logs_table.setItem(row, 3, QTableWidgetItem(evt.target or "-"))
            status_item = QTableWidgetItem(evt.status.upper())
            status_item.setForeground(
                QColor("#10B981") if evt.status == "success" else QColor("#EF4444")
            )
            self.logs_table.setItem(row, 4, status_item)

    # =========================================================================
    # Refresh All Views
    # =========================================================================
    def _refresh_all_views(self):
        """Fetch real system metrics and populate all tabs."""
        sysinfo = get_system_info()
        self.cpu_label.setText(f"<b>CPU:</b> {sysinfo.cpu_count} Cores ({sysinfo.architecture})")
        self.virt_label.setText(f"<b>Environment:</b> {sysinfo.hypervisor or 'Physical Hardware'}")

        used_ram = sysinfo.memory.total_mb - sysinfo.memory.available_mb
        ram_pct = (
            int((used_ram / sysinfo.memory.total_mb) * 100) if sysinfo.memory.total_mb > 0 else 0
        )
        self.ram_label.setText(
            f"<b>RAM:</b> {used_ram} MB / {sysinfo.memory.total_mb} MB ({ram_pct}%)"
        )
        self.ram_bar.setValue(ram_pct)

        disk_pct = int(sysinfo.disk.percent_used)
        self.disk_label.setText(
            f"<b>Storage:</b> {sysinfo.disk.free_gb:.1f} GB free of {sysinfo.disk.total_gb:.1f} GB ({disk_pct}% used)"
        )
        self.disk_bar.setValue(disk_pct)

        # Network adapters
        self.net_table.setRowCount(len(sysinfo.network_interfaces))
        for row, iface in enumerate(sysinfo.network_interfaces):
            self.net_table.setItem(row, 0, QTableWidgetItem(iface.name))
            self.net_table.setItem(
                row, 1, QTableWidgetItem(", ".join(iface.ip_addresses) or "No IPv4")
            )
            self.net_table.setItem(row, 2, QTableWidgetItem(iface.mac_address or "-"))
            status_item = QTableWidgetItem("UP" if iface.is_up else "DOWN")
            status_item.setForeground(QColor("#10B981") if iface.is_up else QColor("#94A3B8"))
            self.net_table.setItem(row, 3, status_item)

        self._refresh_scope_table()
        self._populate_tools_table(self.tool_catalog.list_tools())
        self._refresh_labs_table()
        self._refresh_logs_table()
