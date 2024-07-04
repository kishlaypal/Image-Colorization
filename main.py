from flask import Flask, request, send_file, render_template
import os
import cv2
import numpy as np
import io
from PIL import Image

app = Flask(__name__)


prototxt_path = 'models/colorization_deploy_v2.prototxt'
model_path = 'models/colorization_release_v2.caffemodel'
kernel_path = 'models/pts_in_hull.npy'


net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
points = np.load(kernel_path)


points = points.transpose().reshape(2, 313, 1, 1)
net.getLayer(net.getLayerId("class8_ab")).blobs = [points.astype(np.float32)]
net.getLayer(net.getLayerId("conv8_313_rh")).blobs = [np.full([1, 313], 2.606, dtype="float32")]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/colorize', methods=['POST'])
def colorize_image():
    file = request.files['file']
    if not file:
        return "No file uploaded", 400


    file_stream = io.BytesIO(file.read())
    bw_image = Image.open(file_stream).convert('RGB')
    bw_image = np.array(bw_image)

    normalized = bw_image.astype("float32") / 255.0
    lab = cv2.cvtColor(normalized, cv2.COLOR_BGR2LAB)


    resized = cv2.resize(lab, (224, 224))
    L = cv2.split(resized)[0]
    L -= 50


    net.setInput(cv2.dnn.blobFromImage(L))
    ab = net.forward()[0, :, :, :].transpose((1, 2, 0))


    ab = cv2.resize(ab, (bw_image.shape[1], bw_image.shape[0]))
    L = cv2.split(lab)[0]


    colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)
    colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
    colorized = (255.0 * colorized).astype("uint8")


    _, buffer = cv2.imencode('.jpg', colorized)
    colorized_stream = io.BytesIO(buffer)

    return send_file(colorized_stream, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)





