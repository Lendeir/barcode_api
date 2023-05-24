import asyncio
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from pyzbar import pyzbar
import cv2
import os
from PIL import Image

input_pdf_path = "/pdf/"
output_images_folder = '/result/'
error_scan_images = '/error_scan/'

async def resize_image(input_image_path, output_image_path, scale_factor):
    img = Image.open(input_image_path)
    width, height = img.size
    print(width)
    width = int(width * scale_factor)
    height = int(height * scale_factor)
    img = img.resize((width, height))
    width, height = img.size
    print(width)
    img = img.convert("RGB")
    img.save(output_image_path)

async def find_barcodes(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    barcodes = pyzbar.decode(gray)
    return barcodes

app = Flask(__name__)
app = Flask(__name__, template_folder='/app')

@app.route("/barcode", methods=['GET', 'POST'])
async def upload_file():
    if request.method == 'POST':
        if 'the_file' not in request.files:
            return "Файл не выбран."
        file = request.files['the_file']
        
        if file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            file_path = input_pdf_path + filename
            file.save(file_path)

            images = await asyncio.to_thread(convert_from_path, file_path)

            for i, image in enumerate(images):
                image_path = output_images_folder + f"{filename}_{i}.jpg"
                image.save(image_path)

            image_path = output_images_folder + f"{filename}.jpg"
            barcodes = await find_barcodes(image_path)

            if barcodes == []:
                await resize_image(image_path, image_path, 2.0)
                barcodes = await find_barcodes(image_path)

                if barcodes == []:
                    image.save(error_scan_images + f"{filename}.jpg")
                    return 'barcode not readible', 400

            code_barcode = barcodes[0].data.decode('utf-8').strip("'")

            if os.path.exists(image_path):
                os.remove(image_path)
            if os.path.exists(file_path):
                os.remove(file_path)
            return f"<p>{code_barcode}</p>"
    else:
        return render_template('upload.html')

if __name__ == '__main__':
    app.run(app.run(host='0.0.0.0', port=8000))
