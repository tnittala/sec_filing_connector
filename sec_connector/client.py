from sec_connector.models import Company, Filing, FilingFilter
from datetime import date
from pathlib import Path
import json
class SECClient:
    def __init__(self, companies_data: dict[str, dict], filings_data: list[dict]):
        """
        Initialize the SECClient.

        Args:
            companies_data: Mapping of ticker symbol → company info.
            filings_data: List of raw filing entries (dictionaries).
        """
        if not companies_data:
            raise ValueError("companies_data must not be empty")
        if not filings_data:
            raise ValueError("filings_data must not be empty")
        
        self._companies = companies_data
        self._filings = filings_data
    
    def lookup_company(self, ticker: str) -> Company:
        """
        Look up a company by ticker symbol.

        Args:
            ticker: The stock ticker symbol (e.g., 'AAPL').

        Returns:
            A Company object with normalized CIK and name.

        Raises:
            ValueError: If ticker is empty, not found, or missing a CIK.
        """
        if not ticker or not ticker.strip():
            raise ValueError("Ticker must be a non-empty string")

        key = ticker.upper()

        data = self._companies.get(key)
        if data is None:
            raise ValueError(f"Company with ticker '{key}' not found")

        cik = str(data.get("cik", "")).strip()
        if not cik:
            raise ValueError(f"Company data for {key} missing CIK")

        name = data.get("name") or key
        return Company(ticker=key, cik=cik, name=name)

    def list_filings(self, cik: str, filters: FilingFilter) -> list[Filing]:
        """
        Retrieve filings for a given company CIK and apply filters.

        Args:
            cik: Central Index Key (CIK) of the company.
            filters: FilingFilter specifying form types, date range, and limit.

        Returns:
            List of Filing objects satisfying the filters.

        Raises:
            ValueError: If CIK is invalid or filters contain invalid dates.
        """
        if not cik or not cik.strip():
            raise ValueError("CIK must be provided")
        cik_padded = cik.zfill(10)
        filings = []
        for raw in self._filings:
            raw_cik = str(raw.get("cik", "")).zfill(10)
            if raw_cik != cik_padded:
                continue
            filing_date_str = raw.get("filing_date")
            if not filing_date_str: # skip if there is no filing date because a date is required for a Filing object, alternatives would be to make the date None or use a default date
                continue
            try:
                filing_date = date.fromisoformat(filing_date_str)
            except ValueError: # Skip filings without valid filing_date
                continue 
            filing = Filing(
                cik=raw_cik,
                company_name=raw.get("company_name", ""),
                form_type=raw.get("form_type", ""), # could add additional validity checks if we knew all form types
                filing_date=filing_date, 
                accession_number=raw.get("accession_number", ""),
            )
            filings.append(filing)

        if filters.form_types:
            allowed = {ft.upper() for ft in filters.form_types}
            filings = [f for f in filings if f.form_type.upper() in allowed]
        if filters.date_from:
            if not isinstance(filters.date_from, date):
                raise ValueError("date_from must be a valid date object.")
            filings = [f for f in filings if f.filing_date >= filters.date_from]
        if filters.date_to:
            if not isinstance(filters.date_to, date):
                raise ValueError("date_to must be a valid date object.")
            filings = [f for f in filings if f.filing_date <= filters.date_to]
        filings.sort(key=lambda f: f.filing_date, reverse=True)
        
        return filings[: filters.limit]

    def download_filing(self, filing: Filing, out_dir: str | None = None) -> Path:
        """
        Simulate downloading a filing by saving its metadata as JSON.

        Args:
            filing: Filing object to save.
            out_dir: Optional directory path (default: 'downloads').

        Returns:
            Path to the saved JSON file.

        Raises:
            ValueError: If filing is invalid or cannot be written.
        """
        if not filing or not isinstance(filing, Filing):
            raise ValueError("Invalid Filing object provided for download.")
        
        out_dir = Path(out_dir or "downloads")
        out_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{filing.accession_number}.json"
        file_path = out_dir / filename

        try:
            with open(file_path, "w") as f:
                # Use default=str to handle datetime.date
                json.dump(filing.model_dump(), f, indent=2, default=str)
        except Exception as e:
            raise ValueError(f"Failed to save filing: {e}") from e

        return file_path