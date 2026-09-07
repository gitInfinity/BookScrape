from pydantic import BaseModel, Field, HttpUrl

class BookRecord(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float = Field(ge=0)
    availability_text: str | None = None
    rating_text: str | None = None
    description: str | None = None
    source_page: HttpUrl
    fetched_at: str


class BookError(BaseModel):
    product_url: str
    source_page: str | None = None
    reason: str