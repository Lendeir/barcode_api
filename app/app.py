from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from pyzbar import pyzbar
import asyncio
import requests
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

@app.route("/barcode/", methods=['GET', 'POST'])
async def upload_file():
    if request.method == 'POST':

        upload_name = request.form.get('name')
        if 'the_file' not in request.files:
          return "Файл не выбран."
        file = request.files['the_file']
        
        if file.filename.endswith('.pdf'):

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
                        # url = 'http://localhost:8000/precombain_without_barcode/'
                        # response = requests.get(url)
                code_barcode = barcodes[0].data.decode('utf-8').strip("'")
                barcodes_decoded.append(code_barcode)

                url = f'http://localhost:8000/precombain/"{output_images_folder}"^{code_barcode}^{upload_name}^{filename}.jpg'
                requests.get(url)
            
            # if os.path.exists(image_path):
            #     os.remove(image_path)
            # if os.path.exists(file_path):
            #     os.remove(file_path)

            
            return f"<p>{barcodes_decoded}</p><p>{len(barcodes_decoded)}</p>"#</p><p>{stderr}</p>" 
    else:
        return render_template('upload.html')
@app.route("/precombain/<data>", methods=['GET'])
def precombain(data):
    split_data=data.split("^")
    file_path = split_data[0].strip('"') 
    id = hex(int(split_data[1]))[:-3]
    upload_name= split_data[2] 
    name = split_data[3]
    # запускаем асинронный субпроцесс обработки


    async def run_subprocess():
        command = ['python', 'minio_upload.py', file_path, id, upload_name,name]
        # Создаем субпроцесс
        process = await asyncio.create_subprocess_exec(*command)



        stdout, stderr = await process.communicate()
        # Обрабатываем вывод и ошибки при необходимости
        # ...
        # Возвращаем вывод
        return stdout

    # Запускаем субпроцесс в асинхронном цикле событий asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_subprocess())


#     def run_subprocess():
#         command = ['python', 'minio_upload.py', file_path, id, upload_name, name]
#         # Запуск субпроцесса
#         subprocess.run(command)

# # Вызов функции для запуска субпроцесса
#     run_subprocess()
#     return print("lol")

# @app.route("/precombain_without_barcode/<file_path>", methods=['GET'])
# def precombain_error():


if __name__ == '__main__':
    app.run(app.run(host='0.0.0.0', port=8000))
