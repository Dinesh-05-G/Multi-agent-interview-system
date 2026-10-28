from pydantic import BaseModel
from typing import List


class InterviewStartRequest(BaseModel):
    name: str
    email: str
    education: str
    skills: List[str]
    projects: List[str]
    experience: str
    target_role: str

    topic: str
    selected_concepts: List[str]
    question_type: str
    starting_difficulty: str
    max_questions: int


class AnswerRequest(BaseModel):
    answer: str


class InterviewStartResponse(BaseModel):
    session_id: int
    question_id: int
    question_number: int
    question: str
    concept: str
    question_type: str
    difficulty: str