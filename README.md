# Reading Topography

A notebook-first exploratory data project to visualize your reading list by difficulty and rating.

## Features

### Current (Milestone 1: CSV Ingestion)
- ✅ Load Goodreads CSV exports with validation
- ✅ Normalize title and author fields for consistent matching
- ✅ Deduplicate books based on ISBN13 or normalized identifiers
- ✅ Filter to "to-read" shelf
- ✅ Comprehensive test coverage

### Coming Soon
- Metadata enrichment via Google Books and Open Library APIs
- Difficulty estimation using Flesch-Kincaid readability metrics
- Interactive Plotly visualization
- Local caching for API results

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the MVP notebook**:
   ```bash
   jupyter notebook notebooks/mvp_notebook.ipynb
   ```

3. **Or use the Python module directly**:
   ```python
   from src.data_ingestion import process_goodreads_csv
   
   df = process_goodreads_csv('data/sample_goodreads.csv')
   print(f"Loaded {len(df)} unique books")
   ```

## Project Structure

```
ReadingTopography/
├── notebooks/          # Jupyter notebooks
│   └── mvp_notebook.ipynb
├── src/               # Python modules
│   └── data_ingestion.py
├── tests/             # Unit tests
│   └── test_data_ingestion.py
├── data/              # CSV files (your Goodreads exports)
│   └── sample_goodreads.csv
├── cache/             # Cached API results (created automatically)
└── docs/              # Documentation
    └── tdd.md
```

## Running Tests

```bash
pytest tests/
```

## Documentation
- **[Technical Design Document](docs/tdd.md)** - Implementation-ready design for the MVP
- **[Notebooks README](notebooks/README.md)** - How to use the MVP notebook
- Architecture Decision Records (coming soon)

## Getting Started
See [notebooks/README.md](notebooks/README.md) for detailed instructions on using the MVP notebook.

## Contributing
See open issues for planned work following the milestones in [docs/tdd.md](docs/tdd.md).
