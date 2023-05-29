import io
import sys
from minio import Minio
# Получаем аргументы командной строки
def v(id,file_path,upload_name,name):
    # id = int(sys.argv[1])
    # file_path = sys.argv[2]
    # upload_name = sys.argv[3]
    # name = sys.argv[4]
    minio_endpoint = 'localhost:9000'
    minio_access_key = 'Ymn9qL26cMJ9eiJG9QAr'
    minio_secret_key = 'LlMiKXlK0IlLPoaQSVziEs1iBNmE6jV8nJIb33aQ'

    minio_bucket_name = upload_name
    path = f'{id}'
    object_name = name  # Имя объекта, под которым он будет сохранен в ведре
    # Инициализация клиента MinIO
    minio_client = Minio(minio_endpoint, access_key=minio_access_key, secret_key=minio_secret_key, secure=False)
    try:
        # Проверяем существование ведра, и, если оно не существует, создаем его
        if not minio_client.bucket_exists(minio_bucket_name):
            minio_client.make_bucket(minio_bucket_name)
    except:
        print("error create bucket")
    try:
        # Create the folder by uploading an empty object with a trailing slash
        minio_client.put_object(minio_bucket_name, path, io.BytesIO(b''))
        print(f"Folder '{path}' created successfully in bucket '{minio_bucket_name}'!")
    except:
        print("error create folder")
    try:
        # Загружаем файл в ведро
        minio_client.fput_object(minio_bucket_name, object_name, file_path)
        print(f"Файл {file_path} успешно добавлен в ведро {minio_bucket_name} с именем {object_name}")
    except:
        print("error upload file")
v("/result/",879589840433799967438659843263883536039940,"test1323","1.pdf.jpg")
