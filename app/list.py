from minio import Minio

def v():
    minio_endpoint = 'minio:9000'
    minio_access_key = 'jJ729BHnnL9SOFukANhm'
    minio_secret_key = 'xVq3xfL0QIa1doYHxZhcdpbqoBZxmecKHH7dCcrK'


    try:
        minio_client = Minio(minio_endpoint, access_key=minio_access_key, secret_key=minio_secret_key, secure=False)
    except:
        return "error connection"
    try:
        # Получение списка объектов в корзине
        objects = minio_client.list_objects("listtest")
    except: return"error list"
    # Фильтрация объектов, чтобы получить только папки
    folders = []
    for item in minio_client.list_objects("listtest"):
        folders.append(item.object_name)
    for i in range(len(folders)):
        objects = minio_client.list_objects("listtest", prefix=folders[i], recursive=True)
        for obj in objects:
            print(obj.object_name)
        
    
print(v())