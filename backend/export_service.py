"""
Export Service
Handles exporting analysis results to various formats
Files are saved to system temp directory for direct download
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors


class ExportService:
    """Handles exporting results to JSON and PDF"""
    
    def __init__(self):
        # Use system temp directory instead of project directory
        self.temp_dir = Path(tempfile.gettempdir()) / 'visionai_exports'
        self.temp_dir.mkdir(exist_ok=True)
        print(f"📁 Export directory: {self.temp_dir}")
    
    def export_json(self, data: Dict[str, Any]) -> Tuple[str, Path]:
        """Export to JSON file - returns filename and filepath"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"visionai_analysis_{timestamp}.json"
        filepath = self.temp_dir / filename
        
        # Clean data for JSON export
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": data.get('summary', ''),
            "captions": data.get('captions', []),
            "statistics": data.get('statistics', {}),
            "labels": data.get('labels', []),
            "objects": data.get('objects', []),
            "scene_analysis": data.get('scene_analysis', []),
            "metadata": data.get('metadata', {}),
            "model_info": data.get('model_info', {})
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON exported: {filepath}")
        return filename, filepath
    
    def export_pdf(self, data: Dict[str, Any]) -> Tuple[str, Path]:
        """Export to PDF file - returns filename and filepath"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"visionai_analysis_{timestamp}.pdf"
        filepath = self.temp_dir / filename
        
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles - minimal and clean
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=20
        )
        
        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#374151'),
            spaceAfter=10,
            spaceBefore=10
        )
        
        # Title
        story.append(Paragraph("VisionAI Analysis Report", title_style))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.3 * inch))
        
        # Summary
        summary = data.get('summary', '')
        if summary:
            story.append(Paragraph("Summary", heading_style))
            story.append(Paragraph(summary, styles['Normal']))
            story.append(Spacer(1, 0.2 * inch))
        
        # Statistics
        stats = data.get('statistics', {})
        if stats:
            story.append(Paragraph("Statistics", heading_style))
            stats_data = [['Metric', 'Value']]
            for key, value in stats.items():
                stats_data.append([key.replace('_', ' ').title(), str(value)])
            
            stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb'))
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 0.2 * inch))
        
        # Captions
        captions = data.get('captions', [])
        if captions:
            story.append(Paragraph("Generated Captions", heading_style))
            for i, caption in enumerate(captions, 1):
                story.append(Paragraph(f"{i}. {caption}", styles['Normal']))
            story.append(Spacer(1, 0.2 * inch))
        
        # Labels
        labels = data.get('labels', [])
        if labels:
            story.append(Paragraph("Classification Labels", heading_style))
            label_data = [['Label', 'Confidence']]
            for label in labels[:15]:
                label_data.append([
                    label['description'],
                    f"{label['confidence']}%"
                ])
            
            label_table = Table(label_data, colWidths=[3.5*inch, 1.5*inch])
            label_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb'))
            ]))
            story.append(label_table)
            story.append(Spacer(1, 0.2 * inch))
        
        # Objects
        objects = data.get('objects', [])
        if objects:
            story.append(Paragraph("Detected Objects", heading_style))
            obj_data = [['Object', 'Count', 'Confidence']]
            for obj in objects[:10]:
                obj_data.append([
                    obj['name'],
                    str(obj['count']),
                    f"{obj['confidence']}%"
                ])
            
            obj_table = Table(obj_data, colWidths=[2.5*inch, 1*inch, 1.5*inch])
            obj_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb'))
            ]))
            story.append(obj_table)
            story.append(Spacer(1, 0.2 * inch))
        
        # Metadata
        metadata = data.get('metadata', {})
        if metadata:
            story.append(Paragraph("Image Metadata", heading_style))
            meta_data = [['Property', 'Value']]
            for key, value in metadata.items():
                if key not in ['has_exif']:
                    meta_data.append([
                        key.replace('_', ' ').title(),
                        str(value)
                    ])
            
            meta_table = Table(meta_data, colWidths=[2.5*inch, 2.5*inch])
            meta_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb'))
            ]))
            story.append(meta_table)
        
        # Build PDF
        doc.build(story)
        print(f"✅ PDF exported: {filepath}")
        return filename, filepath