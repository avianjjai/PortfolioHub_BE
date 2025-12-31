from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.experience import Experience
from app.models.project import Project
from app.models.skill import Skill
from app.models.education import Education
from app.models.certification import Certification
from app.models.award import Award
from app.models.about import About
from app.models.user import User
from app.models.message import Message
from app.models.access_token import AccessToken
from app.config import settings

async def init_db():
    # Construct MongoDB URL with database name
    # Remove trailing slash if present, then add database name
    mongodb_url = settings.mongodb_url.rstrip('/')
    mongodb_url = f"{mongodb_url}/{settings.database_name}"
    client = AsyncIOMotorClient(mongodb_url)
    await init_beanie(
        database=client.get_default_database(), # type: ignore
        document_models=[
            User,
            Project,
            Skill,
            Experience,
            Education,
            Certification,
            Award,
            About,
            Message,
            AccessToken,
        ]
    )