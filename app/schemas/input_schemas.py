from pydantic import BaseModel, Field

class UserInput(BaseModel):
    input: str = Field(..., description="User input text")