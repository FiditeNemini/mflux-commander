"""Configuration management for MFlux Commander."""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any

@dataclass
class Resolution:
    width: int
    height: int

    @classmethod
    def from_string(cls, resolution_str: str) -> 'Resolution':
        """Create Resolution from string like '1024x768'."""
        width, height = map(int, resolution_str.split('x'))
        return cls(width=width, height=height)

    def __str__(self) -> str:
        return f"{self.width}x{self.height}"

class MFluxConfig:
    """Configuration settings for MFlux Commander."""
    
    def __init__(self):
        # Base directory for output
        self.OUTPUT_BASE_DIR = os.getenv("MFLUX_OUTPUT_DIR", "mflux_output")
        
        # Session timeout in hours
        self.SESSION_TIMEOUT_HOURS = 4
        
        # Available models and their default settings
        self.AVAILABLE_MODELS = ["schnell", "dev"]
        self.DEFAULT_MODEL = "schnell"
        
        # Default image dimensions
        self.DEFAULT_WIDTH = 1024
        self.DEFAULT_HEIGHT = 1024
        
        # Resolution presets
        self.RESOLUTIONS = {
            'default': Resolution(1024, 1024),
            'landscape': Resolution(1024, 576),
            'portrait': Resolution(768, 1024),
            'landscape_sm': Resolution(512, 288),
            'portrait_sm': Resolution(384, 512),
            'square_sm': Resolution(512, 512),
            'landscape_lg': Resolution(1536, 864),
            'portrait_lg': Resolution(1152, 1536),
            'square_lg': Resolution(1536, 1536),
            'landscape_xl': Resolution(2048, 1152),
            'portrait_xl': Resolution(1536, 2048),
            'square_xl': Resolution(2048, 2048),
        }
        
        # Default generation parameters
        self.DEFAULT_STEPS = {
            "schnell": 1,
            "dev": 5
        }
        self.DEFAULT_ITERATIONS = 3
        
        self.styles_dir = Path(os.path.expanduser('~/.mflux_commander/styles'))
        os.makedirs(self.styles_dir, exist_ok=True)

    def get_resolution(self, format_name: str) -> Resolution:
        """Get resolution by format name."""
        return self.RESOLUTIONS.get(format_name, self.RESOLUTIONS['default'])

    def get_default_steps(self, model: str) -> int:
        """Get default steps for a model."""
        return self.DEFAULT_STEPS.get(model, 1)

config = MFluxConfig() 