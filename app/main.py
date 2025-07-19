from fastapi import FastAPI
from app.api import projects

app = FastAPI()

# Include the projects router
app.include_router(projects.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}