"""
VisionAI Flask Application
Main application entry point - Updated for direct downloads
"""

import os
import sys
import base64
import webbrowser
from pathlib import Path
from threading import Timer
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Suppress Flask development server warnings
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

from config import HOST, PORT, DEBUG, APP_NAME, VERSION
from analyzer import VisionAnalyzer
from image_processor import ImageProcessor
from export_service import ExportService


# Initialize Flask
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Initialize services
print("\n🚀 Starting VisionAI...")
analyzer = VisionAnalyzer()
processor = ImageProcessor()
exporter = ExportService()

# Track browser opening
_browser_opened = False


@app.route('/')
def index():
    """Serve main application page"""
    return send_from_directory('../frontend', 'index.html')


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "app": APP_NAME,
        "version": VERSION,
        "models": analyzer.models.device.upper()
    })


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze image endpoint"""
    try:
        image_data = None
        
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({"success": False, "message": "No file selected"}), 400
            
            if not processor.validate_extension(file.filename):
                return jsonify({"success": False, "message": "Invalid file type"}), 400
            
            image_data = file.read()
        
        # Handle JSON payload
        elif request.is_json:
            data = request.get_json()
            req_type = data.get('type')
            req_data = data.get('data')
            
            if req_type == 'url':
                image_data, error = processor.download_from_url(req_data)
                if error:
                    return jsonify({"success": False, "message": error}), 400
            
            elif req_type == 'base64':
                try:
                    if ',' in req_data:
                        req_data = req_data.split(',')[1]
                    image_data = base64.b64decode(req_data)
                except Exception as e:
                    return jsonify({"success": False, "message": f"Invalid base64: {str(e)}"}), 400
            
            else:
                return jsonify({"success": False, "message": "Invalid request type"}), 400
        
        else:
            return jsonify({"success": False, "message": "No image provided"}), 400
        
        # Validate image
        is_valid, error = processor.validate_image(image_data)
        if not is_valid:
            return jsonify({"success": False, "message": error}), 400
        
        # Analyze image
        results = analyzer.analyze(image_data)
        
        if 'error' in results:
            return jsonify({"success": False, "message": results['error']}), 500
        
        return jsonify({
            "success": True,
            "data": results,
            "message": "Analysis completed successfully"
        })
    
    except Exception as e:
        print(f"❌ Analysis Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@app.route('/api/export', methods=['POST'])
def export():
    """Export results endpoint - returns file data directly"""
    try:
        data = request.get_json()
        export_format = data.get('format', 'json').lower()
        analysis_data = data.get('data')
        
        if not analysis_data:
            return jsonify({"success": False, "message": "No data to export"}), 400
        
        if export_format == 'json':
            filename, filepath = exporter.export_json(analysis_data)
        elif export_format == 'pdf':
            filename, filepath = exporter.export_pdf(analysis_data)
        else:
            return jsonify({"success": False, "message": "Invalid format"}), 400
        
        return jsonify({
            "success": True,
            "data": {"filename": filename},
            "message": f"Exported as {export_format.upper()}"
        })
    
    except Exception as e:
        print(f"❌ Export Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/download/<filename>')
def download(filename):
    """Download exported file - serves from temp directory"""
    try:
        # Files are stored in system temp directory
        import tempfile
        temp_dir = Path(tempfile.gettempdir()) / 'visionai_exports'
        filepath = temp_dir / filename
        
        if not filepath.exists():
            return jsonify({"success": False, "message": "File not found"}), 404
        
        return send_file(
            filepath, 
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        print(f"❌ Download Error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 404


def open_browser():
    """Open browser after server start"""
    global _browser_opened
    if not _browser_opened:
        _browser_opened = True
        webbrowser.open(f'http://{HOST}:{PORT}')


def main():
    """Main application entry point"""
    print("\n" + "="*70)
    print(f"🌐 {APP_NAME} v{VERSION} - Server Ready")
    print("="*70)
    print(f"🔗 URL: http://{HOST}:{PORT}")
    print(f"🤖 AI: {analyzer.models.device.upper()}")
    print(f"🌐 Opening browser...")
    print(f"\n💡 Press Ctrl+C to stop")
    print("="*70 + "\n")
    
    # Open browser after delay
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        Timer(1.5, open_browser).start()
    
    # Run application
    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG,
        use_reloader=False,
        threaded=True
    )


if __name__ == '__main__':
    main()