from pydantic import BaseModel
from typing import List

class Citation(BaseModel):
    text: str
    source: str

class Report(BaseModel):
    title: str
    section: dict
    citations: List[Citation]

