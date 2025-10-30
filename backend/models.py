"""
AI Models Manager
Handles loading and inference for all local AI models
"""

import torch
from PIL import Image
from pathlib import Path
from transformers import (
    BlipProcessor, BlipForConditionalGeneration,
    ViTImageProcessor, ViTForImageClassification,
    DetrImageProcessor, DetrForObjectDetection,
    CLIPProcessor, CLIPModel
)
import io
import os
from typing import Dict, List, Any
from config import MODELS, CONFIDENCE_THRESHOLD, MAX_LABELS, MAX_OBJECTS, MODELS_CACHE
import warnings

# Suppress all transformer warnings for cleaner output
warnings.filterwarnings('ignore')
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class VisionModels:
    """Singleton class to manage all AI models"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print("\n" + "="*70)
        print(f"🤖 Initializing AI Models")
        print("="*70)
        print(f"📍 Device: {self.device.upper()}")
        print(f"📂 Cache: {MODELS_CACHE}")
        print("="*70)
        
        try:
            # Load BLIP for captioning
            print("\n[1/4] 🖼️  BLIP Image Captioning...")
            self.caption_processor = BlipProcessor.from_pretrained(
                MODELS['CAPTIONING'],
                cache_dir=str(MODELS_CACHE)
            )
            self.caption_model = BlipForConditionalGeneration.from_pretrained(
                MODELS['CAPTIONING'],
                cache_dir=str(MODELS_CACHE)
            ).to(self.device)
            print("      ✅ Loaded")
            
            # Load ViT for classification
            print("\n[2/4] 🏷️  ViT Image Classification...")
            self.class_processor = ViTImageProcessor.from_pretrained(
                MODELS['CLASSIFICATION'],
                cache_dir=str(MODELS_CACHE)
            )
            self.class_model = ViTForImageClassification.from_pretrained(
                MODELS['CLASSIFICATION'],
                cache_dir=str(MODELS_CACHE)
            ).to(self.device)
            print("      ✅ Loaded")
            
            # Load DETR for object detection
            print("\n[3/4] 🎯 DETR Object Detection...")
            self.obj_processor = DetrImageProcessor.from_pretrained(
                MODELS['OBJECT_DETECTION'],
                cache_dir=str(MODELS_CACHE)
            )
            self.obj_model = DetrForObjectDetection.from_pretrained(
                MODELS['OBJECT_DETECTION'],
                cache_dir=str(MODELS_CACHE)
            ).to(self.device)
            print("      ✅ Loaded")
            
            # Load CLIP for advanced features
            print("\n[4/4] 🔍 CLIP Scene Understanding...")
            self.clip_processor = CLIPProcessor.from_pretrained(
                MODELS['CLIP'],
                cache_dir=str(MODELS_CACHE)
            )
            self.clip_model = CLIPModel.from_pretrained(
                MODELS['CLIP'],
                cache_dir=str(MODELS_CACHE)
            ).to(self.device)
            print("      ✅ Loaded")
            
            self._initialized = True
            print("\n" + "="*70)
            print("✅ All Models Ready!")
            print("="*70 + "\n")
            
        except Exception as e:
            print(f"\n❌ ERROR: Failed to load models")
            print(f"   {str(e)}")
            print("\n💡 First time? Models will download automatically (~5-7 GB)")
            raise
    
    def generate_captions(self, image: Image.Image) -> List[str]:
        """Generate multiple image captions using BLIP"""
        try:
            inputs = self.caption_processor(image, return_tensors="pt").to(self.device)
            
            captions = []
            
            # Generate diverse captions with different parameters
            with torch.no_grad():
                # Standard caption
                out1 = self.caption_model.generate(
                    **inputs, max_length=50, num_beams=3
                )
                captions.append(self.caption_processor.decode(out1[0], skip_special_tokens=True))
                
                # Detailed caption
                out2 = self.caption_model.generate(
                    **inputs, max_length=80, num_beams=5, temperature=0.9
                )
                captions.append(self.caption_processor.decode(out2[0], skip_special_tokens=True))
                
                # Creative caption
                out3 = self.caption_model.generate(
                    **inputs, max_length=60, num_beams=4, do_sample=True, top_k=50
                )
                captions.append(self.caption_processor.decode(out3[0], skip_special_tokens=True))
            
            # Remove duplicates while preserving order
            unique_captions = []
            for cap in captions:
                if cap not in unique_captions:
                    unique_captions.append(cap)
            
            return unique_captions
            
        except Exception as e:
            print(f"[ERROR] Caption generation failed: {str(e)}")
            return ["Unable to generate caption"]
    
    def classify_image(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Classify image into categories using ViT"""
        try:
            inputs = self.class_processor(image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.class_model(**inputs)
                logits = outputs.logits
            
            # Get top predictions
            probs = torch.nn.functional.softmax(logits, dim=-1)[0]
            top_probs, top_indices = torch.topk(probs, k=MAX_LABELS)
            
            results = []
            for prob, idx in zip(top_probs, top_indices):
                confidence = prob.item()
                if confidence >= CONFIDENCE_THRESHOLD:
                    label = self.class_model.config.id2label[idx.item()]
                    results.append({
                        'label': label.replace('_', ' ').title(),
                        'confidence': round(confidence * 100, 2)
                    })
            
            return results
            
        except Exception as e:
            print(f"[ERROR] Classification failed: {str(e)}")
            return []
    
    def detect_objects(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Detect objects in image using DETR"""
        try:
            inputs = self.obj_processor(images=image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.obj_model(**inputs)
            
            # Post-process detections
            target_sizes = torch.tensor([image.size[::-1]])
            results = self.obj_processor.post_process_object_detection(
                outputs, target_sizes=target_sizes, threshold=CONFIDENCE_THRESHOLD
            )[0]
            
            # Group objects by label and count
            object_counts = {}
            for score, label, box in zip(
                results["scores"], results["labels"], results["boxes"]
            ):
                label_name = self.obj_model.config.id2label[label.item()]
                confidence = score.item()
                
                if label_name in object_counts:
                    object_counts[label_name]['count'] += 1
                    object_counts[label_name]['confidence'] = max(
                        object_counts[label_name]['confidence'], confidence
                    )
                else:
                    object_counts[label_name] = {
                        'name': label_name.replace('_', ' ').title(),
                        'count': 1,
                        'confidence': round(confidence * 100, 2)
                    }
            
            # Sort by confidence
            objects = list(object_counts.values())
            objects.sort(key=lambda x: x['confidence'], reverse=True)
            
            return objects[:MAX_OBJECTS]
            
        except Exception as e:
            print(f"[ERROR] Object detection failed: {str(e)}")
            return []
    
    def analyze_with_clip(self, image: Image.Image) -> Dict[str, Any]:
        """Advanced analysis using CLIP"""
        try:
            # Define comprehensive categories
            categories = [
                # Scene types
                "indoor scene", "outdoor scene", "landscape", "cityscape", "portrait",
                "nature photography", "urban environment", "underwater scene",
                
                # Time and lighting
                "daytime", "nighttime", "sunset", "sunrise", "bright lighting",
                "dark atmosphere", "dramatic lighting", "natural light",
                
                # Style and mood
                "professional photography", "artistic composition", "minimalist style",
                "vibrant colors", "black and white", "vintage style", "modern design",
                
                # Activities and content
                "people", "animals", "food", "technology", "architecture",
                "transportation", "sports", "nature", "art", "fashion"
            ]
            
            # Process image and text
            inputs = self.clip_processor(
                text=categories, images=image, return_tensors="pt", padding=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)[0]
            
            # Get top matches
            top_probs, top_indices = torch.topk(probs, k=10)
            
            results = []
            for prob, idx in zip(top_probs, top_indices):
                confidence = prob.item()
                if confidence >= CONFIDENCE_THRESHOLD:
                    results.append({
                        'category': categories[idx.item()].title(),
                        'confidence': round(confidence * 100, 2)
                    })
            
            return {'scene_understanding': results}
            
        except Exception as e:
            print(f"[ERROR] CLIP analysis failed: {str(e)}")
            return {'scene_understanding': []}


# Global model instance
_models = None

def get_models() -> VisionModels:
    """Get or create the global models instance"""
    global _models
    if _models is None:
        _models = VisionModels()
    return _models