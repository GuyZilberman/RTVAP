from argparse import ArgumentParser
import os
import cv2
import sys
import json
from config import OUTPUT_JSON_PATH


def parse_arguments():
    parser = ArgumentParser(description='Process video feed from a given RTSP address')
    # parser.add_argument('rtsp', type=str, help='RTSP address to process video from') #TODO guy BRING BACK
    parser.add_argument('-o', '--output', metavar='', type=str, help='output json path', default=OUTPUT_JSON_PATH)

    args = parser.parse_args()

    if args.output and args.output != OUTPUT_JSON_PATH:
        try:
            is_valid_json_path(args.output)
        except ValueError as e:
            print(e)
            sys.exit(1)

    # TODO guy bring back
    # try:
    #     is_valid_rtsp_address(args.rtsp)
    # except ValueError as e:
    #     print(e)
    #     sys.exit(1)

    return args


def is_valid_rtsp_address(url):
    if not url.startswith("rtsp://"):
        raise ValueError("URL does not start with 'rtsp://'")

    # Attempt to connect
    cap = cv2.VideoCapture(url)
    ret, _ = cap.read()
    cap.release()

    if not ret:
        raise ValueError("Failed to connect to the provided RTSP address")


def is_valid_json_path(path):
    dir_name = os.path.dirname(path)

    # Check if the directory exists
    if not os.path.exists(dir_name):
        raise ValueError(f"The directory '{dir_name}' does not exist.")

    # Check if the file exists
    if not os.path.exists(path):
        with open(path, 'w') as f:
            json.dump({}, f)  # Create an empty JSON file
        return True

    return True
