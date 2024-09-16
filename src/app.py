"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from api.utils import APIException, generate_sitemap
from api.models import db, User
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

from flask_bcrypt import Bcrypt

# from models import Person

ENV = "development" if os.getenv("FLASK_DEBUG") == "1" else "production"
static_file_dir = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '../public/')
app = Flask(__name__)
app.url_map.strict_slashes = False

bcrypt = Bcrypt(app)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret" 
jwt = JWTManager(app)

# database condiguration
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type=True)
db.init_app(app)

# add the admin
setup_admin(app)

# add the admin
setup_commands(app)

# Add all endpoints form the API with a "api" prefix
app.register_blueprint(api, url_prefix='/api')

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# any other endpoint will try to serve it like a static file


@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0  # avoid cache memory
    return response

@app.route('/api/signup', methods=['POST'])
def signup(): 
    body = request.get_json(silent=True)
    if body is None: 
        return jsonify({'msg': 'el cuerpo esta vacio'}), 400
    if 'email' not in body: 
        return jsonify({'msg': 'email es requerido'}), 400
    if 'password' not in body: 
        return jsonify({'msg': 'password es requerido'}), 400
    new_user = User()
    new_user.email = body['email']
    new_user.password = bcrypt.generate_password_hash(body['password']).decode('utf-8')
    new_user.is_active = True

    db.session.add(new_user)
    db.session.commit() 

    return jsonify({"msg": "User creado"}), 201

@app.route('/api/login', methods=['POST'])
def login(): 
    body = request.get_json(silent=True)
    if body is None: 
        return jsonify({"msg": "el cuerpo esta vacio"}), 400
    if 'email' not in body: 
        return jsonify({"msg": "email es requerido"}), 400
    if 'password' not in body: 
        return jsonify({"msg": "password es requerido"}), 400
    user = User.query.filter_by(email=body["email"]).all()
    if len(user) == 0: 
        return jsonify({"msg": "user or password invalid"}), 400
    
    correct_password = bcrypt.check_password_hash(user[0].password, body["password"]) 
    if correct_password is False:
        return jsonify({"msg": "user or password invalid"}), 400
    access_token = create_access_token(identity=user[0].email)
    return jsonify({"msg": "ok", "access_token" : access_token}), 200 

@app.route('/api/private', methods=['GET'])
@jwt_required()
def private(): 
    identity = get_jwt_identity()
    print(identity)
    return jsonify({"msg": "thi is a provate message"})

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)
