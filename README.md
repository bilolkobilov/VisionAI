# VisionAI

Advanced image analysis powered by AI models running locally on your machine.

## Features

- Image Captioning (BLIP)
- Classification (ViT)
- Object Detection (DETR)
- Scene Understanding (CLIP)
- Export to JSON/PDF
- Local processing, no API calls

## Requirements

- Python 3.8+
- 4GB+ RAM (8GB recommended)
- CUDA GPU (optional)

## Installation
```bash
git clone https://github.com/bilolkobilov/visionai.git
cd visionai
pip install -r requirements.txt
python backend/app.py
```

First Run
⚠️ Important: First run downloads ~2.2GB of models (10-30 minutes)
Models downloaded:

BLIP: 990MB
ViT: 330MB
DETR: 160MB
CLIP: 600MB

After download, subsequent runs are instant!

Application runs at `http://127.0.0.1:5000`

## Models

- BLIP (990MB) - Image Captioning
- ViT (330MB) - Classification
- DETR (160MB) - Object Detection
- CLIP (600MB) - Scene Analysis

Models download automatically on first run (~2GB total).

## Usage

1. Upload image (file/URL/camera)
2. Analyze
3. Review results
4. Export (JSON/PDF)

## Configuration

Edit `backend/config.py` to customize model settings, thresholds, and limits.

## License

MIT License