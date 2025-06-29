from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Material:
    _id: str
    title: str
    description: str
    url: str
    last_watched: datetime = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    rating: int = 0
    tags: list[str] = field(default_factory=list)
    ratings: dict = field(default_factory=dict)


@dataclass
class User:
    _id: str
    email: str
    username: str
    password: str
    role: str  # "profesor", "estudiante" o "admin"
    materials: list[str] = field(default_factory=list)
    watched: list[str] = field(default_factory=list)  # IDs de materiales vistos
    ratings: dict = field(default_factory=dict)  # Calificaciones dadas por estudiantes
    rating: float = 0.0  # Promedio de calificación
