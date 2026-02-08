"""
Tests for notebook_utils module.
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.notebook_utils import (
    is_colab,
    get_repo_root,
    get_data_path,
    setup_notebook_environment
)


def test_is_colab_false():
    """Test is_colab returns False when not in Colab."""
    # Ensure 'google.colab' is not in sys.modules
    if 'google.colab' in sys.modules:
        del sys.modules['google.colab']
    
    assert is_colab() is False


def test_is_colab_true():
    """Test is_colab returns True when in Colab."""
    # Mock the presence of google.colab module
    sys.modules['google.colab'] = MagicMock()
    
    try:
        assert is_colab() is True
    finally:
        # Clean up
        if 'google.colab' in sys.modules:
            del sys.modules['google.colab']


def test_get_repo_root():
    """Test get_repo_root returns valid repository root."""
    # This should work in local environment
    if 'google.colab' in sys.modules:
        del sys.modules['google.colab']
    
    repo_root = get_repo_root()
    
    # Verify it's a valid repository root
    assert repo_root.is_dir()
    assert (repo_root / 'src').is_dir()
    assert (repo_root / 'notebooks').is_dir()
    assert (repo_root / 'data').is_dir()


def test_get_data_path_default():
    """Test get_data_path with no argument returns data directory."""
    data_path = get_data_path()
    
    assert data_path.is_dir()
    assert data_path.name == 'data'


def test_get_data_path_with_file():
    """Test get_data_path with filename returns correct path."""
    csv_path = get_data_path('sample_goodreads.csv')
    
    assert csv_path.name == 'sample_goodreads.csv'
    assert csv_path.parent.name == 'data'
    # The file should exist in the repo
    assert csv_path.exists()


def test_setup_notebook_environment_local():
    """Test setup_notebook_environment in local environment."""
    # Ensure not in Colab
    if 'google.colab' in sys.modules:
        del sys.modules['google.colab']
    
    env = setup_notebook_environment()
    
    # Verify returned dictionary
    assert 'is_colab' in env
    assert 'repo_root' in env
    assert 'data_dir' in env
    
    assert env['is_colab'] is False
    assert env['repo_root'].is_dir()
    assert env['data_dir'].is_dir()
    assert env['data_dir'].name == 'data'


@patch('subprocess.run')
def test_setup_colab_environment(mock_subprocess):
    """Test setup_colab_environment clones repository in Colab."""
    from src.notebook_utils import setup_colab_environment
    
    # Mock Colab environment
    sys.modules['google.colab'] = MagicMock()
    
    try:
        # Mock Path.exists to return False (repo not yet cloned)
        # Using a more specific patch to avoid affecting other Path objects
        with patch('src.notebook_utils.Path.exists', return_value=False):
            setup_colab_environment()
            
            # Verify git clone was called
            mock_subprocess.assert_called_once()
            call_args = mock_subprocess.call_args
            assert 'git' in call_args[0][0]
            assert 'clone' in call_args[0][0]
            assert 'https://github.com/olivialynn/ReadingTopography.git' in call_args[0][0]
    finally:
        # Clean up
        if 'google.colab' in sys.modules:
            del sys.modules['google.colab']


def test_get_data_path_subdirectory():
    """Test get_data_path with subdirectory path."""
    # Test with a potential subdirectory structure
    path = get_data_path('subfolder/file.csv')
    
    assert path.name == 'file.csv'
    assert path.parent.name == 'subfolder'
    assert path.parent.parent.name == 'data'
