import cv2
import threading
import time
from ultralytics import YOLO
import queue
import sys
from config import *
from writer import *


def handle_camera_disconnection(cap, video_source):
    consecutive_failures = 0
    while True:
        print("Camera connection lost. Attempting to reconnect...")
        cap.release()
        time.sleep(FAILURE_TIMEOUT)
        cap = cv2.VideoCapture(video_source)
        ret, frame = cap.read()
        if ret and frame is not None:
            print("Reconnected successfully!")
            return cap, True, frame
        consecutive_failures += 1
        if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
            print("Failed to reconnect. Exiting...")
            return cap, False, None


def process_video_feed(video_source, output_json_path):
    if USE_CUDA:
        print("CUDA is available. Running on GPU.")
    else:
        print("CUDA is not available. Running on CPU.")

    # Initialize YOLO model
    try:
        model = YOLO(MODEL_NAME)
        if USE_CUDA:
            model.cuda()
    except Exception as e:
        print(f"Failed to load model: {e}")
        sys.exit(1)

    # Open webcam
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        print(f"Error: Unable to open video source {video_source}")
        sys.exit(1)

    # Create data queue to hold data to be written to the JSON file by a separate thread
    data_queue = queue.Queue()

    # Clear the JSON file
    initialize_output_file(output_json_path)

    # Create and start a writer thread
    writer_thread = threading.Thread(target=write_to_json, args=(data_queue, output_json_path))
    writer_thread.start()

    try:
        while True:
            # Read a frame
            ret, frame = cap.read()

            if not ret:
                cap, reconnected, frame = handle_camera_disconnection(cap, video_source)
                if not reconnected:
                    break

            # If available, move the frame to the GPU for inference
            if USE_CUDA:
                frame = torch.from_numpy(frame).float().cuda()

            # Predict using YOLO
            try:
                results = model.predict(source=frame)
            except Exception as e:
                print(f"Error during YOLO prediction: {e}")
                continue

            timestamp = time.time()  # Get the current timestamp

            output_data = {
                "timestamp": timestamp,
                "detections": []
            }

            # Loop over each result object in the list
            for res in results:
                # Get bounding boxes, labels, and confidence scores
                bounding_boxes = res.boxes.data
                labels = res.boxes.cls
                confidences = res.boxes.conf

                for box, label, conf in zip(bounding_boxes, labels, confidences):
                    # Only consider detections of 'person' class, which has label 0
                    if label == 0 and conf > CONFIDENCE_THRESHOLD:
                        # Convert tensor data to numpy for OpenCV compatibility
                        box = box[:4].cpu().numpy().astype(int)
                        conf = conf.cpu().item()

                        # Convert the dimensions to yolo format
                        frame_height, frame_width = frame.shape[:2]  # Get image dimensions
                        center_x, center_y, width, height = convert_to_yolo_format(box[0], box[1], box[2], box[3],
                                                                                   frame_width, frame_height)

                        # Append detection data to output
                        detection = {
                            "relative_bbox": [center_x, center_y, width, height],
                            "confidence": conf
                        }
                        output_data["detections"].append(detection)

            # Only write to the JSON output file if a person was detected in the frame
            if output_data["detections"]:
                data_queue.put(output_data)

    except KeyboardInterrupt:
        print("Program terminated by user.")

    # Tell writer thread to finish up, and wait for it to finish
    data_queue.put(STOP_SIGNAL)
    writer_thread.join()

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
