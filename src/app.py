"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, user_planet, Character, user_character, user_vehicle,Vehicle
from sqlalchemy.exc import SQLAlchemyError
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)

def validate_required(data, required_fields):
    """Valida campos requeridos en un JSON y retorna lista de faltantes."""
    missing = [field for field in required_fields if not data.get(field)]
    return missing

# rutas para el modelo User
@app.route('/user', methods=['GET'])
def get_all_users():
    try:
        users = User.query.all()
        if not users:
            return jsonify({"message": "No hay Usuarios Registrados"}), 200
        return jsonify([user.serialize() for user in users]), 200
    except SQLAlchemyError as e:
        return jsonify({"Error": "Error en la base de datos", "detatls": str(e)}), 500
    except Exception as e:
        return jsonify({"Error": "Error en el servidor", "detail": str(e)}), 500

@app.route("/user", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No hay Datos Verifique"}), 400

        # name = data.get("name")
        # last_name = data.get("last_name")
        # phone = data.get("phone")
        # email = data.get("email")
        # password = data.get("password")
        # is_active = data.get("is_active")

        # if not email or not name or not password or not is_active:
        #    return jsonify({"message": "Se necesitan todos los valores"})

        required = ["name", "last_name", "phone", "email", "password",
                   "is_active"]


        clean_data = {field: data[field] for field in required if field in data}

        for field in required:
            if not data.get(field):
                return jsonify({"message": f"El campo '{field}' es requerido"}), 400



        new_user = User(**clean_data)
            #name=name,
            #last_name=last_name,
            #phone=phone,
            #email=email,
            #password=password,
            #is_active=is_active
             #)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"new_user": new_user.serialize()}), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"Error": "Error en la base de datos", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"Error": "Error en el servidor ", "detalles": str(e)}), 500

@app.route("/user/<int:user_id>", methods=["GET"])
def get_one_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "Usuario no encontrado", "user_id": user_id}), 200
        return jsonify({"user": user.serialize()}), 200
    except SQLAlchemyError as e:
        return jsonify({"Error": "error en la base de datos", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "se produjo un error en el servidor", "Details": str(e)}), 500

@app.route("/user/<int:user_id>", methods=["PUT"]) # prueba
def update_user(user_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No hay datos para actualizar"}), 400
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "Usuario no encontrado"}), 404
        # Campos permitidos para actualizar
        updatable_fields = ["name", "last_name", "phone", "email", "password", "is_active"]
        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])
        db.session.commit()
        return jsonify({"updated_user": user.serialize()}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"Error": "Error en la base de datos", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"Error": "Error en el servidor", "details": str(e)}), 500

@app.route("/user/<int:user_id>", methods=["DELETE"]) # prueba 
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "Usuario no encontrado"}), 404
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Usuario eliminado correctamente"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"Error": "Error en la base de datos", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"Error": "Error en el servidor", "details": str(e)}), 500
# fin modelo User


# rutas para el modelo Character
@app.route("/get_all_character", methods=["GET"])
def get_all_character():
    try:
        characters = Character.query.all()
        if not characters:
            return jsonify({"message": "No hay Characters registrados"}), 200
        return jsonify([character.serialize() for character in characters]), 200
    except SQLAlchemyError as e:
        return jsonify({"Error": "Error, en la base de datos", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"Error": "Error en el servidor", "details": str(e)}), 500

@app.route("/get_one_character/<int:character_id>", methods=["GET"])
def get_one_character(character_id):
    try:
        character = Character.query.get(character_id)
        if not character:
            return jsonify({"message": "Character no encontrado", "character_id": character_id})
        return jsonify({"character": character.serialize()}), 200
    except SQLAlchemyError as e:
        return jsonify({"Error": "Error, en la base de datos", "detail": str(e)}), 500
    except Exception as e:
        return jsonify({"Error": "Error, en el servidor", "detail": str(e)}), 500

