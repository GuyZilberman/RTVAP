# Real-Time Video Analysis Pipeline: Captain's Eye

This is an end-to-end pipeline that processes video from an RTSP source, applies a given PyTorch model for object detection (specifically detecting persons), and writes the results to a JSON file.

## Installation

Clone this repository:
   ```
   git clone https://github.com/GuyZilberman/RTVAP
   ```

Navigate to the project directory:
   ```
   cd RTVAP
   ```

(Optional) Create a Conda environment:
   ```
   conda create --name captain python=3.8
   conda activate captain
   ```

Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the pipeline using the following command:

```
python main.py <RTSP-ADDRESS>
```

Replace `<RTSP-ADDRESS>` with the desired RTSP video address.

Optional Flags:

-o or --output: Allows you to specify a custom path for the output.json file. If not specified, the output.json file will be created in the project directory.
Example:

To process a video from a specific RTSP address and save the output to a custom directory:

	python main.py rtsp://example.com/live.sdp -o /path_to_custom_directory/output.json
	
To process a video from a specific RTSP address and save the output to the default directory:

	python main.py rtsp://example.com/live.sdp

2. Stopping the Program:

To gracefully terminate the program while it's running, simply press Ctrl+C in the terminal or command prompt. The program will clean up any resources it's using and then exit.

## Implementation Details

- The pipeline streams video from the provided RTSP address.
- Each frame from the stream is passed through a YOLOv8-based object detection model.
- Detected objects of class "person" are processed and written to a JSON file in YOLO relative format.
- The pipeline auto-detects the availability of CUDA and leverages GPU acceleration if available.
- The writing of detection results to the JSON file is handled in a separate thread.

##Assumptions and Simplifications
- Single Stream Processing: The current pipeline has been designed to process one RTSP stream at a time. While multi-stream processing is feasible, it would require additional modifications to the current implementation.
- Detection of "Person" Class: While the YOLO model used can detect various classes, this pipeline specifically targets and processes objects of the "person" class, filtering out other classes' detections.
- Pre-trained YOLO Model: A pre-trained YOLOv8 model was employed due to its balance between detection speed and accuracy, suitable for real-time applications.
- CUDA Support: The pipeline is designed to auto-detect the availability of CUDA. It automatically toggles between GPU and CPU processing based on this.
- Continuous Frame-by-Frame Processing: The design focuses on processing video streams frame by frame, rather than in batches.
- JSON Output: The pipeline appends detection results to a JSON file. While each appended result is a valid JSON object, the entire file does not conform to the JSON format due to the append nature. This was a deliberate choice for ease of writing results on-the-go.

##Design Choices
- YOLO Model for Object Detection: YOLOv8 was chosen as it's known for its real-time processing capabilities. Given that the pipeline needs to process live RTSP streams, the YOLO model's efficiency and speed made it an apt choice.
- Threading for JSON Writing: To ensure the main video processing loop isn't slowed down by file I/O operations, a separate thread writes detection results to the JSON file. This ensures smoother and faster frame processing.
- CUDA Auto-Detection: To harness the acceleration capabilities of GPUs, the pipeline checks for CUDA availability. This allows for faster model inference when a compatible GPU is available.
- Error Handling and Camera Reconnection: Given the nature of live streams, disconnections can be common. A mechanism has been added to attempt reconnection to the RTSP source in case of disruptions, enhancing the robustness of the pipeline.
- Keyboard Interrupt for Graceful Termination: To provide a user-friendly way of terminating the program, a keyboard interrupt (Ctrl+C) is implemented. It ensures that all resources, like video streams and threads, are properly closed before exiting.
