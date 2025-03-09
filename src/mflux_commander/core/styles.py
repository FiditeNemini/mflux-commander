"""Style management for MFlux Commander."""

import json
import os
from pathlib import Path
from typing import Dict, Optional, List

from ..core.config import config

class StyleManager:
    """Manages saving and loading of styles."""
    
    def __init__(self):
        self.styles_dir = Path(config.styles_dir)
        self.styles_dir.mkdir(parents=True, exist_ok=True)
        
    def save_style(self, name: str, description: str) -> None:
        """Save a new style."""
        style_file = self.styles_dir / f"{name}.json"
        with open(style_file, 'w') as f:
            json.dump({
                "name": name,
                "description": description
            }, f, indent=2)
            
    def get_style(self, name: str) -> Optional[str]:
        """Get style description by name."""
        style_file = self.styles_dir / f"{name}.json"
        if style_file.exists():
            with open(style_file) as f:
                data = json.load(f)
                return data.get("description")
        return None
        
    def list_styles(self) -> List[Dict[str, str]]:
        """List all available styles."""
        styles = []
        for style_file in self.styles_dir.glob("*.json"):
            with open(style_file) as f:
                try:
                    style_data = json.load(f)
                    styles.append({
                        "name": style_data["name"],
                        "description": style_data["description"]
                    })
                except (json.JSONDecodeError, KeyError):
                    continue
        return sorted(styles, key=lambda x: x["name"])
        
    def delete_style(self, name: str) -> bool:
        """Delete a style by name."""
        style_file = self.styles_dir / f"{name}.json"
        if style_file.exists():
            style_file.unlink()
            return True
        return False 