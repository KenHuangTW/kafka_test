from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProductData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    price: int
    currency: str
    create_at: datetime
    update_at: datetime
    delete_at: datetime | None
