from datetime import datetime
from typing import List, Dict

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from . import crud, models, schemas
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
def read_questions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    questions = crud.get_questions(db, skip=skip, limit=limit)
    return questions


@app.get("/answers/")
def read_answers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    answers = crud.get_answers_formatted(db, skip=skip, limit=limit)
    return answers


@app.get("/analyse/")
def analyse(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    analysis_result = crud.get_analyse(db, skip=skip, limit=limit)
    return JSONResponse(content={"analysis_result": analysis_result})

@app.get("/analyse/period/")
def analyse_period(
    start_time: datetime = Query(..., description="Start time of the analysis period"),
    end_time: datetime = Query(..., description="End time of the analysis period"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    analysis_result = crud.get_analyse_period(db, start_time=start_time, end_time=end_time, skip=skip, limit=limit)
    return analysis_result
