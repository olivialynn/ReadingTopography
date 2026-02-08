"""
Notebook utilities for Reading Topography.

This module provides helper functions for running notebooks in different
environments, including Google Colab, Jupyter, and local Python.
"""

import os
import sys
from pathlib import Path
from typing import Optional


def is_colab() -> bool:
    """
    Check if running in Google Colab environment.
    
    Returns:
        True if running in Colab, False otherwise
    """
    return 'google.colab' in sys.modules


def setup_colab_environment(repo_url: str = "https://github.com/olivialynn/ReadingTopography.git") -> None:
    """
    Setup Google Colab environment by cloning the repository.
    
    This function should be called once at the beginning of a notebook
    when running in Colab. It clones the repository to /content/ReadingTopography
    and adds the src directory to the Python path.
    
    Args:
        repo_url: URL of the GitHub repository to clone
    """
    if not is_colab():
        return
    
    import subprocess
    
    # Check if repository is already cloned
    repo_path = Path('/content/ReadingTopography')
    if repo_path.exists():
        print(f"✓ Repository already cloned at {repo_path}")
    else:
        # Clone the repository
        print(f"Cloning repository from {repo_url}...")
        subprocess.run(['git', 'clone', repo_url], cwd='/content', check=True)
        print(f"✓ Repository cloned to {repo_path}")
    
    # Add to Python path if not already there
    src_path = str(repo_path / 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
        print(f"✓ Added {src_path} to Python path")


def get_repo_root() -> Path:
    """
    Get the root directory of the Reading Topography repository.
    
    This function works in both local and Colab environments:
    - In Colab: /content/ReadingTopography
    - Locally: Finds the repo root by looking for the src directory
    
    Returns:
        Path object pointing to the repository root
        
    Raises:
        RuntimeError: If repository root cannot be determined
    """
    if is_colab():
        return Path('/content/ReadingTopography')
    
    # For local environment, start from current file and walk up
    current = Path(__file__).resolve()
    
    # Walk up the directory tree looking for the src directory
    for parent in [current.parent] + list(current.parents):
        if (parent / 'src').is_dir() and (parent / 'notebooks').is_dir():
            return parent
    
    # Fallback: try relative to current working directory
    cwd = Path.cwd()
    if (cwd / 'src').is_dir():
        return cwd
    
    # Check if we're in the notebooks directory
    if cwd.name == 'notebooks' and (cwd.parent / 'src').is_dir():
        return cwd.parent
    
    raise RuntimeError(
        "Could not determine repository root. "
        "Make sure you're running from within the ReadingTopography repository."
    )


def get_data_path(relative_path: str = '') -> Path:
    """
    Get the absolute path to a file or directory in the data folder.
    
    Works in both Colab and local environments by using get_repo_root().
    
    Args:
        relative_path: Path relative to the data directory (e.g., 'sample_goodreads.csv')
    
    Returns:
        Absolute Path object to the data file or directory
        
    Example:
        >>> csv_path = get_data_path('sample_goodreads.csv')
        >>> df = pd.read_csv(csv_path)
    """
    data_dir = get_repo_root() / 'data'
    if relative_path:
        return data_dir / relative_path
    return data_dir


def setup_notebook_environment(repo_url: Optional[str] = None) -> dict:
    """
    Complete notebook environment setup for both Colab and local environments.
    
    This is the main function to call at the beginning of a notebook.
    It handles:
    - Colab repository cloning (if in Colab)
    - Python path setup
    - Repository root detection
    
    Args:
        repo_url: Optional custom repository URL for Colab cloning
                 Defaults to the official ReadingTopography repository
    
    Returns:
        Dictionary with environment information:
        - 'is_colab': bool indicating if running in Colab
        - 'repo_root': Path to repository root
        - 'data_dir': Path to data directory
        
    Example:
        >>> env = setup_notebook_environment()
        >>> print(f"Data directory: {env['data_dir']}")
        >>> csv_path = env['data_dir'] / 'sample_goodreads.csv'
    """
    if repo_url is None:
        repo_url = "https://github.com/olivialynn/ReadingTopography.git"
    
    # Get repository paths
    # Note: Colab setup (repo cloning and path setup) should be done 
    # BEFORE importing this module to avoid ImportError
    repo_root = get_repo_root()
    data_dir = repo_root / 'data'
    
    environment = {
        'is_colab': is_colab(),
        'repo_root': repo_root,
        'data_dir': data_dir
    }
    
    # Print summary
    print("=" * 60)
    print("NOTEBOOK ENVIRONMENT")
    print("=" * 60)
    print(f"Environment: {'Google Colab' if environment['is_colab'] else 'Local'}")
    print(f"Repository root: {environment['repo_root']}")
    print(f"Data directory: {environment['data_dir']}")
    print("=" * 60)
    
    return environment
