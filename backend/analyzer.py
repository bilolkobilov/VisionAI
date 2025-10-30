"""
Vision Analyzer Service
Main service for coordinating AI analysis
"""

from PIL import Image
from typing import Dict, Any, List
from models import get_models
from image_processor import ImageProcessor


class VisionAnalyzer:
    """Coordinates all AI analysis operations"""
    
    def __init__(self):
        self.models = get_models()
        self.processor = ImageProcessor()
    
    def analyze(self, image_data: bytes) -> Dict[str, Any]:
        """
        Perform comprehensive image analysis
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Complete analysis results
        """
        print("\n" + "─"*70)
        print("🔍 Starting Image Analysis...")
        print("─"*70)
        
        try:
            # Optimize image
            image, optimized_bytes = self.processor.optimize_image(image_data)
            print(f"📐 Image: {image.size[0]}x{image.size[1]} pixels")
            
            # Extract metadata
            metadata = self.processor.extract_metadata(image_data)
            print(f"💾 Size: {metadata.get('size_kb', 0)} KB")
            
            # Run all AI models
            results = {}
            
            # 1. Generate captions
            print("\n[1/4] 🖼️  Generating captions...", end=' ')
            captions = self.models.generate_captions(image)
            results['captions'] = captions
            print(f"✅ {len(captions)} captions")
            
            # 2. Classify image
            print("[2/4] 🏷️  Classifying image...", end=' ')
            classifications = self.models.classify_image(image)
            results['classifications'] = classifications
            print(f"✅ {len(classifications)} labels")
            
            # 3. Detect objects
            print("[3/4] 🎯 Detecting objects...", end=' ')
            objects = self.models.detect_objects(image)
            results['objects'] = objects
            print(f"✅ {len(objects)} objects")
            
            # 4. CLIP scene understanding
            print("[4/4] 🔍 Analyzing scene...", end=' ')
            clip_results = self.models.analyze_with_clip(image)
            results['scene_analysis'] = clip_results.get('scene_understanding', [])
            print(f"✅ Complete")
            
            # Process and format results
            formatted = self._format_results(results, metadata)
            
            print("─"*70)
            print("✅ Analysis Complete!")
            print("─"*70 + "\n")
            
            return formatted
            
        except Exception as e:
            print(f"\n❌ Analysis Failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _format_results(self, results: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Format analysis results for frontend"""
        
        # Generate comprehensive summary
        summary = self._generate_summary(results)
        
        # Calculate statistics
        stats = self._calculate_statistics(results)
        
        # Format for frontend
        formatted = {
            "summary": summary,
            "statistics": stats,
            "captions": results.get('captions', []),
            "labels": self._format_labels(results.get('classifications', [])),
            "objects": results.get('objects', []),
            "scene_analysis": results.get('scene_analysis', []),
            "metadata": metadata,
            "model_info": {
                "captioning": "BLIP (Salesforce)",
                "classification": "ViT (Google)",
                "detection": "DETR (Facebook)",
                "scene_understanding": "CLIP (OpenAI)",
                "mode": "Local Inference",
                "device": self.models.device.upper()
            }
        }
        
        return formatted
    
    def _format_labels(self, classifications: List[Dict]) -> List[Dict]:
        """Format classification labels"""
        return [{
            'description': cls['label'],
            'confidence': cls['confidence']
        } for cls in classifications]
    
    def _generate_summary(self, results: Dict[str, Any]) -> str:
        """Generate human-readable summary"""
        parts = []
        
        # Primary caption
        captions = results.get('captions', [])
        if captions:
            parts.append(captions[0].capitalize() + ".")
        
        # Object counts
        objects = results.get('objects', [])
        if objects:
            total_objects = sum(obj['count'] for obj in objects[:3])
            obj_names = [obj['name'].lower() for obj in objects[:3]]
            
            if len(obj_names) == 1:
                parts.append(f"Contains {total_objects} {obj_names[0]}.")
            elif len(obj_names) > 1:
                parts.append(f"Contains {', '.join(obj_names[:-1])} and {obj_names[-1]}.")
        
        # Scene description
        scene = results.get('scene_analysis', [])
        if scene:
            top_scenes = [s['category'].lower() for s in scene[:2]]
            if top_scenes:
                parts.append(f"Scene appears to be {' and '.join(top_scenes)}.")
        
        # Top classifications
        classifications = results.get('classifications', [])
        if classifications and not parts:  # Fallback if no other info
            top_classes = [c['label'].lower() for c in classifications[:3]]
            parts.append(f"Image features: {', '.join(top_classes)}.")
        
        return " ".join(parts) if parts else "Image analyzed successfully."
    
    def _calculate_statistics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate interesting statistics"""
        stats = {}
        
        # Object statistics
        objects = results.get('objects', [])
        if objects:
            stats['total_objects'] = sum(obj['count'] for obj in objects)
            stats['unique_objects'] = len(objects)
            stats['most_common'] = objects[0]['name'] if objects else None
        
        # Classification confidence
        classifications = results.get('classifications', [])
        if classifications:
            confidences = [c['confidence'] for c in classifications]
            stats['avg_confidence'] = round(sum(confidences) / len(confidences), 2)
            stats['top_confidence'] = max(confidences)
        
        # Scene analysis
        scene = results.get('scene_analysis', [])
        if scene:
            stats['scene_matches'] = len(scene)
        
        return stats