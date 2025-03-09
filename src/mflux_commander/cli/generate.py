import click
import sys
from typing import Optional
from mflux_commander.session import Session
from mflux_commander.generator import Generator

@click.option("--prompt", required=True, help="The prompt to generate from")
@click.option("--iterations", default=1, help="Number of images to generate")
@click.option("--seed", type=int, help="Random seed for reproducibility")
@click.option("--force-new-session", is_flag=True, help="Force creation of new session")
def generate(prompt: str, iterations: int, seed: Optional[int], force_new_session: bool):
    """Generate images from a prompt."""
    try:
        session = Session(force_new=force_new_session)
        generator = Generator(session)
        
        run_dir = generator.generate(
            prompt=prompt,
            iterations=iterations,
            seed=seed
        )
        
        click.echo(f"Generated {iterations} image(s) in {run_dir}")
        click.echo(f"View results at {run_dir.parent}/index.html")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1) 