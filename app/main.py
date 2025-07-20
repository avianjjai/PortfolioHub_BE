from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import projects, skills, experience, educations, certifications, about, auth

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include the projects router
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