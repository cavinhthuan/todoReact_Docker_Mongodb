from flask import Flask, request, jsonify, send_file
from gtts import gTTS
import os
import requests
import traceback
from flask_cors import CORS
from pymongo import MongoClient
import time

# from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm
import pandas as pd
from bson import json_util
from werkzeug.utils import secure_filename
import os
# Check if the upload folder exists
app = Flask(__name__)

CORS(app)


# Connect to MongoDB
# mongo_uri = "mongodb+srv://cathuan113:cvt30112001@cluster0.pqpc4hx.mongodb.net/?retryWrites=true&w=majority"  # Update with your MongoDB URI
# database_name = "todo"  # Update with your database name
mongo_uri = os.environ['MONGO_URI']  # Update with your MongoDB URI
database_name = "todo"  # Update with your database name
print(mongo_uri)
client = MongoClient(mongo_uri)
db = client[database_name]


@app.errorhandler(Exception)
def handle_error(e):
    traceback.print_exc()
    return {"error": str(e)}, 500


@app.route('/add', methods=['POST'])
def addTodo():
    try:
        data = request.get_json()
        message = data.get("message", "")
        id = data.get("id", "")

        if not message:
            return jsonify({"error": "message not provided"}), 400


        # Store the result in MongoDB
        greeting_collection = db["TodoApp"]
        greeting_collection.insert_one({"id": id, "message": message})

        return jsonify({"result ": "OK"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/all', methods=['GET'])
def getAllTodo():
    try:
        greeting_collection = db["TodoApp"]
        todos_cursor = greeting_collection.find({}, {"id":1, "message":1})

        # Convert the cursor to a list of dictionaries and serialize ObjectId to string
        todos_list = []
        for todo in todos_cursor:
            todo["_id"] = str(todo["_id"])  # Convert ObjectId to string
            todos_list.append(todo)
        return json_util.dumps({"todos": todos_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/edit', methods=['POST'])
def editTodo():
    try:
        data = request.get_json()
        id = data.get("id", "")
        message = data.get("newMessage", "")

        if not message:
            return jsonify({"error": "message not provided"}), 400


        # Store the result in MongoDB
        greeting_collection = db["TodoApp"]
        greeting_collection.update_one({"id": id}, {"$set":{"message": message}})

        return jsonify({"result ": "OK"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/delete', methods=['POST'])
def deleteTodo():
    try:
        data = request.get_json()
        id = data.get("id", "")

        if not id:
            return jsonify({"error": "message not provided"}), 400


        # Store the result in MongoDB
        greeting_collection = db["TodoApp"]
        greeting_collection.delete_one({"id": id})

        return jsonify({"result ": "OK"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Configure the upload folder and allowed extensions
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Set the upload folder and the maximum file size
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB

# Define a function to check the file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Define a function to generate a unique filename
def unique_filename(filename):
    # Split the filename into name and extension
    name, ext = os.path.splitext(filename)
    # Generate a unique name using the current timestamp
    name = name + '_' + str(int(time.time()))
    # Return the unique filename
    return name + ext
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    # Create the upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'])
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        print(request.files)
        # Check if the request has a file
        if 'file' not in request.files:
            return jsonify({"error": "no file in request"}), 400
        # Get the file from the request
        file = request.files['file']
        # Check if the file is empty
        if file.filename == '':
            return jsonify({"error": "no file selected"}), 400
        # Check if the file has a valid extension
        if not allowed_file(file.filename):
            return jsonify({"error": "invalid file extension"}), 400
        # Generate a unique filename
        filename = unique_filename(file.filename)
        # Save the file to the upload folder
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Return a success response
        return jsonify({"result": "OK", "filename": filename})
    except Exception as e:
        # Return an error response
        return jsonify({"error": str(e)}), 500
    
@app.route('/', methods=['GET'])
def home():
    return "TODO: API"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
