"""Image generation management for MFlux Commander."""

import subprocess
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import random
from datetime import datetime

from ..core.config import config
from ..utils.gallery import GalleryGenerator
from ..core.session import Session

class Generator:
    """Handles image generation using mflux-generate."""
    
    def __init__(self, session: Session, model: str = config.DEFAULT_MODEL):
        self.session = session
        self.model = model
        self.width = config.DEFAULT_WIDTH
        self.height = config.DEFAULT_HEIGHT
        self.steps = config.get_default_steps(model)
        self.subprocess = subprocess  # Added for test mocking
        self.validate_model()
        
    def validate_model(self):
        """Validate that selected model is available."""
        if self.model not in config.AVAILABLE_MODELS:
            raise ValueError(f"Invalid model: {self.model}. Available models: {config.AVAILABLE_MODELS}")
            
    def generate(self, prompt: str, iterations: int = 1, seed: Optional[int] = None) -> Path:
        """Generate images with the given prompt."""
        run_dir = self.session.get_next_run_dir()
        
        # Initialize run info
        run_info = {
            "prompt": prompt,
            "model": self.model,
            "steps": self.steps,
            "width": self.width,
            "height": self.height,
            "total_iterations": iterations,
            "completed_iterations": 0,
            "status": "in_progress",
            "start_time": datetime.now().isoformat(),
            "generation_times": [],  # List to store generation times for each image
            "generated_files": []  # List to store metadata for each generated file
        }
        self._update_run_info(run_dir, run_info)
        
        # Create initial gallery
        gallery = GalleryGenerator(self.session.current_session_dir)
        gallery.generate_session_gallery()
        gallery.generate_run_gallery(run_dir)
        
        for i in range(iterations):
            current_seed = seed if seed is not None else random.randint(1, 100000)
            output_path = run_dir / f"image_{current_seed}.png"
            
            cmd = [
                "mflux-generate",
                "--prompt", prompt,
                "-m", self.model,  # Use schnell or dev
                "--width", str(self.width),
                "--height", str(self.height),
                "--steps", str(self.steps),
                "--seed", str(current_seed),
                "--output", str(output_path),
                "--metadata"  # Always include metadata
            ]
            
            # Record generation time
            start_time = datetime.now()
            self.subprocess.run(cmd, check=True)
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            
            # Create file metadata
            file_info = {
                "file_name": output_path.name,
                "prompt": prompt,
                "model": self.model,
                "steps": self.steps,
                "seed": current_seed,
                "resolution": f"{self.width}x{self.height}",
                "generation_time": generation_time
            }
            
            # Update metadata for this image
            self.session.save_metadata(run_dir, file_info)
            
            # Update run info and galleries
            run_info["completed_iterations"] = i + 1
            run_info["generation_times"].append(generation_time)
            run_info["generated_files"].append(file_info)
            self._update_run_info(run_dir, run_info)
            
            # Update galleries after each image
            gallery.generate_session_gallery()
            gallery.generate_run_gallery(run_dir)
            
        # Mark run as completed
        run_info["status"] = "completed"
        run_info["end_time"] = datetime.now().isoformat()
        run_info["total_generation_time"] = sum(run_info["generation_times"])
        run_info["average_generation_time"] = sum(run_info["generation_times"]) / len(run_info["generation_times"])
        self._update_run_info(run_dir, run_info)
        
        # Final gallery update
        gallery.generate_session_gallery()
        gallery.generate_run_gallery(run_dir)
        
        return run_dir
        
    def _update_run_info(self, run_dir: Path, run_info: Dict[str, Any]):
        """Update run info file."""
        run_info_file = run_dir / "run_info.json"
        with open(run_info_file, "w") as f:
            json.dump(run_info, f, indent=2)
        
    def generate_variations(self, prompt: str, iterations: Optional[int] = None, 
                          base_seed: Optional[int] = None, vary_steps: Optional[List[int]] = None) -> List[Path]:
        """Generate multiple variations of an image.
        
        Args:
            prompt: The prompt to generate from
            iterations: Number of seed variations to generate (if vary_steps not provided)
            base_seed: Base seed for step variations (required if vary_steps provided)
            vary_steps: List of step counts to iterate through (requires base_seed)
        """
        results = []
        
        if vary_steps and base_seed:
            # Generate variations with different step counts in a single run
            run_dir = self.session.get_next_run_dir()
            results.append(run_dir)
            
            run_info = {
                "prompt": prompt,
                "model": self.model,
                "base_seed": base_seed,
                "width": self.width,
                "height": self.height,
                "total_iterations": len(vary_steps),
                "completed_iterations": 0,
                "status": "in_progress",
                "start_time": datetime.now().isoformat(),
                "variation_type": "steps",
                "step_variations": vary_steps,
                "generation_times": [],  # List to store generation times for each image
                "generated_files": []  # List to store metadata for each generated file
            }
            self._update_run_info(run_dir, run_info)
            
            # Create initial gallery
            gallery = GalleryGenerator(self.session.current_session_dir)
            gallery.generate_session_gallery()
            gallery.generate_run_gallery(run_dir)
            
            original_steps = self.steps
            for i, step_count in enumerate(vary_steps):
                self.steps = step_count
                output_path = run_dir / f"image_{base_seed}_steps_{step_count}.png"
                
                cmd = [
                    "mflux-generate",
                    "--prompt", prompt,
                    "-m", self.model,
                    "--width", str(self.width),
                    "--height", str(self.height),
                    "--steps", str(step_count),
                    "--seed", str(base_seed),
                    "--output", str(output_path),
                    "--metadata"  # Always include metadata
                ]
                
                # Record generation time
                start_time = datetime.now()
                self.subprocess.run(cmd, check=True)
                end_time = datetime.now()
                generation_time = (end_time - start_time).total_seconds()
                
                # Create file metadata
                file_info = {
                    "file_name": output_path.name,
                    "prompt": prompt,
                    "model": self.model,
                    "steps": step_count,
                    "seed": base_seed,
                    "resolution": f"{self.width}x{self.height}",
                    "generation_time": generation_time
                }
                
                # Update metadata for this image
                self.session.save_metadata(run_dir, file_info)
                
                # Update run info and galleries
                run_info["completed_iterations"] = i + 1
                run_info["generation_times"].append(generation_time)
                run_info["generated_files"].append(file_info)
                self._update_run_info(run_dir, run_info)
                
                gallery.generate_session_gallery()
                gallery.generate_run_gallery(run_dir)
                
            self.steps = original_steps
            
            # Mark run as completed
            run_info["status"] = "completed"
            run_info["end_time"] = datetime.now().isoformat()
            run_info["total_generation_time"] = sum(run_info["generation_times"])
            run_info["average_generation_time"] = sum(run_info["generation_times"]) / len(run_info["generation_times"])
            self._update_run_info(run_dir, run_info)
            
            # Final gallery update
            gallery.generate_session_gallery()
            gallery.generate_run_gallery(run_dir)
            
        elif iterations:
            # Generate variations with different seeds
            run_dir = self.session.get_next_run_dir()
            results.append(run_dir)
            
            run_info = {
                "prompt": prompt,
                "model": self.model,
                "steps": self.steps,
                "width": self.width,
                "height": self.height,
                "total_iterations": iterations,
                "completed_iterations": 0,
                "status": "in_progress",
                "start_time": datetime.now().isoformat(),
                "variation_type": "seeds",
                "generation_times": [],  # List to store generation times for each image
                "generated_files": []  # List to store metadata for each generated file
            }
            self._update_run_info(run_dir, run_info)
            
            # Create initial gallery
            gallery = GalleryGenerator(self.session.current_session_dir)
            gallery.generate_session_gallery()
            gallery.generate_run_gallery(run_dir)
            
            for i in range(iterations):
                current_seed = random.randint(1, 100000)
                output_path = run_dir / f"image_{current_seed}.png"
                
                cmd = [
                    "mflux-generate",
                    "--prompt", prompt,
                    "-m", self.model,
                    "--width", str(self.width),
                    "--height", str(self.height),
                    "--steps", str(self.steps),
                    "--seed", str(current_seed),
                    "--output", str(output_path),
                    "--metadata"  # Always include metadata
                ]
                
                # Record generation time
                start_time = datetime.now()
                self.subprocess.run(cmd, check=True)
                end_time = datetime.now()
                generation_time = (end_time - start_time).total_seconds()
                
                # Create file metadata
                file_info = {
                    "file_name": output_path.name,
                    "prompt": prompt,
                    "model": self.model,
                    "steps": self.steps,
                    "seed": current_seed,
                    "resolution": f"{self.width}x{self.height}",
                    "generation_time": generation_time
                }
                
                # Update metadata for this image
                self.session.save_metadata(run_dir, file_info)
                
                # Update run info and galleries
                run_info["completed_iterations"] = i + 1
                run_info["generation_times"].append(generation_time)
                run_info["generated_files"].append(file_info)
                self._update_run_info(run_dir, run_info)
                
                gallery.generate_session_gallery()
                gallery.generate_run_gallery(run_dir)
            
            # Mark run as completed
            run_info["status"] = "completed"
            run_info["end_time"] = datetime.now().isoformat()
            run_info["total_generation_time"] = sum(run_info["generation_times"])
            run_info["average_generation_time"] = sum(run_info["generation_times"]) / len(run_info["generation_times"])
            self._update_run_info(run_dir, run_info)
            
            # Final gallery update
            gallery.generate_session_gallery()
            gallery.generate_run_gallery(run_dir)
        
        return results 