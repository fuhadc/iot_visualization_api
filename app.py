import datetime
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_cors import CORS  # Import the CORS module
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)
api = Api(app)
CORS(app)  # Enable CORS for all routes

# MongoDB configuration
client = MongoClient("mongodb://localhost:27017/")
db = client["user_db"]
users_collection = db["users"]
collection = db['data']
@app.route('/', methods=['GET'])
def documentation():
    return {"message": "Username and password are required"} ,200

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
temperature_data = [
    {"time": "12:00 PM", "temperature": 23.5},
    {"time": "12:15 PM", "temperature": 24.0},
    {"time": "12:30 PM", "temperature": 24.5},
    {"time": "12:45 PM", "temperature": 25.0},
    {"time": "1:00 PM", "temperature": 25.5},
    {"time": "1:15 PM", "temperature": 26.0},
    {"time": "1:30 PM", "temperature": 26.5},
    {"time": "1:45 PM", "temperature": 27.0},
    {"time": "2:00 PM", "temperature": 27.5},
    {"time": "2:15 PM", "temperature": 28.0},
    {"time": "2:30 PM", "temperature": 28.5},
    {"time": "2:45 PM", "temperature": 29.0},
    {"time": "3:00 PM", "temperature": 29.5},
    {"time": "3:15 PM", "temperature": 30.0},
    {"time": "3:30 PM", "temperature": 30.5},
    {"time": "3:45 PM", "temperature": 31.0},
    {"time": "4:00 PM", "temperature": 31.5},
    {"time": "4:15 PM", "temperature": 32.0},
    {"time": "4:30 PM", "temperature": 32.5},
    {"time": "4:45 PM", "temperature": 33.0},
]

class TemperatureResource(Resource):
    def get(self):
        return {"data": temperature_data}


class UserDataResource(Resource):
    def post(self, userid, parameter_name):
        try:
            # Get the value from the request data
            value = request.json['value']

            # Save data to MongoDB with timestamp
            data = {
                "userid": userid,
                "parameter_name": parameter_name,
                "value": value,
                "timestamp": datetime.utcnow()
            }
            collection.insert_one(data)

            return {"message": "Data saved successfully"}, 201

        except KeyError:
            return {"error": "Invalid data format"}, 400

    

class ControlSystem(Resource):
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["user_db"]
        self.collection = self.db['data']
        
    def post(self, userid, value):
        if value not in ['0', '1']:
            return {"error": "Invalid value. Only 0 or 1 allowed."}, 400
            
        try:
            # Save data to MongoDB with timestamp
            data = {
                "userid": userid,
                "parameter_name": "control",
                "value": int(value),
            }
            self.collection.insert_one(data)

            return {"message": "Data saved successfully"}, 201

        except Exception as e:
            return {"error": str(e)}, 500
class Controlget(Resource):
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["user_db"]
        self.collection = self.db['data']
    def get(self, userid):
        try:
            # Retrieve the latest control value for the user
            latest_data = self.collection.find_one({"userid": userid, "parameter_name": "control"}, sort=[("timestamp", -1)])
            
            if latest_data:
                value = latest_data["value"]
                return {"data":1},200
            else:
                return {"data":0},200

                
        except Exception as e:
            return {"error": str(e)}, 500
api.add_resource(Controlget,'/Controlget/<string:userid>')
api.add_resource(TemperatureResource, '/temperature')
api.add_resource(UserDataResource, '/userdata/<string:userid>/<string:parameter_name>')
api.add_resource(UserRegistration, '/register')
api.add_resource(UserAuthentication, '/authenticate')
api.add_resource(ControlSystem, '/control/<string:userid>/<string:value>')
if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=2020)