from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.experience import Experience
from app.models.project import Project
from app.models.skill import Skill
from app.models.education import Education
from app.models.certification import Certification
from app.models.about import About
from app.models.user import User

MONGODB_URL = "mongodb://localhost:27017/portfolio"

async def init_db():
    client = AsyncIOMotorClient(MONGODB_URL)
    await init_beanie(
        database=client.get_default_database(), # type: ignore
        document_models=[
            User,
            Project,
            Skill,
            Experience,
            Education,
            Certification,
        ]
    )