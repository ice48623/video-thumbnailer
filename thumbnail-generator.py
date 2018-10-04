#!/usr/bin/env python3
from subprocess import call
import os
import subprocess
import shlex
import json
import requests
import pika
import time
import os
import hashlib

def get_video_info(pathToInputVideo):
    cmd = "ffprobe -v quiet -print_format json -show_streams"
    args = shlex.split(cmd)
    args.append(pathToInputVideo)
    # run the ffprobe process, decode stdout into utf-8 & convert to JSON
    ffprobeOutput = subprocess.check_output(args).decode('utf-8')
    ffprobeOutput = json.loads(ffprobeOutput)

    # import pprint
    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(ffprobeOutput)

    height = ffprobeOutput['streams'][0]['height']
    width = ffprobeOutput['streams'][0]['width']
    duration = ffprobeOutput['streams'][0]['duration']
    fps = ffprobeOutput['streams'][0]['avg_frame_rate'].split("/")[0]
    return height, width, duration, fps

def download_file(video_host, video_bucket_name, video_object_name, port = "8080"):
    print("downloading " + video_object_name)
    url = "http://" + video_host + ":" + port + '/' + video_bucket_name + '/' + video_object_name
    tmp_folder = "./tmp/"

    directory = tmp_folder + video_bucket_name
    save_location = directory + "/" + video_object_name
    if not os.path.exists(directory):
        os.makedirs(directory)

    r = requests.get(url, stream=True)
    with open(save_location, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian
    return save_location

def md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def create_bucket(target_host, target_bucket_name, target_object_name, port="8080"):
    try:
        url = "http://" + target_host + ":" + port + "/" + target_bucket_name + "?create"
        requests.post(url)
    except:
        print("may be bucket only exist")

def create_upload_ticket(target_host, target_bucket_name, target_object_name, port="8080"):
    url = "http://" + target_host + ":" + port + "/" + target_bucket_name + "/" + target_object_name + "?create"
    requests.post(url)

def complete_upload(target_host, target_bucket_name, target_object_name, port="8080"):
    url = "http://" + target_host + ":" + port + "/" + target_bucket_name + "/" + target_object_name + "?complete"
    requests.post(url)

def upload_file(file_path, target_host, target_bucket_name, target_object_name, part_number="1", port = "8080"):
    print("uploading")
    file_size = 0
    try:
        file_size = os.path.getsize(file_path)
    except:
        print("file not found")

    with open(file_path,'rb') as payload:
        headers = {'Content-Type': 'application/octet-stream', 'Content-Length': str(file_size), 'Content-MD5': str(md5(file_path))}
        url = "http://" + target_host + ":" + port + "/" + target_bucket_name + "/" + target_object_name + "?partNumber=" + part_number
        print(url)
        requests.put(url, data=payload, headers=headers)


def generateGIF(video_host, video_bucket_name, video_object_name, target_host, target_bucket_name, target_object_name):
    print("Generating GIF")
    file_format = "frame-%03d.png"
    desired_frame = 1.0
    output_duration = 10.0
    BASE_FOLDER = "./tmp/"
    # height, width, duration, fps = findVideoMetada(BASE_FOLDER + video_bucket_name + "/" + video_object_name)
    height, width, duration, fps = get_video_info(BASE_FOLDER + video_bucket_name + "/" + video_object_name)
    duration = float(duration)
    fps = float(fps)

    total_frame = duration * fps
    extracted_frame = duration * desired_frame
    output_fps = extracted_frame / output_duration
    interval = round(60 / output_fps, 1) * 10

    output_file_path = BASE_FOLDER + target_bucket_name + "/" + target_object_name

    call(["mkdir", BASE_FOLDER + video_bucket_name + "/frames"])
    call(["ffmpeg", "-i", BASE_FOLDER + video_bucket_name + "/" + video_object_name, "-r", str(desired_frame), "-vf", "scale=320:-1", BASE_FOLDER + video_bucket_name + "/frames/" + file_format])
    call(["convert", "-delay", str(interval), "-loop", "0", BASE_FOLDER + video_bucket_name + "/frames/*.png", BASE_FOLDER + target_bucket_name + "/" + target_object_name])
    call(["rm", "-rf", BASE_FOLDER + video_bucket_name + "/frames"])
    print("GIF generated!")
    return output_file_path

def parser(ch, method, properties, body):
    print(" [x] Received %r" % body)
    body = body.decode('utf8').replace("'", '"')
    parsed_body = json.loads(body)
    video_host = parsed_body.get('video_host')
    video_bucket_name = parsed_body.get('video_bucket_name')
    video_object_name = parsed_body.get('video_object_name')
    target_host = parsed_body.get('gif_host')
    target_bucket_name = parsed_body.get('gif_target_bucket_name')
    target_object_name = parsed_body.get('gif_target_object_name')

    logic(video_host,video_bucket_name,video_object_name,target_host,target_bucket_name,target_object_name)

def logic(video_host, video_bucket_name, video_object_name, target_host, target_bucket_name, target_object_name):
    download_file(video_host, video_bucket_name, video_object_name)
    output_file_path = generateGIF(video_host, video_bucket_name, video_object_name, target_host, target_bucket_name, target_object_name)
    create_bucket(target_host, target_bucket_name, target_object_name)
    create_upload_ticket(target_host, target_bucket_name, target_object_name)
    upload_file(output_file_path, target_host, target_bucket_name, target_object_name)
    complete_upload(target_host, target_bucket_name, target_object_name)
    
print("Start worker")
time.sleep(5)
RABBIT_HOST = os.getenv('RABBIT_HOST','localhost')
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
channel = connection.channel()

channel.queue_declare(queue='task_queue')
channel.basic_qos(prefetch_count=1)
channel.basic_consume(parser,
                      queue='task_queue')
print('Waiting for messages.')
channel.start_consuming()
