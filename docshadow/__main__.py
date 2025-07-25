#!/usr/bin/env python3
"""
docShadow CLI - Main entry point

Usage:
    doc init             # Initialize docShadow in current repo
    doc generate         # Generate documentation for current commit
    doc status           # Show docShadow status
"""

import click
import os
import sys
from pathlib import Path

from .commands.init import init_command
from .commands.generate import generate_command
from .commands.status import status_command


@click.group()
@click.version_option(version="0.1.0", prog_name="docShadow")
@click.pass_context
def cli(ctx):
    """
    docShadow CLI - Silent companion for Git documentation generation.
    
    Automatically generates JSON documentation for every Git commit.
    """
    # Ensure we're in a git repository for most commands
    if ctx.invoked_subcommand not in ['init'] and not Path('.git').exists():
        click.echo("❌ Error: Not in a Git repository. Run 'git init' first.", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def init(ctx):
    """Initialize docShadow in the current Git repository."""
    init_command()


@cli.command()
@click.option('--commit', '-c', help='Generate docs for specific commit hash')
@click.pass_context 
def generate(ctx, commit):
    """Generate documentation for current or specified commit."""
    generate_command(commit)


@cli.command()
@click.pass_context
def status(ctx):
    """Show docShadow status and missing documentation."""
    status_command()


if __name__ == '__main__':
    cli() 