"""Tool catalog manager and metadata repository."""

import shutil
from pathlib import Path

import yaml

from secura.tools.schema import RiskLevel, ToolCategory, ToolDefinition


class ToolCatalog:
    """Loads, validates, and queries cybersecurity tool metadata."""

    def __init__(self, custom_catalog_dir: Path | None = None):
        self.default_catalog_file = Path(__file__).parent / "default_catalog.yaml"
        self.custom_catalog_dir = custom_catalog_dir or (
            Path.home() / ".config" / "secura" / "catalog"
        )
        self._tools: list[ToolDefinition] = []
        self.reload()

    def reload(self) -> None:
        """Load tools from built-in YAML and custom user definition files."""
        loaded: list[ToolDefinition] = []

        # 1. Load built-in default catalog
        if self.default_catalog_file.exists():
            try:
                with open(self.default_catalog_file, encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                raw_tools = data.get("tools", [])
                for t in raw_tools:
                    loaded.append(ToolDefinition.model_validate(t))
            except Exception:
                pass

        # 2. Load custom user catalogs if present
        if self.custom_catalog_dir.exists():
            for p in self.custom_catalog_dir.glob("*.yaml"):
                try:
                    with open(p, encoding="utf-8") as f:
                        data = yaml.safe_load(f) or {}
                    raw_tools = data.get("tools", [])
                    for t in raw_tools:
                        tool = ToolDefinition.model_validate(t)
                        # Replace default tool if custom definition overrides name
                        loaded = [item for item in loaded if item.name != tool.name]
                        loaded.append(tool)
                except Exception:
                    continue

        self._tools = loaded

    def list_tools(
        self,
        category: ToolCategory | None = None,
        risk_level: RiskLevel | None = None,
        enabled_only: bool = False,
    ) -> list[ToolDefinition]:
        """Query tool list with optional filtering."""
        results = self._tools
        if category:
            results = [t for t in results if t.category == category]
        if risk_level:
            results = [t for t in results if t.risk_level == risk_level]
        if enabled_only:
            results = [t for t in results if t.enabled_by_default]
        return results

    def get_tool(self, name: str) -> ToolDefinition | None:
        """Fetch tool definition by unique name."""
        return next((t for t in self._tools if t.name.lower() == name.lower()), None)

    @staticmethod
    def is_installed(tool: ToolDefinition) -> bool:
        """Check if the tool's underlying binary exists on system PATH."""
        return shutil.which(tool.binary) is not None
