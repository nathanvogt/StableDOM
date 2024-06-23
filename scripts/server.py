from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import base64
from eval_td import make_main, app as eval_app

app = Flask(__name__)
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)

CORS(app)
socketio = SocketIO(app, cors_allowed_origins='*')


# argv = "--checkpoint_name assets/td_csg2da.pt --ar_checkpoint_name assets/ar_csg2da.pt --problem_filename assets/csg2da_test_set.pkl --device cpu".split(" ")


@socketio.on('upload-image')
def handle_upload_image(json):
    image_data = json['image']

    main = make_main(update_step, image_data)
    main()
    # update_step({"expression": "Image processed successfully", "image": image_data})

def update_step(step):
    print("Updating step")
    emit('new-step', step, broadcast=True)

def initialize(argv):
    socketio.run(app, debug=True)

if __name__ == '__main__':
    eval_app.run(initialize)