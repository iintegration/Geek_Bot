from collections import Counter, defaultdict
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


def get_analyse(db: Session, skip: int = 0, limit: int = 100) -> Dict:
    answers = db.query(models.Answer).offset(skip).limit(limit).all()

    user_answers = {}
    for answer in answers:
        user_id = answer.user_id
        question_id = str(answer.question_id)
        answer_text = answer.answer

        if user_id not in user_answers:
            user_answers[user_id] = {}

        user_answers[user_id][f"question_{question_id}"] = answer_text

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

    pred_object_count = Counter(pred_object)
    pred_positive_count = Counter(pred_positive)
    pred_relevant_count = Counter(pred_relevant)

    total_samples = len(data_format)

    formatted_result = {
        "pred_object": {
            "вебинар": pred_object_count.get(0, 0),
            "программа": pred_object_count.get(1, 0),
            "преподаватель": pred_object_count.get(2, 0),
            "percentages": {
                "вебинар": pred_object_count.get(0, 0) / total_samples * 100,
                "программа": pred_object_count.get(1, 0) / total_samples * 100,
                "преподаватель": pred_object_count.get(2, 0) / total_samples * 100
            }
        },
        "pred_positive": {
            "позитивные": pred_positive_count.get(1, 0),
            "негативные": pred_positive_count.get(0, 0),
            "percentages": {
                "позитивные": pred_positive_count.get(1, 0) / total_samples * 100,
                "негативные": pred_positive_count.get(0, 0) / total_samples * 100
            }
        },
        "pred_relevant": {
            "counts": {
                "релевантные": pred_relevant_count.get(1, 0),
                "нерелевантные": pred_relevant_count.get(0, 0)
            },
            "percentages": {
                "релевантные": pred_relevant_count.get(1, 0) / total_samples * 100,
                "нерелевантные": pred_relevant_count.get(0, 0) / total_samples * 100
            }
        },
        "data": data_format
    }

    # Добавляем неотформатированные данные
    raw_data = get_analyse_raw(db, skip, limit)
    formatted_result["raw_data"] = raw_data

    return formatted_result


def get_analyse_raw(db: Session, skip: int = 0, limit: int = 100) -> List[int]:
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
        "pred_relevant": pred_relevant,
    })

    return result


def get_analyse_period(db: Session, start_time: datetime, end_time: datetime, skip: int = 0, limit: int = 100) -> Dict:
    answers_formatted = get_answers_formatted(db, skip=skip, limit=limit)

    # Фильтруем ответы по временному промежутку
    answers_in_period = [answer for answer in answers_formatted if start_time <= answer['created_at'] <= end_time]

    user_answers = {}
    # user_ids_to_remove = set()

    for answer in answers_in_period:
        user_id = answer['user']
        question_keys = [key for key in answer.keys() if key.startswith('question_')]
        for question_key in question_keys:
            user_answers.setdefault(user_id, {}).update({question_key: answer[question_key]})

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

    pred_object_count = Counter(pred_object)
    pred_positive_count = Counter(pred_positive)
    pred_relevant_count = Counter(pred_relevant)

    total_samples = len(data_format)

    formatted_result = {
        "pred_object": {
            "вебинар": pred_object_count.get(0, 0),
            "программа": pred_object_count.get(1, 0),
            "преподаватель": pred_object_count.get(2, 0),
            "percentages": {
                "вебинар": pred_object_count.get(0, 0) / total_samples * 100,
                "программа": pred_object_count.get(1, 0) / total_samples * 100,
                "преподаватель": pred_object_count.get(2, 0) / total_samples * 100
            }
        },
        "pred_positive": {
            "позитивные": pred_positive_count.get(1, 0),
            "негативные": pred_positive_count.get(0, 0),
            "percentages": {
                "позитивные": pred_positive_count.get(1, 0) / total_samples * 100,
                "негативные": pred_positive_count.get(0, 0) / total_samples * 100
            }
        },
        "pred_relevant": {
            "counts": {
                "релевантные": pred_relevant_count.get(1, 0),
                "нерелевантные": pred_relevant_count.get(0, 0)
            },
            "percentages": {
                "релевантные": pred_relevant_count.get(1, 0) / total_samples * 100,
                "нерелевантные": pred_relevant_count.get(0, 0) / total_samples * 100
            }
        },
        "data": data_format
    }

    # Добавляем неотформатированные данные
    raw_data = get_analyse_raw_period(db, start_time, end_time, skip, limit)
    formatted_result["raw_data"] = raw_data

    return formatted_result


def get_analyse_raw_period(db: Session, start_time: datetime, end_time: datetime, skip: int = 0, limit: int = 100) -> \
        List[int]:
    answers_formatted = get_answers_formatted(db, skip=skip, limit=limit)

    # Фильтруем ответы по временному промежутку
    answers_in_period = [answer for answer in answers_formatted if start_time <= answer['created_at'] <= end_time]

    user_answers = {}
    for answer in answers_in_period:
        user_id = answer['user']
        question_keys = [key for key in answer.keys() if key.startswith('question_')]
        for question_key in question_keys:
            user_answers.setdefault(user_id, {}).update({question_key: answer[question_key]})

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
        "pred_relevant": pred_relevant,
    })

    return result


