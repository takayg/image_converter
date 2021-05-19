import os
import numpy as np
from flask import Flask, render_template, request, url_for, send_from_directory
from werkzeug.utils import secure_filename
import cv2
import base64

app = Flask(__name__)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'PNG', 'JPG'])
IMAGE_WIDTH = 256
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.urandom(24)

def allowed_file(filename): 
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def ndarray2base64(dst, extension):
    result, dst_data = cv2.imencode('.' + extension, dst)
    dst_base64 = base64.b64encode(dst_data).decode('utf-8')

    return dst_base64

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        img_file = request.files['img_file']
    
        # check file's extension
        if img_file and allowed_file(img_file.filename):
            filename = secure_filename(img_file.filename)
        else:
            return ''' <p>This extension is not permitted</p> '''
        
        # get file's extension
        extension = filename.rsplit('.', 1)[1]

        # make image array for using OpenCV
        f = img_file.stream.read()
        img_array = np.asarray(bytearray(f), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # make raw image(small image)
        img_height, img_width = img.shape[0], img.shape[1]
        raw_img = cv2.resize(img, (IMAGE_WIDTH, int(IMAGE_WIDTH * img_height / img_width)))

        # make gray image
        gray_img = cv2.cvtColor(raw_img, cv2.COLOR_BGR2GRAY)
        
        # convert image to binary data
        b64_raw_data = ndarray2base64(raw_img, extension)
        b64_gray_data = ndarray2base64(gray_img, extension)

        return render_template('index.html', b64_raw_data=b64_raw_data, b64_gray_data=b64_gray_data, extension=extension)
    
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.debug = True
    app.run()