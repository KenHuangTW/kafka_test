from pydantic import BaseModel


class DependencyStatus(BaseModel):
    kafka: str
    mysql: str
    redis: str


class HealthResponse(BaseModel):
    service: str
    status: str
    dependencies: DependencyStatus
