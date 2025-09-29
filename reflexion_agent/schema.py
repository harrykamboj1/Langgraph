from pydantic import BaseModel, Field
from typing import List


class Reflection(BaseModel):
    missing: str = Field(description="Critique of what is missing")
    superfluous: str = Field(description="Critique of what is superfluous")


class AnswerQuestion(BaseModel):
    answer: str = Field(description="250 detailed answer to the question")
    search_queries: str = Field(
        description="1-3 search queries seperate for improvements to address the critiques of your current answer")
    reflection: str = Field(
        description="Your reflection to the initial answer.")
