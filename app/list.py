# нужно запускать с передачей upload name
import sys
from fpdf import FPDF
import os
from minio import Minio
import json


def v():
    try:
        minio_client = Minio(minio_endpoint, access_key=minio_access_key, secret_key=minio_secret_key, secure=False)
    except:
        return "error connection"
    try:
        # Получение списка объектов в корзине
        objects = minio_client.list_objects(minio_bucket_name)
    except: return"error list"
    # Фильтрация объектов, чтобы получить только папки
    folders = []
    for item in minio_client.list_objects(minio_bucket_name):
        folders.append(item.object_name)
    for i in range(len(folders)):
        objects = minio_client.list_objects(minio_bucket_name, prefix=folders[i], recursive=True)
        for obj in objects:
            name=str(obj.object_name).split("/")
            if name[1] != '' and name[1] != 'empty-object':
                file_path = download_folder + name[0]
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                minio_client.fget_object(minio_bucket_name,obj.object_name, download_folder + name[0]+"/"+name[1])
                # print(f"Файл {obj.object_name} успешно скачан в {file_path}")
    return folders



def convert_images_to_pdf(folder_path, output_path):
    pdf = FPDF()
    files=[]
    files = os.listdir(folder_path) 
    image_files = [file for file in files if file.endswith(('.jpg', '.jpeg', '.png'))]

    image_files.sort()

    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        pdf.add_page()
        pdf.image(image_path, x=10, y=10, w=190)

    pdf.output(output_path, "F")

data = sys.stdin.read()
input_data = json.loads(data)
upload_name = input_data['upload_name']
# barcode = input_data['barcode']



minio_endpoint = 'minio:9000'
minio_access_key = 'cKrvC8E4mbUhH6vuC2dx'
minio_bucket_name = upload_name
minio_secret_key = 'J7UvQS0DzFeGEYzEDA7pflEryoIyGsiHzr8VVU6G'
download_folder = f'/making/{minio_bucket_name}/'

if not os.path.exists(download_folder):
        os.makedirs(download_folder)
if not os.path.exists(f'/spdf'):
        os.makedirs(f'/spdf')
if not os.path.exists(f'/spdf/{upload_name}'):
        os.makedirs(f'/spdf/{upload_name}')

folders=v()
for i in range(len(folders)):
    convert_images_to_pdf(f'{download_folder}/{folders[i]}', f'/spdf/{upload_name}/{folders[i].strip("/")}.pdf')
# create_zip_archive(f'{download_folder}/pdf', f'{download_folder}/pdf/{minio_bucket_name}.zip')
    

