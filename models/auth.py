from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str
    business_id: int = 1
