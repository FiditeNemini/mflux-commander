"""Tests for the style management module."""

import pytest
from pathlib import Path
import json
from mflux_commander.core.styles import StyleManager

def test_style_manager_init(temp_dir, monkeypatch):
    """Test StyleManager initialization."""
    # Mock the styles directory
    monkeypatch.setattr("mflux_commander.core.config.config.styles_dir", 
                       str(temp_dir / ".mflux_commander" / "styles"))
    
    manager = StyleManager()
    assert manager.styles_dir.exists()
    assert manager.styles_dir.is_dir()
    
def test_save_style(temp_dir, monkeypatch):
    """Test saving a new style."""
    # Mock the styles directory
    monkeypatch.setattr("mflux_commander.core.config.config.styles_dir", 
                       str(temp_dir / ".mflux_commander" / "styles"))
    
    manager = StyleManager()
    
    # Save a new style
    manager.save_style("test_style", "Test style description")
    
    # Verify style file
    style_file = manager.styles_dir / "test_style.json"
    assert style_file.exists()
    
    with open(style_file) as f:
        data = json.load(f)
        assert data["name"] == "test_style"
        assert data["description"] == "Test style description"
        
def test_get_style(mock_styles_dir, monkeypatch):
    """Test getting style description."""
    # Mock the styles directory
    monkeypatch.setattr("mflux_commander.core.config.config.styles_dir", 
                       str(mock_styles_dir))
    
    manager = StyleManager()
    
    # Get existing style
    desc = manager.get_style("ghibli")
    assert desc == "in the style of Studio Ghibli"
    
    # Get non-existent style
    desc = manager.get_style("nonexistent")
    assert desc is None
    
def test_list_styles(mock_styles_dir, monkeypatch):
    """Test listing available styles."""
    # Mock the styles directory
    monkeypatch.setattr("mflux_commander.core.config.config.styles_dir", 
                       str(mock_styles_dir))
    
    manager = StyleManager()
    styles = manager.list_styles()
    
    assert len(styles) == 2
    assert styles[0]["name"] == "cyberpunk"
    assert styles[0]["description"] == "cyberpunk aesthetic with neon colors"
    assert styles[1]["name"] == "ghibli"
    assert styles[1]["description"] == "in the style of Studio Ghibli"
    
def test_delete_style(mock_styles_dir, monkeypatch):
    """Test deleting a style."""
    # Mock the styles directory
    monkeypatch.setattr("mflux_commander.core.config.config.styles_dir", 
                       str(mock_styles_dir))
    
    manager = StyleManager()
    
    # Delete existing style
    assert manager.delete_style("ghibli") is True
    assert not (manager.styles_dir / "ghibli.json").exists()
    
    # Try to delete non-existent style
    assert manager.delete_style("nonexistent") is False
    
def test_invalid_style_file(mock_styles_dir, monkeypatch):
    """Test handling invalid style files."""
    # Mock the styles directory
    monkeypatch.setattr("mflux_commander.core.config.config.styles_dir", 
                       str(mock_styles_dir))
    
    # Create invalid style file
    invalid_file = mock_styles_dir / "invalid.json"
    invalid_file.write_text("invalid json")
    
    manager = StyleManager()
    styles = manager.list_styles()
    
    # Invalid file should be skipped
    assert len(styles) == 2
    assert all(style["name"] != "invalid" for style in styles) 