@app.route("/add_character", methods=["POST"])
def add_character():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No hay datos Verifique"}), 400
        name = data.get("name")
        age = data.get("age")
        height = data.get("height")
        weight = data.get("weight")
        eye_color = data.get("eye_color")
        hair_color = data.get("hair_color")
        skin_color = data.get("skin_color")
        gender = data.get("gender")
        mass = data.get("mass")
        homeworld = data.get("homeworld")
        birth_year = data.get("birth_year")
        description = data.get("description")
 
        fields = [
            name, age, height, weight, eye_color, hair_color,
            skin_color, gender, mass, homeworld, birth_year,
            description
        ]

        if any(f is None or f == "" for f in fields):
            return jsonify({"message": "Se necesitan todos los campos"})

        new_user = Character(
            name=name,
            age=age,
            height=height,
            weight=weight,
            eye_color=eye_color,
            hair_color=hair_color,
            skin_color=skin_color,
            gender=gender,
            mass=mass,
            homeworld=homeworld,
            birth_year=birth_year,
            description=description
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"New Character": new_user.serialize()}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"Error": "Error en la base de datos", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"Error": "Error en el servidor", "detail": str(e)}), 500

@app.route("/delete_character/<int:character_id>", methods=["DELETE"])
def delete_character(character_id):
    if not character_id:
        return jsonify({"error": "Error, no se recibio Character_id a eliminar"}), 400
    try:
        character = Character.query.get(character_id)
        if not character:
            return jsonify({"error": f"Error, en character_id {character_id} no existe"}), 404
        db.session.delete(character)
        db.session.commit()
        return jsonify({"message": f"Character con ID {character_id}, ha sido eliminado"}),200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": "Error, en la base de datos", "details": str(e)}),500
    except Exception as e:
        return jsonify({"message": "Error, en el servidor", "details": str(e)}),500
    
@app.route("/put_character/<int:character_id", methods=["PUT"])
def put_character(character_id):
    if not character_id:
        return jsonify({"message": "Error no existe character_id para eliminar, verifique"}),400
    data = request.get_json()
    if not data:
        return jsonify({"message": "Error, no hay data a modificar, verifique"}),400
    try:
        character = Character.query.get(character_id)
        if not character:
            return jsonify({"message": f"Error, character_id {character_id} no existe, verifique"}), 404
        updatable_fields = ["name", "age", "height", "weight", "eye_color", "hair_color", "skin_color", "gender",
                            "mass", "homeworld", "birth_year", "description"]
        for field in updatable_fields:
            if field in data:
                setattr(character, field, data[field])
        db.session.commit()
        return jsonify({"updated_character": character.serialize()}),200    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": "Error, en la base de datos", "details": str(e)}),500
    except Exception as e:
        return jsonify({"message": "Error, en el servidor", "details": str(e)}),500
# fin modelo Character

# rutas para modelo Planet
@app.route("/get_all_planet", methods=["GET"])
def get_all_planet():
    try:
        planets = Planet.query.all()
        if not planets:
            return jsonify({"message": "No hay planet registrador"}), 200
        return jsonify([planet.serialize() for planet in planets]), 200
    except SQLAlchemyError as e:
        return jsonify({"Error": "Error, en la base de dastos"}), 500
    except Exception as e:
        return jsonify({"Error": "Error, en el servidor"}), 500

@app.route("/get_one_planet/<int:planet_id>", methods=["GET"])
def get_one_planet(planet_id):
    try:
        planet = Planet.query.get(planet_id)
        if not planet:
            return jsonify({"message": "Planet no existe", "Planet_id": planet_id})
        return jsonify({"planet": planet.serialize()}), 200
    except SQLAlchemyError as e:
        return jsonify({"Error": "Error en la base de datos", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"Error": "Error en el servidor", "details": str(e)}), 500

