"""Session management for MFlux Commander."""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from ..core.config import config

class Session:
    """Manages output directories and session state."""
    
    def __init__(self, force_new: bool = False):
        self.base_dir = Path(config.OUTPUT_BASE_DIR)
        self.current_session_dir = self._get_or_create_session_dir(force_new)
        self.run_counter = self._load_run_counter()
        
    def _get_or_create_session_dir(self, force_new: bool) -> Path:
        """Get existing valid session or create new one."""
        if not force_new:
            existing = self._find_valid_session()
            if existing:
                return existing
                
        # Use current year for session directory
        current_time = datetime.now()
        timestamp = current_time.strftime("%Y%m%d_%H%M%S")
        session_dir = self.base_dir / f"mflux_output_{timestamp}"
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir
        
    def _find_valid_session(self) -> Optional[Path]:
        """Find most recent valid session within timeout period."""
        if not self.base_dir.exists():
            return None
            
        current_time = datetime.now()
        timeout = timedelta(hours=config.SESSION_TIMEOUT_HOURS)
        
        sessions = []
        for d in self.base_dir.glob("mflux_output_*"):
            try:
                # Parse the timestamp from the directory name
                # Format: mflux_output_20250308_170709
                dir_timestamp = d.name[len("mflux_output_"):]
                year = int(dir_timestamp[:4])
                month = int(dir_timestamp[4:6])
                day = int(dir_timestamp[6:8])
                hour = int(dir_timestamp[9:11])
                minute = int(dir_timestamp[11:13])
                second = int(dir_timestamp[13:])
                timestamp = datetime(year, month, day, hour, minute, second)
                
                # Use absolute time difference instead of comparing timestamps directly
                time_diff = abs(current_time - timestamp)
                if time_diff < timeout:
                    sessions.append((timestamp, d))
            except (ValueError, IndexError):
                continue
                
        if sessions:
            return sorted(sessions, reverse=True)[0][1]
        return None
        
    def _load_run_counter(self) -> int:
        """Load or initialize run counter."""
        counter_file = self.current_session_dir / "run_counter.txt"
        if counter_file.exists():
            return int(counter_file.read_text().strip())
        return 0
        
    def _save_run_counter(self):
        """Save current run counter."""
        counter_file = self.current_session_dir / "run_counter.txt"
        counter_file.write_text(str(self.run_counter))
        
    def get_next_run_dir(self) -> Path:
        """Get directory for next run."""
        self.run_counter += 1
        run_dir = self.current_session_dir / f"run_{self.run_counter}"
        run_dir.mkdir(parents=True, exist_ok=True)
        self._save_run_counter()
        return run_dir
        
    def save_metadata(self, run_dir: Path, metadata: Dict[str, Any]):
        """Save run metadata to JSON file."""
        metadata_file = run_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
            
    def save_brainstorm_results(self, prompts: list[str]):
        """Save brainstormed prompts to JSON file."""
        results_file = self.current_session_dir / "brainstorm_results.json"
        with open(results_file, 'w') as f:
            json.dump({"prompts": prompts}, f, indent=2)
            
    def load_brainstorm_results(self) -> Optional[list[str]]:
        """Load previously brainstormed prompts."""
        results_file = self.current_session_dir / "brainstorm_results.json"
        if results_file.exists():
            with open(results_file) as f:
                data = json.load(f)
                return data.get("prompts", []) 