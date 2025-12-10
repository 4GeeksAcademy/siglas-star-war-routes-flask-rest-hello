from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
​
db = SQLAlchemy()
​
# ---------- TABLA INTERMEDIA USER-PLANET ----------
user_planet = Table(
    "user_planet",
    db.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("planet_id", ForeignKey("planet.id"), primary_key=True)
)
​
# ---------- TABLA INTERMEDIA USER-PEOPLE ----------
user_people = Table(
    "user_people",
    db.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("people_id", ForeignKey("people.id"), primary_key=True)
)
​
# ---------- MODELO USER ----------
class User(db.Model):
    _tablename_ = "user"
​
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
​
    planets: Mapped[list["Planet"]] = relationship(
        "Planet",
        secondary=user_planet,
        back_populates="users"
    )
​
    favorites_people: Mapped[list["People"]] = relationship(
        "People",
        secondary=user_people,
        back_populates="users"
    )
​
    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "planets": [planet.serialize() for planet in self.planets],
            "people": [p.serialize() for p in self.favorites_people]
        }
​
# ---------- MODELO PLANET ----------
class Planet(db.Model):
    _tablename_ = "planet"
​
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
​
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_planet,
        back_populates="planets"
    )
​
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }
​
# ---------- MODELO PEOPLE ----------
class People(db.Model):
    _tablename_ = "people"
​
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    eyes_color: Mapped[str] = mapped_column(String(50), nullable=False)
    hair_color: Mapped[str] = mapped_column(String(50), nullable=False)
​
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_people,
        back_populates="favorites_people"
    )
​
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "last_name": self.last_name,
            "eyes_color": self.eyes_color,
            "hair_color": self.hair_color
        }