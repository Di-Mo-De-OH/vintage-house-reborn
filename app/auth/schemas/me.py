
from pydantic import BaseModel,Field,ConfigDict
from app.core.utils.validators import EmailField


class MeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(examples=["01JB3X8Z9Q0K4C7D2E5F6G7H8J"])
    email: str = Field(examples = ["test@example.com"])
    name: str = Field(examples=["name"])
    nickname: str = Field(examples=["nickname"])
    address: str|None = Field(default = None,examples=["address"])