@app.route("/add_planet", methods=["POST"])
def add_planet():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "Error, no hay dstos"}), 400
        name = data.get("name")
        climate = data.get("climate")
        surface_water = data.get("surface_water")
        diameter = data.get("diameter")
        rotation_period = data.get("rotation_period")
        terrain = data.get("terrain")
        gravity = data.get("gravity")
        orbital_period = data.get("orbital_period")
        population = data.get("population")
        description = data.get("description")
        if (
            not name or
            not climate or
            not surface_water or
            not diameter or
            not rotation_period or
            not terrain or
            not gravity or
            not orbital_period or 
            not population or
            not description

        ): 
            return jsonify({"message": "se necesitan todo los campos "})
        new_planet = Planet(
            name = name,
            climate = climate,
            surface_water = surface_water,
            diameter = diameter,
            rotation_period = rotation_period,
            terrain = terrain,
            gravity = gravity,
            orbital_period = orbital_period,
            population = population,
            description = description
        )
        db.session.add(new_planet)
        db.session.commit()
        return jsonify({"new_planet": new_planet.serialize()}),201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"Error": "Error en la base de datos", "details": str(e)}),500
    except Exception as e:
        return jsonify({"Error": "Error en el servidor", "details": str(e)}),500

@app.route("/planet/<int:planet_id>", methods=["PUT"])
def put_planet(planet_id): # no es la mejor manera de hacerlo en los demas modelos esta corregido
    data = request.get_json()
    if not data:
        return jsonify({"message": "Error, no hay datos verifique"}),400
    new_name = data.get("name")
    new_climate = data.get("climate")
    new_surface_water = data.get("surface_water")
    new_diameter = data.get("diameter")
    new_rotation_period = data.get("rotation_period")
    new_terrain = data.get("terrain")
    new_gravity = data.get("gravity")
    new_orbital_period = data.get("orbital_period")
    new_population = data.get("population")
    new_description = data.get("description")
    if(
        not new_name or
        not new_climate or
        not new_surface_water or
        not new_diameter or
        not new_rotation_period or
        not new_terrain or 
        not new_gravity or
        not new_orbital_period or 
        not new_population or 
        not new_description 
    ):
        return jsonify({"message": "Se necesitan todos los datos"})
    try:
        planet = Planet.query.get(planet_id)
        if not planet:
           return jsonify({"message": "Planet no encontrado, verifique"}), 404 
        planet.name = new_name  
        planet.climate = new_climate 
        planet.surface_water = new_surface_water
        planet.diameter = new_diameter
        planet.rotation_period = new_rotation_period 
        planet.terrain = new_terrain 
        planet.gravity = new_gravity 
        planet.orbital_period = new_orbital_period 
        planet.population = new_population 
        planet.description = new_description
        db.session.commit()
        return jsonify({"message": "Planet, modificado correctamente", "planet": planet.serialize()}),200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": "Error, en la base de datos", "details": str(e)}),500
    except Exception as e:
        return jsonify({"message": "Error, en el servidor", "details": str(e)}), 500

@app.route("/planet/<int:planet_id", mothods=["DELETE"])
def delete_planet(planet_id):
    try:
        planet = Planet.query.get(planet_id)
        if not planet:
            return jsonify({"message": "Error, planet no existe"}),404
        db.session.delete(planet)
        db.session.commit()
        return jsonify({"message": "Planet eliminado correctamente"}),200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": "Error, en la base de datos", "details": str(e)}),500
    except Exception as e:
        return jsonify({"message": "Error, en el servidor", "details": str(e)}),500
# fin modelo Planet

# ruras para modelo user_planet
@app.route("/user_planet", methods=["POST"])
def add_user_planet():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No hay datos Verifique "}), 400
 
        required_fields = [
           "user_id", "planet_id"]

        # Validación
        missing = validate_required(data, required_fields)

        if missing:
            return jsonify({
                "message": "Faltan campos requeridos",
                "missing_fields": missing
            }), 400

        user_id = data.get("user_id")
        planet_id = data.get("planet_id")
        #if not user_id or not planet_id:
        #    return jsonify({"message": "Se necesitan todos los datos"})
        new_planet_fav = user_planet.insert().values(
            user_id=user_id,
            planet_id=planet_id
        )
        db.session.execute(new_planet_fav)
        db.session.commit()
        return jsonify({"New_planet_favorite": "Favorito creado"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"Error": "Error en la base de dastos", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"Error": "Error en el servidor", "details": str(e)}), 500

