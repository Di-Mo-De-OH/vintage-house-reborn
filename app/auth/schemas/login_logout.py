from pydantic import BaseModel, Field

from app.core.utils.validators import EmailField


class LoginRequest(BaseModel):
    email: EmailField = Field(examples=["test@example.com"])
    password: str = Field(examples=["Password@1"])


class LoginResponse(BaseModel):
    access_token: str = Field(examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])
    token_type: str = Field(default="bearer", examples=["bearer"])
