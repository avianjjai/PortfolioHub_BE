from enum import Enum

class UserRole(str, Enum):
    viewer = "viewer"
    admin = "admin"
    super_admin = "super_admin"

class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"

class UserGender(str, Enum):
    male = "male"
    female = "female"
    other = "other"