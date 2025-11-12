import json
import argparse
from pathlib import Path
from sec_connector.client import SECClient
from sec_connector.models import FilingFilter
from datetime import date

def main():
    """
    Usage: python -m sec_connector.cli AAPL --form 10-K --limit 5
    """
    # TODO: Parse args (use argparse or simple sys.argv)
    # Load fixtures
    # Call client methods
    # Print results as table or JSON

    # arg parsing
    parser = argparse.ArgumentParser(description="Fetch SEC filings by ticker symbol.")
    parser.add_argument("ticker", help="Company ticker symbol (e.g., AAPL)")
    parser.add_argument("--form", dest="form_types", nargs="*", help="Filter by form types (e.g., 10-K 10-Q)")
    parser.add_argument("--limit", type=int, default=5, help="Limit number of results (default=5)")
    parser.add_argument("--date_from", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--date_to", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument("--download", action="store_true", help="Save filings locally as JSON")
    args = parser.parse_args()

    # load fixture data
    fixtures_dir = Path(__file__).resolve().parent.parent / "tests" / "fixtures"
    try:
        with open(fixtures_dir / "company_tickers.json") as f:
            companies = json.load(f)
        with open(fixtures_dir / "filing_sample.json") as f:
            filings = json.load(f)
    except FileNotFoundError:
        print("Error: Could not find fixture data. Make sure tests/fixtures/ exists.")
        return

    # client
    client = SECClient(companies, filings)

    # company lookup
    try:
        company = client.lookup_company(args.ticker)
    except ValueError as e:
        print(f"Error: {e}")
        return

    print(f"\nCompany: {company.name} (CIK {company.cik})\n")

    # build filters
    filters = FilingFilter(
        form_types=args.form_types,
        date_from=date.fromisoformat(args.date_from) if args.date_from else None,
        date_to=date.fromisoformat(args.date_to) if args.date_to else None,
        limit=args.limit,
    )

    # build filings list
    filings_list = client.list_filings(company.cik, filters)
    if not filings_list:
        print("No filings found for the given filters.")
        return
    
    # print results
    print(f"{'DATE':<12} | {'FORM':<6} | {'ACCESSION #'}")
    print("-" * 45)
    for f in filings_list:
        print(f"{f.filing_date} | {f.form_type:<6} | {f.accession_number}")

    # download
    if args.download:
        print("\nDownloading filings...")
        for f in filings_list:
            path = client.download_filing(f)
            print(f"Saved: {path}")
        print(f"\n {len(filings_list)} filings saved to 'downloads/'")

if __name__ == "__main__":
    main()