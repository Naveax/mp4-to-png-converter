# MP4 to PNG Converter

This application extracts all frames from an MP4 video file and saves them as individual PNG images.

## Features

- Select any MP4 video file
- Choose output directory for the PNG images
- Displays video information (FPS, frame count, duration)
- Shows real-time conversion progress
- Can cancel conversion process

## Requirements

- Python 3.6+
- OpenCV
- Tkinter (included with Python)

## Installation

1. Clone this repository
2. Install the required packages:

```
pip install -r requirements.txt
```

## Usage

1. Run the application:

```
python mp4_to_png_converter.py
```

2. Click "Browse" to select an MP4 file
3. Choose an output directory (default is './output')
4. Click "Start Conversion" to begin extracting frames
5. The progress bar will show conversion status
6. You can cancel the process at any time by clicking "Cancel"

## Output

The application will save all frames as PNG images in the format:
`frame_000000.png`, `frame_000001.png`, etc.

For a 10-minute video at 60 FPS, expect approximately 36,000 PNG files (10 min × 60 sec × 60 fps).
