"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint, current_app
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)


@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200

@api.route('/login', methods=['POST'])
def login(): 
    body = request.get_json(silent=True)
    if body is None: 
        return jsonify({"msg": "el cuerpo esta vacio"}), 400
    if 'email' not in body: 
        return jsonify({"msg": "email es requerido"}), 400
    if 'password' not in body: 
        return jsonify({"msg": "password es requerido"}), 400
    user = User.query.filter_by(email=body["email"]).all()
    print(user[0].serialize())
    if user == []:
        return jsonify({"msg": "user or password invalid"}), 400
    
    correct_password = current_app.bcrypt.check_password_hash(user[0].password, body["password"]) 
    if correct_password is False:
        return jsonify({"msg": "user or password invalid"}), 400
    access_token = create_access_token(identity=user[0].email)
    return jsonify({"msg": "ok", 
                    "access_token" : access_token, 
                    "user": user[0].serialize()
                    }), 200 

@api.route('/private', methods=['GET'])
@jwt_required()
def private(): 
    identity = get_jwt_identity()
    print(identity)
    return jsonify({"msg": "thi is a provate message"})

@api.route('/signup', methods=['POST'])
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
    new_user.password = current_app.bcrypt.generate_password_hash(body['password']).decode('utf-8')
    new_user.is_active = True

    db.session.add(new_user)
    db.session.commit() 

    return jsonify({"msg": "User creado"}), 201

#Validacion del token
@api.route("/validation", methods=["GET"])
@jwt_required()
def valid_token():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email = current_user).first()
    if user is None:
        return jsonify({"status": False}), 401
    response_body = {
        "status": True,
        "user": user.serialize()
    }
    return jsonify(response_body), 200