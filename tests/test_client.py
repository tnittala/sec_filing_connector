import json
from pathlib import Path
from datetime import date
import pytest
from sec_connector.models import Company, Filing, FilingFilter
from sec_connector.client import SECClient


# ---------------------------------------------------------------------
# FIXTURE LOADING (shared JSON data)
# ---------------------------------------------------------------------

fixtures_dir = Path(__file__).resolve().parent / "fixtures"
companies = json.load(open(fixtures_dir / "company_tickers.json"))
filings = json.load(open(fixtures_dir / "filing_sample.json"))


# ---------------------------------------------------------------------
# TASK 1 — MODEL VALIDATION TESTS
# ---------------------------------------------------------------------

def test_company_model_valid():
    c = Company(ticker="AAPL", cik="320193", name="Apple Inc.")
    assert c.cik == "0000320193"
    assert c.ticker == "AAPL"
    assert c.name == "Apple Inc."

def test_company_model_rejects_bad_data(): #new
    """Missing required fields or wrong types should raise errors."""
    with pytest.raises(ValueError):
        Company(ticker="", cik="", name="") 

def test_filing_model_valid():
    f = Filing(
        cik="320193",
        company_name="Apple Inc.",
        form_type="10-K",
        filing_date=date(2024, 10, 1),
        accession_number="0000320193-24-000001",
    )
    assert f.cik == "0000320193"
    assert f.form_type == "10-K"
    assert f.filing_date == date(2024, 10, 1)


def test_filing_filter_defaults():
    filt = FilingFilter()
    assert filt.form_types is None
    assert filt.date_from is None
    assert filt.date_to is None
    assert filt.limit == 10


# ---------------------------------------------------------------------
# TASK 2 — COMPANY LOOKUP TESTS
# ---------------------------------------------------------------------

def test_lookup_company_valid():
    client = SECClient(companies, filings)
    company = client.lookup_company("aapl")
    assert company.name == "Apple Inc."
    assert company.cik == "0000320193"


def test_lookup_company_invalid_ticker():
    client = SECClient(companies, filings)
    with pytest.raises(ValueError):
        client.lookup_company("GOOG")


def test_lookup_company_empty_string():
    client = SECClient(companies, filings)
    with pytest.raises(ValueError):
        client.lookup_company("  ")

def test_lookup_company_cik_is_zero_padded(): #new
    client = SECClient(companies, filings)
    company = client.lookup_company("MSFT")
    assert company.cik == "0000789019"


# ---------------------------------------------------------------------
# TASK 3 — FILINGS LIST & FILTER TESTS
# ---------------------------------------------------------------------

def test_no_filters_returns_all_filings_limited(): #new
    client = SECClient(companies, filings)
    cik = client.lookup_company("AAPL").cik
    results = client.list_filings(cik, FilingFilter())
    assert len(results) <= 10  # limit defaults to 10
    assert all(isinstance(f, Filing) for f in results)
    # Should be sorted newest first
    dates = [f.filing_date for f in results]
    assert dates == sorted(dates, reverse=True)


def test_form_type_filter_only_10K():
    client = SECClient(companies, filings)
    cik = client.lookup_company("AAPL").cik
    results = client.list_filings(cik, FilingFilter(form_types=["10-K"]))
    assert all(f.form_type.upper() == "10-K" for f in results)


def test_date_range_filter():
    client = SECClient(companies, filings)
    cik = client.lookup_company("AAPL").cik
    filters = FilingFilter(date_from=date(2024, 1, 1))
    results = client.list_filings(cik, filters)
    assert all(f.filing_date >= date(2024, 1, 1) for f in results)


def test_results_sorted_newest_first():
    client = SECClient(companies, filings)
    cik = client.lookup_company("AAPL").cik
    results = client.list_filings(cik, FilingFilter())
    dates = [f.filing_date for f in results]
    assert dates == sorted(dates, reverse=True)


def test_limit_respected():
    client = SECClient(companies, filings)
    cik = client.lookup_company("AAPL").cik
    filters = FilingFilter(limit=1)
    results = client.list_filings(cik, filters)
    assert len(results) == 1


def test_missing_or_invalid_filing_date_skipped():
    # Create a copy of filings with one invalid and one missing date
    broken_filings = filings + [
        {
            "cik": "0000320193",
            "company_name": "Apple Inc.",
            "form_type": "8-K",
            "filing_date": "invalid-date",
            "accession_number": "0000320193-24-000005",
        },
        {
            "cik": "0000320193",
            "company_name": "Apple Inc.",
            "form_type": "8-K",
            "accession_number": "0000320193-24-000006",
        },
    ]
    client = SECClient(companies, broken_filings)
    cik = client.lookup_company("AAPL").cik
    results = client.list_filings(cik, FilingFilter())
    assert all(isinstance(f.filing_date, date) for f in results)


# ---------------------------------------------------------------------
# TASK 4 — DOWNLOAD CAPABILITY TEST
# ---------------------------------------------------------------------

def test_download_filing_creates_valid_json(tmp_path):
    client = SECClient(companies, filings)
    cik = client.lookup_company("AAPL").cik
    filing = client.list_filings(cik, FilingFilter(limit=1))[0]

    # Save to a temporary directory
    path = client.download_filing(filing, out_dir=tmp_path)
    assert path.exists()

    # Verify JSON content is valid
    text = path.read_text()
    data = json.loads(text)
    assert data["cik"] == "0000320193"
    assert data["form_type"] == "10-K"
    assert "filing_date" in data
    assert isinstance(data["filing_date"], str)  # Should be ISO string


# ---------------------------------------------------------------------
# TASK 5 — EDGE CASES & INPUT VALIDATION TESTS
# ---------------------------------------------------------------------

def test_list_filings_invalid_cik():
    client = SECClient(companies, filings)
    with pytest.raises(ValueError):
        client.list_filings("", FilingFilter())


def test_lookup_company_missing_cik_field():
    bad_companies = {"FAKE": {"name": "Fake Co"}}
    client = SECClient(bad_companies, filings)
    with pytest.raises(ValueError):
        client.lookup_company("FAKE")


def test_filing_filter_zero_limit():
    with pytest.raises(ValueError):
        FilingFilter(limit=0)


def test_filing_filter_invalid_dates():
    """If an invalid date range is passed, no crash should occur (graceful handling)."""
    client = SECClient(companies, filings)
    cik = client.lookup_company("AAPL").cik
    # Using future date range that yields no results
    filters = FilingFilter(date_from=date(2030, 1, 1), date_to=date(2030, 12, 31))
    results = client.list_filings(cik, filters)
    assert results == []
