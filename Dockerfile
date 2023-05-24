FROM python:3.10

RUN mkdir pdf result error_scan 
WORKDIR /app

# Установка необходимых пакетов
RUN apt-get update && \
    apt-get install -y libzbar0 libzbar-dev poppler-utils libgl1-mesa-glx

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app
CMD ["python3", "app.py"]