def get_analyse_period_course(db: Session, start_time: datetime, end_time: datetime, course: str, skip: int = 0,
                              limit: int = 100) -> Dict:
    answers_formatted = get_answers_formatted(db, skip=skip, limit=limit)

    # Фильтруем ответы по временному промежутку и курсу
    answers_in_period_and_course = [answer for answer in answers_formatted if
                                    (start_time <= answer['created_at'] <= end_time) and (
                                            answer.get('course') == course)]

    user_answers = {}
    for answer in answers_in_period_and_course:
        user_id = answer['user']
        question_keys = [key for key in answer.keys() if key.startswith('question_')]
        for question_key in question_keys:
            user_answers.setdefault(user_id, {}).update({question_key: answer[question_key]})

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

    pred_object_count = Counter(pred_object)
    pred_positive_count = Counter(pred_positive)
    pred_relevant_count = Counter(pred_relevant)

    total_samples = len(data_format)

    formatted_result = {
        "pred_object": {
            "вебинар": pred_object_count.get(0, 0),
            "программа": pred_object_count.get(1, 0),
            "преподаватель": pred_object_count.get(2, 0),
            "percentages": {
                "вебинар": pred_object_count.get(0, 0) / total_samples * 100,
                "программа": pred_object_count.get(1, 0) / total_samples * 100,
                "преподаватель": pred_object_count.get(2, 0) / total_samples * 100
            }
        },
        "pred_positive": {
            "позитивные": pred_positive_count.get(1, 0),
            "негативные": pred_positive_count.get(0, 0),
            "percentages": {
                "позитивные": pred_positive_count.get(1, 0) / total_samples * 100,
                "негативные": pred_positive_count.get(0, 0) / total_samples * 100
            }
        },
        "pred_relevant": {
            "counts": {
                "релевантные": pred_relevant_count.get(1, 0),
                "нерелевантные": pred_relevant_count.get(0, 0)
            },
            "percentages": {
                "релевантные": pred_relevant_count.get(1, 0) / total_samples * 100,
                "нерелевантные": pred_relevant_count.get(0, 0) / total_samples * 100
            }
        },
        "data": data_format
    }

    # Добавляем неотформатированные данные
    raw_data = get_analyse_raw_period_course(db, start_time, end_time, course, skip, limit)
    formatted_result["raw_data"] = raw_data

    return formatted_result


def get_analyse_raw_period_course(db: Session, start_time: datetime, end_time: datetime, course: str, skip: int = 0,
                                  limit: int = 100) -> List[int]:
    answers_formatted = get_answers_formatted(db, skip=skip, limit=limit)

    # Фильтруем ответы по временному промежутку и курсу
    answers_in_period_and_course = [answer for answer in answers_formatted if
                                    start_time <= answer['created_at'] <= end_time and answer.get('course') == course]

    user_answers = {}
    for answer in answers_in_period_and_course:
        user_id = answer['user']
        question_keys = [key for key in answer.keys() if key.startswith('question_')]
        for question_key in question_keys:
            user_answers.setdefault(user_id, {}).update({question_key: answer[question_key]})

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
        "pred_relevant": pred_relevant,
    })

    return result


def get_answers_for_course(db: Session, course: str, skip: int = 0, limit: int = 100):
    formatted_answers = get_answers_formatted(db, skip=skip, limit=limit)
    answers_for_course = [answer for answer in formatted_answers if answer.get('course') == course]
    return answers_for_course


def get_course_stats_no_date(db: Session, course: str, skip: int = 0, limit: int = 100) -> Dict:
    answers_formatted = get_answers_formatted(db, skip=skip, limit=limit)

    # Фильтруем ответы только для указанного курса
    answers_for_course = [answer for answer in answers_formatted if answer.get('course') == course]

    user_answers = {}
    for answer in answers_for_course:
        user_id = answer['user']
        question_keys = [key for key in answer.keys() if key.startswith('question_')]
        for question_key in question_keys:
            user_answers.setdefault(user_id, {}).update({question_key: answer[question_key]})

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

    pred_object_count = Counter(pred_object)
    pred_positive_count = Counter(pred_positive)
    pred_relevant_count = Counter(pred_relevant)

    total_samples = len(data_format)

    formatted_result = {
        "pred_object": {
            "вебинар": pred_object_count.get(0, 0),
            "программа": pred_object_count.get(1, 0),
            "преподаватель": pred_object_count.get(2, 0),
            "percentages": {
                "вебинар": pred_object_count.get(0, 0) / total_samples * 100,
                "программа": pred_object_count.get(1, 0) / total_samples * 100,
                "преподаватель": pred_object_count.get(2, 0) / total_samples * 100
            }
        },
        "pred_positive": {
            "позитивные": pred_positive_count.get(1, 0),
            "негативные": pred_positive_count.get(0, 0),
            "percentages": {
                "позитивные": pred_positive_count.get(1, 0) / total_samples * 100,
                "негативные": pred_positive_count.get(0, 0) / total_samples * 100
            }
        },
        "pred_relevant": {
            "counts": {
                "релевантные": pred_relevant_count.get(1, 0),
                "нерелевантные": pred_relevant_count.get(0, 0)
            },
            "percentages": {
                "релевантные": pred_relevant_count.get(1, 0) / total_samples * 100,
                "нерелевантные": pred_relevant_count.get(0, 0) / total_samples * 100
            }
        },
        "data": data_format
    }

    return formatted_result


def get_course_names(db: Session, skip: int = 0, limit: int = 100) -> List[str]:
    answers = get_answers_formatted(db, skip=skip, limit=limit)
    course_names = set()
    for answer in answers:
        course_names.add(answer.get("course"))
    return list(course_names)


def get_course_stats_for_all_courses(db: Session, skip: int = 0, limit: int = 100) -> Dict[str, Dict]:
    course_names = get_course_names(db, skip=skip, limit=limit)
    all_course_stats = {}
    for course in course_names:
        course_stats = get_course_stats_no_date(db, course=course, skip=skip, limit=limit)
        all_course_stats[course] = course_stats
    return all_course_stats