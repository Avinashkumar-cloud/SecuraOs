"""Tests for security assessment report data models and generation."""

from pathlib import Path

from secura.reports.generator import ReportGenerator
from secura.reports.models import AssessmentReport, Finding, SeverityLevel


def test_report_generation_markdown_and_html(temp_dir: Path):
    report = AssessmentReport(
        title="Internal Lab Assessment",
        assessor="Secura Trainee",
        scope_summary=["192.168.1.0/24"],
        findings=[
            Finding(
                title="Unencrypted FTP Service Detected",
                severity=SeverityLevel.MEDIUM,
                description="The FTP service transmits credentials in cleartext.",
                affected_target="192.168.1.20:21",
                evidence="USER anonymous\nPASS secret_ftp_pass\n230 Login successful.",
                recommendation="Disable plain FTP and transition to SFTP (SSH File Transfer Protocol).",
            )
        ],
    )

    gen = ReportGenerator(output_dir=temp_dir)
    md_content = gen.generate_markdown(report)
    html_content = gen.generate_html(report)

    # 1. Verify markdown contents
    assert "# Internal Lab Assessment" in md_content
    assert "Unencrypted FTP Service Detected" in md_content
    assert "MEDIUM" in md_content
    assert "192.168.1.0/24" in md_content

    # 2. Verify redaction occurred in evidence
    assert "secret_ftp_pass" not in md_content
    assert "[REDACTED_SECRET]" in md_content
    assert "secret_ftp_pass" not in html_content
    assert "[REDACTED_SECRET]" in html_content

    # 3. Verify HTML structure
    assert "<!DOCTYPE html>" in html_content
    assert "Internal Lab Assessment" in html_content
    assert "badge" in html_content

    # 4. Verify file saving
    md_file, html_file = gen.save_report(report)
    assert md_file.exists()
    assert html_file.exists()
