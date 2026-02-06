# Technical Design Document (TDD)
## Reading Topography (Notebook-First MVP)

---

## 0. References
- Architecture Overview: Reading Topography
- ADR-001: Notebook-First MVP with No Backend
- ADR-002: Readability Metrics as Approximate Proxies for Difficulty

---

## 1. Purpose
Define an implementation-ready design for the notebook-first MVP of Reading Topography: ingest a Goodreads "Want to Read" export, enrich books via public APIs, estimate difficulty via readability metrics when possible, and render an interactive Plotly scatter plot.

---

## 2. Scope

### In Scope (MVP)
- Manual import of Goodreads CSV export
- Book resolution and metadata enrichment via:
  - Google Books (primary)
  - Open Library (secondary)
- Difficulty estimation:
  - Compute Flesch–Kincaid Grade Level when text sample exists
  - Always label provenance (`computed`, `imputed`, `missing`)
- Visualization:
  - Plotly interactive scatter
  - Hover tooltip with key book info + link to Goodreads
  - Dot size encodes length when available (pages preferred)

### Out of Scope (MVP)
- Persistent user accounts, authentication
- Backend services / databases
- Other shelves (e.g., "Read") beyond filtering the imported CSV if present
- Alternative rating sources (StoryGraph/Amazon)
- Recommendations / ranking engine

---

## 3. Assumptions & Constraints
- Notebook-first execution (ADR-001)
- Difficulty metrics are approximate (ADR-002)
- External APIs can be rate-limited and incomplete; design must degrade gracefully
- Cost sensitivity: no paid infrastructure

---

## 4. High-Level Flow
1. Load Goodreads CSV
2. Normalize book identifiers (title/author/ISBN)
3. Resolve each book to external IDs + metadata
4. Acquire a text sample (if available) and compute readability
5. Assemble a unified dataframe with ratings + difficulty + length + links
6. Render Plotly scatter with provenance flags and hover tooltips
7. Cache enrichment results locally to speed reruns

---

## 5. Components

### 5.1 Notebook Sections (recommended structure)
1. **Setup**
   - imports, configuration, API keys (optional)
2. **Load Goodreads**
   - read CSV, validate required fields
3. **Normalize & Deduplicate**
   - normalize title/author, dedupe books
4. **Enrichment**
   - Google Books lookup
   - Open Library fallback lookup
5. **Difficulty Estimation**
   - readability computation for available text samples
   - imputation / missing classification
6. **Visualization**
   - interactive scatter + filters
7. **Export (optional)**
   - write enriched dataset to CSV/Parquet for reuse

---

## 6. Data Model

### 6.1 Input Schema (Goodreads CSV)
Minimum required fields (best-effort; tolerate variations):
- `Title`
- `Author`
Optional but useful:
- `ISBN`, `ISBN13`
- `Average Rating` (or compute via enrichment if absent)
- `My Rating` (ignored for MVP)
- `Bookshelves` / `Exclusive Shelf` (use to filter "to-read")

### 6.2 Internal Canonical Record
Each book becomes one row with canonical fields:

**Identifiers**
- `title_raw`, `author_raw`
- `title_norm`, `author_norm`
- `isbn13` (nullable)
- `goodreads_book_id` (nullable; if present in export)

**Ratings**
- `rating_avg` (float, nullable)
- `rating_count` (int, nullable)
- `rating_source` (enum: `goodreads_csv`, `google_books`, `open_library`, `missing`)

**Length**
- `page_count` (int, nullable)
- `length_source` (enum: `google_books`, `open_library`, `missing`)

**Difficulty**
- `fk_grade` (float, nullable)
- `flesch_reading_ease` (float, nullable)
- `difficulty_status` (enum: `computed`, `imputed`, `missing`)
- `difficulty_source` (enum: `google_books_text`, `open_library_text`, `imputed_metadata`, `missing`)

**Links**
- `goodreads_url` (nullable; derived if ID present, else absent)
- `google_books_url` (nullable)
- `open_library_url` (nullable)

**Diagnostics**
- `match_confidence` (float 0–1 or categorical; optional)
- `enrichment_errors` (string; optional)

---

## 7. Enrichment Design

### 7.1 Lookup Strategy (deterministic order)
For each book:
1. If `isbn13` exists:
   - Google Books query by ISBN
   - If not found: Open Library by ISBN
2. Else:
   - Google Books query by `(intitle:title + inauthor:author)`
   - If low confidence or not found: Open Library search by title+author