@app.route("/delete_user_planet", methods=["DELETE"])
def delete_user_planet():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No hay datos verifique"}), 400
    required_fields = ["user_id", "planet_id"]
    missing = validate_required(data, required_fields)
    if missing:
        return jsonify({
            "message": "Faltan campos requeridos",
            "missing_fields": missing
        }),400
    try:
        stmt = user_planet.delete().where(
            user_planet.c.user_id == data["user_id"],
            user_planet.c.planet_id == data["planet_id"]
        )
        result = db.session.execute(stmt)
        db.session.commit()
        if result.rowcount == 0:
            return jsonify({"message": "No existe ese favotiro"}), 404
        return jsonify({"message": "Favorito eliminado correctamente"}),200
    except SQLAlchemyError as e:
        db.session.rollbak()
        return jsonify({"Error": "Error en la base de datos", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"Error": "Error en el servidor", "details": str(e)}),500

@app.route("/user_planet", methods=["PUT"]) # ruta de prueba 
def update_user_planet():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No hay datos verifique"}), 400

        required_fields = ["user_id", "planet_id"]
        missing = validate_required(data, required_fields)

        if missing:
            return jsonify({
                "message": "Faltan campos requeridos",
                "missing_fields": missing
            }), 400

        new_planet_id = data.get("new_planet_id")
        new_user_id = data.get("new_user_id")

        if not new_planet_id and not new_user_id:
            return jsonify({
                "message": "Debes enviar new_planet_id o new_user_id para modificar"
            }), 400

        stmt = user_planet.update().where(
            user_planet.c.user_id == data["user_id"],
            user_planet.c.planet_id == data["planet_id"]
        ).values(
            user_id=new_user_id if new_user_id else data["user_id"],
            planet_id=new_planet_id if new_planet_id else data["planet_id"]
        )

        result = db.session.execute(stmt)
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({"message": "No existe ese favorito"}), 404

        return jsonify({"message": "Favorito modificado correctamente"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"Error": "Error en la base de datos", "details": str(e)}), 500

    except Exception as e:
        return jsonify({"Error": "Error en el servidor", "details": str(e)}), 500
# fin modelo user_planet

# rutas para modelo user_character
@app.route("/add_user_character", methods=["POST"])
def add_user_character():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No hay datos verifique"}),400
    required_fields = ["user_id", "character_id"]
    missing = validate_required(data, required_fields)
    if missing:
       return jsonify({
           "message": "Faltan campos requeridos",
            "missing_fields": missing
        }), 400
    try:
        user_id = data.get("user_id")
        character_id = data.get("character_id")
        new_char_fav = user_character.insert().values(
            user_id = user_id,
            character_id = character_id
        )
        db.session.execute(new_char_fav)
        db.session.commit()
        return jsonify({"New_character_fav": "Favorito creado", "test": {
            "user_id": user_id,
            "character_id": character_id,
        }}),201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"Error": "Error en la base de datos", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"Error": "Error en el servidor", "Details": str(e)}),500

@app.route("/delete_user_character", methods=["DELETE"])
def delete_user_character():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No hay datos verifique"}), 400
    required_fields = ["user_id", "character_id"]
    missing = validate_required(data, required_fields)
    if missing:
        return jsonify({
            "message": "Faltan campos requeridos",
            "missing_fields": missing
        }),400
    try:
        stmt = user_character.delete().where(
            user_character.c.user_id == data["user_id"],
            user_character.c.character_id == data["character_id"]
        )
        result = db.session.execute(stmt)
        db.session.commit()
        if result.rowcount == 0:
            return jsonify({"message": "No existe ese favotiro"}), 404
        return jsonify({"message": "Favorito eliminado correctamente"}),200
    except SQLAlchemyError as e:
        db.session.rollbak()
        return jsonify({"Error": "Error en la base de datos", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"Error": "Error en el servidor", "details": str(e)}),500
