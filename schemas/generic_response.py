from pydantic import BaseModel
from typing import Any, Optional

class GenericResponse(BaseModel):
    success: bool
    code: int
    response: Optional[Any] = None
    detail: Optional[str] = None
