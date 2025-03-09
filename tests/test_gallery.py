"""Tests for the gallery generation module."""

import pytest
from pathlib import Path
import json
import re
from datetime import datetime
from mflux_commander.utils.gallery import GalleryGenerator

def test_gallery_generator_init(mock_session_dir):
    """Test GalleryGenerator initialization."""
    generator = GalleryGenerator(mock_session_dir)
    assert generator.session_dir == mock_session_dir
    
def test_load_metadata(mock_session_dir):
    """Test loading metadata from run directory."""
    generator = GalleryGenerator(mock_session_dir)
    run_dir = mock_session_dir / "run_1"
    
    metadata = generator._load_metadata(run_dir)
    assert metadata["prompt"] == "Test prompt 1"
    assert metadata["model"] == "schnell"
    assert metadata["steps"] == 1
    assert metadata["seed"] == 12345
    assert metadata["resolution"] == "1024x1024"
    
def test_find_image_files(mock_session_dir):
    """Test finding image files in run directory."""
    generator = GalleryGenerator(mock_session_dir)
    run_dir = mock_session_dir / "run_1"
    
    images = generator._find_image_files(run_dir)
    assert len(images) == 1
    assert images[0].name == "image.png"
    
def test_generate_run_gallery(mock_session_dir):
    """Test generating gallery for a single run."""
    generator = GalleryGenerator(mock_session_dir)
    run_dir = mock_session_dir / "run_1"
    
    gallery_file = generator.generate_run_gallery(run_dir)
    assert gallery_file.exists()
    
    html_content = gallery_file.read_text()
    
    # Check basic HTML structure
    assert "<!DOCTYPE html>" in html_content
    assert "<title>Run Results - run_1</title>" in html_content
    
    # Check metadata inclusion
    assert "Test prompt 1" in html_content
    assert "schnell" in html_content
    assert "12345" in html_content
    assert "1024x1024" in html_content
    
    # Check image inclusion
    assert 'src="image.png"' in html_content
    
    # Check timestamp
    assert re.search(r"Generated: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", html_content)
    
def test_generate_session_gallery(mock_session_dir):
    """Test generating gallery for entire session."""
    generator = GalleryGenerator(mock_session_dir)
    
    gallery_file = generator.generate_session_gallery()
    assert gallery_file.exists()
    
    html_content = gallery_file.read_text()
    
    # Check basic HTML structure
    assert "<!DOCTYPE html>" in html_content
    assert "<title>Session Gallery</title>" in html_content
    
    # Check both runs are included
    assert "Test prompt 1" in html_content
    assert "Test prompt 2" in html_content
    
    # Check image paths are relative to session directory
    assert 'src="run_1/image.png"' in html_content
    assert 'src="run_2/image.png"' in html_content
    
    # Check timestamp
    assert re.search(r"Generated: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", html_content)
    
def test_gallery_styling(mock_session_dir):
    """Test gallery CSS styling."""
    generator = GalleryGenerator(mock_session_dir)
    gallery_file = generator.generate_session_gallery()
    
    html_content = gallery_file.read_text()
    
    # Check for required CSS classes and properties
    assert ".gallery {" in html_content
    assert "grid-template-columns" in html_content
    assert ".image-card {" in html_content
    assert ".metadata {" in html_content
    assert ".timestamp {" in html_content
    
    # Check for responsive design elements
    assert "max-width: 1200px" in html_content
    assert "repeat(auto-fit, minmax(300px, 1fr))" in html_content
    
def test_empty_run_directory(mock_session_dir):
    """Test handling empty run directory."""
    generator = GalleryGenerator(mock_session_dir)
    empty_run = mock_session_dir / "empty_run"
    empty_run.mkdir()
    
    gallery_file = generator.generate_run_gallery(empty_run)
    assert gallery_file.exists()
    
    html_content = gallery_file.read_text()
    assert "Unknown" in html_content  # Default values for missing metadata
    assert '<div class="gallery">' in html_content  # Gallery div should still exist
    
def test_missing_metadata(mock_session_dir):
    """Test handling missing metadata."""
    generator = GalleryGenerator(mock_session_dir)
    run_dir = mock_session_dir / "run_no_metadata"
    run_dir.mkdir()
    (run_dir / "image.png").touch()
    
    gallery_file = generator.generate_run_gallery(run_dir)
    assert gallery_file.exists()
    
    html_content = gallery_file.read_text()
    assert "Unknown" in html_content  # Default values for missing metadata 

def test_metadata_display(mock_session_dir):
    """Test that metadata is correctly displayed in the gallery."""
    generator = GalleryGenerator(mock_session_dir)
    run_dir = mock_session_dir / "run_metadata_test"
    run_dir.mkdir()
    
    # Create a test image
    test_image = run_dir / "image_12345.png"
    test_image.touch()
    
    # Create metadata file
    metadata = {
        "prompt": "Test prompt",
        "model": "schnell",
        "steps": 5,
        "seed": 12345,
        "resolution": "1024x1024",
        "command": "mflux-generate ..."
    }
    metadata_file = run_dir / "metadata.json"
    with open(metadata_file, "w") as f:
        json.dump(metadata, f)
    
    # Generate gallery
    gallery_file = generator.generate_run_gallery(run_dir)
    html_content = gallery_file.read_text()
    
    # Verify metadata is displayed correctly
    assert "<strong>Prompt:</strong> Test prompt" in html_content
    assert "<strong>Model:</strong> schnell (5 steps)" in html_content
    assert "<strong>Seed:</strong> 12345" in html_content
    assert "<strong>Resolution:</strong> 1024x1024" in html_content 