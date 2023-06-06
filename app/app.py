import json
import subprocess
from flask import Flask, jsonify, request, render_template, send_file
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from flask import Flask, request
from pyzbar import pyzbar
import asyncio
from minio import Minio
import cv2
import io
import os
import sys
from PIL import Image

input_pdf_path = "/pdf/"
output_images_folder = '/result/'
error_scan_images = '/error_scan/'

async def resize_image(input_image_path, output_image_path, scale_factor):
    img = Image.open(input_image_path)
    width, height = img.size
    width = int(width * scale_factor)
    height = int(height * scale_factor)
    img = img.resize((width, height))
    width, height = img.size
    img = img.convert("RGB")
    img.save(output_image_path)

async def find_barcodes(image_path):
    image = cv2.imread(image_path)
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # barcodes = pyzbar.decode(gray)
    barcodes = pyzbar.decode(image)
    
    return barcodes

app = Flask(__name__)
app = Flask(__name__, template_folder='/app')


@app.route("/barcode/", methods=['GET', 'POST'])
async def upload_file():
    if request.method == 'POST':
        barcodes_decoded=[]
        paths=[]
        file_names=[]
        upload_name = request.form.get('name')
        if 'the_file' not in request.files:
          return "Файл не выбран."
        file = request.files['the_file']
        
        if file.filename.endswith('.pdf'):

            filename = secure_filename(file.filename)
            file_path = input_pdf_path + filename
            file.save(file_path)

            images = await asyncio.to_thread(convert_from_path, file_path)
            
            for i, image in enumerate(images):
                image_path = f"{i}.jpg"
                image.save(output_images_folder + image_path)
                barcodes = await find_barcodes(output_images_folder + image_path)

                paths.append(output_images_folder+image_path)
                file_names.append(f"{i}.jpg")
                
                if barcodes == []:
                    await resize_image(output_images_folder + image_path, output_images_folder + image_path, 2.0)
                    barcodes = await find_barcodes(output_images_folder + image_path)
                    if barcodes == []:
                        image.save(error_scan_images + f"{filename}.jpg")
                        barcodes_decoded.append("error")
                try:
                    code_barcode = barcodes[0].data.decode('utf-8').strip("'")
                    code_barcode=hex(int(code_barcode))#[:-3]
                    barcodes_decoded.append(code_barcode)
                except:
                    print()
        data = {'barcodes_decoded': barcodes_decoded, 'paths': paths, 'file_names': file_names,'upload_name': upload_name}
        data_for_back={'barcodes_decoded': barcodes_decoded}
        json_data = json.dumps(data)
        json_data_s = json.dumps(data_for_back)
        # Запуск внешнего скрипта с передачей данных через stdin
        cmd = ['python', '/app/minio_upload.py']
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        process.communicate(input=json_data.encode())

        # return 'External code executed.'

        # +++++++++++
        
        return f"<p>{barcodes_decoded}</p><p>{paths}</p><p>{file_names}</p>" 
    else:
        return render_template('upload.html')
    


@app.route("/data_upload/", methods=['GET', 'POST'])
async def upload_data():
    if request.method == 'POST':
        upload_name = request.form.get('name')
        try:
            data = request.get_json()  # Получение JSON-данных из запроса
            # Дальнейшая обработка полученных данных
            print(data)

            # Save JSON data to a file
            with open('data.json', 'w') as file:
                json.dump(data, file)

            return jsonify({'message': 'Data received and saved'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return render_template('upload-data.html')
    


@app.route("/download_file/", methods=['GET'])
def download_file():
    return send_file("/pdf/2_merged.pdf", as_attachment=True)

if __name__ == '__main__':
    app.run(app.run(host='0.0.0.0', port=8000))