### 7.2 Match Confidence Heuristic (simple, explainable)
Assign a confidence score based on:
- exact/near-exact normalized title match
- author last-name match
- publication year similarity (if present)
- ISBN match (highest)
Store `match_confidence` and allow the notebook to show a small "low confidence" warning count.

### 7.3 Text Sample Acquisition
Best-effort sources (in order):
- Google Books `searchInfo.textSnippet` (easy but short; HTML-stripped)
- If available: additional snippet fields (varies)
- Open Library description/excerpts if present

Implementation note:
- Snippets are often short; readability metrics will be noisier. This is acceptable per ADR-002 but must be flagged.

---

## 8. Readability Computation

### 8.1 Metrics
- Flesch–Kincaid Grade Level (primary)
- Flesch Reading Ease (secondary)

### 8.2 Text Cleaning
- Strip HTML tags
- Normalize whitespace
- Remove non-content boilerplate when obvious (minimal heuristics)

### 8.3 Minimal Requirements for "computed"
- Minimum character count threshold (e.g., 400–800 chars) OR minimum sentence count (e.g., >= 5)
- If below threshold:
  - still compute but mark `difficulty_status=imputed` or `missing` depending on policy
Recommended policy:
- Compute if text exists, but if too short mark as `computed_low_confidence` (optional) or treat as `imputed`

(If you want to keep enums simpler: keep `computed` but store `text_length_chars` and treat low text length as a filter in the viz.)

---

## 9. Handling Missing Data (must be visible)
- If difficulty missing:
  - plot point remains visible
  - encoded distinctly (marker symbol or separate trace)
  - tooltip shows "Difficulty: unavailable"
- If rating missing:
  - keep visible but plot requires x-value; either:
    - place in a separate "missing rating" panel, or
    - exclude from scatter and report count
Recommended MVP:
- Require rating for scatter; keep a separate summary table for "missing rating".

---

## 10. Caching & Reproducibility

### 10.1 Cache Goals
- Avoid repeated API calls on reruns
- Make results stable across sessions when inputs unchanged

### 10.2 Cache Design
- Local on-disk cache keyed by a stable hash:
  - prefer `isbn13`
  - else hash of `title_norm|author_norm`
- Store as JSON per book and/or a single `cache.parquet`

Suggested files:
- `cache/enrichment.jsonl` (append-only per run) or
- `cache/books.parquet` (overwrite each run)

### 10.3 Rebuild Rules
- If user uploads new CSV, re-run normalization and merge with cache
- Only query external sources for books not already cached OR cached with low confidence and user opts to refresh

---

## 11. Visualization (Plotly)

### 11.1 Scatter Spec
- x: `rating_avg`
- y: `fk_grade`
- size: `page_count` (if null, use constant)
- color: `difficulty_status` (computed / imputed / missing)
- hover:
  - Title, author
  - Rating + count
  - FK grade + provenance
  - Page count
  - Link(s)

### 11.2 Filters (MVP)
- Shelf filter (to-read vs others if present)
- Toggle visibility for:
  - computed
  - imputed
  - missing

Implementation options:
- Plotly dropdown menus
- Or simple dataframe filtering + re-render cell

---

## 12. Error Handling & Rate Limits
- All external calls must be wrapped with:
  - timeout
  - retry with backoff (small, capped)
  - graceful failure per-book (no global abort)
- Store error messages in `enrichment_errors` and continue
- Throttle requests (sleep or batch) to reduce rate-limit risk

---

## 13. Testing Strategy (Notebook-Appropriate)
Even notebook-first, keep core logic in importable functions to test.

### 13.1 Unit Tests (if you add a small package/module)
- Title/author normalization
- Matching confidence scoring
- Readability computation on known samples
- Cache key stability

### 13.2 Smoke Tests (notebook)
- Load small sample CSV (5–10 books)
- Verify pipeline completes with:
  - at least one computed difficulty
  - at least one missing difficulty
  - plot renders

---

## 14. Security & Privacy
- No credentials stored in the notebook output
- API keys (if used) loaded from environment variables
- No uploaded Goodreads data is transmitted anywhere except requests to public APIs for enrichment (based on title/author/ISBN)

---

## 15. Milestones (implementation plan)
1. CSV ingestion + normalization + dedupe
2. Google Books enrichment + cache
3. Open Library fallback + cache
4. Readability computation + provenance flags
5. Plotly scatter + hover + filters
6. Polish: summaries (coverage stats, missing counts), low-confidence matches report

---

## 16. Open Questions
- Which minimum text threshold (if any) should downgrade computed scores?
- Should imputation exist in MVP, or only computed/missing?
- How to handle books with no rating in input or enrichment?
- Desired output format for exporting enriched results (CSV vs Parquet)?
