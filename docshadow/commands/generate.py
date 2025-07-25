"""
docShadow generate command - Generate documentation manually
"""

import json
from pathlib import Path
import click

from ..generator import generate_documentation


def generate_command(commit_hash=None):
    """
    Generate documentation for current or specified commit.
    
    Args:
        commit_hash: Optional commit hash to generate docs for
    """
    # Check if docShadow is initialized
    if not Path("docshadow.config.json").exists():
        click.echo("❌ Error: docShadow not initialized. Run 'doc init' first.", err=True)
        return False
    
    # Load configuration
    try:
        with open("docshadow.config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        click.echo(f"❌ Error loading configuration: {e}", err=True)
        return False
    
    # Generate documentation
    success = generate_documentation(commit_hash)
    
    if success:
        click.echo("🎉 Documentation generation completed!")
    else:
        click.echo("❌ Documentation generation failed.")
    
    return success 