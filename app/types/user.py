import enum

class RoleType(enum.Enum):
    USER = "user"
    TRAINER = "trainer"
    ADMIN = "admin"

class GenderType(enum.Enum):
    MALE = "male"
    FEMALE = "female"