from app.db.database import engine, Base
from app.models.project import Project

print('Creating database tables...')
Base.metadata.create_all(bind=engine)
print('Database tables created')