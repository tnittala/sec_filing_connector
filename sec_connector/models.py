from pydantic import BaseModel, field_validator
from datetime import date

class Company(BaseModel):
    ticker: str
    cik: str
    name: str

    @field_validator("cik")
    @classmethod
    def pad_cik(cls, v: str) -> str:
        v = v.strip()
        if not v.isdigit():
            raise ValueError("CIK must be numeric")
        return v.zfill(10)

class Filing(BaseModel):
    cik: str
    company_name: str
    form_type: str
    filing_date: date
    accession_number: str

    @field_validator("cik")
    @classmethod
    def pad_cik(cls, v: str) -> str:
        return v.zfill(10)

    
class FilingFilter(BaseModel):
    form_types: list[str] | None = None
    date_from: date | None = None
    date_to: date | None = None
    limit: int = 10

    @field_validator("limit")
    @classmethod
    def positive_limit(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("limit must be positive")
        return v