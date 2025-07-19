from fastapi import FastAPI
from app.api import projects, skills, experience, educations, certifications, about

app = FastAPI()

# Include the projects router
app.include_router(projects.router)
app.include_router(skills.router)
app.include_router(experience.router)
app.include_router(educations.router)
app.include_router(certifications.router)
app.include_router(about.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}