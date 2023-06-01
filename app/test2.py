import os
from minio import Minio
from fpdf import FPDF

minio_endpoint = 'minio:9000'
minio_access_key = 'jJ729BHnnL9SOFukANhm'
minio_secret_key = 'xVq3xfL0QIa1doYHxZhcdpbqoBZxmecKHH7dCcrK'
# Параметры подключения к серверу MinIO
minio_url =  minio_endpoint
access_key = minio_access_key
secret_key = minio_secret_key

# Параметры корзины и базовой папки, в которой находятся папки с изображениями
bucket_name = "listtest"
base_folder = "/result"

# Создание экземпляра клиента MinIO
client =  Minio(minio_endpoint, access_key=minio_access_key, secret_key=minio_secret_key, secure=False)

# Создание класса PDF-документа
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Images to PDF", ln=True, align="C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, "Page %s" % self.page_no(), 0, 0, "C")

# Функция для получения списка изображений в папке
def get_images_in_folder(folder_path):
    images = []
    for item in client.list_objects(bucket_name, prefix=folder_path, recursive=True):
        if item.object_name.endswith((".jpg", ".jpeg", ".png")):
            images.append(item.object_name)
    return images

# Функция для создания PDF-файла из списка изображений
def create_pdf(folder_name, images):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Folder: {folder_name}", ln=True, align="L")

    for image in images:
        file_data = client.get_object(bucket_name, image)
        image_data = file_data.data
        image_path = image.split("/")[-1]  # Получаем имя файла из пути
        with open(image_path, "wb") as file:
            file.write(image_data)
        pdf.image(image_path, x=10, y=pdf.get_y() + 10, w=190)

    output_path =  "/result/"+f"{folder_name}.pdf"
    print(output_path)
    pdf.output(output_path, "F")
    os.remove(image_path)  # Удаление временного файла изображения

# Получение списка папок в корзине
folders = []
for item in client.list_objects(bucket_name, prefix=base_folder, recursive=True):
    if item.is_dir and item.object_name != base_folder:
        folders.append(item.object_name)

# Обход папок и создание PDF-файлов
for folder in folders:
    folder_name = os.path.basename(folder.rstrip("/"))
    folder_images = get_images_in_folder(folder)
    try:
        create_pdf(folder_name, folder_images)
        print("PDF-файлы успешно созданы и сохранены в текущей директории.")
    except:print("error")