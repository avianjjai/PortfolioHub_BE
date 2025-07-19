Migration Tool (Alembic)
    1. Install: pip install alembic
    2. Initialize Alembic: alembic init alembic
    3. Create First Migration: alembic revision --autogenerate -m "create projects table"
    4. Apply the migration: alembic upgrade head