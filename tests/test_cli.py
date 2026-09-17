"""Tests for Secura CLI commands and formatting."""

import json

from typer.testing import CliRunner

from secura.cli.main import app

runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "Secura OS Core CLI" in result.stdout
    assert "0.1.0-alpha" in result.stdout


def test_cli_version_json():
    result = runner.invoke(app, ["--version", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["version"] == "0.1.0-alpha"
    assert "disclaimer" in data


def test_cli_status():
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "Secura OS Core Platform" in result.stdout
    assert "Operating System" in result.stdout


def test_cli_status_json():
    result = runner.invoke(app, ["status", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert "system" in data
    assert "active_scopes_count" in data
    assert "total_tools_count" in data


def test_cli_tools_list():
    result = runner.invoke(app, ["tools", "list"])
    assert result.exit_code == 0
    assert "nmap" in result.stdout.lower()
    assert "wireshark" in result.stdout.lower()


def test_cli_tools_list_json():
    result = runner.invoke(app, ["tools", "list", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert isinstance(data, list)
    assert any(t["name"] == "nmap" for t in data)


def test_cli_scope_crud_flow():
    # 1. Add target
    add_res = runner.invoke(app, ["scope", "add", "192.168.1.75", "--description", "Test Target"])
    assert add_res.exit_code == 0
    assert "Successfully added target" in add_res.stdout

    # 2. List target
    list_res = runner.invoke(app, ["scope", "list"], env={"COLUMNS": "160"})
    assert list_res.exit_code == 0
    assert "192.168.1.75" in list_res.stdout

    # 3. List target JSON
    list_json = runner.invoke(app, ["scope", "list", "--json"])
    assert list_json.exit_code == 0
    data = json.loads(list_json.stdout)
    assert any(t["target"] == "192.168.1.75" for t in data)

    # 4. Remove target
    del_res = runner.invoke(app, ["scope", "remove", "192.168.1.75"])
    assert del_res.exit_code == 0
    assert "Removed target" in del_res.stdout


def test_cli_scope_add_invalid():
    res = runner.invoke(app, ["scope", "add", "not_a_valid_ip_or_domain_###"])
    assert res.exit_code != 0
    assert "Error" in res.stdout


def test_cli_logs():
    res = runner.invoke(app, ["logs", "--limit", "10"])
    assert res.exit_code == 0


def test_cli_report_new():
    res = runner.invoke(
        app, ["report", "new", "Automated CLI Test Report", "--assessor", "Test Bot"]
    )
    assert res.exit_code == 0
    assert "Created Assessment Report" in res.stdout
