#!/usr/bin/env python3
from subprocess import call
import os
import subprocess
import shlex
import json

def findVideoMetada(pathToInputVideo):
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
    print(height, width, duration, fps)
    return height, width, duration, fps

def main():
    input_file = os.environ['input']
    output_file = os.environ['output']
    BASE_FOLDER = "./video/"
    folder_name = os.environ['input'] + "-frames"
    file_format = "frame-%03d.png"
    desired_frame = 1.0
    output_duration = 10.0

    height, width, duration, fps = findVideoMetada(BASE_FOLDER + input_file)
    duration = float(duration)
    fps = float(fps)

    total_frame = duration * fps
    extracted_frame = duration * desired_frame
    output_fps = extracted_frame / output_duration
    interval = round(60 / output_fps, 1) * 10

    call(["mkdir", BASE_FOLDER + folder_name])
    call(["ffmpeg", "-i", BASE_FOLDER + input_file, "-r", str(desired_frame), "-vf", "scale=320:-1", BASE_FOLDER + folder_name + "/" + file_format])
    call(["convert", "-delay", str(interval), "-loop", "0", BASE_FOLDER + folder_name + "/*.png", BASE_FOLDER + output_file])

if __name__ == '__main__':
    main()
