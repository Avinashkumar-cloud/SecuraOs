"""Configuration manager for loading, persisting, and initializing Secura configs."""

import os
from pathlib import Path

import yaml

from secura.config.schema import SecuraConfig


class ConfigManager:
    """Manages Secura system configuration loading, serialization, and directory initialization."""

    def __init__(self, config_path: Path | None = None):
        if config_path:
            self.config_file = Path(config_path)
        elif "SECURA_CONFIG_PATH" in os.environ:
            self.config_file = Path(os.environ["SECURA_CONFIG_PATH"])
        else:
            base_config = Path.home() / ".config" / "secura"
            self.config_file = base_config / "config.yaml"

        self._config: SecuraConfig | None = None

    def get_config(self) -> SecuraConfig:
        """Retrieve current configuration or load from disk/defaults."""
        if self._config is None:
            self._config = self.load()
        return self._config

    def load(self) -> SecuraConfig:
        """Load configuration from YAML file or initialize with defaults if not present."""
        if not self.config_file.exists():
            cfg = SecuraConfig()
            self.save(cfg)
            return cfg

        try:
            with open(self.config_file, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            self._config = SecuraConfig.model_validate(data)
            return self._config
        except Exception:
            # Fallback to pristine defaults if corrupt
            self._config = SecuraConfig()
            return self._config

    def save(self, config: SecuraConfig | None = None) -> None:
        """Persist configuration to disk."""
        if config is not None:
            self._config = config
        elif self._config is None:
            self._config = SecuraConfig()

        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        data = self._config.model_dump(mode="json")

        with open(self.config_file, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)

    def initialize_directories(self) -> None:
        """Ensure all runtime directories exist with appropriate permissions."""
        cfg = self.get_config()
        for path in [
            cfg.paths.config_dir,
            cfg.paths.data_dir,
            cfg.paths.logs_dir,
            cfg.paths.reports_dir,
            cfg.paths.labs_dir,
            cfg.paths.catalog_dir,
        ]:
            Path(path).mkdir(parents=True, exist_ok=True)
