"""Tests for the Generator class."""

import pytest
from pathlib import Path
import json
from unittest.mock import patch, MagicMock
from mflux_commander.core.generator import Generator
from mflux_commander.core.config import Resolution
from mflux_commander.core.session import Session

@pytest.fixture
def mock_session(tmp_path):
    """Create a mock session."""
    session = Session(force_new=True)
    session.current_session_dir = tmp_path / "mflux_output_20240306_123456"
    session.current_session_dir.mkdir(parents=True)
    return session

@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for testing."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        yield mock_run

def test_generator_init(mock_session):
    """Test Generator initialization."""
    # Test with default model
    gen = Generator(mock_session)
    assert gen.model == "schnell"
    
    # Test with custom model
    gen = Generator(mock_session, model="dev")
    assert gen.model == "dev"
    
    # Test with invalid model
    with pytest.raises(ValueError):
        Generator(mock_session, model="invalid")

def test_generate(tmp_path, mock_subprocess_run, mock_session):
    """Test single image generation."""
    gen = Generator(mock_session)
    
    run_dir = gen.generate(
        prompt="test prompt",
        iterations=1,
        seed=12345
    )
    
    assert run_dir.exists()
    assert mock_subprocess_run.called
    
    # Check command construction
    cmd = mock_subprocess_run.call_args[0][0]
    assert "--prompt" in cmd
    assert "test prompt" in cmd
    assert "--seed" in cmd
    assert "12345" in cmd

def test_generate_with_defaults(tmp_path, mock_subprocess_run, mock_session):
    """Test generation with default parameters."""
    gen = Generator(mock_session)
    
    run_dir = gen.generate(prompt="test")
    
    assert run_dir.exists()
    assert mock_subprocess_run.called
    
    # Check command construction
    cmd = mock_subprocess_run.call_args[0][0]
    assert "--prompt" in cmd
    assert "test" in cmd
    assert "--width" in cmd
    assert "--height" in cmd

def test_generate_variations(tmp_path, mock_subprocess_run, mock_session):
    """Test generating multiple variations."""
    gen = Generator(mock_session)
    
    results = gen.generate_variations(
        prompt="test",
        iterations=2,
        base_seed=12345
    )
    
    assert len(results) == 1  # One run with multiple iterations
    assert mock_subprocess_run.called
    
    # Test with step variations
    results = gen.generate_variations(
        prompt="test",
        vary_steps=[1, 2, 3],
        base_seed=12345
    )
    
    assert len(results) == 1  # One run with multiple step variations
    assert mock_subprocess_run.call_count >= 3  # Called at least once per step variation
    
    # Verify the run info contains all step variations
    run_dir = results[0]
    run_info_file = run_dir / "run_info.json"
    assert run_info_file.exists()
    with open(run_info_file) as f:
        run_info = json.load(f)
    assert run_info["variation_type"] == "steps"
    assert run_info["step_variations"] == [1, 2, 3]
    assert len(run_info["generated_files"]) == 3  # One file per step variation

def test_generate_error_handling(tmp_path, mock_session):
    """Test handling of generation errors."""
    gen = Generator(mock_session)
    
    # Test with subprocess error
    mock_run = MagicMock(side_effect=Exception("Generation failed"))
    gen.subprocess.run = mock_run
    
    with pytest.raises(Exception):
        gen.generate(prompt="test") 