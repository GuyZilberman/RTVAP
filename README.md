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

## Assumptions and Simplifications
- Single Stream Processing: The current pipeline has been designed to process one RTSP stream at a time. While multi-stream processing is feasible, it would require additional modifications to the current implementation.
- Detection of "Person" Class: While the YOLO model used can detect various classes, this pipeline specifically targets and processes objects of the "person" class, filtering out other classes' detections.
- Pre-trained YOLO Model: A pre-trained YOLOv8 model was employed due to its balance between detection speed and accuracy, suitable for real-time applications.
- CUDA Support: The pipeline is designed to auto-detect the availability of CUDA. It automatically toggles between GPU and CPU processing based on this.
- Continuous Frame-by-Frame Processing: The design focuses on processing video streams frame by frame, rather than in batches.
- JSON Output: The pipeline appends detection results to a JSON file. While each appended result is a valid JSON object, the entire file does not conform to the JSON format due to the append nature. This was a deliberate choice for ease of writing results on-the-go.

## Design Choices
- YOLO Model for Object Detection: YOLOv8 was chosen as it's known for its real-time processing capabilities. Given that the pipeline needs to process live RTSP streams, the YOLO model's efficiency and speed made it an apt choice.
- Threading for JSON Writing: To ensure the main video processing loop isn't slowed down by file I/O operations, a separate thread writes detection results to the JSON file. This ensures smoother and faster frame processing.
- CUDA Auto-Detection: To harness the acceleration capabilities of GPUs, the pipeline checks for CUDA availability. This allows for faster model inference when a compatible GPU is available.
- Error Handling and Camera Reconnection: Given the nature of live streams, disconnections can be common. A mechanism has been added to attempt reconnection to the RTSP source in case of disruptions, enhancing the robustness of the pipeline.
- Keyboard Interrupt for Graceful Termination: To provide a user-friendly way of terminating the program, a keyboard interrupt (Ctrl+C) is implemented. It ensures that all resources, like video streams and threads, are properly closed before exiting.

## Questions & Answers
1. How would you improve your code to handle multiple stream sources?
- Multithreading/Multiprocessing: Each stream source can be processed in a separate thread or process. 
Choosing Between Multithreading and Multiprocessing for Model Inference:
**Multithreading**: If you have a powerful GPU that can handle multiple inferences simultaneously, and the model framework is thread-safe (like PyTorch with CUDA), multithreading can be beneficial. Threads are lightweight, allowing for easier management of video streams. However, if the model and CPU computations become a bottleneck due to Python's Global Interpreter Lock (GIL), this approach might not scale well.
**Multiprocessing**: Each video stream is processed in a separate process, each having its own model instance and memory space. This approach is more robust against CPU-level bottlenecks and can take full advantage of multi-core CPUs. However, if using the GPU, ensure each process can access the GPU without causing memory contention or other access-related issues. Also, consider the memory overhead, as each process will have its own instance of the model.

- Use a List of RTSP Addresses:
Instead of a single RTSP address, you can accept a list of RTSP addresses as input.

- Manage Outputs:
When handling multiple streams, it's important to manage where the outputs (e.g., the JSON results) are saved. Consider using separate files or sections within a file for each stream.

- Error Handling:
Concurrently processing multiple streams increases the likelihood of errors. Enhance your error handling to account for stream-specific issues. You might also want to introduce a logging system to log issues specific to each stream.

- Rate Limiting:
Depending on the number of streams and the processing power of the system, you might want to introduce rate limiting or prioritization to prevent overloading the system.

- Concurrent Queue for Writing Outputs:
If multiple threads/processes are writing to the same output, ensure that this operation is thread-safe. Using a concurrent queue can be a good strategy.

- Dynamic Stream Addition/Removal:
Consider implementing functionality to dynamically add or remove streams without stopping the entire pipeline.

2. Advantage of GPU for inference:
Using a GPU for inference offers several advantages, especially when dealing with tasks that require substantial computational power. Here are 2-3 strong points:

1. **Parallelism**: One of the most significant advantages of GPUs is their inherent ability to handle massive parallelism. A typical GPU consists of thousands of small cores designed for parallel processing, whereas a CPU might only have a few cores optimized for sequential tasks. In the context of inference, especially for deep learning models, this means that the many operations required for each layer of a neural network can be processed concurrently on a GPU, resulting in much faster computations.

2. **Throughput**: Given the parallel nature of GPUs, they can achieve higher throughput for matrix operations and computations typical in deep learning inference. When predicting on a batch of inputs, the GPU can process many inputs simultaneously, making it especially efficient for large-scale tasks or real-time applications that need quick responses.

3. **Specialized Libraries and Frameworks**: Over the years, there has been a proliferation of software libraries and frameworks optimized for GPU-based inference. Libraries such as CUDA, cuDNN, and TensorRT by NVIDIA, as well as various deep learning frameworks, have specific optimizations when running on GPUs. This ecosystem ensures that models can be efficiently loaded, optimized, and executed on GPUs without requiring significant manual intervention.

GPUs can offer significant performance benefits where it comes to video decoding:

1. **Dedicated Hardware Decoders**: Many modern GPUs come with built-in hardware units specifically designed to decode popular video codecs, enabling efficient video playback without straining the main GPU cores or the CPU.

2. **Parallel Processing**: GPUs have multiple cores that can process parts of a video frame concurrently, speeding up the decoding process for codecs without dedicated hardware support.

3. **GPU-Accelerated Libraries**: There are specific tools and SDKs, like NVIDIA's Video Codec SDK, that facilitate GPU-accelerated video decoding, streamlining the integration for developers.

3. SDK/Python Package Descriptions:
    - **asyncio**: Used for asynchronous I/O operations, improving performance in I/O-bound tasks.
    - **GStreamer**: Can handle video decoding and streaming efficiently.
    - **Nvidia DeepStream SDK**: Offers GPU-accelerated video analysis.
    - **Docker**: Provides containerized environments, ensuring compatibility across different systems.
				  Relevance to my Implementation:
					Reproducibility: By using Docker, I can ensure that the video analysis pipeline runs consistently across different environments. This is especially relevant if there are specific library dependencies or configurations required.
					Distribution: A Docker image can encapsulate the entire project, making it easier for users to run without dealing with dependency issues.
					Isolation: If the video analysis pipeline might interfere with other applications or if there are concerns about library version conflicts, Docker can provide the necessary isolation.
					