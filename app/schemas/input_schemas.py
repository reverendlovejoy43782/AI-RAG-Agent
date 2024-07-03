from pydantic import BaseModel, Field

class UserInput(BaseModel):
    input: str = Field(..., description="User input text")
    agent_scratchpad: list = Field(default_factory=list, description="Agent scratchpad")