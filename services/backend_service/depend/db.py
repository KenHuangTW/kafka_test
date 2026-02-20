from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from services.backend_service.database.mysql import get_db_session

DBSessionDep = Annotated[Session, Depends(get_db_session)]
