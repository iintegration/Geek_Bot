from collections import Counter
from datetime import datetime
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


def get_answers_formatted(db: Session, skip: int = 0, limit: int = 100):
    answers = db.query(models.Answer).offset(skip).limit(limit).all()
    user_answers = {}
    for answer in answers:
        user_id = answer.user_id
        question_id = str(answer.question_id)
        answer_text = answer.answer.lower()
        created_at = answer.created_at  # Добавляем получение времени создания

        if user_id not in user_answers:
            user_answers[user_id] = {"user": user_id}

        if question_id == "2":
            user_answers[user_id]["course"] = answer_text

        user_answers[user_id][f"question_{question_id}"] = answer_text
        user_answers[user_id]["created_at"] = created_at  # Добавляем время создания

    data_format = []
    for answers in user_answers.values():
        data_format.append(answers)

    return data_format


def get_analyse(db: Session, skip: int = 0, limit: int = 100) -> list[dict[str, list[int]]]:
    answers = db.query(models.Answer).offset(skip).limit(limit).all()

    user_answers = {}
    # user_ids_to_remove = set()

    for answer in answers:
        user_id = answer.user_id
        question_id = str(answer.question_id)
        answer_text = answer.answer

        if user_id not in user_answers:
            user_answers[user_id] = {}

        user_answers[user_id][f"question_{question_id}"] = answer_text

    # REMOVE FILTER_QUESTION > 4 <11
    # for user_id, answers in user_answers.items():
    #     if 'question_6' in answers and (int(answers['question_6']) < 5) or (int(answers['question_6']) > 11):
    #         user_ids_to_remove.add(user_id)

    # for user_id in user_ids_to_remove:
    #     del user_answers[user_id]

    data_format = list(user_answers.values())

    object_cats = Model(model_path=best_model_path)
    positive_cats = Model(model_path=best_model_path_positive)
    relevant_cats = Model(model_path=best_model_path_relevant)

    pred_object = object_cats.predict(data_format)
    pred_positive = positive_cats.predict(data_format)
    pred_relevant = relevant_cats.predict(data_format)

    pred_object = [int(value) for value in pred_object]
    pred_positive = [int(value) for value in pred_positive]
    pred_relevant = [int(value) for value in pred_relevant]

    # Подсчеты и процентное соотношение для каждой модели
    pred_object_count = Counter(pred_object)
    pred_positive_count = Counter(pred_positive)
    pred_relevant_count = Counter(pred_relevant)

    total_samples = len(data_format)

    result = {
        "pred_object": {
            "counts": pred_object_count,
            "percentages": {key: value / total_samples * 100 for key, value in pred_object_count.items()}
        },
        "pred_positive": {
            "counts": pred_positive_count,
            "percentages": {key: value / total_samples * 100 for key, value in pred_positive_count.items()}
        },
        "pred_relevant": {
            "counts": pred_relevant_count,
            "percentages": {key: value / total_samples * 100 for key, value in pred_relevant_count.items()}
        },
        "data": data_format
    }

    return result


def get_analyse_period(db: Session, start_time: datetime, end_time: datetime, skip: int = 0, limit: int = 100):
    answers_formatted = get_answers_formatted(db, skip=skip, limit=limit)

    # Фильтруем ответы по временному промежутку
    answers_in_period = [answer for answer in answers_formatted if start_time <= answer['created_at'] <= end_time]

    user_answers = {}
    user_ids_to_remove = set()

    for answer in answers_in_period:
        user_id = answer['user']
        question_keys = [key for key in answer.keys() if key.startswith('question_')]
        for question_key in question_keys:
            user_answers.setdefault(user_id, {}).update({question_key: answer[question_key]})

    # REMOVE FILTER_QUESTION > 4 <11
    # for user_id, answers in user_answers.items():
    #     if 'question_6' in answers and (int(answers['question_6']) < 5) or (int(answers['question_6']) > 11):
    #         user_ids_to_remove.add(user_id)

    for user_id in user_ids_to_remove:
        del user_answers[user_id]

    data_format = list(user_answers.values())

    object_cats = Model(model_path=best_model_path)
    positive_cats = Model(model_path=best_model_path_positive)
    relevant_cats = Model(model_path=best_model_path_relevant)

    pred_object = [int(value) for value in object_cats.predict(data_format)]
    pred_positive = [int(value) for value in positive_cats.predict(data_format)]
    pred_relevant = [int(value) for value in relevant_cats.predict(data_format)]

    pred_object_count = Counter(pred_object)
    pred_positive_count = Counter(pred_positive)
    pred_relevant_count = Counter(pred_relevant)

    total_samples = len(data_format)

    result = {
        "pred_object": {
            "counts": pred_object_count,
            "percentages": {key: value / total_samples * 100 for key, value in pred_object_count.items()}
        },
        "pred_positive": {
            "counts": pred_positive_count,
            "percentages": {key: value / total_samples * 100 for key, value in pred_positive_count.items()}
        },
        "pred_relevant": {
            "counts": pred_relevant_count,
            "percentages": {key: value / total_samples * 100 for key, value in pred_relevant_count.items()}
        },
        "data": data_format
    }

    return result
