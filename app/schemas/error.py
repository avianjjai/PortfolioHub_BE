from pydantic import BaseModel
class Error(BaseModel):
    message: str
    status_code: int