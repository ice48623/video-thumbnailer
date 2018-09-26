FROM python:3.7
ADD . ./docker
WORKDIR /docker
RUN chmod +x *
RUN apt-get update
RUN apt-get install ffmpeg imagemagick -y
CMD ["./thumbnail-generator.py"]
