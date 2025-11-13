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

### 🖼️ **BLIP — Bootstrapped Language-Image Pre-training**

* **Full name:** *Bootstrapped Language-Image Pre-training*
* **Developed by:** Salesforce Research
* **Purpose:** Image captioning and vision-language understanding (can both generate captions and answer questions about images).
* **Paper:** *“BLIP: Bootstrapped Language-Image Pre-training for Unified Vision-Language Understanding and Generation”* (2022).

---

### 🔍 **ViT — Vision Transformer**

* **Full name:** *Vision Transformer*
* **Developed by:** Google Research
* **Purpose:** Image classification (treats image patches as tokens, like words in NLP).
* **Paper:** *“An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale”* (2020).

---

### 🎯 **DETR — DEtection TRansformer**

* **Full name:** *End-to-End Object Detection with Transformers*
* **Developed by:** Facebook AI Research (FAIR)
* **Purpose:** Object detection and segmentation using a transformer-based architecture instead of traditional CNN-based pipelines.
* **Paper:** *“End-to-End Object Detection with Transformers”* (2020).

---

### 🌆 **CLIP — Contrastive Language–Image Pre-training**

* **Full name:** *Contrastive Language–Image Pre-training*
* **Developed by:** OpenAI
* **Purpose:** Scene and concept understanding — learns to associate images with natural language descriptions, enabling zero-shot classification and scene analysis.
* **Paper:** *“Learning Transferable Visual Models From Natural Language Supervision”* (2021).

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
