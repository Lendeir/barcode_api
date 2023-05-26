from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from pyzbar import pyzbar
import asyncio
import subprocess
import cv2
import os
import time
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

        barcode_data = request.form.get('data')
        if 'the_file' not in request.files:
          return "Файл не выбран."
        file = request.files['the_file']
        
        if file.filename.endswith('.pdf'):

            start_time = time.time()

            filename = secure_filename(file.filename)
            file_path = input_pdf_path + filename
            file.save(file_path)

            images = await asyncio.to_thread(convert_from_path, file_path)
            barcodes_decoded=[]
            for i, image in enumerate(images):
                image_path = output_images_folder + f"{filename}_{i}.jpg"
                image.save(image_path)
                barcodes = await find_barcodes(image_path)
                if barcodes == []:
                    await resize_image(image_path, image_path, 2.0)
                    barcodes = await find_barcodes(image_path)
                    if barcodes == []:
                        image.save(error_scan_images + f"{filename}.jpg")
                        barcodes_decoded.append("error")
                code_barcode = barcodes[0].data.decode('utf-8').strip("'")
                barcodes_decoded.append(code_barcode)
            # if os.path.exists(image_path):
            #     os.remove(image_path)
            # if os.path.exists(file_path):
            #     os.remove(file_path)
            
            end_time = time.time()
    #         process = await asyncio.create_subprocess_exec(
    #             'python', 'minio_upload.py',
    #             '--param1', barcodes_decoded,
    #             '--param2', barcode_data,
    #             '--param3', image_path,         
    #             stdout=subprocess.PIPE,
    #             stderr=subprocess.PIPE
    # )
            # stdout, stderr = await process.communicate()
            execution_time = end_time - start_time
            print("Время выполнения функции:", execution_time, "секунд")
            
            return f"<p>{barcodes_decoded}</p><p>{len(barcodes_decoded)}</p><p>{execution_time} секунд"#</p><p>{stderr}</p>" 
    else:
        return render_template('upload.html')
@app.route("/precombain/<data>", methods=['GET'])
def precombain(data):
    split_data=data.split("^")
    id = hex(int(split_data[1]))[:-3]
    return f"{id}"


if __name__ == '__main__':
    app.run(app.run(host='0.0.0.0', port=8000))
