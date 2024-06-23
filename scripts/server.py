from flask import Flask, Response
import time
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"


def generate_data():
    """Generator function that yields data continuously."""
    count = 0
    while True:
        time.sleep(1)
        yield f"data: {count}\n\n"
        count += 1


@app.route("/generate")
@cross_origin()
def generate():
    """Route to return a streamed response from the generator."""
    return Response(generate_data(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(debug=True)
