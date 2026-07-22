import enum

class StatusType(enum.Enum):
    PENDING = "pending"
    FILLED = "filled"
    REJECTED = "rejected"
