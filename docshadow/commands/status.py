"""
docShadow status command - Show docShadow status and info
"""

import json
from pathlib import Path
import click

from ..utils import get_git_repo, get_python_files, load_docignore


def status_command():
    """Show docShadow status and information."""
    
    click.echo("📊 docShadow Status")
    click.echo("=" * 20)
    
    # Check if initialized
    if not Path("docshadow.config.json").exists():
        click.echo("❌ docShadow not initialized")
        click.echo("   Run 'doc init' to initialize.")
        return
    
    click.echo("✅ docShadow initialized")
    
    # Load and display configuration
    try:
        with open("docshadow.config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        click.echo()
        click.echo("📋 Configuration:")
        click.echo(f"   Project: {config.get('project_name', 'Unknown')}")
        click.echo(f"   Languages: {', '.join(config.get('languages', []))}")
        click.echo(f"   Output dir: {config.get('output_dir', '.docshadow/')}")
        click.echo(f"   Post-commit hook: {'Enabled' if config.get('hooks', {}).get('post_commit', False) else 'Disabled'}")
        
    except Exception as e:
        click.echo(f"⚠️  Warning: Could not load configuration: {e}")
    
    # Check Git repository
    repo = get_git_repo()
    if not repo:
        click.echo("❌ Not in a Git repository")
        return
    
    click.echo()
    click.echo("📁 Git Repository:")
    try:
        current_commit = repo.head.commit
        click.echo(f"   Current commit: {current_commit.hexsha[:7]}")
        click.echo(f"   Branch: {repo.active_branch.name}")
        click.echo(f"   Last commit: {current_commit.message.strip()[:50]}...")
    except Exception as e:
        click.echo(f"   ⚠️  Could not get Git info: {e}")
    
    # Check files to document
    click.echo()
    click.echo("📄 Files to document:")
    
    docignore_spec = load_docignore()
    python_files = get_python_files(docignore_spec=docignore_spec)
    
    if python_files:
        click.echo(f"   Found {len(python_files)} Python files:")
        for py_file in python_files[:10]:  # Show first 10
            click.echo(f"     • {py_file}")
        if len(python_files) > 10:
            click.echo(f"     ... and {len(python_files) - 10} more")
    else:
        click.echo("   ⚠️  No Python files found")
    
    # Check documentation status
    click.echo()
    click.echo("📚 Documentation status:")
    
    docshadow_dir = Path(".docshadow")
    if docshadow_dir.exists():
        # Check if index.json exists
        index_file = docshadow_dir / "index.json"
        if index_file.exists():
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    index_data = json.load(f)
                click.echo(f"   Last documented commit: {index_data.get('short_commit', 'Unknown')}")
                click.echo(f"   Documentation date: {index_data.get('date', 'Unknown')}")
                click.echo(f"   Documented files: {len(index_data.get('files', []))}")
            except Exception as e:
                click.echo(f"   ⚠️  Could not read index.json: {e}")
        else:
            click.echo("   ⚠️  No documentation generated yet")
            click.echo("   Run 'doc generate' to create documentation")
        
        # Check for docshadow.json
        structure_file = docshadow_dir / "docshadow.json"
        if structure_file.exists():
            click.echo(f"   ✅ Project structure mapping available")
        else:
            click.echo(f"   ⚠️  Project structure mapping missing")
    else:
        click.echo("   ❌ .docshadow/ directory not found")
    
    # Check Git hook
    click.echo()
    click.echo("🔗 Git hook status:")
    hook_file = Path(".git/hooks/post-commit")
    if hook_file.exists():
        try:
            with open(hook_file, "r", encoding="utf-8") as f:
                hook_content = f.read()
            if "docShadow" in hook_content:
                click.echo("   ✅ Post-commit hook installed")
            else:
                click.echo("   ⚠️  Post-commit hook exists but not for docShadow")
        except Exception as e:
            click.echo(f"   ⚠️  Could not read hook file: {e}")
    else:
        click.echo("   ❌ Post-commit hook not installed")
        click.echo("   Run 'doc init' to install the hook")
    
    click.echo()
    click.echo("💡 Next steps:")
    if not python_files:
        click.echo("   • Add Python files to your project")
    elif not docshadow_dir.exists() or not (docshadow_dir / "index.json").exists():
        click.echo("   • Run 'doc generate' to create documentation")
    else:
        click.echo("   • Make changes and commit to auto-generate docs")
        click.echo("   • Or run 'doc generate' to update documentation manually") 