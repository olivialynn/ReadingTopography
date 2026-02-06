"""
Data ingestion module for Reading Topography.

This module provides functions for loading, normalizing, and deduplicating
Goodreads CSV exports.
"""

import pandas as pd
import re
import logging
from typing import Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def normalize_title(title: str) -> str:
    """
    Normalize a book title for consistent matching.
    
    Applies lowercase, strips whitespace, and handles common punctuation.
    
    Args:
        title: Raw book title
        
    Returns:
        Normalized title string
    """
    if pd.isna(title) or not isinstance(title, str):
        return ""
    
    # Convert to lowercase and strip whitespace first
    normalized = title.lower().strip()
    
    # Remove articles at the beginning (a, an, the)
    normalized = re.sub(r'^(a|an|the)\s+', '', normalized)
    
    # Replace multiple spaces with single space
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Remove common punctuation but keep apostrophes
    normalized = re.sub(r'[-.,;:!?"""''—–]+', '', normalized)
    
    # Strip again to handle any trailing whitespace from punctuation removal
    normalized = normalized.strip()
    
    return normalized


def normalize_author(author: str) -> str:
    """
    Normalize an author name for consistent matching.
    
    Applies lowercase, strips whitespace, and handles common variations.
    
    Args:
        author: Raw author name
        
    Returns:
        Normalized author string
    """
    if pd.isna(author) or not isinstance(author, str):
        return ""
    
    # Convert to lowercase
    normalized = author.lower()
    
    # Replace multiple spaces with single space
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Remove periods (for initials like J.R.R. -> jrr)
    normalized = re.sub(r'\.', '', normalized)
    
    # Remove common punctuation
    normalized = re.sub(r'[-,;:!?"""''—–]+', '', normalized)
    
    # Strip leading/trailing whitespace
    normalized = normalized.strip()
    
    return normalized


def load_goodreads_csv(
    filepath: str,
    required_fields: Optional[list] = None,
    filter_shelf: Optional[str] = "to-read"
) -> pd.DataFrame:
    """
    Load a Goodreads CSV export with validation and optional filtering.
    
    Args:
        filepath: Path to the Goodreads CSV file
        required_fields: List of required column names (defaults to ['Title', 'Author'])
        filter_shelf: Filter to specific shelf (e.g., 'to-read'). 
                     Set to None to include all books.
    
    Returns:
        DataFrame with validated columns
        
    Raises:
        ValueError: If required fields are missing
        FileNotFoundError: If file doesn't exist
    """
    if required_fields is None:
        required_fields = ['Title', 'Author']
    
    # Load CSV
    try:
        df = pd.read_csv(filepath)
        logger.info(f"Loaded {len(df)} books from {filepath}")
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        raise
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        raise
    
    # Validate required fields
    missing_fields = [field for field in required_fields if field not in df.columns]
    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")
    
    # Filter by shelf if specified
    if filter_shelf:
        shelf_column = None
        # Check for various shelf column names
        for col in ['Exclusive Shelf', 'Bookshelves', 'Shelf']:
            if col in df.columns:
                shelf_column = col
                break
        
        if shelf_column:
            original_count = len(df)
            df = df[df[shelf_column].str.contains(filter_shelf, case=False, na=False)]
            filtered_count = len(df)
            logger.info(f"Filtered to '{filter_shelf}' shelf: {filtered_count}/{original_count} books")
    
    return df


def deduplicate_books(df: pd.DataFrame) -> pd.DataFrame:
    """
    Deduplicate books based on normalized identifiers.
    
    Prefers ISBN13 if present, otherwise uses normalized title+author.
    Keeps the first occurrence of each duplicate.
    
    Args:
        df: DataFrame with title_norm, author_norm, and optionally isbn13
        
    Returns:
        Deduplicated DataFrame with duplicate count logged
    """
    original_count = len(df)
    
    # Create a deduplication key
    # Prefer ISBN13 if available, else use title_norm + author_norm
    df['_dedup_key'] = df.apply(
        lambda row: (
            f"isbn13:{row['isbn13']}" 
            if pd.notna(row.get('isbn13')) and row.get('isbn13') != ''
            else f"title_author:{row['title_norm']}|{row['author_norm']}"
        ),
        axis=1
    )
    
    # Keep first occurrence
    df_deduped = df.drop_duplicates(subset=['_dedup_key'], keep='first')
    
    # Remove temporary column
    df_deduped = df_deduped.drop(columns=['_dedup_key'])
    
    # Log results
    duplicates_removed = original_count - len(df_deduped)
    if duplicates_removed > 0:
        logger.info(f"Removed {duplicates_removed} duplicate(s). {len(df_deduped)} unique books remain.")
    else:
        logger.info(f"No duplicates found. {len(df_deduped)} books.")
    
    return df_deduped.reset_index(drop=True)


def process_goodreads_csv(
    filepath: str,
    filter_shelf: Optional[str] = "to-read"
) -> pd.DataFrame:
    """
    Complete pipeline: load, normalize, and deduplicate Goodreads CSV.
    
    Args:
        filepath: Path to the Goodreads CSV file
        filter_shelf: Filter to specific shelf (e.g., 'to-read'). 
                     Set to None to include all books.
    
    Returns:
        Clean DataFrame with normalized fields and no duplicates
    """
    # Load CSV
    df = load_goodreads_csv(filepath, filter_shelf=filter_shelf)
    
    # Normalize fields
    df['title_norm'] = df['Title'].apply(normalize_title)
    df['author_norm'] = df['Author'].apply(normalize_author)
    
    # Handle ISBN13 - ensure it's present even if empty
    if 'ISBN13' in df.columns:
        df['isbn13'] = df['ISBN13'].astype(str).replace('nan', '')
    elif 'ISBN' in df.columns:
        # Fallback to ISBN if ISBN13 not available
        df['isbn13'] = df['ISBN'].astype(str).replace('nan', '')
        logger.info("Using ISBN field as isbn13 (ISBN13 column not found)")
    else:
        df['isbn13'] = ''
        logger.info("No ISBN column found, isbn13 will be empty")
    
    # Deduplicate
    df = deduplicate_books(df)
    
    logger.info("Processing complete")
    
    return df
