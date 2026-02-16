from pydantic import BaseModel


class EventPublishRequest(BaseModel):
    event_type: str
    entity: str
    entity_id: str
    version: int


class EventPublishResponse(BaseModel):
    status: str
    topic: str
