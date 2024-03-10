from flask import Flask, request
from flask_restful import Api, Resource
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)
api = Api(app)

# MongoDB configuration
client = MongoClient("mongodb://localhost:27017/")
db = client["user_db"]
users_collection = db["users"]

class UserRegistration(Resource):
    def post(self):
        data = request.get_json()

        if not data.get("username") or not data.get("password"):
            return {"message": "Username and password are required"}, 400

        # Check if the username is already taken
        if users_collection.find_one({"username": data["username"]}):
            return {"message": "Username already taken"}, 400

        # Generate a unique user ID
        user_id = str(uuid.uuid4())

        hashed_password = generate_password_hash(data["password"], method="sha256")

        # Store user information in the database
        users_collection.insert_one({
            "user_id": user_id,
            "username": data["username"],
            "password": hashed_password
        })

        return {"message": "User registered successfully", "user_id": user_id}, 201


class UserAuthentication(Resource):
    def post(self):
        data = request.get_json()

        if not data.get("username") or not data.get("password"):
            return {"message": "Username and password are required"}, 400

        # Find the user in the database
        user = users_collection.find_one({"username": data["username"]})

        if not user or not check_password_hash(user["password"], data["password"]):
            return {"message": "Invalid credentials"}, 401

        return {"message": "User authenticated successfully", "user_id": user["user_id"]}, 200


api.add_resource(UserRegistration, '/register')
api.add_resource(UserAuthentication, '/authenticate')

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=6667)