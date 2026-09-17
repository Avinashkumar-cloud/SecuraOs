"""Report generator producing Markdown and HTML assessment documents."""

import html
from pathlib import Path

from secura.logging.redactor import Redactor
from secura.reports.models import AssessmentReport, SeverityLevel


class ReportGenerator:
    """Renders sanitized Markdown and standalone HTML security reports."""

    def __init__(self, output_dir: Path | None = None):
        self.output_dir = output_dir or (Path.home() / "SecuraReports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_markdown(self, report: AssessmentReport) -> str:
        """Render report into GitHub-flavored Markdown."""
        lines = [
            f"# {Redactor.redact_text(report.title)}",
            "",
            f"**Report ID:** `{report.id}`  ",
            f"**Assessor:** {Redactor.redact_text(report.assessor)}  ",
            f"**Date:** {report.created_at}  ",
            "",
            "> **Safety Disclaimer:**",
            f"> {report.disclaimer}",
            "",
            "---",
            "",
            "## 1. Assessment Scope",
            "",
        ]

        if report.scope_summary:
            for s in report.scope_summary:
                lines.append(f"- `{Redactor.redact_text(s)}`")
        else:
            lines.append("*No targets recorded in scope.*")

        lines.extend(
            [
                "",
                "## 2. Methodology",
                "",
                Redactor.redact_text(report.methodology),
                "",
                "---",
                "",
                "## 3. Findings Summary",
                "",
            ]
        )

        if not report.findings:
            lines.append("*No security findings recorded.*")
        else:
            lines.append("| ID | Severity | Title | Affected Target |")
            lines.append("| :--- | :--- | :--- | :--- |")
            for f in report.findings:
                sev_tag = f.severity.value.upper()
                lines.append(
                    f"| `{f.id}` | **{sev_tag}** | {Redactor.redact_text(f.title)} | `{Redactor.redact_text(f.affected_target)}` |"
                )

            lines.extend(["", "---", "", "## 4. Detailed Findings", ""])

            for idx, f in enumerate(report.findings, start=1):
                lines.extend(
                    [
                        f"### {idx}. [{f.severity.value.upper()}] {Redactor.redact_text(f.title)}",
                        f"- **Finding ID:** `{f.id}`",
                        f"- **Target:** `{Redactor.redact_text(f.affected_target)}`",
                        "",
                        "#### Description",
                        Redactor.redact_text(f.description),
                        "",
                    ]
                )

                if f.evidence:
                    lines.extend(
                        [
                            "#### Evidence & Technical Artifacts",
                            "```text",
                            Redactor.redact_text(f.evidence.strip()),
                            "```",
                            "",
                        ]
                    )

                if f.recommendation:
                    lines.extend(
                        [
                            "#### Remediation Recommendation",
                            Redactor.redact_text(f.recommendation),
                            "",
                        ]
                    )

        return "\n".join(lines)

    def generate_html(self, report: AssessmentReport) -> str:
        """Render report into a modern, responsive, standalone HTML document."""
        sev_colors = {
            SeverityLevel.CRITICAL: "#DC2626",
            SeverityLevel.HIGH: "#EA580C",
            SeverityLevel.MEDIUM: "#D97706",
            SeverityLevel.LOW: "#2563EB",
            SeverityLevel.INFO: "#4B5563",
        }

        # Format findings list
        findings_html = ""
        for f in report.findings:
            color = sev_colors.get(f.severity, "#4B5563")
            evidence_block = ""
            if f.evidence:
                evidence_block = f"""
                <div class="evidence">
                    <strong>Evidence:</strong>
                    <pre><code>{html.escape(Redactor.redact_text(f.evidence))}</code></pre>
                </div>
                """

            findings_html += f"""
            <div class="finding-card">
                <div class="finding-header">
                    <span class="badge" style="background-color: {color};">{html.escape(f.severity.value.upper())}</span>
                    <span class="finding-title">{html.escape(Redactor.redact_text(f.title))}</span>
                    <span class="finding-id">{html.escape(f.id)}</span>
                </div>
                <p><strong>Target:</strong> <code>{html.escape(Redactor.redact_text(f.affected_target))}</code></p>
                <p>{html.escape(Redactor.redact_text(f.description))}</p>
                {evidence_block}
                <div class="recommendation">
                    <strong>Recommendation:</strong> {html.escape(Redactor.redact_text(f.recommendation))}
                </div>
            </div>
            """

        scope_items = "".join(
            f"<li><code>{html.escape(Redactor.redact_text(s))}</code></li>"
            for s in report.scope_summary
        )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(report.title)} - Secura Report</title>
    <style>
        :root {{
            --bg: #0F172A;
            --surface: #1E293B;
            --border: #334155;
            --text: #F8FAFC;
            --text-muted: #94A3B8;
            --accent: #38BDF8;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 40px 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        .header {{
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 24px;
            border-radius: 8px;
            margin-bottom: 24px;
        }}
        h1 {{ margin-top: 0; color: var(--accent); }}
        .meta {{ color: var(--text-muted); font-size: 0.95rem; margin-bottom: 12px; }}
        .disclaimer {{
            background: #1e1b4b;
            border-left: 4px solid #6366f1;
            padding: 12px 16px;
            font-size: 0.9rem;
            color: #c7d2fe;
            margin-top: 16px;
        }}
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 24px;
            border-radius: 8px;
            margin-bottom: 24px;
        }}
        .badge {{
            color: #fff;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .finding-card {{
            background: #111827;
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 18px;
            margin-bottom: 16px;
        }}
        .finding-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }}
        .finding-title {{ font-size: 1.15rem; font-weight: 600; flex-grow: 1; }}
        .finding-id {{ color: var(--text-muted); font-family: monospace; font-size: 0.9rem; }}
        pre {{
            background: #030712;
            padding: 12px;
            border-radius: 4px;
            overflow-x: auto;
            border: 1px solid #1F2937;
        }}
        code {{ font-family: "SFMono-Regular", Consolas, Menlo, monospace; font-size: 0.9rem; }}
        .recommendation {{
            background: #064E3B;
            border-left: 4px solid #10B981;
            padding: 10px 14px;
            border-radius: 4px;
            margin-top: 12px;
            font-size: 0.95rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{html.escape(Redactor.redact_text(report.title))}</h1>
            <div class="meta">
                <strong>Assessor:</strong> {html.escape(Redactor.redact_text(report.assessor))} |
                <strong>Report ID:</strong> {html.escape(report.id)} |
                <strong>Date:</strong> {html.escape(report.created_at)}
            </div>
            <div class="disclaimer">
                <strong>Safety Notice:</strong> {html.escape(report.disclaimer)}
            </div>
        </div>

        <div class="card">
            <h2>Authorized Scope</h2>
            <ul>{scope_items or "<li>No specific targets recorded.</li>"}</ul>
        </div>

        <div class="card">
            <h2>Assessment Findings ({len(report.findings)})</h2>
            {findings_html or "<p>No security findings recorded.</p>"}
        </div>
    </div>
</body>
</html>
"""

    def save_report(
        self, report: AssessmentReport, base_filename: str | None = None
    ) -> tuple[Path, Path]:
        """Save report to disk in both Markdown and HTML formats."""
        name = base_filename or f"{report.id.lower()}_{report.title.lower().replace(' ', '_')[:30]}"
        md_path = self.output_dir / f"{name}.md"
        html_path = self.output_dir / f"{name}.html"

        md_content = self.generate_markdown(report)
        html_content = self.generate_html(report)

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return md_path, html_path
