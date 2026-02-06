# Notebooks

This directory contains Jupyter notebooks for the Reading Topography project.

## MVP Notebook

**File**: `mvp_notebook.ipynb`

### Purpose
Implements the first milestone of the Reading Topography project: CSV ingestion, normalization, and deduplication of Goodreads "Want to Read" exports.

### Features
- Load Goodreads CSV exports with validation
- Normalize title and author fields for consistent matching
- Deduplicate books based on ISBN13 or normalized identifiers
- Filter to "to-read" shelf
- Comprehensive logging and statistics

### How to Use

1. **Install dependencies**:
   ```bash
   pip install -r ../requirements.txt
   ```

2. **Prepare your data**:
   - Export your Goodreads library as CSV (from Goodreads → My Books → Import/Export)
   - Place the CSV file in the `../data/` directory
   - Or use the provided sample: `../data/sample_goodreads.csv`

3. **Run the notebook**:
   ```bash
   jupyter notebook mvp_notebook.ipynb
   ```

4. **Update the CSV path** (cell 2):
   ```python
   CSV_PATH = '../data/your_goodreads_export.csv'
   ```

### Expected Output

The notebook will:
- Load and validate your Goodreads CSV
- Filter to books on your "to-read" shelf
- Normalize titles and author names
- Remove duplicate entries
- Display statistics about your reading list
- Output a clean DataFrame with `title_norm`, `author_norm`, and `isbn13` fields

### Sample Output

```
✓ Setup complete
Loaded 10 books from ../data/sample_goodreads.csv
Filtered to 'to-read' shelf: 9/10 books
Removed 1 duplicate(s). 8 unique books remain.

Total unique books: 8
ISBN Coverage: 8 (100.0%)
All titles normalized: True
All authors normalized: True
```

### Next Steps

Future milestones will add:
1. Metadata enrichment via Google Books and Open Library APIs
2. Difficulty estimation using readability metrics
3. Interactive Plotly visualization
4. Local caching for API results

See [../docs/tdd.md](../docs/tdd.md) for the full technical design.
