# Sign Language Detector Python

Sign language detector with Python, OpenCV and Mediapipe !

[![Watch the video](https://img.youtube.com/vi/MJCSjXepaAM/0.jpg)](https://www.youtube.com/watch?v=MJCSjXepaAM)

## Introduction

This project is a sign language detection system that uses computer vision techniques to recognize hand gestures in real-time. It leverages Python, OpenCV for image processing, and MediaPipe for hand tracking.

## Requirements

- Python 3.7+
- OpenCV
- MediaPipe
- NumPy
- TensorFlow (for the machine learning model)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/sign-language-detector-python.git
   cd sign-language-detector-python-master
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the main detector script:
   ```
   python detect_signs.py
   ```

2. Position your hand in front of the camera and make sign language gestures.

3. The system will display the recognized sign in real-time.

## Features

- Real-time hand tracking using MediaPipe
- Sign language recognition for basic signs
- Visual feedback on detected signs
- User-friendly interface

## Project Structure

- `detect_signs.py`: Main script for sign detection
- `model/`: Contains the trained machine learning model
- `utils/`: Helper functions and utilities
- `data/`: Training and testing data

## Training Your Own Model

If you want to train the model on your own dataset:

1. Collect images of sign language gestures in the `data/raw` directory
2. Run the preprocessing script:
   ```
   python preprocess_data.py
   ```
3. Train the model:
   ```
   python train_model.py
   ```

## SmartIoTControl

This project can be integrated with SmartIoTControl systems to enable gesture-based control of IoT devices. See integration documentation for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
