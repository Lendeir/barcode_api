import sys
from minio import Minio

if __name__ == '__main__':
    # Получаем аргументы командной строки
    id = int(sys.argv[1])
    file_path = int(sys.argv[2])
    upload_name = int(sys.argv[3])
    name = int(sys.argv[4])

    minio_endpoint = 'localhost:9000'
    minio_access_key = 'Ymn9qL26cMJ9eiJG9QAr'
    minio_secret_key = 'LlMiKXlK0IlLPoaQSVziEs1iBNmE6jV8nJIb33aQ'
    
    minio_bucket_name = upload_name
    path = f'{upload_name}/{id}'

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
        # Создание фиктивного объекта, представляющего новый путь (папку)
        data = b''  # Пустые данные для папки
        content_type = 'application/octet-stream'

        # Сохранение объекта в ведре с новым путем
        minio_client.put_object(
            bucket_name=minio_bucket_name,
            object_name=path,
            data=data,
            length=0,
            content_type=content_type
        )

        print(f"Путь '{path}' успешно создан в ведре '{minio_bucket_name}'!")
    except:
        print("error create folder")

    try:
        # Загружаем файл в ведро
        minio_client.fput_object(minio_bucket_name, object_name, file_path)

        print(f"Файл {file_path} успешно добавлен в ведро {minio_bucket_name} с именем {object_name}")
    except:
        print("error upload file")