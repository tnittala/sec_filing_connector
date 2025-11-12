# SEC Filing Connector

A Python module for fetching and filtering SEC EDGAR filings (using local JSON fixtures).  
Implements company lookup, filing filters, and a simple CLI — designed as part of the **DS@GT FinTech Project SEC API Assessment**.

---

## 📁 Project Structure

```
sec_filing_connector/
├── pyproject.toml
├── README.md
├── sec_connector/
│   ├── __init__.py
│   ├── models.py
│   ├── client.py
│   └── cli.py
└── tests/
    ├── test_client.py
    └── fixtures/
        ├── company_tickers.json
        └── filings_sample.json
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/tnittala/sec_filing_connector.git
cd sec_filing_connector
```

### 2️⃣ (Optional) Create and activate a virtual environment
**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install the package in editable mode
Run this **from the project root**:
```bash
pip install -e .
```

This installs the package along with all dependencies defined in `pyproject.toml`.

Dependencies include:
- Python ≥ 3.11  
- `pydantic>=2.0`  
- `httpx>=0.24`  
- `pytest>=7.0`

---

## 🧪 Running Tests

Once installed, run the full test suite with:
```bash
pytest -v
```

✅ This runs all tests in verbose mode, including model validation, company lookup, filing filtering, CLI functionality, and error handling.  
You should see all tests pass.

If pytest isn’t recognized, use:
```bash
python -m pytest -v
```

---

## 🧾 Example CLI Usage

After installation, the command-line interface can be used to interact with the fixture data.

List all recent filings for Apple:
```bash
python -m sec_connector.cli AAPL
```

Filter by form type (e.g., 10-K only):
```bash
python -m sec_connector.cli AAPL --form 10-K
```

Limit the number of results:
```bash
python -m sec_connector.cli AAPL --limit 3
```

Filter by date range:
```bash
python -m sec_connector.cli AAPL --date_from 2024-01-01 --date_to 2024-12-31
```

Download filings (saves JSON files under `downloads/`):
```bash
python -m sec_connector.cli AAPL --form 10-K --download
```

If the fixtures can’t be found, the CLI will print a helpful error message.

---

## 🧩 Design Overview

### Components
- **`models.py`** — Pydantic data models (`Company`, `Filing`, `FilingFilter`)
- **`client.py`** — `SECClient` for company lookup, filing filtering, and local “download”
- **`cli.py`** — Command-line interface built with `argparse`
- **`tests/`** — pytest suite with structured sample data

### Validation & Error Handling
- CIKs normalized to 10 digits (`zfill(10)`)
- Empty or invalid input raises `ValueError`
- Invalid or missing filing dates skipped
- Clear, descriptive error messages for bad input
- Strong type hints and docstrings throughout

---

## 🧠 Example Output

Example:
```bash
> python -m sec_connector.cli AAPL --form 10-K --limit 1
Company: Apple Inc. (CIK 0000320193)

DATE         | FORM   | ACCESSION #
---------------------------------------------
2024-10-01   | 10-K   | 0000320193-24-000001
```

With `--download`, you’ll see:
```bash
Downloading filings...
Saved: downloads/0000320193-24-000001.json
✅ 1 filings saved to 'downloads/'
```

---

**Author:** Trisha Nittala  
**Georgia Tech | DS@GT FinTech Project**
