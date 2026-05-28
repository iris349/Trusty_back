from fastapi import FastAPI
from app.database import engine
from app.models.user import User
from app.models.analysis import Analysis
from app.models.report import Report
from app.models.lookup import Lookup
from app.models.post import Post
from app.models.comment import Comment
from app.routers import community
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base
from app.routers import auth, users

Base.metadata.create_all(bind=engine)

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(community.router)

@app.get("/")
def root():
    return {"message": "Trusty backend run"}