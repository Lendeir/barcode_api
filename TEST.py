from minio import Minio


# Initialize MinIO client
minio_client = Minio(
    endpoint='localhost:9000',
    access_key='Ymn9qL26cMJ9eiJG9QAr',
    secret_key='LlMiKXlK0IlLPoaQSVziEs1iBNmE6jV8nJIb33aQ',
    secure=False  # Set to False if you're using an insecure connection (HTTP instead of HTTPS)
)

# Define the name of the bucket you want to create
bucket_name = 'test23'
# Create the bucket
minio_client.make_bucket(bucket_name)

print(f"Bucket '{bucket_name}' created successfully!")

