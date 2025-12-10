from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import String, Boolean
#from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, Column, ForeignKey, Table, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

user_character = Table(
    "user_character",
    db.metadata,  
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("character_id", ForeignKey("character.id"), primary_key=True)
)

user_planet = Table(
    "user_planet",
    db.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("planet_id", ForeignKey("planet.id"), primary_key=True)
)

user_vehicle = Table(
    "user_vehicle",
    db.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("vehicle_id", ForeignKey("vehicle.id"), primary_key=True)
)

class User(db.Model):
    __tablaname__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    planets: Mapped[list["Planet"]] = relationship("Planet", secondary=user_planet, back_populates="users")
    
    
    characters: Mapped[list["Character"]] = relationship("Character", secondary=user_character, back_populates="users")
    
    vehicles: Mapped[list["Vehicle"]] = relationship("Vehicle", secondary=user_vehicle, back_populates="users")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "last_name": self.last_name,
            "phone": self.phone,
            "email": self.email,
            "is_active": self.is_active,
            "planets": [planet.serialize() for planet in self.planets],
            "characters": [character.serialize() for character in self.characters],
            "vehicles": [vehicle.serialize() for vehicle in self.vehicles],
            # do not serialize the password, its a security breach
        }


class Character(db.Model):
    __tablename__ = "character"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[float] = mapped_column(Float(6), nullable=True)
    weight: Mapped[float] = mapped_column(Float(6), nullable=True)
    eye_color: Mapped[str] = mapped_column(String(30), nullable=True)
    hair_color: Mapped[str] = mapped_column(String(30), nullable=True)
    skin_color: Mapped[str] = mapped_column(String(30), nullable=True)
    gender: Mapped[str] = mapped_column(String(30), nullable=True)
    mass: Mapped[str] = mapped_column(String(30), nullable=True)
    homeworld: Mapped[str] = mapped_column(String(50), nullable=True)
    birth_year: Mapped[str] = mapped_column(String(30), nullable=True)
    description: Mapped[str] = mapped_column(String(100), nullable=True)
    users: Mapped[list["User"]] = relationship("User", secondary=user_character, back_populates="characters")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "height": self.height,
            "weight": self.weight,
            "eye_color": self.eye_color,
            "hair_color": self.hair_color,
            "skin_color": self.skin_color,
            "gender": self.gender,
            "mass": self.mass,
            "homeworld": self.homeworld,
            "birth_year": self.birth_year,
            "description": self.description,
        }

class Planet(db.Model):
    __tablename__ = "planet"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    climate: Mapped[str] = mapped_column(String(30), nullable=True)
    surface_water: Mapped[str] = mapped_column(String(30), nullable=True)
    diameter: Mapped[str] = mapped_column(String(30), nullable=True)
    rotation_period: Mapped[str] = mapped_column(String(30), nullable=True)
    terrain: Mapped[str] = mapped_column(String(30), nullable=True)
    gravity: Mapped[str] = mapped_column(String(30), nullable=True)
    orbital_period: Mapped[str] = mapped_column(String(30), nullable=True)
    population: Mapped[str] = mapped_column(String(30), nullable=True)
    description: Mapped[str] = mapped_column(String(30), nullable=True)
    users: Mapped[list["User"]] = relationship("User", secondary=user_planet, back_populates="planets")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "surface_water": self.surface_water,
            "diameter": self.diameter,
            "rotation_period": self.rotation_period,
            "terrain": self.terrain,
            "gravity": self.gravity,
            "orbital_period": self.orbital_period,
            "population": self.population,
            "description": self.description
        }
    
class Vehicle(db.Model):
    __tablename__ = "vehicle"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    consumables: Mapped[str] = mapped_column(String(30), nullable=True)
    cargo_capacity: Mapped[str] = mapped_column(String(30), nullable=True)
    passenger: Mapped[str] = mapped_column(String(30), nullable=True)
    max_atmosphering_speed: Mapped[str] = mapped_column(String(30), nullable=True)
    crew: Mapped[str] = mapped_column(String(30), nullable=True)
    length: Mapped[str] = mapped_column(String(30), nullable=True)
    model: Mapped[str] = mapped_column(String(30), nullable=True)
    cost_in_credits: Mapped[str] = mapped_column(String(30), nullable=True)
    manufactured: Mapped[str] = mapped_column(String(30), nullable=True)
    vehicle_class: Mapped[str] = mapped_column(String(30), nullable=True)
    description: Mapped[str] = mapped_column(String(100), nullable=True)
    users: Mapped[list["User"]] = relationship("User", secondary=user_vehicle, back_populates="vehicles")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "consumables": self.consumables,
            "cargo_capacity": self.cargo_capacity,
            "passenger": self.passenger,
            "max_atmosphering_speed": self.max_atmosphering_speed,
            "crew": self.crew,
            "length": self.length,
            "model": self.model,
            "cost_in_credits": self.cost_in_credits,
            "manufactured": self.manufactured,
            "vehicle_class": self.vehicle_class,
            "description": self.description,
        }
    
