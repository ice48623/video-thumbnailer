FROM python:3.7
ADD . ./docker
WORKDIR /docker
RUN chmod +x *
RUN apt-get update
RUN apt-get install ffmpeg imagemagick -y
# RUN pip install ffmpeg-python
# ENTRYPOINT ["python3", "thumbnail-generator.py", "./asdf"]
CMD ["./thumbnail-generator.py"]

# RUN apt-get -y install software-properties-common
# RUN add-apt-repository ppa:jon-severinsson/ffmpeg
# RUN apt-get update
# RUN apt-get -y install ffmpeg unzip imagemagick curl
