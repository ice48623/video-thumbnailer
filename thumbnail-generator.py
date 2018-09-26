#!/usr/bin/env python3
from subprocess import call
import os

def main():
    input_file = os.environ['input']
    output_file = os.environ['output']
    BASE_FOLDER = "./video/"
    folder_name = os.environ['input'] + "-frames"
    file_format = "frame-%03d.png"

    call(["mkdir", BASE_FOLDER + folder_name])
    call(["ffmpeg", "-i", BASE_FOLDER + input_file, "-r", "1", "-vf", "scale=320:-1", BASE_FOLDER + folder_name + "/" + file_format])
    call(["convert", "-delay", "15", "-loop", "0", BASE_FOLDER + folder_name + "/*.png", BASE_FOLDER + output_file])

if __name__ == '__main__':
    main()
