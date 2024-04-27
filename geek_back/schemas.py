from typing import Dict, List

from pydantic import BaseModel


class AnswerBase(BaseModel):
    answer: str


class AnswerCreate(AnswerBase):
    pass


class Answer(AnswerBase):
    id: int
    question_id: int
    user_id: int

    class Config:
        orm_mode = True


class AnswerResponse(BaseModel):
    question_id: int
    answer: str

class UserAnswer(BaseModel):
    user_id: int
    answers: Dict[str, str]

class AnalysisResult(BaseModel):
    analysis_result: List[UserAnswer]


class QuestionBase(BaseModel):
    question_text: str
    order_number: int


class QuestionCreate(QuestionBase):
    pass


class Question(QuestionBase):
    id: int

    class Config:
        orm_mode = True
