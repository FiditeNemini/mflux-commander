"""Gallery generation for MFlux Commander."""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import shutil
from datetime import datetime

class GalleryGenerator:
    """Generates HTML galleries for viewing generated images."""
    
    GALLERY_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .run-group {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }}
            .run-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }}
            .progress-bar {{
                width: 200px;
                height: 20px;
                background: #eee;
                border-radius: 10px;
                overflow: hidden;
            }}
            .progress-fill {{
                height: 100%;
                background: #4CAF50;
                transition: width 0.3s ease;
            }}
            .gallery {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            .image-card {{
                background: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .image-card img {{
                width: 100%;
                height: auto;
                border-radius: 4px;
                transition: transform 0.2s ease;
                cursor: pointer;
            }}
            .metadata {{
                margin-top: 10px;
                font-size: 14px;
                color: #666;
            }}
            .cli-command {{
                background: #f5f5f5;
                padding: 8px;
                border-radius: 4px;
                font-family: monospace;
                margin-top: 8px;
                word-break: break-all;
                cursor: text;
            }}
            .timestamp {{
                color: #999;
                font-size: 12px;
                margin-bottom: 20px;
            }}
            h1 {{
                color: #333;
                border-bottom: 2px solid #ddd;
                padding-bottom: 10px;
            }}
            .status {{
                font-size: 14px;
                color: #666;
            }}
            .status.in-progress {{
                color: #2196F3;
            }}
            .status.completed {{
                color: #4CAF50;
            }}
            .fullscreen-overlay {{
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.9);
                z-index: 1000;
                cursor: pointer;
            }}
            .fullscreen-image {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                max-width: 90%;
                max-height: 90vh;
                object-fit: contain;
            }}
            .fullscreen-metadata {{
                position: absolute;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(0, 0, 0, 0.7);
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
                text-align: center;
            }}
        </style>
        <script>
            function refreshGallery() {{
                if (document.querySelector('.status.in-progress')) {{
                    setTimeout(() => window.location.reload(), 5000);
                }}
            }}

            function showFullscreen(imgSrc) {{
                const overlay = document.createElement('div');
                overlay.className = 'fullscreen-overlay';
                
                const img = document.createElement('img');
                img.src = imgSrc;
                img.className = 'fullscreen-image';
                
                overlay.appendChild(img);
                document.body.appendChild(overlay);
                
                // Fade in
                requestAnimationFrame(() => {{
                    overlay.style.display = 'block';
                    overlay.style.opacity = '0';
                    requestAnimationFrame(() => {{
                        overlay.style.transition = 'opacity 0.3s ease';
                        overlay.style.opacity = '1';
                    }});
                }});
                
                function hideOverlay() {{
                    overlay.style.opacity = '0';
                    setTimeout(() => overlay.remove(), 300);
                }}
                
                overlay.onclick = hideOverlay;
                document.addEventListener('keydown', function(e) {{
                    if (e.key === 'Escape') hideOverlay();
                }});
            }}

            window.onload = function() {{
                refreshGallery();
                
                // Add click handlers to all images
                document.querySelectorAll('.image-card img').forEach(img => {{
                    img.onclick = () => showFullscreen(img.src);
                }});
            }};
        </script>
    </head>
    <body>
        <h1>{title}</h1>
        <div class="timestamp">Generated: {timestamp}</div>
        {run_groups}
    </body>
    </html>
    """
    
    IMAGE_CARD_TEMPLATE = """
    <div class="image-card">
        <img src="{image_path}" alt="{prompt}">
        <div class="metadata">
            <p><strong>Prompt:</strong> {prompt}</p>
            <p><strong>Model:</strong> {model} ({steps} steps)</p>
            <p><strong>Seed:</strong> {seed}</p>
            <p><strong>Resolution:</strong> {resolution}</p>
            <p><strong>Generation Time:</strong> {generation_time:.1f}s</p>
            <p class="cli-command">mflux-commander generate --prompt "{prompt}" --seed {seed} --vary-steps {steps}{format_option}{model_option}</p>
        </div>
    </div>
    """
    
    RUN_GROUP_TEMPLATE = """
    <div class="run-group">
        <div class="run-header">
            <h2>Run {run_number}</h2>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress_pct}%"></div>
            </div>
            <div class="status {status_class}">{status}</div>
        </div>
        <div class="run-stats">
            <p><strong>Total Generation Time:</strong> {total_time:.1f}s</p>
            <p><strong>Average Time per Image:</strong> {avg_time:.1f}s</p>
        </div>
        <div class="gallery">
            {image_cards}
        </div>
    </div>
    """
    
    def __init__(self, session_dir: Path):
        self.session_dir = session_dir
        
    def _load_metadata(self, run_dir: Path) -> Dict[str, Any]:
        """Load metadata from a run directory."""
        metadata_file = run_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                return json.load(f)
        return {}
        
    def _find_image_files(self, run_dir: Path) -> List[Path]:
        """Find all image files in a run directory."""
        return list(run_dir.glob("*.png"))
        
    def _get_image_info(self, img: Path, run_info: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """Get image info including steps and metadata."""
        try:
            # First try to get seed from metadata
            img_seed = None
            
            # For seed variations, get the seed from the filename
            if run_info.get("variation_type") == "seeds":
                try:
                    img_seed = int(img.stem.split("_")[1])
                except (IndexError, ValueError):
                    pass
            
            # For step variations, use the base seed
            elif run_info.get("variation_type") == "steps":
                img_seed = run_info.get("base_seed")
            
            # Fallback to run_info seed or extract from filename
            if img_seed is None:
                img_seed = run_info.get("seed")
                if img_seed is None:
                    try:
                        img_seed = int(img.stem.split("_")[1])
                    except (IndexError, ValueError):
                        img_seed = "Unknown"
                
            # Get steps from filename for step variations
            img_steps = run_info.get("steps", "Unknown")
            if "steps_" in img.stem:
                try:
                    img_steps = int(img.stem.split("steps_")[1])
                except (IndexError, ValueError):
                    pass

            # Get generation time for this image
            generation_time = 0.0
            if "generation_times" in run_info:
                img_index = len([f for f in img.parent.glob("*.png") if f.stat().st_mtime <= img.stat().st_mtime]) - 1
                if 0 <= img_index < len(run_info["generation_times"]):
                    generation_time = run_info["generation_times"][img_index]
                
        except (IndexError, ValueError):
            img_seed = "Unknown"
            img_steps = run_info.get("steps", "Unknown")
            generation_time = 0.0
            
        # Convert steps to int for sorting, using 0 if unknown
        sort_steps = int(img_steps) if isinstance(img_steps, int) else 0
            
        # Determine format option
        width = run_info.get("width", 1024)
        height = run_info.get("height", 1024)
        format_option = ""
        if width != 1024 or height != 1024:
            if width == 1024 and height == 576:
                format_option = " --format landscape"
            elif width == 768 and height == 1024:
                format_option = " --format portrait"
            elif width == 512 and height == 288:
                format_option = " --format landscape_sm"
            elif width == 384 and height == 512:
                format_option = " --format portrait_sm"
            elif width == 1536 and height == 864:
                format_option = " --format landscape_lg"
            elif width == 1152 and height == 1536:
                format_option = " --format portrait_lg"
                
        # Add model option if not default
        model_option = ""
        if run_info.get("model") != "schnell":
            model_option = f" --model {run_info.get('model')}"
            
        return sort_steps, {
            "seed": img_seed,
            "steps": img_steps,
            "format_option": format_option,
            "model_option": model_option,
            "generation_time": generation_time
        }
        
    def generate_run_gallery(self, run_dir: Path) -> Path:
        """Generate gallery for a single run."""
        run_info = self._load_run_info(run_dir)
        images = self._find_image_files(run_dir)
        
        # Calculate progress
        total_iterations = run_info.get("total_iterations", 1)
        completed_iterations = len(images)
        progress = (completed_iterations / total_iterations) * 100
        
        # Determine status
        is_complete = run_info.get("status") == "completed"
        status = "Completed" if is_complete else "Generating..."
        status_class = "completed" if is_complete else "in-progress"
        
        # Get timing information
        total_time = run_info.get("total_generation_time", 0.0)
        avg_time = run_info.get("average_generation_time", 0.0)
        
        image_cards = []
        if not images:
            # Add placeholder for empty directory
            card = self.IMAGE_CARD_TEMPLATE.format(
                image_path="",
                prompt=run_info.get("prompt", "Unknown"),
                model=run_info.get("model", "Unknown"),
                steps=run_info.get("steps", "Unknown"),
                seed="N/A",
                resolution=run_info.get("resolution") or f"{run_info.get('width', 'Unknown')}x{run_info.get('height', 'Unknown')}",
                format_option="",
                model_option="",
                generation_time=0.0
            )
            image_cards.append(card)
        else:
            # Sort images by steps
            image_info = []
            for img in images:
                steps, info = self._get_image_info(img, run_info)
                image_info.append((steps, img, info))
            image_info.sort()  # Sort by steps
            
            for _, img, info in image_info:
                card = self.IMAGE_CARD_TEMPLATE.format(
                    image_path=img.name,
                    prompt=run_info.get("prompt", "Unknown"),
                    model=run_info.get("model", "Unknown"),
                    steps=info["steps"],
                    seed=info["seed"],
                    resolution=run_info.get("resolution") or f"{run_info.get('width', 'Unknown')}x{run_info.get('height', 'Unknown')}",
                    format_option=info["format_option"],
                    model_option=info["model_option"],
                    generation_time=info["generation_time"]
                )
                image_cards.append(card)
            
        run_group = self.RUN_GROUP_TEMPLATE.format(
            run_number=run_dir.name.split("_")[1] if "_" in run_dir.name else "unknown",
            progress_pct=progress,
            status=status,
            status_class=status_class,
            image_cards="\n".join(image_cards),
            total_time=total_time,
            avg_time=avg_time
        )
        
        gallery_html = self.GALLERY_TEMPLATE.format(
            title=f"Run Results - {run_dir.name}",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            run_groups=run_group
        )
        
        gallery_file = run_dir / "index.html"
        gallery_file.write_text(gallery_html)
        return gallery_file
        
    def generate_session_gallery(self) -> Path:
        """Generate gallery for entire session."""
        # Get all run directories and sort by creation time (newest first)
        run_dirs = sorted(
            [d for d in self.session_dir.iterdir() if d.is_dir() and d.name.startswith("run_")],
            key=lambda d: d.stat().st_mtime,
            reverse=True
        )
        
        run_groups = []
        for run_dir in run_dirs:
            run_info = self._load_run_info(run_dir)
            images = self._find_image_files(run_dir)
            
            # Calculate progress
            total_iterations = run_info.get("total_iterations", 1)
            completed_iterations = len(images)
            progress = (completed_iterations / total_iterations) * 100
            
            # Determine status
            is_complete = run_info.get("status") == "completed"
            status = "Completed" if is_complete else "Generating..."
            status_class = "completed" if is_complete else "in-progress"
            
            # Get timing information
            total_time = run_info.get("total_generation_time", 0.0)
            avg_time = run_info.get("average_generation_time", 0.0)
            
            image_cards = []
            if not images:
                # Add placeholder for empty directory
                card = self.IMAGE_CARD_TEMPLATE.format(
                    image_path="",
                    prompt=run_info.get("prompt", "Unknown"),
                    model=run_info.get("model", "Unknown"),
                    steps=run_info.get("steps", "Unknown"),
                    seed="N/A",
                    resolution=run_info.get("resolution") or f"{run_info.get('width', 'Unknown')}x{run_info.get('height', 'Unknown')}",
                    format_option="",
                    model_option="",
                    generation_time=0.0
                )
                image_cards.append(card)
            else:
                # Sort images by steps
                image_info = []
                for img in images:
                    steps, info = self._get_image_info(img, run_info)
                    image_info.append((steps, img, info))
                image_info.sort()  # Sort by steps
                
                for _, img, info in image_info:
                    # Create relative path from session gallery to image
                    rel_path = f"{run_dir.name}/{img.name}"
                    
                    card = self.IMAGE_CARD_TEMPLATE.format(
                        image_path=rel_path,
                        prompt=run_info.get("prompt", "Unknown"),
                        model=run_info.get("model", "Unknown"),
                        steps=info["steps"],
                        seed=info["seed"],
                        resolution=run_info.get("resolution") or f"{run_info.get('width', 'Unknown')}x{run_info.get('height', 'Unknown')}",
                        format_option=info["format_option"],
                        model_option=info["model_option"],
                        generation_time=info["generation_time"]
                    )
                    image_cards.append(card)
                
            run_group = self.RUN_GROUP_TEMPLATE.format(
                run_number=run_dir.name.split("_")[1] if "_" in run_dir.name else "unknown",
                progress_pct=progress,
                status=status,
                status_class=status_class,
                image_cards="\n".join(image_cards),
                total_time=total_time,
                avg_time=avg_time
            )
            run_groups.append(run_group)
                
        gallery_html = self.GALLERY_TEMPLATE.format(
            title="Session Gallery",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            run_groups="\n".join(run_groups)
        )
        
        gallery_file = self.session_dir / "index.html"
        gallery_file.write_text(gallery_html)
        return gallery_file
        
    def _load_run_info(self, run_dir: Path) -> Dict[str, Any]:
        """Load run info from a run directory."""
        run_info = {}
        
        # First try to load metadata.json
        metadata = self._load_metadata(run_dir)
        if metadata:
            run_info.update({
                "prompt": metadata.get("prompt", "Unknown"),
                "model": metadata.get("model", "Unknown"),
                "steps": metadata.get("steps", "Unknown"),
                "width": metadata.get("width", "Unknown"),
                "height": metadata.get("height", "Unknown"),
                "resolution": metadata.get("resolution", "UnknownxUnknown"),
                "seed": metadata.get("seed", "Unknown"),
                "status": "completed",
                "total_iterations": 1,
                "completed_iterations": 1
            })
        
        # Then try to load and merge run_info.json
        run_info_file = run_dir / "run_info.json"
        if run_info_file.exists():
            with open(run_info_file) as f:
                run_info.update(json.load(f))
                
        return run_info 