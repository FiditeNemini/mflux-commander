"""Tests for the configuration module."""

import pytest
from mflux_commander.core.config import Resolution, MFluxConfig

def test_resolution_from_string():
    """Test creating Resolution from string."""
    res = Resolution.from_string("1024x768")
    assert res.width == 1024
    assert res.height == 768
    
def test_resolution_str():
    """Test Resolution string representation."""
    res = Resolution(width=800, height=600)
    assert str(res) == "800x600"
    
def test_resolution_invalid_string():
    """Test handling invalid resolution string."""
    with pytest.raises(ValueError):
        Resolution.from_string("invalid")
        
def test_config_default_resolutions():
    """Test default resolution configurations."""
    config = MFluxConfig()
    
    # Test default resolution
    default = config.get_resolution('default')
    assert default.width == 1024
    assert default.height == 1024
    
    # Test landscape resolution
    landscape = config.get_resolution('landscape')
    assert landscape.width == 1024
    assert landscape.height == 576
    
    # Test portrait resolution
    portrait = config.get_resolution('portrait')
    assert portrait.width == 768
    assert portrait.height == 1024
    
def test_config_get_default_steps():
    """Test getting default steps for models."""
    config = MFluxConfig()
    
    # Test schnell model
    assert config.get_default_steps('schnell') == 1
    
    # Test dev model
    assert config.get_default_steps('dev') == 5
    
    # Test unknown model (should return default model's steps)
    assert config.get_default_steps('unknown') == config.get_default_steps(config.DEFAULT_MODEL)
    
def test_config_styles_dir():
    """Test styles directory initialization."""
    config = MFluxConfig()
    assert config.styles_dir.exists()
    assert config.styles_dir.is_dir() 