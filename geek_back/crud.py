from itertools import groupby
from typing import Dict, List, Type

from sqlalchemy.orm import Session

from . import models
from .analyser import Model

import os

best_model_path = os.path.join(os.path.dirname(__file__), 'models', 'best_model_object')
best_model_path_positive = os.path.join(os.path.dirname(__file__), 'models', 'best_model_positive')
best_model_path_relevant = os.path.join(os.path.dirname(__file__), 'models', 'best_model_relevant')


def get_questions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Question).offset(skip).limit(limit).all()


def get_answers_formatted(db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, str]]:
    answers = db.query(models.Answer).offset(skip).limit(limit).all()

    user_answers = {}
    for answer in answers:
        user_id = answer.user_id
        question_id = str(answer.question_id)
        answer_text = answer.answer

        if user_id not in user_answers:
            user_answers[user_id] = {"user_id": user_id}

        user_answers[user_id][f"question_{question_id}"] = answer_text

    data_format = list(user_answers.values())

    return data_format


def get_analyse(db: Session, skip: int = 0, limit: int = 100) -> List[int]:
    answers = db.query(models.Answer).offset(skip).limit(limit).all()

    user_answers = {}
    for answer in answers:
        user_id = answer.user_id
        question_id = str(answer.question_id)
        answer_text = answer.answer

        if user_id not in user_answers:
            user_answers[user_id] = {}

        user_answers[user_id][f"question_{question_id}"] = answer_text

    data_format = []
    for answers in user_answers.values():
        data_format.append(answers)

    object_cats = Model(model_path=best_model_path)
    positive_cats = Model(model_path=best_model_path_positive)
    relevant_cats = Model(model_path=best_model_path_relevant)

    pred_object = object_cats.predict(data_format)
    pred_positive = positive_cats.predict(data_format)
    pred_relevant = relevant_cats.predict(data_format)

    pred_object = [int(value) for value in pred_object]
    pred_positive = [int(value) for value in pred_positive]
    pred_relevant = [int(value) for value in pred_relevant]

    result = []
    result.append({
        "pred_object": pred_object,
        "pred_positive": pred_positive,
        "pred_relevant": pred_relevant
    })

    return result
