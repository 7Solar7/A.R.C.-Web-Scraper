# A.R.C. — Automated Retrieval of Chapters

A Python CLI tool that scrapes web novel chapters from akknovel.com and saves them as numbered UTF-8 text files locally. Walks chapter URLs via Previous/Next navigation links, extracts clean text content, and handles transient errors with retry logic.

## Installation

```bash
git clone <repo>
cd web-scraper
pip install -e .
```

For development (includes pytest + responses for mocking):

```bash
pip install -e ".[dev]"
```

## Quick Start

Scrape chapters 1–5 of a series:

```bash
python -m arc "https://www.akknovel.com/series/..." --start 1 --end 5
```

Scrape a specific range to a custom directory, overwriting existing files:

```bash
python -m arc "https://www.akknovel.com/series/..." --start 703 --end 704 --output ./my-chapters --force
```

## CLI Reference

| Argument | Default | Description |
|----------|---------|-------------|
| `series_url` | (required) | URL of the series page on akknovel.com |
| `--start N` | `1` | Starting chapter number |
| `--end N` | all chapters | Ending chapter number (omit for all) |
| `--output DIR, -o DIR` | `./chapters` | Output directory |
| `--delay SECS` | `1.0` | Delay between requests in seconds |
| `--retries N` | `3` | Max retries on 5xx/timeout (exponential backoff) |
| `--force, -f` | off | Overwrite existing files without warning |

## Output Format

```
chapters/
  chapter_001.txt
  chapter_002.txt
  chapter_003.txt
```

Each file starts with a `# Chapter N` header followed by the chapter's paragraph text, UTF-8 encoded.

## Architecture

```
arc/
├── __init__.py          # Package marker
├── __main__.py          # Entry point (python -m arc)
├── types.py             # Exit codes, constants, dataclasses (NovelInfo, ChapterInfo)
├── scraper.py           # RSS discovery, chapter walking, content extraction
├── output.py            # File naming, save/skip/force, UTF-8 output
└── cli.py               # argparse CLI, orchestration, error handling
```

**Discovery strategy**: RSS feed → chapter URLs → walk via Previous/Next navigation links.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid arguments |
| 2 | Network error (RSS unreachable, request failed, Cloudflare detected) |
| 3 | Content error (missing chapter, empty page, no text found) |
| 4 | File system error (can't write output) |

## Requirements

- Python 3.10+
- `requests >= 2.31`
- `beautifulsoup4 >= 4.12`

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -v      # 45 tests, all mocked, no live calls
```

The test suite uses the `responses` library to mock all HTTP requests against HTML fixtures saved from the live site (RSS feed, series page, chapter pages, error pages).

### Live Smoke Test

```bash
python scripts/live_smoke_test.py
```

Runs 8 checks against the real akknovel.com: validates RSS feed, fetches a real chapter, verifies CSS selectors match, checks for Cloudflare blocking.

## Project Structure

```
web-scraper/
├── arc/                   # Core Python package
│   ├── __init__.py
│   ├── __main__.py
│   ├── types.py
│   ├── scraper.py
│   ├── output.py
│   └── cli.py
├── tests/                 # Pytest test suite (45 tests)
│   ├── conftest.py        # Fixtures + HTML/XML test data
│   ├── fixtures/          # Static HTML from live akknovel.com
│   ├── test_types.py      # 11 tests
│   ├── test_scraper.py    # 13 tests
│   ├── test_output.py     # 11 tests
│   ├── test_cli.py        # 6 tests
│   └── test_integration.py # 4 tests
├── scripts/
│   └── live_smoke_test.py # Live site validation
├── pyproject.toml
├── README.md
└── .gitignore
```

## License

MIT License. See [LICENSE](LICENSE) for details.

## Disclaimer

Respect the website's `robots.txt`, rate limiting, and terms of service. This tool is for personal archival use only. I am not responsible for misuse.
