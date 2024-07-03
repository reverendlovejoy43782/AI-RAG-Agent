"""
from pydantic import BaseModel, Field

class WikipediaInput(BaseModel):
    query: str = Field(..., description="Query to search for on Wikipedia")

class TavilyInput(BaseModel):
    query: str = Field(..., description="Query to search for on Tavily")
"""