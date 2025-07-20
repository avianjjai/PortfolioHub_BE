from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import projects, skills, experience, educations, certifications, about, auth
from app.db.mongodb import init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(skills.router)
app.include_router(experience.router)
app.include_router(educations.router)
app.include_router(certifications.router)
app.include_router(about.router)
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}