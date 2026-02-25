from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductUpsertRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: str | None = None
    price: int
    currency: str = Field(min_length=1, max_length=8)
    sale_limit: int | None = Field(ge=1)


class ProductData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    price: int
    currency: str
    sale_limit: int | None
    create_at: datetime
    update_at: datetime
    delete_at: datetime | None


class ProductActionResponse(BaseModel):
    success: bool
