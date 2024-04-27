from sqlalchemy import Column, ForeignKey, Integer, String

from .database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, index=True)
    question_text = Column(String, index=True)


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    answer = Column(String, index=True)
    user_id = Column(String, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
