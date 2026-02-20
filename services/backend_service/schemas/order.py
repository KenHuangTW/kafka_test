from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class OrderData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    member_id: int
    product_id: int
    amount: Decimal
    currency: str
    create_at: datetime
    update_at: datetime
    delete_at: datetime | None
