"""Command line interface for MFlux Commander."""

import click
import webbrowser
import sys
from pathlib import Path
from typing import List, Optional

from ..core.config import config, Resolution
from ..core.session import Session
from ..core.styles import StyleManager
from ..core.generator import Generator
from ..core.brainstorm import Brainstormer
from ..utils.gallery import GalleryGenerator

@click.group()
def cli():
    """MFlux Commander - AI Image Generation Tool"""
    pass

@cli.command()
@click.option("--prompt", required=True, help="The prompt to generate from")
@click.option("--vary-seed", type=int, help="Generate N variations with different random seeds")
@click.option("--seed", type=int, help="Random seed for reproducibility")
@click.option("--vary-steps", help="Comma-separated list of step counts to iterate through (requires --seed)")
@click.option("--force-new-session", is_flag=True, help="Force creation of new session")
@click.option("--format", type=str, help="Resolution format (e.g., landscape, portrait, square_sm)")
@click.option("--style", type=str, help="Style to apply")
def generate(prompt: str, vary_seed: Optional[int], seed: Optional[int], vary_steps: Optional[str], 
            force_new_session: bool, format: Optional[str], style: Optional[str]):
    """Generate images from a prompt."""
    try:
        session = Session(force_new=force_new_session)
        generator = Generator(session)
        
        # Apply resolution format if specified
        if format:
            resolution = config.get_resolution(format)
            generator.width = resolution.width
            generator.height = resolution.height
            
        # Apply style if specified
        if style:
            style_manager = StyleManager()
            style_description = style_manager.get_style(style)
            if style_description:
                prompt = f"{prompt}, {style_description}"
            else:
                click.echo(f"Warning: Style '{style}' not found")
        
        # Parse vary_steps if provided
        step_list = None
        if vary_steps:
            if not seed:
                raise click.UsageError("--vary-steps requires --seed to be set")
            try:
                step_list = [int(s.strip()) for s in vary_steps.split(",")]
            except ValueError:
                raise click.UsageError("--vary-steps must be comma-separated integers (e.g., '1,3,5,9')")
        
        # Generate images
        if step_list:
            # Generate variations with different step counts
            results = generator.generate_variations(
                prompt=prompt,
                base_seed=seed,
                vary_steps=step_list
            )
            click.echo(f"Generated {len(step_list)} step variations in {results[0].parent}")
        elif vary_seed:
            # Generate variations with different seeds
            results = generator.generate_variations(
                prompt=prompt,
                iterations=vary_seed
            )
            click.echo(f"Generated {vary_seed} seed variations in {results[0].parent}")
        else:
            # Single generation or fixed seed
            run_dir = generator.generate(
                prompt=prompt,
                iterations=1,
                seed=seed
            )
            click.echo(f"Generated image in {run_dir}")
            
        click.echo(f"View results at {session.current_session_dir}/index.html")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('name')
@click.argument('description')
def save_style(name: str, description: str):
    """Save a new style."""
    style_manager = StyleManager()
    style_manager.save_style(name, description)
    click.echo(f"Saved style '{name}'")

@cli.command()
def list_styles():
    """List all available styles."""
    style_manager = StyleManager()
    styles = style_manager.list_styles()
    
    if not styles:
        click.echo("No styles found.")
        return
        
    click.echo("\nAvailable Styles:")
    click.echo("-" * 40)
    for style in styles:
        click.echo(f"{style['name']}: {style['description']}")
    click.echo("-" * 40)

@cli.command()
@click.argument('concept')
def brainstorm(concept: str):
    """Generate prompt variations for a concept."""
    try:
        brainstormer = Brainstormer()
        prompts = brainstormer.generate_variations(concept)
        
        # Save results to current session
        session = Session()
        session.save_brainstorm_results(prompts)
        
        # Display results
        click.echo(brainstormer.format_results(prompts))
        
    except ValueError as e:
        click.echo(f"Error: {str(e)}")
        click.echo("Please set the ANTHROPIC_API_KEY environment variable.")
    except Exception as e:
        click.echo(f"Error: {str(e)}")

@cli.command()
@click.argument('indices')
def run_prompts(indices: str):
    """Run specific prompts from last brainstorm."""
    session = Session()
    prompts = session.load_brainstorm_results()
    
    if not prompts:
        click.echo("No brainstorm results found.")
        return
        
    try:
        # Parse indices (e.g., "1,3,5")
        idx_list = [int(i.strip()) - 1 for i in indices.split(',')]
        selected_prompts = [prompts[i] for i in idx_list if 0 <= i < len(prompts)]
        
        for prompt in selected_prompts:
            click.echo(f"\nGenerating: {prompt}")
            generate.callback(prompt=prompt, iterations=1, seed=None, force_new_session=False)
            
    except (ValueError, IndexError):
        click.echo("Invalid indices. Please provide comma-separated numbers (e.g., '1,3,5')")

if __name__ == "__main__":
    cli() 