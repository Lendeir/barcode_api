from minio import Minio
import argparse
import os
import psutil
pid=os.getpid()
parser = argparse.ArgumentParser()
parser.add_argument('--param1')
# parser.add_argument('--param2')
# parser.add_argument('--param3')
args = parser.parse_args()

barcodes_decoded = args.param1

def get_python_processes():
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
            python_processes.append(proc)
    return python_processes

# Получаем список процессов Python
python_processes = get_python_processes()

# Выводим информацию о каждом процессе
# for proc in python_processes:
#     print("ID процесса:", proc.info['pid'])
#     print("Имя процесса:", proc.info['name'])
#     print("")

# Или просто выводим список ID процессов Python

# python_pids = [proc.info['pid'] for proc in python_processes]
# print("Список ID процессов Python:\n", python_pids)

python_pids = [proc.info['pid'] for proc in python_processes]
pids_text = ', '.join(str(pid) for pid in python_pids)

print("Список ID процессов Python:")
print(pids_text)


# barcode_data = args.param2
# file_path = args.param3

# print(pid)
# print(barcode_data)
# print(file_path)

# data=[]
# minio_endpoint = 'localhost:9000'
# minio_access_key = 'Ymn9qL26cMJ9eiJG9QAr'
# minio_secret_key = 'LlMiKXlK0IlLPoaQSVziEs1iBNmE6jV8nJIb33aQ'
# minio_bucket_name = 'test'
# # file_path = 'C:/Users/i.miniakhmetov/Desktop/mimio upload/2.pdf' 
# object_name = '2.pdf'  # Имя объекта, под которым он будет сохранен в ведре

# # Инициализация клиента MinIO
# minio_client = Minio(minio_endpoint, access_key=minio_access_key, secret_key=minio_secret_key, secure=False)

# try:
#     # Проверяем существование ведра, и, если оно не существует, создаем его
#     if not minio_client.bucket_exists(minio_bucket_name):
#         minio_client.make_bucket(minio_bucket_name)

#     # Загружаем файл в ведро
#     minio_client.fput_object(minio_bucket_name, object_name, file_path)

#     print(f"Файл {file_path} успешно добавлен в ведро {minio_bucket_name} с именем {object_name}")
# except:
#     print("error")






