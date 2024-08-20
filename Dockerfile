from python:3.10

WORKDIR /app

copy requirements.txt /app
run pip3 install -r requirements.txt
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

copy . /app
cmd ["python", "SussyServer.py"]
expose 5000