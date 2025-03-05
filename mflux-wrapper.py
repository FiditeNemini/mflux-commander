#!/usr/bin/env python3
"""
MFlux Generator Wrapper

A tool for managing and exploring prompts with mflux-generate, including:
- Running variations with random seeds
- Storing metadata
- Generating HTML pages for output review
- Tracking runs for iterative development
"""

import argparse
import json
import os
import subprocess
import datetime
import random
import shutil
from pathlib import Path

STYLE_FILE = os.path.expanduser("~/.mflux_styles.json")

def load_styles():
    """Load saved styles from the style file."""
    if os.path.exists(STYLE_FILE):
        try:
            with open(STYLE_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_style(name, description):
    """Save a new style to the style file."""
    styles = load_styles()
    styles[name] = description
    os.makedirs(os.path.dirname(STYLE_FILE), exist_ok=True)
    with open(STYLE_FILE, 'w') as f:
        json.dump(styles, f, indent=2)

def list_styles():
    """List all saved styles."""
    styles = load_styles()
    if not styles:
        print("No saved styles found.")
        return
    
    print("\nSaved Styles:")
    print("-" * 40)
    for name, description in styles.items():
        print(f"{name}:")
        print(f"  {description}")
        print("-" * 40)

def get_style(name):
    """Get a style by name."""
    styles = load_styles()
    return styles.get(name)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Wrapper for mflux-generate to manage prompt exploration")
    
    # Style management commands
    style_group = parser.add_mutually_exclusive_group()
    style_group.add_argument("--save-style", nargs=2, metavar=('NAME', 'DESCRIPTION'),
                        help="Save a new style with name and description")
    style_group.add_argument("--list-styles", action="store_true",
                        help="List all saved styles")
    style_group.add_argument("--style", type=str, metavar='STYLE_NAME',
                        help="Apply a saved style to the prompt")
    
    # Arguments
    parser.add_argument("--prompt", type=str, help="The prompt to use for generation (if not specified, uses last prompt from current session)")
    parser.add_argument("--model", type=str, default="schnell", choices=["schnell", "dev"], 
                        help="Model type to use (schnell or dev, default: schnell)")
    parser.add_argument("--new", action="store_true", help="Force creation of new output directory")
    parser.add_argument("--iterate", type=str, help="Comma-separated list of step counts to iterate through (requires --seed)")
    parser.add_argument("--no-watch", action="store_true", help="Don't start live-server to monitor changes")
    
    # Resolution options (mutually exclusive)
    resolution_group = parser.add_mutually_exclusive_group()
    resolution_group.add_argument("--resolution", type=str, default="1024x1024", 
                        help="Resolution in format WIDTHxHEIGHT (default: 1024x1024)")
    resolution_group.add_argument("--landscape", action="store_true", help="Use 16:9 landscape format (1024x576)")
    resolution_group.add_argument("--landscape-sm", action="store_true", help="Use 16:9 landscape format small (512x288)")
    resolution_group.add_argument("--landscape-lg", action="store_true", help="Use 16:9 landscape format large (1536x864)")
    resolution_group.add_argument("--landscape-xl", action="store_true", help="Use 16:9 landscape format xl (2048x1152)")
    resolution_group.add_argument("--portrait", action="store_true", help="Use 3:4 portrait format (768x1024)")
    resolution_group.add_argument("--portrait-sm", action="store_true", help="Use 3:4 portrait format small (384x512)")
    resolution_group.add_argument("--portrait-lg", action="store_true", help="Use 3:4 portrait format large (1152x1536)")
    resolution_group.add_argument("--portrait-xl", action="store_true", help="Use 3:4 portrait format xl (1536x2048)")
    resolution_group.add_argument("--square-sm", action="store_true", help="Use square format small (512x512)")
    resolution_group.add_argument("--square-xl", action="store_true", help="Use square format xl (2048x2048)")
    
    # Other optional arguments
    parser.add_argument("--steps", type=int, help="Number of steps (defaults: 1 for schnell, 5 for dev)")
    parser.add_argument("--variations", type=int, default=4, help="Number of variations to generate (default: 4)")
    parser.add_argument("--metadata", action="store_true", help="Include metadata in output")
    parser.add_argument("--output-dir", type=str, help="Output directory (default: auto-generated based on date)")
    parser.add_argument("--seed", type=int, help="Starting seed (random if not provided)")
    
    args = parser.parse_args()
    
    # Handle style commands
    if args.save_style:
        save_style(args.save_style[0], args.save_style[1])
        print(f"Style '{args.save_style[0]}' saved successfully.")
        exit(0)
    elif args.list_styles:
        list_styles()
        exit(0)
    elif args.style:
        if args.style.lower() == "none":
            # Clear any existing style
            args.style = None
            args.style_desc = None
        else:
            style_desc = get_style(args.style)
            if not style_desc:
                raise ValueError(f"Style '{args.style}' not found. Use --list-styles to see available styles.")
            if args.prompt:
                args.prompt = f"{args.prompt}, {style_desc}"
            else:
                # Will try to get last prompt later
                args.style_desc = style_desc
    
    # Set resolution based on format flags
    if args.landscape:
        args.resolution = "1024x576"
    elif args.landscape_sm:
        args.resolution = "512x288"
    elif args.landscape_lg:
        args.resolution = "1536x864"
    elif args.landscape_xl:
        args.resolution = "2048x1152"
    elif args.portrait:
        args.resolution = "768x1024"
    elif args.portrait_sm:
        args.resolution = "384x512"
    elif args.portrait_lg:
        args.resolution = "1152x1536"
    elif args.portrait_xl:
        args.resolution = "1536x2048"
    elif args.square_sm:
        args.resolution = "512x512"
    elif args.square_xl:
        args.resolution = "2048x2048"
    
    # Validate iterate command
    if args.iterate:
        if args.seed is None:
            raise ValueError("--iterate requires --seed to be specified")
        try:
            args.iterate_steps = [int(s.strip()) for s in args.iterate.split(",")]
        except ValueError:
            raise ValueError("--iterate must be a comma-separated list of integers (e.g., '1,3,5,9')")
        args.variations = len(args.iterate_steps)  # Override variations to match iterate steps
        args.steps = None  # Clear any manually set steps
    
    return args

def get_last_settings(base_dir):
    """Get the prompt, resolution, style, and variations from the most recent run in the directory."""
    runs = sorted([d for d in os.listdir(base_dir) if d.startswith("run_")], 
                 key=lambda x: int(x.split("_")[1]), reverse=True)
    
    for run in runs:
        info_path = os.path.join(base_dir, run, "run_info.json")
        if os.path.exists(info_path):
            try:
                with open(info_path, "r") as f:
                    info = json.load(f)
                    # Extract style from prompt if it exists
                    prompt = info.get("prompt", "")
                    style = None
                    if "," in prompt:
                        # Try to match the style with known styles
                        styles = load_styles()
                        base_prompt = prompt.split(",")[0].strip()
                        style_part = prompt.split(",", 1)[1].strip()
                        if style_part in styles.values():
                            # Find the style name that matches this description
                            for name, desc in styles.items():
                                if desc == style_part:
                                    style = name
                                    prompt = base_prompt
                                    break
                    
                    return {
                        "prompt": prompt,
                        "resolution": info.get("resolution"),
                        "style": style,
                        "variations": info.get("variations", 4)  # Default to 4 if not found
                    }
            except:
                continue
    return None

def create_output_directories(args):
    """Create the output directory structure."""
    # Create base directory if not specified
    if not args.output_dir:
        # Check if there's a recent session directory (within last hour) and --new wasn't specified
        now = datetime.datetime.now()
        recent_dirs = []
        
        if not args.new:  # Only look for recent dirs if --new wasn't specified
            for d in os.listdir('.'):
                if d.startswith('mflux_output_'):
                    try:
                        dir_time = datetime.datetime.strptime(d.split('_', 2)[2], "%Y%m%d_%H%M%S")
                        if (now - dir_time).total_seconds() < 3600:  # Within last hour
                            recent_dirs.append((dir_time, d))
                    except ValueError:
                        continue
        
        if recent_dirs:
            # Use most recent session directory
            base_dir = sorted(recent_dirs, reverse=True)[0][1]
            
            # If no settings specified, try to get the last ones used
            last_settings = get_last_settings(base_dir)
            if last_settings:
                # Apply last prompt if none specified
                if args.prompt is None:
                    args.prompt = last_settings["prompt"]
                    # If we have a style from args, apply it to the last prompt
                    if hasattr(args, 'style_desc'):
                        args.prompt = f"{args.prompt}, {args.style_desc}"
                    # Otherwise, if we had a style from last time and no new style specified, reuse it
                    elif last_settings["style"] and not args.style:
                        style_desc = get_style(last_settings["style"])
                        if style_desc:
                            args.prompt = f"{args.prompt}, {style_desc}"
                
                # Apply last resolution if none specified (no format flag used)
                if not any([args.landscape, args.landscape_sm, args.landscape_lg, args.landscape_xl, args.portrait, args.portrait_sm, args.portrait_lg, args.portrait_xl, args.square_sm, args.square_xl]) and args.resolution == "1024x1024":
                    args.resolution = last_settings["resolution"]
                
                # Apply last variations if none specified and not using iterate
                if args.variations == 4 and not hasattr(args, 'iterate_steps'):
                    args.variations = last_settings["variations"]
                
                if args.prompt is None:
                    raise ValueError("No prompt specified and couldn't find last prompt in current session")
        else:
            # Create new session directory
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            base_dir = f"mflux_output_{timestamp}"
            if args.prompt is None:
                raise ValueError("No prompt specified and no recent session to get prompt from")
    else:
        base_dir = args.output_dir
        if args.prompt is None:
            last_settings = get_last_settings(base_dir)
            if last_settings:
                args.prompt = last_settings["prompt"]
                # If we have a style from args, apply it to the last prompt
                if hasattr(args, 'style_desc'):
                    args.prompt = f"{args.prompt}, {args.style_desc}"
                # Otherwise, if we had a style from last time and no new style specified, reuse it
                elif last_settings["style"] and not args.style:
                    style_desc = get_style(last_settings["style"])
                    if style_desc:
                        args.prompt = f"{args.prompt}, {style_desc}"
                
                # Apply last resolution if none specified (no format flag used)
                if not any([args.landscape, args.landscape_sm, args.landscape_lg, args.landscape_xl, args.portrait, args.portrait_sm, args.portrait_lg, args.portrait_xl, args.square_sm, args.square_xl]) and args.resolution == "1024x1024":
                    args.resolution = last_settings["resolution"]
                
                # Apply last variations if none specified and not using iterate
                if args.variations == 4 and not hasattr(args, 'iterate_steps'):
                    args.variations = last_settings["variations"]
            else:
                raise ValueError("No prompt specified and couldn't find last prompt in output directory")
    
    # Ensure base directory exists
    os.makedirs(base_dir, exist_ok=True)
    
    # Determine the next run number
    existing_runs = [d for d in os.listdir(base_dir) if d.startswith("run_")]
    if existing_runs:
        run_numbers = [int(run.split("_")[1]) for run in existing_runs]
        next_run = max(run_numbers) + 1
    else:
        next_run = 1
    
    run_dir = os.path.join(base_dir, f"run_{next_run}")
    os.makedirs(run_dir, exist_ok=True)
    
    # Create initial run_info.json with empty results
    initial_info = {
        "timestamp": datetime.datetime.now().isoformat(),
        "prompt": args.prompt,
        "model": args.model,
        "steps": args.iterate if hasattr(args, 'iterate_steps') else (args.steps if args.steps is not None else get_default_steps(args.model)),
        "resolution": args.resolution,
        "variations": args.variations,
        "command_args": {
            "prompt": args.prompt,
            "model": args.model,
            "resolution": args.resolution,
            "metadata": args.metadata,
            "style": args.style if hasattr(args, 'style') else None,
            "steps": args.iterate if hasattr(args, 'iterate_steps') else (args.steps if args.steps is not None else get_default_steps(args.model)),
            "iterate": args.iterate if hasattr(args, 'iterate') else None,
        },
        "results": []
    }
    
    with open(os.path.join(run_dir, "run_info.json"), "w") as f:
        json.dump(initial_info, f, indent=2)
    
    # Generate initial HTML files
    generate_html(base_dir, run_dir, [], args)
    update_main_index(base_dir)
    
    return base_dir, run_dir

def get_default_steps(model):
    """Get default steps based on model type."""
    if model == "schnell":
        return 1
    elif model == "dev":
        return 5
    else:
        return 1  # Fallback

def generate_images(args, run_dir):
    """Run mflux-generate command and return results."""
    results = []
    
    # Use provided steps or default based on model
    steps = args.steps if args.steps is not None else get_default_steps(args.model)
    
    # Parse resolution
    width, height = map(int, args.resolution.split('x'))
    
    # Generate each variation
    for i in range(args.variations):
        # Generate a random seed if not provided
        if args.seed is not None:
            seed = args.seed + i
        else:
            seed = random.randint(1, 1000000)
        
        # If iterating, use the corresponding step count
        if hasattr(args, 'iterate_steps'):
            current_steps = args.iterate_steps[i]
        else:
            current_steps = steps
        
        output_path = os.path.join(run_dir, f"image_{i+1}.png")
        
        # Build the mflux-generate command
        cmd = [
            "mflux-generate",
            "--prompt", args.prompt,
            "--model", args.model,
            "--steps", str(current_steps),
            "--seed", str(seed),
            "--width", str(width),
            "--height", str(height),
            "--output", output_path
        ]
        
        if args.metadata:
            cmd.extend(["--metadata"])
        
        # Execute the command
        try:
            print(f"\nGenerating variation {i+1}/{args.variations} with seed {seed} and steps {current_steps}...")
            start_time = datetime.datetime.now()
            
            # Use Popen to capture output in real-time
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Track progress
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # Clean and display the output
                    output = output.strip()
                    if output:  # Only print non-empty lines
                        print(f"  {output}")
            
            # Check for any errors
            rc = process.poll()
            if rc != 0:
                error = process.stderr.read()
                raise subprocess.CalledProcessError(rc, cmd, error)
            
            end_time = datetime.datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            
            # Store the result
            image_info = {
                "index": i+1,
                "seed": seed,
                "steps": current_steps,
                "file_path": output_path,
                "metadata_path": output_path + ".json" if args.metadata else None,
                "command": " ".join(cmd),
                "generation_time": generation_time
            }
            results.append(image_info)
            
            # Update HTML files after each successful generation
            save_run_info(run_dir, args, results)  # Save current progress
            generate_html(os.path.dirname(run_dir), run_dir, results, args)
            
            print(f"  ✓ Generated in {generation_time:.2f} seconds")
            
        except subprocess.CalledProcessError as e:
            print(f"Error generating image {i+1}: {e}")
            print(f"stderr: {e.stderr}")
    
    return results

def generate_html(base_dir, run_dir, results, args):
    """Generate HTML pages for viewing the results."""
    # Create HTML for this run
    run_html_path = os.path.join(run_dir, "index.html")
    
    # Get the original prompt without style if possible
    base_prompt = args.prompt
    if hasattr(args, 'style') and args.style and "," in args.prompt:
        base_prompt = args.prompt.split(",")[0].strip()
    
    # Format steps info
    if hasattr(args, 'iterate_steps'):
        steps_info = f"Steps: {args.iterate} (iterating)"
    else:
        steps = args.steps if args.steps is not None else get_default_steps(args.model)
        steps_info = f"Steps: {steps}"
    
    with open(run_html_path, "w") as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>MFlux Generation Run</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .image-container {{ display: flex; flex-wrap: wrap; gap: 20px; }}
        .image-card {{ border: 1px solid #ccc; padding: 15px; border-radius: 5px; max-width: 550px; }}
        .image-card img {{ max-width: 100%; cursor: pointer; }}
        .metadata {{ margin-top: 10px; font-family: monospace; white-space: pre-wrap; background: #f5f5f5; padding: 10px; border-radius: 5px; }}
        .command {{ margin-top: 10px; font-family: monospace; background: #f0f0f0; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        .command code {{ display: block; margin-top: 5px; }}
        .status {{ padding: 5px 10px; border-radius: 3px; display: inline-block; }}
        .in-progress {{ background: #fff3cd; color: #856404; }}
        .complete {{ background: #d4edda; color: #155724; }}
        h2, h3 {{ color: #333; }}
        .generation-time {{ color: #666; font-size: 0.9em; margin-top: 5px; }}
    </style>
</head>
<body>
    <h1>MFlux Generation Results</h1>
    <div class="run-info">
        <h2>Run Information</h2>
        <p><strong>Prompt:</strong> {args.prompt}</p>
        <p><strong>Model:</strong> {args.model}</p>
        <p><strong>Resolution:</strong> {args.resolution}</p>
        <p><strong>{steps_info}</strong></p>
        <p><strong>Date:</strong> {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p><strong>Status:</strong> <span class="status {'complete' if len(results) == args.variations else 'in-progress'}">
            {f"Complete ({len(results)}/{args.variations})" if len(results) == args.variations else f"Generating... ({len(results)}/{args.variations})"}
        </span></p>
    </div>
    
    <h2>Generated Images ({len(results)})</h2>
    <div class="image-container">
""")
        
        # Add each image
        for result in results:
            image_filename = os.path.basename(result["file_path"])
            metadata_html = ""
            
            # Add metadata if available
            if result["metadata_path"] and os.path.exists(result["metadata_path"]):
                try:
                    with open(result["metadata_path"], "r") as meta_file:
                        metadata = json.load(meta_file)
                        # Format a simplified version of metadata
                        metadata_html = f"""<div class="metadata">
<strong>Seed:</strong> {result["seed"]}
<strong>Steps:</strong> {result["steps"]}
<strong>Generation Time:</strong> {result["generation_time"]:.2f} seconds
</div>"""
                except json.JSONDecodeError:
                    metadata_html = "<p>Error reading metadata.</p>"
            else:
                metadata_html = f"""<div class="metadata">
<strong>Seed:</strong> {result["seed"]}
<strong>Steps:</strong> {result["steps"]}
<strong>Generation Time:</strong> {result["generation_time"]:.2f} seconds
</div>"""
            
            # Generate commands for reusing this seed
            # Build the base command with all necessary flags
            base_cmd = f"./mflux-wrapper.py --prompt \"{base_prompt}\" --model {args.model} --resolution {args.resolution}"
            
            # Add style if it was used
            if hasattr(args, 'style') and args.style:
                base_cmd += f" --style {args.style}"
            elif hasattr(args, 'style_desc'):
                # If we have a style description but no name, it was from a previous run
                # Include it in the prompt instead
                base_cmd = f"./mflux-wrapper.py --prompt \"{args.prompt}\" --model {args.model} --resolution {args.resolution}"
            
            # Add metadata flag if it was used
            if args.metadata:
                base_cmd += " --metadata"
            
            # Generate the refine and iterate commands
            refine_cmd = f"{base_cmd} --seed {result['seed']} --variations 1 --steps {result['steps']}"
            iterate_cmd = f"{base_cmd} --seed {result['seed']} --iterate 1,3,5,9"
            
            f.write(f"""    <div class="image-card">
        <h3>Image {result["index"]} (Seed: {result["seed"]})</h3>
        <img src="{image_filename}" alt="Generated image {result['index']}" data-full-image="{image_filename}" />
        {metadata_html}
        <div class="command">
            <strong>Exact Reproduction Command:</strong>
            <code>{refine_cmd}</code>
            <strong>Iterate Steps Command:</strong>
            <code>{iterate_cmd}</code>
        </div>
    </div>
""")
        
        f.write("""    </div>
<script>
document.querySelectorAll('.image-card img').forEach(img => {
    img.addEventListener('click', () => {
        window.open(img.getAttribute('data-full-image'), '_blank');
    });
});
</script>
</body>
</html>""")
    
    # Update or create the main index.html in the base directory
    update_main_index(base_dir)
    
    return run_html_path

def update_main_index(base_dir):
    """Update or create the main index.html that lists all runs."""
    index_path = os.path.join(base_dir, "index.html")
    
    # Get all run directories in reverse order (newest first)
    runs = sorted([d for d in os.listdir(base_dir) if d.startswith("run_")], 
                 key=lambda x: int(x.split("_")[1]), reverse=True)
    
    with open(index_path, "w") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>MFlux Generation Runs</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .run-list { display: flex; flex-direction: column; gap: 20px; }
        .run-item { border: 1px solid #ccc; padding: 15px; border-radius: 5px; }
        .image-grid { 
            display: flex; 
            flex-wrap: wrap; 
            gap: 10px; 
            margin-top: 10px; 
        }
        .image-grid a { 
            flex: 1 1 calc(33.333% - 10px);
            min-width: 250px;
            max-width: calc(33.333% - 10px);
            text-decoration: none;
        }
        .image-grid img { 
            width: 100%; 
            height: auto; 
            border-radius: 3px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .image-grid img:hover {
            transform: scale(1.02);
        }
        .run-header { display: flex; justify-content: space-between; align-items: center; }
        h1 { color: #333; }
        h2 { margin: 0; }
        .timestamp { color: #666; }
        .status { padding: 5px 10px; border-radius: 3px; display: inline-block; margin-left: 10px; }
        .in-progress { background: #fff3cd; color: #856404; }
        .complete { background: #d4edda; color: #155724; }
        .generation-time { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>MFlux Generation Runs</h1>
    <div class="run-list">
""")
        
        for run in runs:
            run_index = run.split("_")[1]
            run_dir = os.path.join(base_dir, run)
            run_path = os.path.join(run, "index.html")
            
            # Try to extract run info and status
            run_info = ""
            status_html = ""
            total_time = 0
            info_path = os.path.join(run_dir, "run_info.json")
            if os.path.exists(info_path):
                try:
                    with open(info_path, "r") as info_file:
                        info = json.load(info_file)
                        current_images = len(info.get('results', []))
                        total_variations = info.get('variations', 0)
                        
                        # Calculate total generation time if available
                        for result in info.get('results', []):
                            if 'generation_time' in result:
                                total_time += result['generation_time']
                        
                        time_info = f"<p class='generation-time'>Total generation time: {total_time:.2f} seconds</p>" if total_time > 0 else ""
                        
                        # Handle steps display for both normal and iteration mode
                        steps_info = info.get('steps')
                        if isinstance(steps_info, list):
                            steps_display = f"{','.join(map(str, steps_info))} (iterating)"
                        else:
                            steps_display = str(steps_info)
                        
                        run_info = f"""
                        <p><strong>Prompt:</strong> "{info['prompt']}"</p>
                        <p><strong>Model:</strong> {info['model']}, <strong>Steps:</strong> {steps_display}</p>
                        {time_info}
                        """
                        
                        is_complete = current_images == total_variations
                        status_html = f"""<span class="status {'complete' if is_complete else 'in-progress'}">
                            {f"Complete ({current_images}/{total_variations})" if is_complete else f"Generating... ({current_images}/{total_variations})"}
                        </span>"""
                except:
                    pass
            
            # Get all PNG images in the run directory
            images = sorted([f for f in os.listdir(run_dir) if f.endswith('.png')])
            image_grid = ""
            if images:
                image_grid = '<div class="image-grid">'
                for img in images:
                    img_path = os.path.join(run, img)
                    image_grid += f'<a href="{run_path}"><img src="{img_path}" alt="{img}" loading="lazy"></a>'
                image_grid += '</div>'
            
            f.write(f"""        <div class="run-item">
            <div class="run-header">
                <h2>Run {run_index}{status_html}</h2>
                <span class="timestamp">{datetime.datetime.fromtimestamp(os.path.getctime(run_dir)).strftime('%Y-%m-%d %H:%M:%S')}</span>
            </div>
            {run_info}
            <a href="{run_path}">View Details</a>
            {image_grid}
        </div>
""")
        
        f.write("""    </div>
</body>
</html>""")

def save_run_info(run_dir, args, results):
    """Save run information for future reference."""
    # Collect all relevant arguments
    command_args = {
        "prompt": args.prompt,
        "model": args.model,
        "resolution": args.resolution,
        "metadata": args.metadata,
        "style": args.style if hasattr(args, 'style') else None,
        "steps": args.steps if args.steps is not None else get_default_steps(args.model),
        "iterate": args.iterate if hasattr(args, 'iterate') else None,
    }
    
    info = {
        "timestamp": datetime.datetime.now().isoformat(),
        "prompt": args.prompt,
        "model": args.model,
        "steps": args.steps if args.steps is not None else get_default_steps(args.model),
        "resolution": args.resolution,
        "variations": args.variations,
        "command_args": command_args,  # Store all arguments for reproduction
        "results": [{
            "index": result["index"],
            "seed": result["seed"],
            "steps": result["steps"],
            "file_path": os.path.basename(result["file_path"]),
            "generation_time": result.get("generation_time", 0)
        } for result in results]
    }
    
    with open(os.path.join(run_dir, "run_info.json"), "w") as f:
        json.dump(info, f, indent=2)

def check_live_server():
    """Check if live-server is available."""
    try:
        result = subprocess.run(['pnpx', 'live-server', '--version'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              text=True,
                              timeout=2)  # Timeout after 2 seconds
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def main():
    """Main function to execute the tool."""
    args = parse_args()
    
    # Create directory structure
    base_dir, run_dir = create_output_directories(args)
    print(f"Created run directory: {run_dir}")
    
    # Start live-server if watching is enabled and available
    live_server_process = None
    if not args.no_watch:
        if check_live_server():
            try:
                print(f"\nStarting live-server for {base_dir}...")
                live_server_process = subprocess.Popen(['pnpx', 'live-server', base_dir])
                print("Live-server started. Your browser will refresh automatically as images are generated.")
            except Exception as e:
                print(f"\nWarning: Could not start live-server: {e}")
                live_server_process = None
        else:
            print("\nLive-server not found. To enable live preview, install it with:")
            print("  npm install -g live-server")
    
    try:
        # Generate images
        results = generate_images(args, run_dir)
        
        # Final HTML update is already done in generate_images
        print(f"\nGeneration complete!")
        print(f"Generated {len(results)} variations")
        print(f"Results saved to: {run_dir}")
        print(f"View results: {os.path.join(run_dir, 'index.html')}")
        
        if live_server_process:
            print("\nStopping live-server...")
            live_server_process.terminate()
            live_server_process.wait()
            print("Live-server stopped.")
        elif not args.no_watch:
            print("\nTo monitor changes in real-time, install and run:")
            print("  npm install -g live-server")
            print(f"  pnpx live-server {base_dir}")
    
    except KeyboardInterrupt:
        print("\nGeneration interrupted!")
        if live_server_process:
            print("Stopping live-server...")
            live_server_process.terminate()
            live_server_process.wait()
            print("Live-server stopped.")
        raise

if __name__ == "__main__":
    main()

    