# fin modelo user_character

# rutas para modelo de user_vehicle
@app.route("/add_user_vehicle", methods=["POST"])
def add_user_vehicle():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No hay datos Verifique"}), 400
    required_fields = ["user_id", "vehicle_id"]
    missing = validate_required(data, required_fields)
    if missing:
        return jsonify({"message": "faltan campos requeridos", "missing_fields": missing}),400
    try:
        user_id = data.get("user_id")
        vehicle_id = data.get("vehicle_id")
        new_vehicle_fav = user_vehicle.insert().values(
            user_id = user_id,
            vehicle_id = vehicle_id
        )
        db.session.execute(new_vehicle_fav)
        db.session.commit()
        return jsonify({"new_vehicle_fav": "Favorito creado "}),201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"Error": "error en la base de datos", "details": str(e)}),500
    except Exception as e:
        return jsonify({"Error": "Error en el servidor", "details": str(e)}), 500

@app.route("/delete_user_vehicle", methods=["DELETE"])
def delete_user_vehicle():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No hay datos verifique"}), 400
    required_fields = ["user_id", "vehicle_id"]
    missing = validate_required(data, required_fields)
    if missing:
        return jsonify({
            "message": "Faltan campos requeridos",
            "missing_fields": missing
        }),400
    try:
        stmt = user_vehicle.delete().where(
            user_vehicle.c.user_id == data["user_id"],
            user_vehicle.c.vehicle_id == data["vehicle_id"]
        )
        result = db.session.execute(stmt)
        db.session.commit()
        if result.rowcount == 0:
            return jsonify({"message": "No existe ese favotiro"}), 404
        return jsonify({"message": "Favorito eliminado correctamente"}),200
    except SQLAlchemyError as e:
        db.session.rollbak()
        return jsonify({"Error": "Error en la base de datos", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"Error": "Error en el servidor", "details": str(e)}),500
# fin modelo user_vehicle


# rutas para modelo vehicles
@app.route("/get_all_vehicle", methods=["GET"])
def get_all_vehicles():
    try:
        vehicles = Vehicle.query.all()
        if not vehicles:
            return jsonify({"message": "No hay Vehicles registrador"}), 200
        return jsonify([vehicle.serialize() for vehicle in vehicles]), 200
    except SQLAlchemyError as e:
        return jsonify({"Error": "Error en la base de datos", "Details": str(e)}), 500
    except Exception as e:
        return jsonify({"Error": "Error en el servidor", "Details": str(e)}),500

@app.route("/get_one_vehicle/<int:vehicle_id>", methods=["GET"])
def get_one_vehicle(vehicle_id):
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({"Error": f"No existe el vehicle con id {vehicle_id}"}), 404
        return jsonify({"vehicle": vehicle.serialize()}),200
    except SQLAlchemyError as e:
        return jsonify({"Error": "Error en la base de dstos", "Details": str(e)})
    except Exception as e:
        return jsonify({"Error": "Error en el servidor", "Details": str(2)})
 
