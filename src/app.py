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
from models import db, Person
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
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


@app.route("/health-check", methods=["GET"])
def health_check():
    return "ok"

# consulta todas las personas de mi base de datos
@app.route("/person", methods=["GET"])
def get_all():
    
    people = Person.query.all()
    return jsonify(list(map(lambda item: item.serialize(), people))), 200
        
           
# consulta por id las personas
@app.route("/person/<int:theid>", methods=["GET"])
def get_one_person(theid=None):
    people = Person.query.get(theid)
    if people:
        return jsonify(people.serialize()), 200
    else:
        return jsonify({"message":"person not found"}), 404


# agrega una nueva persona a mi base de datos
@app.route("/person", methods=["POST"])
def add_new_person():
    body = request.json

    if body.get("name") is None:
        return jsonify({"message":"wrong property"}),400
    if body.get("lastname") is None:
        return jsonify({"message":"wrong property"}),400
    
    person = Person(name=body.get("name"), lastname=body.get("lastname"))

    db.session.add(person)

    try:
        db.session.commit()  
        return jsonify({"message":"user registered success"}), 201  

    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify({"message":f"error: {error}"}), 500


# editamos una persona por su identificador único (id)
@app.route("/person/<int:theid>", methods=["PUT"])
def update_person(theid=None):
    if theid is None:
        return jsonify({"message":"Wrong property"}), 400

    body = request.json

    if body.get("name") is None:
        return jsonify({"message":"wrong property"}),400
    if body.get("lastname") is None:
        return jsonify({"message":"wrong property"}),400

    person = Person.query.get(theid)

    if person is None:
        return jsonify({"message":"the user not found"}), 404

    person.name = body.get("name")
    person.lastname = body.get("lastname")

    try:
        db.session.commit()
        return jsonify({"message":"user updated success"}), 201
    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify({"message":f"error: {error}"}), 500

    

# Eliminamos a las personas por su identificador único (id)
@app.route("/person/<int:position>", methods=["DELETE"])
def delete_person(position=None):
    person = Person.query.get(position)

    if person is None:
        return jsonify({"message":"the user not found"}), 404   

    if person is not None:
        db.session.delete(person)

        try:
            db.session.commit()
            return jsonify([]), 204
        except Exception as error:
            print(error)
            db.session.rollback()
            return jsonify({"message":f"error: {error.args}"})


# query usados en este proyecto 
# Model.query.all() --> consultamos todas los registro de la tabla
# Model.query.get(theid) --> consultamos un registro de la clase pasandole el id
# Crear un registro en la tabla
## instanciamos la clase y le agregamos los parametros a guardar
### instance =  Model(name=body.get("name"), lastname=body.get("lastname"))
### db.session.add(Model) --> agregamos en la session (aquí aún no se guarda)
### db.session.commit() --> aquí se guarda el registro en la base de datos

# borrar 
##  db.session.delete(Model)



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
