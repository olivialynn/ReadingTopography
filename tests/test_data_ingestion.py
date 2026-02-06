"""
Unit tests for data ingestion module.
"""

import pytest
import pandas as pd
import tempfile
import os
from src.data_ingestion import (
    normalize_title,
    normalize_author,
    load_goodreads_csv,
    deduplicate_books,
    process_goodreads_csv
)


class TestNormalization:
    """Tests for title and author normalization."""
    
    def test_normalize_title_basic(self):
        """Test basic title normalization."""
        assert normalize_title("The Great Gatsby") == "great gatsby"
        assert normalize_title("To Kill a Mockingbird") == "to kill a mockingbird"
        assert normalize_title("1984") == "1984"
    
    def test_normalize_title_punctuation(self):
        """Test title normalization with punctuation."""
        assert normalize_title("The Catcher in the Rye") == "catcher in the rye"
        assert normalize_title("Harry Potter: Book 1") == "harry potter book 1"
        assert normalize_title("Pride and Prejudice!") == "pride and prejudice"
    
    def test_normalize_title_whitespace(self):
        """Test title normalization with extra whitespace."""
        # Leading article "The" is removed, other articles like "A" are kept
        assert normalize_title("  The   Hobbit  ") == "hobbit"
        assert normalize_title("A\nBook\tTitle") == "book title"
    
    def test_normalize_title_empty(self):
        """Test title normalization with empty/null values."""
        assert normalize_title("") == ""
        assert normalize_title(None) == ""
        assert normalize_title(pd.NA) == ""
    
    def test_normalize_author_basic(self):
        """Test basic author normalization."""
        assert normalize_author("F. Scott Fitzgerald") == "f scott fitzgerald"
        assert normalize_author("J.R.R. Tolkien") == "jrr tolkien"
        assert normalize_author("George Orwell") == "george orwell"
    
    def test_normalize_author_punctuation(self):
        """Test author normalization with punctuation."""
        # Apostrophes are kept for contractions/possessives
        assert normalize_author("O'Brien, John") == "o'brien john"
        # Hyphens are removed
        assert normalize_author("Smith-Jones, Mary") == "smithjones mary"
    
    def test_normalize_author_empty(self):
        """Test author normalization with empty/null values."""
        assert normalize_author("") == ""
        assert normalize_author(None) == ""
        assert normalize_author(pd.NA) == ""


class TestLoadCSV:
    """Tests for CSV loading functionality."""
    
    def test_load_csv_basic(self):
        """Test basic CSV loading."""
        # Create temporary CSV
        csv_content = """Title,Author,ISBN13
The Great Gatsby,F. Scott Fitzgerald,9780743273565
1984,George Orwell,9780451524935
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            df = load_goodreads_csv(temp_path, filter_shelf=None)
            assert len(df) == 2
            assert 'Title' in df.columns
            assert 'Author' in df.columns
        finally:
            os.unlink(temp_path)
    
    def test_load_csv_missing_required_fields(self):
        """Test CSV loading with missing required fields."""
        csv_content = """Title,ISBN13
The Great Gatsby,9780743273565
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Missing required fields"):
                load_goodreads_csv(temp_path, filter_shelf=None)
        finally:
            os.unlink(temp_path)
    
    def test_load_csv_with_shelf_filter(self):
        """Test CSV loading with shelf filtering."""
        csv_content = """Title,Author,Exclusive Shelf
The Great Gatsby,F. Scott Fitzgerald,to-read
1984,George Orwell,read
The Hobbit,J.R.R. Tolkien,to-read
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            df = load_goodreads_csv(temp_path, filter_shelf="to-read")
            assert len(df) == 2
            assert "1984" not in df['Title'].values
        finally:
            os.unlink(temp_path)


class TestDeduplication:
    """Tests for deduplication functionality."""
    
    def test_deduplicate_by_isbn(self):
        """Test deduplication using ISBN13."""
        data = {
            'Title': ['Book 1', 'Book 1 Duplicate'],
            'Author': ['Author 1', 'Author 1'],
            'title_norm': ['book 1', 'book 1 duplicate'],
            'author_norm': ['author 1', 'author 1'],
            'isbn13': ['9780123456789', '9780123456789']
        }
        df = pd.DataFrame(data)
        
        result = deduplicate_books(df)
        assert len(result) == 1
        assert result.iloc[0]['Title'] == 'Book 1'
    
    def test_deduplicate_by_title_author(self):
        """Test deduplication using normalized title and author."""
        data = {
            'Title': ['The Great Gatsby', 'The Great Gatsby'],
            'Author': ['F. Scott Fitzgerald', 'F. Scott Fitzgerald'],
            'title_norm': ['great gatsby', 'great gatsby'],
            'author_norm': ['f scott fitzgerald', 'f scott fitzgerald'],
            'isbn13': ['', '']
        }
        df = pd.DataFrame(data)
        
        result = deduplicate_books(df)
        assert len(result) == 1
    
    def test_deduplicate_keeps_first(self):
        """Test that deduplication keeps the first occurrence."""
        data = {
            'Title': ['Book 1', 'Book 1 v2', 'Book 1 v3'],
            'Author': ['Author', 'Author', 'Author'],
            'title_norm': ['book 1', 'book 1', 'book 1'],
            'author_norm': ['author', 'author', 'author'],
            'isbn13': ['', '', '']
        }
        df = pd.DataFrame(data)
        
        result = deduplicate_books(df)
        assert len(result) == 1
        assert result.iloc[0]['Title'] == 'Book 1'
    
    def test_deduplicate_no_duplicates(self):
        """Test deduplication with no duplicates."""
        data = {
            'Title': ['Book 1', 'Book 2', 'Book 3'],
            'Author': ['Author 1', 'Author 2', 'Author 3'],
            'title_norm': ['book 1', 'book 2', 'book 3'],
            'author_norm': ['author 1', 'author 2', 'author 3'],
            'isbn13': ['', '', '']
        }
        df = pd.DataFrame(data)
        
        result = deduplicate_books(df)
        assert len(result) == 3


class TestFullPipeline:
    """Tests for the complete processing pipeline."""
    
    def test_process_goodreads_csv(self):
        """Test full processing pipeline."""
        csv_content = """Title,Author,ISBN13,Exclusive Shelf
The Great Gatsby,F. Scott Fitzgerald,9780743273565,to-read
The Great Gatsby,F. Scott Fitzgerald,9780743273565,to-read
1984,George Orwell,9780451524935,to-read
The Hobbit,J.R.R. Tolkien,,to-read
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            df = process_goodreads_csv(temp_path, filter_shelf="to-read")
            
            # Should have removed 1 duplicate
            assert len(df) == 3
            
            # Check normalized columns exist
            assert 'title_norm' in df.columns
            assert 'author_norm' in df.columns
            assert 'isbn13' in df.columns
            
            # Check normalization worked
            assert df[df['Title'] == 'The Great Gatsby']['title_norm'].iloc[0] == 'great gatsby'
            assert df[df['Author'] == 'F. Scott Fitzgerald']['author_norm'].iloc[0] == 'f scott fitzgerald'
        finally:
            os.unlink(temp_path)
