"""
Utility functions for docShadow CLI
"""

import os
import shutil
from pathlib import Path
import git
import pathspec
import click


def ensure_git_repo():
    """Check if current directory is a Git repository."""
    return Path(".git").exists()


def get_git_repo():
    """Get GitPython repository object for current directory."""
    try:
        return git.Repo(".")
    except git.InvalidGitRepositoryError:
        return None


def copy_gitignore_to_docignore():
    """Copy .gitignore to .docignore, or create basic .docignore if .gitignore doesn't exist."""
    gitignore_path = Path(".gitignore")
    docignore_path = Path(".docignore")
    
    if gitignore_path.exists():
        shutil.copy2(gitignore_path, docignore_path)
    else:
        # Create basic .docignore
        basic_docignore = """# docShadow ignore file
# Add patterns to exclude files from documentation generation

# Common patterns
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
build/
dist/
*.egg-info/
.pytest_cache/
.coverage
.tox/
.venv/
venv/

# Documentation
docs/
*.md
"""
        with open(docignore_path, "w", encoding="utf-8") as f:
            f.write(basic_docignore)


def load_docignore(docignore_path=".docignore"):
    """Load .docignore patterns and return pathspec object."""
    if not Path(docignore_path).exists():
        return None
    
    try:
        with open(docignore_path, "r", encoding="utf-8") as f:
            patterns = f.read().splitlines()
        return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
    except Exception as e:
        click.echo(f"⚠️  Warning: Could not load {docignore_path}: {e}")
        return None


def should_ignore_file(file_path, docignore_spec):
    """Check if a file should be ignored based on .docignore patterns."""
    if docignore_spec is None:
        return False
    return docignore_spec.match_file(file_path)


def get_python_files(directory=".", docignore_spec=None):
    """Get all Python files in directory, respecting .docignore."""
    python_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip hidden directories and git directory
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path)
                
                # Check if file should be ignored
                if not should_ignore_file(relative_path, docignore_spec):
                    python_files.append(relative_path)
    
    return python_files


def ensure_directory(path):
    """Ensure directory exists, create if necessary."""
    Path(path).mkdir(parents=True, exist_ok=True)


def get_commit_info(repo, commit_hash=None):
    """Get commit information."""
    if commit_hash:
        try:
            commit = repo.commit(commit_hash)
        except git.BadName:
            click.echo(f"❌ Error: Commit {commit_hash} not found.")
            return None
    else:
        commit = repo.head.commit
    
    return {
        "hash": commit.hexsha,
        "short_hash": commit.hexsha[:7],
        "message": commit.message.strip(),
        "author": str(commit.author),
        "date": commit.committed_datetime.isoformat(),
        "files_changed": list(commit.stats.files.keys()) if hasattr(commit, 'stats') else []
    } 