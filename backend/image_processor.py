"""
Image Processing Module
Handles image validation, optimization, and preprocessing
"""

import io
import requests
from PIL import Image
from typing import Tuple, Optional, Dict, Any
from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, MAX_IMAGE_DIMENSION, IMAGE_QUALITY


class ImageProcessor:
    """Handles all image processing operations"""
    
    @staticmethod
    def validate_extension(filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    @staticmethod
    def validate_image(image_data: bytes) -> Tuple[bool, str]:
        """
        Validate image data
        Returns: (is_valid, error_message)
        """
        if not image_data:
            return False, "No image data provided"
        
        if len(image_data) > MAX_FILE_SIZE:
            size_mb = MAX_FILE_SIZE / (1024 * 1024)
            return False, f"Image exceeds {size_mb}MB limit"
        
        try:
            img = Image.open(io.BytesIO(image_data))
            img.verify()
            return True, ""
        except Exception as e:
            return False, f"Invalid image: {str(e)}"
    
    @staticmethod
    def download_from_url(url: str) -> Tuple[Optional[bytes], str]:
        """
        Download image from URL
        Returns: (image_bytes, error_message)
        """
        try:
            response = requests.get(url, timeout=15, stream=True)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type.lower():
                return None, "URL does not point to an image"
            
            image_data = response.content
            is_valid, error = ImageProcessor.validate_image(image_data)
            
            if not is_valid:
                return None, error
            
            return image_data, ""
            
        except requests.exceptions.Timeout:
            return None, "Request timeout"
        except requests.exceptions.RequestException as e:
            return None, f"Download failed: {str(e)}"
    
    @staticmethod
    def optimize_image(image_data: bytes) -> Tuple[Image.Image, bytes]:
        """
        Optimize image for AI processing
        Returns: (PIL Image, optimized bytes)
        """
        try:
            img = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = rgb_img
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if too large
            if max(img.size) > MAX_IMAGE_DIMENSION:
                img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.Resampling.LANCZOS)
            
            # Convert to bytes
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=IMAGE_QUALITY, optimize=True)
            optimized_bytes = output.getvalue()
            
            return img, optimized_bytes
            
        except Exception as e:
            print(f"[ERROR] Image optimization failed: {str(e)}")
            # Return original if optimization fails
            img = Image.open(io.BytesIO(image_data))
            return img, image_data
    
    @staticmethod
    def extract_metadata(image_data: bytes) -> Dict[str, Any]:
        """Extract image metadata"""
        try:
            img = Image.open(io.BytesIO(image_data))
            
            metadata = {
                "width": img.width,
                "height": img.height,
                "format": img.format or "JPEG",
                "mode": img.mode,
                "size_bytes": len(image_data),
                "size_kb": round(len(image_data) / 1024, 2),
                "size_mb": round(len(image_data) / (1024 * 1024), 2),
                "aspect_ratio": round(img.width / img.height, 2) if img.height > 0 else 0
            }
            
            # Add EXIF data if available
            if hasattr(img, '_getexif') and img._getexif():
                exif = img._getexif()
                if exif:
                    metadata['has_exif'] = True
            
            return metadata
            
        except Exception as e:
            print(f"[ERROR] Metadata extraction failed: {str(e)}")
            return {}