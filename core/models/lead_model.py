from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Lead:
    name: str
    category: str
    location: str
    website: str | None = None
    phone: str | None = None
    social_profiles: list[str] = field(default_factory=list)
    score: float = 0.0
    status: str = "new"
    created_at: datetime = field(default_factory=datetime.now)