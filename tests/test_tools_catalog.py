"""Tests for tool catalog schema, filtering, and default catalog integrity."""

from secura.tools.catalog import ToolCatalog
from secura.tools.schema import RiskLevel, ToolCategory


def test_default_catalog_loads_successfully():
    catalog = ToolCatalog()
    tools = catalog.list_tools()
    assert len(tools) >= 6

    names = [t.name for t in tools]
    assert "nmap" in names
    assert "wireshark" in names
    assert "tshark" in names
    assert "bandit" in names
    assert "exiftool" in names
    assert "lynis" in names


def test_catalog_query_by_category():
    catalog = ToolCatalog()
    net_tools = catalog.list_tools(category=ToolCategory.NETWORK_SECURITY)
    assert len(net_tools) >= 3
    for t in net_tools:
        assert t.category == ToolCategory.NETWORK_SECURITY


def test_catalog_query_by_risk():
    catalog = ToolCatalog()
    high_risk = catalog.list_tools(risk_level=RiskLevel.HIGH)
    assert len(high_risk) >= 1
    assert any(t.name == "nikto" for t in high_risk)


def test_no_destructive_tools_in_default_catalog():
    catalog = ToolCatalog()
    forbidden_terms = [
        "exploit",
        "payload",
        "ransomware",
        "malware",
        "botnet",
        "c2",
        "persistence",
        "stealth",
        "meterpreter",
    ]
    for t in catalog.list_tools():
        combined = f"{t.name} {t.description} {t.purpose}".lower()
        for term in forbidden_terms:
            assert f" {term} " not in f" {combined} ", (
                f"Found forbidden destructive term '{term}' in tool {t.name}"
            )
