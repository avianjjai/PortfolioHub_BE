import sys
import os
from db.database import Base
from models.project import Project

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

target_metadata = Base.metadata
