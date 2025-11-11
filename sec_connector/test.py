from models import Company, Filing, FilingFilter
from datetime import date

c = Company(ticker="AAPL", cik="320193", name="Apple Inc.")
print(c)
# → ticker='AAPL' cik='0000320193' name='Apple Inc.'

f = Filing(
    cik="320193",
    company_name="Apple Inc.",
    form_type="10-K",
    filing_date=date(2024, 10, 1),
    accession_number="0000320193-24-000001",
)
print(f)