from sec_connector.models import Company, Filing, FilingFilter
from datetime import date
class SECClient:
    def __init__(self, companies_data: dict[str, dict]):
        """Initialize with company ticker->info mapping."""
        self._companies = companies_data
    
    def lookup_company(self, ticker: str) -> Company:
        """Find company by ticker, raise ValueError if not found."""
        # TODO: implement
        if not ticker or not ticker.strip():
            raise ValueError("Ticker must be a non-empty string")

        key = ticker.upper()

        data = self._companies.get(key)
        if data is None:
            raise ValueError(f"Company with ticker '{key}' not found")

        cik = str(data.get("cik", "")).strip()
        if not cik:
            raise ValueError(f"Company data for {key} missing CIK")

        name = data.get("name") or data.get("title") or key
        return Company(ticker=key, cik=cik, name=name)

    def list_filings(self, cik: str, filters: FilingFilter) -> list[Filing]:
        """
        Get filings for a CIK, applying filters.
        
        - Filter by form_types (if provided)
        - Filter by date range (if provided)
        - Sort by date descending
        - Limit results
        """
        # TODO: implement
        