@app.route("/add_vehicle", methods=["POST"])
def add_vehicle():
    data = request.get_json()
    if not data:
        return jsonify({"Error": "No hay datos verifique"}),400
    required_fields = ["name", "consumables", "cargo_capacity", "passenger",
                       "max_atmosphering_speed", "crew", "length", "model", "cost_in_credits",
                       "manufactured", "vehicle_class", "description"]
    missing = validate_required(data, required_fields)
    if missing:
        return jsonify({"message": "Faltan campos requeridos",
            "missing_fields": missing
        }), 400
    try:
        name = data.get("name")
        consumables = data.get("consumables")
        cargo_capacity = data.get("cargo_capacity")
        passenger = data.get("passenger")
        max_atmosphering_speed = data.get("max_atmosphering_speed")
        crew = data.get("crew")
        length = data.get("length")
        model = data.get("model")
        cost_in_credits = data.get("cost_in_credits")
        manufactured = data.get("manufactured")
        vehicle_class = data.get("vehicle_class")
        description = data.get("description") 
        new_vehicle = Vehicle(
            name = name,
            consumables = consumables,
            cargo_capacity = cargo_capacity,
            passenger = passenger,
            max_atmosphering_speed = max_atmosphering_speed,
            crew = crew,
            length = length,
            model = model,
            cost_in_credits = cost_in_credits,
            manufactured = manufactured,
            vehicle_class = vehicle_class,
            description = description
        )
        db.session.add(new_vehicle)
        db.session.commit()
        return jsonify({"new_vehicle": new_vehicle.serialize()}),201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"Error": "error en la base de datos ", "details": str(e)}),500
    except Exception as e:
        return jsonify({"Error": "error en el servidor", "details": str(e)}),500

@app.route("/vehicle/<int:vehicle_id", methods=["DELETE"])
def delete_vehicle(vehicle_id):
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({"message": "Error, Vehicle no encontrado, Verifique"}), 404  
        deleted_data = vehicle.serialize()
        db.session.delete(vehicle) # el orm elimina el registro e internamente hace dele from vehicle where vehicle.id = vehicle_id           
        # Planet.query.filter_by(id=planet_id).delete() # no controla las relaciones , pero creo que la base de datos mysql se encargaria de eso
        # db.session.execute(db.delete(Planet).where(Planet.id == planet_id)) # compatible con la nueva version de sqlalchemy 2.0
        db.session.commit()
        return jsonify({
            "message": "Registro eliminado Correctamente", 
            "deleted": deleted_data
            }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": "Error, en la base de datos", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"message": "Error, en el servidor", "details": str(e)})

@app.route("/vehicle/<int:vehicle_id>", methods=["PUT"])
def put_vehicle(vehicle_id):
   data = request.get_json()
   if not data:
       return jsonify({"message": "No hay datos que procesar, verifique"}), 400
   try:
       vehicle = Vehicle.query.get(vehicle_id)  
       if not vehicle:
            return jsonify({"error": "Vehicle no encontrado, verifique "}), 404
       for field in ["name", "consumables", "cargo_capacity", "passenger",
                      "max_atmosphering_speed", "crew", "length", "model", "cost_in_credits",
                      "manufactured", "vehicle_class", "description"]:
           if field in data:
               setattr(vehicle, field, data[field])  # actualizacion dinamica de datos 
           db.session.commit()
           return jsonify({
               "message": "Vehicle actualizado correctamente",
               "update": vehicle.serialize()
           }) 
   except SQLAlchemyError as e:
       db.session.rollback()
       return jsonify({"message": "Error, en la base de datos"}),500
   except Exception as e:
       return jsonify({"message": "Error, en el servidor"}),500
       
# fin modelo vehicles





@app.route("/users/favorites/<int:user_id>", methods=["GET"])
def get_user_favoritos(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "no se encontrol el usuario con el id- " + str(user_id)})
    fav_planets = user.planets
    fav_planets_serialized = [planet.serialize() for planet in fav_planets]
    fav_character = user.characters
    fav_character_serialized = [character.serialize()
                                for character in fav_character]
    fav_vehicles = user.vehicles
    fav_vehicles_serialized = [vehicle.serialize() for vehicle in fav_vehicles]
    return jsonify({"fav_planets": fav_planets_serialized, "fav_character": fav_character_serialized,
                    "fav_vehicles": fav_vehicles_serialized})


# @app.route("/",methods=["GET"])
# def algo():
    # recupero la informacion de la db
    # data = .....
    # chequeo si lo que se supone que recupere tiene algo
    # si no, respondo con un error al cliente
    # si esta bien mando la respuesta al frontend


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
