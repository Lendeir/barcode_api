from flask import Flask, request, render_template
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

# +++++++++++++++++++++++++++++++++++++++++++++++
def create_folder(minio_client, bucket_name, folder_path):
    folder_name = f"{folder_path}/"
    result = minio_client.put_object(bucket_name, folder_name, io.BytesIO(b""), 0)
    print(f"created folder: {folder_name}")

def create_empty_object(minio_client, bucket_name, folder_path, object_name):
    object_path = f"{folder_path}/{object_name}"
    result = minio_client.put_object(bucket_name, object_path, io.BytesIO(b"hello"), 5)
    print(
        "created {0} object; etag: {1}, version-id: {2}".format(
            result.object_name, result.etag, result.version_id,
        )
    )


def upload_file(minio_client, bucket_name, folder_path, file_path, object_name):
    object_path = f"{folder_path}/{object_name}"
    
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return
    
    if not os.access(file_path, os.R_OK):
        print(f"Error: No read permission for file '{file_path}'.")
        return
    
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        print(f"Error: File '{file_path}' is empty.")
        return
    
    with open(file_path, 'rb') as file_data:
        result = minio_client.put_object(bucket_name, object_path, file_data, file_size)
        print(
            "uploaded {0} file to {1}; etag: {2}, version-id: {3}".format(
                file_path, result.object_name, result.etag, result.version_id,
            )
        )

def v(id, file_path, upload_name, name):
    minio_endpoint = 'minio:9000'
    minio_access_key = 'jJ729BHnnL9SOFukANhm'
    minio_secret_key = 'xVq3xfL0QIa1doYHxZhcdpbqoBZxmecKHH7dCcrK'
    minio_bucket_name = upload_name
    folder_path = str(id)

    try:
        minio_client = Minio(minio_endpoint, access_key=minio_access_key, secret_key=minio_secret_key, secure=False)
        
        if not minio_client.bucket_exists(minio_bucket_name):
            minio_client.make_bucket(minio_bucket_name)
            
        create_folder(minio_client, minio_bucket_name, folder_path)
        create_empty_object(minio_client, minio_bucket_name, folder_path, "empty-object")
        upload_file(minio_client, minio_bucket_name, folder_path, file_path, name)

    except Exception as e:
        print(f"Error: {str(e)}")
# +++++++++++++++++++++++++++++++++++++++++++++++





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
                image_path = output_images_folder + f"{filename}_{i}.jpg"
                image.save(image_path)
                barcodes = await find_barcodes(image_path)

                paths.append(image_path)
                file_names.append(f"{filename}_{i}.jpg")
                
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

            for i in range(len(barcodes_decoded)):
                path_list=f'/result/2.pdf_{i}.jpg'
                file_name=f'2.pdf_{i}.jpg'
                v(barcodes_decoded[i],path_list,upload_name,file_name)    
        return f"<p>{barcodes_decoded}</p><p>{paths}</p><p>{file_names}</p>"#</p><p>{stderr}</p>" 
    else:
        return render_template('upload.html')








if __name__ == '__main__':
    app.run(app.run(host='0.0.0.0', port=8000))

# def precombain(id,file_path,upload_name,name):
#     id = hex(int(id))[:-3]
#     # Запускаем асинхронный субпроцесс обработки
#     async def run_subprocess():
#         command = ['python', 'minio_upload.py', file_path, id, upload_name, name]
#         # Создаем субпроцесс
#         process = await asyncio.create_subprocess_exec(*command)
#         stdout, stderr = await process.communicate()
#         return 

#     # Запускаем субпроцесс в асинхронном цикле событий asyncio
#     output = asyncio.run(run_subprocess())
    
#     return output


# @app.route("/precombain/<data>", methods=['GET'])
# def precombain(data):
#     data=unquote(data)
#     split_data=data.split("^")
#     id = hex(int(split_data[0]))[:-3]
#     file_path = split_data[1].strip('"') 
#     upload_name= split_data[2] 
#     name = split_data[3]
#     # запускаем асинронный субпроцесс обработки
#     async def run_subprocess():
#         command = ['python', 'minio_upload.py', file_path, id, upload_name,name]
#         # Создаем субпроцесс
#         process = await asyncio.create_subprocess_exec(*command)
#         stdout, stderr = await process.communicate()
#         return f"{print(stdout)}"

#     # Запускаем субпроцесс в асинхронном цикле событий asyncio
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(run_subprocess())
