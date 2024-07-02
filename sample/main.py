import cv2
import numpy as np
import os

# Paths to the model files
prototxt_path = 'models/colorization_deploy_v2.prototxt'
model_path = 'models/colorization_release_v2.caffemodel'
kernel_path = 'models/pts_in_hull.npy'
image_path = 'C:/Users/kishl/OneDrive/Desktop/Image Colouriser project/sample/your_img_file_name.jpg'

# Check if files exist
if not os.path.isfile(prototxt_path):
    raise ValueError(f"Prototxt file not found at path: {os.path.abspath(prototxt_path)}")
if not os.path.isfile(model_path):
    raise ValueError(f"Caffe model file not found at path: {os.path.abspath(model_path)}")
if not os.path.isfile(kernel_path):
    raise ValueError(f"Kernel file not found at path: {os.path.abspath(kernel_path)}")
if not os.path.isfile(image_path):
    raise ValueError(f"Image file not found at path: {os.path.abspath(image_path)}")

# Load the model
net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
points = np.load(kernel_path)

# Adjust the points shape and load them into the model
points = points.transpose().reshape(2, 313, 1, 1)
net.getLayer(net.getLayerId("class8_ab")).blobs = [points.astype(np.float32)]
net.getLayer(net.getLayerId("conv8_313_rh")).blobs = [np.full([1, 313], 2.606, dtype="float32")]

# Read and preprocess the image
bw_image = cv2.imread(image_path)
if bw_image is None:
    raise ValueError(f"Image not found or unable to read at path: {os.path.abspath(image_path)}")

normalized = bw_image.astype("float32") / 255.0
lab = cv2.cvtColor(normalized, cv2.COLOR_BGR2LAB)

# Resize the L channel and subtract 50 for model input
resized = cv2.resize(lab, (224, 224))
L = cv2.split(resized)[0]
L -= 50

# Predict the ab channels
net.setInput(cv2.dnn.blobFromImage(L))
ab = net.forward()[0, :, :, :].transpose((1, 2, 0))

# Resize the ab channels to match the original image size
ab = cv2.resize(ab, (bw_image.shape[1], bw_image.shape[0]))
L = cv2.split(lab)[0]

# Combine the L channel with the predicted ab channels
colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)
colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
colorized = (255.0 * colorized).astype("uint8")

screen_res = 1280, 720  # Example resolution, can be changed based on actual screen resolution
scale_width = screen_res[0] / bw_image.shape[1]
scale_height = screen_res[1] / bw_image.shape[0]
scale = min(scale_width, scale_height)

# Resize the images to fit the screen
window_width = int(bw_image.shape[1] * scale)
window_height = int(bw_image.shape[0] * scale)
bw_image_resized = cv2.resize(bw_image, (window_width, window_height))
colorized_resized = cv2.resize(colorized, (window_width, window_height))


# Display the images
cv2.imshow("BW Image", bw_image_resized)
cv2.imshow("Colorized", colorized_resized)
cv2.waitKey(0)
cv2.destroyAllWindows()
