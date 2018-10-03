FROM python:3.7
ADD . ./docker
WORKDIR /docker
VOLUME /docker/tmp
RUN chmod +x *
RUN apt-get update && apt-get install -y \
  ffmpeg \
  imagemagick
RUN pip3 install -r requirements.txt

CMD ["python3", "./thumbnail-generator.py"]
