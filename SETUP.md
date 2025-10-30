# VisionAI Setup Guide

## First-Time Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download AI Models

The models will be automatically downloaded to `cache/models/` on first run. Alternatively, you can pre-download them:

```python
# Run this script to download all models
python download_models.py
```

**Models Downloaded:**
- BLIP Image Captioning (Salesforce)
- ViT Image Classification (Google)
- DETR Object Detection (Facebook)
- CLIP Scene Understanding (OpenAI)

**Total Size:** ~5-7 GB

### 3. Run the Application

```bash
cd backend
python app.py
```

The browser will open automatically at `http://127.0.0.1:5000`

## Project Structure

```
visionai/
├── backend/           # Python Flask backend
├── frontend/          # HTML/JS frontend
├── cache/
│   └── models/       # Local AI models (NOT in git)
├── uploads/          # Temporary image uploads
└── exports/          # Exported analysis results
```

## Notes

- Models are stored locally in `cache/models/` (excluded from git)
- First run may take 5-10 minutes to download models
- Requires ~8 GB disk space for models
- GPU support automatic if CUDA available