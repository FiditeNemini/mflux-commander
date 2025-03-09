"""Test configuration and fixtures for MFlux Commander."""

import pytest
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def mock_session_dir(temp_dir):
    """Create a mock session directory with sample data."""
    session_dir = temp_dir / "mflux_output_20240306_123456"
    session_dir.mkdir(parents=True)
    
    # Create run directories
    for i in range(1, 3):
        run_dir = session_dir / f"run_{i}"
        run_dir.mkdir()
        
        # Add metadata
        metadata = {
            "prompt": f"Test prompt {i}",
            "model": "schnell",
            "steps": 1,
            "seed": 12345,
            "resolution": "1024x1024"
        }
        with open(run_dir / "metadata.json", "w") as f:
            import json
            json.dump(metadata, f)
            
        # Create dummy image
        (run_dir / "image.png").touch()
        
    return session_dir

@pytest.fixture
def mock_styles_dir(temp_dir):
    """Create a mock styles directory with sample styles."""
    styles_dir = temp_dir / ".mflux_commander" / "styles"
    styles_dir.mkdir(parents=True)
    
    styles = {
        "ghibli": "in the style of Studio Ghibli",
        "cyberpunk": "cyberpunk aesthetic with neon colors"
    }
    
    for name, desc in styles.items():
        with open(styles_dir / f"{name}.json", "w") as f:
            import json
            json.dump({"name": name, "description": desc}, f)
            
    return styles_dir 