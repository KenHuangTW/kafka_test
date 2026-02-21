from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .base import BaseResponse


class ProductData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    price: int
    currency: str
    sale_limit: int
    create_at: datetime
    update_at: datetime
    delete_at: datetime | None


class ProductGetResponse(BaseResponse):
    data: ProductData


class ProductListResponse(BaseResponse):
    data: list[ProductData]
