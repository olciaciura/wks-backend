import enum

class EventType(enum.Enum):
    COMPETITION = "competition"
    TRAINING = "training"

class StatusType(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    ARCHIVED = "archived"
    FUTURE = "future"