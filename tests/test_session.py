"""Tests for session management."""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from mflux_commander.core.session import Session

@pytest.fixture
def mock_session_dir(tmp_path):
    """Create a mock session directory."""
    session_dir = tmp_path / "mflux_output_20240306_123456"
    session_dir.mkdir(parents=True)
    return session_dir

def test_session_creation(mock_session_dir):
    """Test creating a new session."""
    session = Session(force_new=True)
    assert session.current_session_dir.exists()
    assert session.run_counter == 0

def test_session_reuse(mock_session_dir, monkeypatch):
    """Test session reuse within timeout period."""
    # Mock the base directory
    monkeypatch.setattr("mflux_commander.core.session.config.OUTPUT_BASE_DIR",
                       str(mock_session_dir.parent))
    
    # Create a fixed datetime for testing
    fixed_time = datetime(2024, 3, 6, 12, 34, 56)
    
    class MockDateTime:
        @classmethod
        def now(cls):
            return fixed_time
        
        @classmethod
        def strptime(cls, date_string, format):
            return datetime.strptime(date_string, format)
            
        def __new__(cls, *args, **kwargs):
            return datetime(*args, **kwargs)
    
    # Mock datetime
    monkeypatch.setattr("mflux_commander.core.session.datetime", MockDateTime)
    
    session = Session(force_new=False)
    assert session.current_session_dir == mock_session_dir

def test_session_force_new(mock_session_dir):
    """Test forcing creation of new session."""
    session = Session(force_new=True)
    assert session.current_session_dir != mock_session_dir

def test_run_counter(mock_session_dir):
    """Test run counter management."""
    session = Session(force_new=True)
    
    # Initial counter
    assert session.run_counter == 0
    
    # Get next run directory
    run_dir = session.get_next_run_dir()
    assert run_dir.name == "run_1"
    assert session.run_counter == 1
    
    # Counter should persist
    counter_file = session.current_session_dir / "run_counter.txt"
    assert counter_file.exists()
    assert counter_file.read_text().strip() == "1"

def test_metadata_management(mock_session_dir):
    """Test metadata saving and loading."""
    session = Session(force_new=True)
    run_dir = session.get_next_run_dir()
    
    metadata = {
        "prompt": "test prompt",
        "model": "test_model",
        "steps": 5
    }
    
    session.save_metadata(run_dir, metadata)
    
    # Verify metadata file
    metadata_file = run_dir / "metadata.json"
    assert metadata_file.exists()

def test_brainstorm_results(mock_session_dir):
    """Test brainstorm results management."""
    session = Session(force_new=True)
    
    prompts = [
        "Test prompt 1",
        "Test prompt 2",
        "Test prompt 3"
    ]
    
    session.save_brainstorm_results(prompts)
    loaded_prompts = session.load_brainstorm_results()
    
    assert loaded_prompts == prompts 