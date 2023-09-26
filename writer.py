import json
from config import STOP_SIGNAL


def write_to_json(data_queue, output_json_path):
    while True:
        data = data_queue.get()
        if data == STOP_SIGNAL:
            break
        with open(output_json_path, "a") as f:
            json.dump(data, f)
            f.write("\n")


def initialize_output_file(output_json_path):
    with open(output_json_path, "w") as _:
        pass


def convert_to_yolo_format(x1, y1, x2, y2, img_width, img_height):
    center_x = (x1 + x2) / 2.0
    center_y = (y1 + y2) / 2.0
    width = x2 - x1
    height = y2 - y1

    # Normalize the values
    center_x /= img_width
    center_y /= img_height
    width /= img_width
    height /= img_height

    return center_x, center_y, width, height
