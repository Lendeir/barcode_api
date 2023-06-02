from minio import Minio
import os
import shutil

def v():
    minio_endpoint = 'minio:9000'
    minio_access_key = 'jJ729BHnnL9SOFukANhm'
    minio_secret_key = 'xVq3xfL0QIa1doYHxZhcdpbqoBZxmecKHH7dCcrK'
    download_folder = '/making/'
    minio_bucket_name = 'listtest'

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
                print(name)
                file_path = download_folder + name[0]
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                minio_client.fget_object(minio_bucket_name,obj.object_name, download_folder + name[0]+"/"+name[1])
                print(f"Файл {obj.object_name} успешно скачан в {file_path}")

# print(v())

from fpdf import FPDF
import os

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
    print("PDF файл успешно создан!")



# Вызываем функцию для преобразования изображений в PDF
convert_images_to_pdf("/making/629695406412629666858686271928847057354753", "/app/result.pdf")