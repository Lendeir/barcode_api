import sys
import io
import requests
import os
from minio import Minio

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
    minio_endpoint = 'localhost:9000'
    minio_access_key = 'Ymn9qL26cMJ9eiJG9QAr'
    minio_secret_key = 'LlMiKXlK0IlLPoaQSVziEs1iBNmE6jV8nJIb33aQ'
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
    return f"Error: {str(e)}"

requests.get("http://localhost:8000")

id = int(sys.argv[1])
file_path = sys.argv[2]
upload_name = sys.argv[3]
name = sys.argv[4]
v(id,file_path,upload_name,name)


# v(879589840433799967438659843263883536039940, "C:/Users/i.miniakhmetov/Desktop/app/app/1.jpg", "test2.3", "1.jpg")