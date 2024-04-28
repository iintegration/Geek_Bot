from datetime import datetime
from typing import List, Dict

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from . import crud, models, schemas
from .crud import get_course_names
from .database import SessionLocal, engine
from .schemas import AnalysisResult

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или конкретные источники: ["https://example.com", "http://localhost"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/questions/", response_model=list[schemas.Question])
def read_questions(skip: int = 0, limit: int = 10000, db: Session = Depends(get_db)):
    questions = crud.get_questions(db, skip=skip, limit=limit)
    return questions


@app.get("/answers/")
def read_answers(skip: int = 0, limit: int = 10000, db: Session = Depends(get_db)):
    answers = crud.get_answers_formatted(db, skip=skip, limit=limit)
    return answers


@app.get("/analyse/")
def analyse(skip: int = 0, limit: int = 10000, db: Session = Depends(get_db)):
    analysis_result = crud.get_analyse(db, skip=skip, limit=limit)
    return JSONResponse(content={"analysis_result": analysis_result})


@app.get("/analyse/period/")
def analyse_period(
        start_time: datetime = Query(..., description="Start time of the analysis period"),
        end_time: datetime = Query(..., description="End time of the analysis period"),
        skip: int = 0,
        limit: int = 10000,
        db: Session = Depends(get_db)
):
    analysis_result = crud.get_analyse_period(db, start_time=start_time, end_time=end_time, skip=skip, limit=limit)
    return analysis_result


@app.get("/analyse/period/course/")
def analyse_period_course(
        start_time: datetime = Query(..., description="Start time of the analysis period"),
        end_time: datetime = Query(..., description="End time of the analysis period"),
        course: str = Query(..., description="Course for analysis"),
        skip: int = 0,
        limit: int = 10000,
        db: Session = Depends(get_db)
):
    analysis_result = crud.get_analyse_period_course(db, start_time=start_time, end_time=end_time, course=course,
                                                     skip=skip, limit=limit)
    return JSONResponse(content={"analysis_result": analysis_result})


@app.get("/answers/course/")
def read_answers_for_course(
        course: str = Query(..., description="Course name for filtering answers"),
        skip: int = 0,
        limit: int = 10000,
        db: Session = Depends(get_db)
):
    answers = crud.get_answers_for_course(db, course=course, skip=skip, limit=limit)

    for answer in answers:
        answer['created_at'] = answer['created_at'].isoformat()

    return JSONResponse(content={"answers": answers})


@app.get("/analyse/course/")
def analyse_single_course(
        course: str = Query(..., description="Course for analysis"),
        skip: int = 0,
        limit: int = 10000,
        db: Session = Depends(get_db)
):
    analysis_result = crud.get_course_stats_no_date(db, course=course, skip=skip, limit=limit)
    return JSONResponse(content={"analysis_result": analysis_result})


@app.get("/courses/names")
def get_courses_names(
        skip: int = 0,
        limit: int = 10000,
        db: Session = Depends(get_db)
):
    course_names = get_course_names(db, skip=skip, limit=limit)
    return JSONResponse(content={"course_names": course_names})


@app.get("/courses/stats")
def get_courses_stats(
        skip: int = 0,
        limit: int = 10000,
        db: Session = Depends(get_db)
):
    courses_stats = crud.get_course_stats_for_all_courses(db, skip=skip, limit=limit)
    return JSONResponse(content={"courses_stats": courses_stats})