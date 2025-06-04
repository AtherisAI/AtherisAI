import json
import yaml
from typing import Dict, Any
import os

class ConfigLoader:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        print(f"[ConfigLoader] Config directory set to '{self.config_dir}'")

    def load_json(self, filename: str) -> Dict[str, Any]:
        path = os.path.join(self.config_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"[ConfigLoader] File not found: {path}")
        with open(path, "r") as f:
            data = json.load(f)
            print(f"[ConfigLoader] Loaded JSON config: {filename}")
            return data

    def load_yaml(self, filename: str) -> Dict[str, Any]:
        path = os.path.join(self.config_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"[ConfigLoader] File not found: {path}")
        with open(path, "r") as f:
            data = yaml.safe_load(f)
            print(f"[ConfigLoader] Loaded YAML config: {filename}")
            return data

    def merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        merged = base.copy()
        merged.update(override)
        print("[ConfigLoader] Merged base and override configs")
        return merged


# Example usage
if __name__ == "__main__":
    config_loader = ConfigLoader()

    try:
        base_config = config_loader.load_json("default_config.json")
    except FileNotFoundError:
        base_config = {"agents_enabled": True, "poll_interval": 10}

    override_config = {
        "poll_interval": 5,
        "log_level": "debug"
    }

    final_config = config_loader.merge_configs(base_config, override_config)
    print("[ConfigLoader] Final config:", final_config)
