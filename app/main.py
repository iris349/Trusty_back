from fastapi import FastAPI
from app.database import engine
from app.models.user import User
from app.models.analysis import Analysis
from app.models.report import Report
from app.database import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Trusty backend run"}