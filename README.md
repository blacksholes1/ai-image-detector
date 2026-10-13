# AI Image Detector

This project helps you determine whether an image or video looks real or AI-generated.

## Features

- Checks a local image or video file
- Identifies whether it appears to be real or AI-generated
- Runs from the command line

## Setup

### 1) Install Python

If Python is not already installed, install it first.

#### Windows

```bash
winget install Python.Python.3.14
```

#### macOS

```bash
brew install python3
```

Then run the setup steps again.

### 2) Download the repository

Clone or download the repository to your computer.

```bash
git clone https://github.com/blacksholes1/ai-image-detector.git
cd ai-image-detector
```

### 3) Install dependencies

Install the required Python packages:

```bash
pip install pillow opencv-python numpy
```

### 4) Run the detector

In your terminal, run:

```bash
python ai_detector.py
```

### 5) Test an image or video

Drag and drop your image or video file from your file manager or Finder into the terminal and press Enter.

The program will then tell you whether the file appears to be real or AI-generated.
