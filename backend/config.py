"""
Configuration Module
Central configuration for VisionAI application
"""

import os
from pathlib import Path

# Application Settings
APP_NAME = "VisionAI"
VERSION = "2.0.0"
HOST = "127.0.0.1"
PORT = 5000
DEBUG = False

# Directories
BASE_DIR = Path(__file__).parent.parent

# Cache directory for AI models (CONFIGURABLE)
# Change this path to your preferred location for model storage
# Default: ./cache/models (relative to project root)
# Example: Path("D:/AI_Models/VisionAI") for custom location
CACHE_FOLDER = BASE_DIR / "cache"
MODELS_CACHE = CACHE_FOLDER / "models"

# Create cache directory if it doesn't exist
MODELS_CACHE.mkdir(parents=True, exist_ok=True)

# Set HuggingFace cache to use local directory
os.environ['TRANSFORMERS_CACHE'] = str(MODELS_CACHE)
os.environ['HF_HOME'] = str(MODELS_CACHE)
os.environ['HF_DATASETS_CACHE'] = str(MODELS_CACHE)

print(f"📦 Models will be stored in: {MODELS_CACHE}")
print(f"💾 Required disk space: ~5-7 GB")

# File Upload Settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Local AI Models Configuration
MODELS = {
    'CAPTIONING': 'Salesforce/blip-image-captioning-base',
    'CLASSIFICATION': 'google/vit-base-patch16-224',
    'OBJECT_DETECTION': 'facebook/detr-resnet-50',
    'CLIP': 'openai/clip-vit-base-patch32'
}

# Analysis Settings
CONFIDENCE_THRESHOLD = 0.05  # Minimum confidence for results
MAX_CAPTIONS = 3  # Number of caption variations
MAX_LABELS = 20  # Maximum classification labels
MAX_OBJECTS = 15  # Maximum detected objects

# Device Configuration (automatically detect CUDA)
DEVICE = "cuda"  # Will be set to "cpu" if CUDA unavailable

# Image Processing
MAX_IMAGE_DIMENSION = 1024  # Resize large images
IMAGE_QUALITY = 90  # JPEG quality for optimization