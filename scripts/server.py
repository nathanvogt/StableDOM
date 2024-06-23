from flask import Flask, jsonify, make_response, request
from flask_cors import CORS, cross_origin

# Create the Flask app
print("cum")
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


# Function to add headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    return response


# Handle preflight requests for the '/step' endpoint
@app.route("/step", methods=["OPTIONS"])
@cross_origin(
    supports_credentials=True
)  # Ensure CORS settings are applied here as well
def preflight():
    response = make_response(jsonify(success=True), 200)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    return response


# Define the route '/step' with a JSON response
@app.route("/step", methods=["GET", "POST"])
@cross_origin(supports_credentials=True)  # Handles CORS for actual requests
def step():
    data = {"key1": "value1", "key2": "value2", "key3": "value3"}
    response = jsonify(data)
    response.headers["Content-Type"] = "application/json"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    return response


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
