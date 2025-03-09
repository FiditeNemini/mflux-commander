"""Prompt brainstorming functionality for MFlux Commander."""

import subprocess
from pathlib import Path
from typing import List

class Brainstormer:
    """Handles prompt brainstorming using Claude via llm command."""
    
    def __init__(self):
        self.validate_llm()
            
    def validate_llm(self):
        """Validate that llm command is available."""
        try:
            subprocess.run(['llm', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise ValueError("'llm' command not found. Please install it first: pip install llm")
            
    def generate_variations(self, concept: str, num_variations: int = 5) -> List[str]:
        """Generate creative prompt variations for a concept."""
        
        prompt = f"""Generate {num_variations} creative and detailed image prompts based on the concept: "{concept}"
        Each prompt should be unique and explore different aspects or interpretations of the concept.
        Focus on vivid, visual descriptions that would work well for image generation.
        Return only the prompts, one per line."""
        
        try:
            result = subprocess.run(
                ['llm', '-m', 'claude-3.7-sonnet', prompt],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Extract prompts from response
            prompts = [line.strip() for line in result.stdout.split("\n") 
                      if line.strip() and not line.startswith(("#", "-"))]
            
            return prompts[:num_variations]
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Brainstorming failed: {str(e)}")
            
    def format_results(self, prompts: List[str]) -> str:
        """Format brainstorming results for display."""
        output = ["Generated Prompts:", "-" * 40]
        for i, prompt in enumerate(prompts, 1):
            output.append(f"{i}. {prompt}")
        output.append("-" * 40)
        return "\n".join(output) 