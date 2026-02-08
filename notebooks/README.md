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

#### Option 1: Run on Google Colab (Recommended for Quick Start)

1. **Open the notebook in Colab**:
   - Click this link: [Open MVP Notebook in Colab](https://colab.research.google.com/github/olivialynn/ReadingTopography/blob/main/notebooks/mvp_notebook.ipynb)
   - Or go to [Google Colab](https://colab.research.google.com/) and use File → Open → GitHub → paste the notebook URL

2. **Run all cells**:
   - The notebook will automatically clone the repository and set up the environment
   - It will use the sample data from the repository by default
   - No manual path configuration needed!

3. **Optional - Use your own data**:
   - Export your Goodreads library as CSV (from Goodreads → My Books → Import/Export)
   - Upload it to Colab using the file browser on the left
   - Update the CSV path in cell 2:
     ```python
     CSV_PATH = '/content/your_goodreads_export.csv'
     ```

#### Option 2: Run Locally

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

4. **Optional - Use custom CSV**:
   - The notebook uses `sample_goodreads.csv` by default
   - To use your own data, update cell 2:
     ```python
     CSV_PATH = get_data_path('your_goodreads_export.csv')
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
============================================================
NOTEBOOK ENVIRONMENT
============================================================
Environment: Local (or Google Colab)
Repository root: /path/to/ReadingTopography
Data directory: /path/to/ReadingTopography/data
============================================================
✓ Setup complete

Loaded 10 books from /path/to/data/sample_goodreads.csv
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
