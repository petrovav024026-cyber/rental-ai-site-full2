from pydantic import BaseModel, Field

class LeadCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=5, max_length=50)
    messenger: str | None = None
    budget: str | None = None
    location: str | None = None
    dates: str | None = None
    message: str | None = None

class FeedbackCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    contact: str | None = None
    message: str = Field(min_length=3)
