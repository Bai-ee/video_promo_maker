#!/usr/bin/env python3
"""
Image Processing Component for Bulk Operations
Handles batch image processing tasks like cropping, resizing, etc.
"""

import streamlit as st
import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from PIL import Image, ImageOps
import io
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json

class ImageProcessor:
    """Handles bulk image processing operations"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.temp_dir = self.project_root / "temp_processing"
        self.output_dir = self.project_root / "output" / "processed_images"
        
        # Create directories if they don't exist
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_zip_to_temp(self, zip_file, job_id: str) -> Path:
        """Extract uploaded zip file to temporary directory"""
        temp_job_dir = self.temp_dir / job_id
        temp_job_dir.mkdir(exist_ok=True)
        
        # Save uploaded file
        zip_path = temp_job_dir / "uploaded.zip"
        with open(zip_path, "wb") as f:
            f.write(zip_file.getvalue())
        
        # Extract zip
        extract_dir = temp_job_dir / "extracted"
        extract_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        return extract_dir
    
    def find_png_files(self, directory: Path) -> List[Path]:
        """Recursively find all PNG files in directory"""
        png_files = []
        for ext in ['*.png', '*.PNG']:
            png_files.extend(directory.rglob(ext))
        return png_files
    
    def crop_to_content(self, image_path: Path, output_path: Path) -> Dict:
        """Crop image to remove transparent/empty space"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGBA if not already
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Get the bounding box of non-transparent pixels
                bbox = img.getbbox()
                
                if bbox:
                    # Crop to bounding box
                    cropped_img = img.crop(bbox)
                    
                    # Save the cropped image
                    cropped_img.save(output_path, 'PNG')
                    
                    # Calculate reduction
                    original_size = img.size
                    cropped_size = cropped_img.size
                    reduction_percent = (1 - (cropped_size[0] * cropped_size[1]) / (original_size[0] * original_size[1])) * 100
                    
                    return {
                        'success': True,
                        'original_size': original_size,
                        'cropped_size': cropped_size,
                        'reduction_percent': reduction_percent,
                        'bbox': bbox
                    }
                else:
                    # Image is completely transparent, copy as-is
                    shutil.copy2(image_path, output_path)
                    return {
                        'success': True,
                        'original_size': img.size,
                        'cropped_size': img.size,
                        'reduction_percent': 0,
                        'bbox': None,
                        'note': 'Image was completely transparent'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_bulk_crop(self, zip_file, job_id: str, progress_callback=None) -> Dict:
        """Process bulk cropping operation"""
        try:
            if progress_callback:
                progress_callback("📦 Extracting zip file...", 5)
            
            # Extract zip file
            extract_dir = self.extract_zip_to_temp(zip_file, job_id)
            
            if progress_callback:
                progress_callback("🔍 Finding PNG files...", 10)
            
            # Find all PNG files
            png_files = self.find_png_files(extract_dir)
            
            if not png_files:
                return {
                    'success': False,
                    'error': 'No PNG files found in the uploaded zip'
                }
            
            if progress_callback:
                progress_callback(f"📋 Found {len(png_files)} PNG files to process", 15)
            
            # Create output directory for this job
            job_output_dir = self.output_dir / job_id
            job_output_dir.mkdir(exist_ok=True)
            
            # Process each PNG file
            results = []
            total_files = len(png_files)
            
            for i, png_file in enumerate(png_files):
                if progress_callback:
                    progress = 15 + (i / total_files) * 70  # 15% to 85%
                    progress_callback(f"✂️ Cropping {png_file.name}... ({i+1}/{total_files})", int(progress))
                
                # Create relative path structure in output
                rel_path = png_file.relative_to(extract_dir)
                output_file = job_output_dir / rel_path
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Process the image
                result = self.crop_to_content(png_file, output_file)
                result['filename'] = png_file.name
                result['relative_path'] = str(rel_path)
                results.append(result)
            
            if progress_callback:
                progress_callback("📦 Creating output zip...", 90)
            
            # Create output zip
            output_zip_path = self.output_dir / f"{job_id}_cropped.zip"
            with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in job_output_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(job_output_dir)
                        zipf.write(file_path, arcname)
            
            if progress_callback:
                progress_callback("✅ Processing complete!", 100)
            
            # Calculate summary statistics
            successful_crops = [r for r in results if r['success']]
            failed_crops = [r for r in results if not r['success']]
            
            total_reduction = sum(r.get('reduction_percent', 0) for r in successful_crops)
            avg_reduction = total_reduction / len(successful_crops) if successful_crops else 0
            
            # Clean up temp directory
            temp_job_dir = self.temp_dir / job_id
            if temp_job_dir.exists():
                shutil.rmtree(temp_job_dir)
            
            return {
                'success': True,
                'job_id': job_id,
                'total_files': total_files,
                'successful_crops': len(successful_crops),
                'failed_crops': len(failed_crops),
                'average_reduction': avg_reduction,
                'output_zip_path': str(output_zip_path),
                'output_directory': str(job_output_dir),
                'results': results,
                'summary': {
                    'files_processed': total_files,
                    'files_successful': len(successful_crops),
                    'files_failed': len(failed_crops),
                    'average_size_reduction': f"{avg_reduction:.1f}%",
                    'output_zip_size': self.get_file_size(output_zip_path)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'job_id': job_id
            }
    
    def get_file_size(self, file_path: Path) -> str:
        """Get human-readable file size"""
        size_bytes = file_path.stat().st_size
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def process_bulk_resize(self, zip_file, job_id: str, target_size: Tuple[int, int], progress_callback=None) -> Dict:
        """Process bulk resize operation"""
        try:
            if progress_callback:
                progress_callback("📦 Extracting zip file...", 5)
            
            # Extract zip file
            extract_dir = self.extract_zip_to_temp(zip_file, job_id)
            
            if progress_callback:
                progress_callback("🔍 Finding PNG files...", 10)
            
            # Find all PNG files
            png_files = self.find_png_files(extract_dir)
            
            if not png_files:
                return {
                    'success': False,
                    'error': 'No PNG files found in the uploaded zip'
                }
            
            if progress_callback:
                progress_callback(f"📋 Found {len(png_files)} PNG files to resize to {target_size}", 15)
            
            # Create output directory for this job
            job_output_dir = self.output_dir / f"{job_id}_resized"
            job_output_dir.mkdir(exist_ok=True)
            
            # Process each PNG file
            results = []
            total_files = len(png_files)
            
            for i, png_file in enumerate(png_files):
                if progress_callback:
                    progress = 15 + (i / total_files) * 70  # 15% to 85%
                    progress_callback(f"🔄 Resizing {png_file.name}... ({i+1}/{total_files})", int(progress))
                
                try:
                    # Create relative path structure in output
                    rel_path = png_file.relative_to(extract_dir)
                    output_file = job_output_dir / rel_path
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Resize the image
                    with Image.open(png_file) as img:
                        original_size = img.size
                        resized_img = img.resize(target_size, Image.Resampling.LANCZOS)
                        resized_img.save(output_file, 'PNG')
                        
                        results.append({
                            'success': True,
                            'filename': png_file.name,
                            'relative_path': str(rel_path),
                            'original_size': original_size,
                            'new_size': target_size
                        })
                        
                except Exception as e:
                    results.append({
                        'success': False,
                        'filename': png_file.name,
                        'error': str(e)
                    })
            
            if progress_callback:
                progress_callback("📦 Creating output zip...", 90)
            
            # Create output zip
            output_zip_path = self.output_dir / f"{job_id}_resized.zip"
            with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in job_output_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(job_output_dir)
                        zipf.write(file_path, arcname)
            
            if progress_callback:
                progress_callback("✅ Resizing complete!", 100)
            
            # Calculate summary statistics
            successful_resizes = [r for r in results if r['success']]
            failed_resizes = [r for r in results if not r['success']]
            
            # Clean up temp directory
            temp_job_dir = self.temp_dir / job_id
            if temp_job_dir.exists():
                shutil.rmtree(temp_job_dir)
            
            return {
                'success': True,
                'job_id': job_id,
                'total_files': len(png_files),
                'successful_resizes': len(successful_resizes),
                'failed_resizes': len(failed_resizes),
                'target_size': target_size,
                'output_zip_path': str(output_zip_path),
                'output_directory': str(job_output_dir),
                'results': results,
                'summary': {
                    'files_processed': len(png_files),
                    'files_successful': len(successful_resizes),
                    'files_failed': len(failed_resizes),
                    'target_size': f"{target_size[0]}x{target_size[1]}",
                    'output_zip_size': self.get_file_size(output_zip_path)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'job_id': job_id
            }
    
    def cleanup_old_files(self, days_old: int = 7):
        """Clean up old temporary and output files"""
        import time
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        
        # Clean temp directory
        for item in self.temp_dir.iterdir():
            if item.stat().st_mtime < cutoff_time:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
        
        # Clean old output files
        for item in self.output_dir.iterdir():
            if item.stat().st_mtime < cutoff_time:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
    
    def create_thumbnail_with_artboard(self, image_path: Path, output_path: Path, 
                                       artboard_size: Tuple[int, int] = (1080, 1080),
                                       scale_percent: float = 90.0,
                                       center_horizontal: bool = True,
                                       center_vertical: bool = True,
                                       background_color: Optional[Tuple[int, int, int, int]] = None) -> Dict:
        """Create thumbnail by cropping to content and placing in custom artboard"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGBA if not already
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                original_size = img.size
                
                # Step 1: Crop to content (remove transparent/empty space)
                bbox = img.getbbox()
                
                if not bbox:
                    # Image is completely transparent, create a small placeholder
                    cropped_img = Image.new('RGBA', (10, 10), (0, 0, 0, 0))
                    cropped_size = (10, 10)
                else:
                    cropped_img = img.crop(bbox)
                    cropped_size = cropped_img.size
                
                # Step 2: Create new artboard
                artboard = Image.new('RGBA', artboard_size, background_color or (0, 0, 0, 0))
                
                # Step 3: Calculate scaling to fit within specified percentage of artboard
                max_width = int(artboard_size[0] * (scale_percent / 100.0))
                max_height = int(artboard_size[1] * (scale_percent / 100.0))
                
                # Calculate scale factor to fit within max dimensions
                scale_factor = min(max_width / cropped_size[0], max_height / cropped_size[1])
                
                new_width = int(cropped_size[0] * scale_factor)
                new_height = int(cropped_size[1] * scale_factor)
                
                # Step 4: Resize cropped image
                scaled_img = cropped_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Step 5: Calculate position for centering
                if center_horizontal:
                    x_pos = (artboard_size[0] - new_width) // 2
                else:
                    x_pos = 0
                    
                if center_vertical:
                    y_pos = (artboard_size[1] - new_height) // 2
                else:
                    y_pos = 0
                
                # Step 6: Paste scaled image onto artboard
                artboard.paste(scaled_img, (x_pos, y_pos), scaled_img)
                
                # Step 7: Save the result
                artboard.save(output_path, 'PNG')
                
                # Calculate statistics
                original_area = original_size[0] * original_size[1]
                cropped_area = cropped_size[0] * cropped_size[1]
                reduction_percent = (1 - (cropped_area / original_area)) * 100 if original_area > 0 else 0
                
                return {
                    'success': True,
                    'original_size': original_size,
                    'cropped_size': cropped_size,
                    'artboard_size': artboard_size,
                    'final_scaled_size': (new_width, new_height),
                    'scale_factor': scale_factor,
                    'scale_percent_used': scale_percent,
                    'position': (x_pos, y_pos),
                    'reduction_percent': reduction_percent,
                    'bbox': bbox
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_bulk_thumbnail(self, zip_file, job_id: str, artboard_size: Tuple[int, int] = (1080, 1080),
                               scale_percent: float = 90.0, center_horizontal: bool = True,
                               center_vertical: bool = True, progress_callback=None) -> Dict:
        """Process bulk thumbnail creation with custom artboards"""
        try:
            if progress_callback:
                progress_callback("📦 Extracting zip file...", 5)
            
            # Extract zip file
            extract_dir = self.extract_zip_to_temp(zip_file, job_id)
            
            if progress_callback:
                progress_callback("🔍 Finding PNG files...", 10)
            
            # Find all PNG files
            png_files = self.find_png_files(extract_dir)
            
            if not png_files:
                return {
                    'success': False,
                    'error': 'No PNG files found in the uploaded zip'
                }
            
            if progress_callback:
                progress_callback(f"📋 Found {len(png_files)} PNG files to process into thumbnails", 15)
            
            # Create output directory for this job
            job_output_dir = self.output_dir / f"{job_id}_thumbnails"
            job_output_dir.mkdir(exist_ok=True)
            
            # Process each PNG file
            results = []
            total_files = len(png_files)
            
            for i, png_file in enumerate(png_files):
                if progress_callback:
                    progress = 15 + (i / total_files) * 70  # 15% to 85%
                    progress_callback(f"🖼️ Creating thumbnail {png_file.name}... ({i+1}/{total_files})", int(progress))
                
                # Create relative path structure in output
                rel_path = png_file.relative_to(extract_dir)
                output_file = job_output_dir / rel_path
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Process the image with artboard
                result = self.create_thumbnail_with_artboard(
                    png_file, 
                    output_file,
                    artboard_size=artboard_size,
                    scale_percent=scale_percent,
                    center_horizontal=center_horizontal,
                    center_vertical=center_vertical
                )
                result['filename'] = png_file.name
                result['relative_path'] = str(rel_path)
                results.append(result)
            
            if progress_callback:
                progress_callback("📦 Creating output zip...", 90)
            
            # Create output zip
            output_zip_path = self.output_dir / f"{job_id}_thumbnails.zip"
            with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in job_output_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(job_output_dir)
                        zipf.write(file_path, arcname)
            
            if progress_callback:
                progress_callback("✅ Thumbnail creation complete!", 100)
            
            # Calculate summary statistics
            successful_thumbnails = [r for r in results if r['success']]
            failed_thumbnails = [r for r in results if not r['success']]
            
            # Calculate average statistics
            if successful_thumbnails:
                avg_reduction = sum(r.get('reduction_percent', 0) for r in successful_thumbnails) / len(successful_thumbnails)
                avg_scale_factor = sum(r.get('scale_factor', 1) for r in successful_thumbnails) / len(successful_thumbnails)
            else:
                avg_reduction = 0
                avg_scale_factor = 1
            
            # Clean up temp directory
            temp_job_dir = self.temp_dir / job_id
            if temp_job_dir.exists():
                shutil.rmtree(temp_job_dir)
            
            return {
                'success': True,
                'job_id': job_id,
                'total_files': total_files,
                'successful_thumbnails': len(successful_thumbnails),
                'failed_thumbnails': len(failed_thumbnails),
                'artboard_size': artboard_size,
                'scale_percent': scale_percent,
                'average_reduction': avg_reduction,
                'average_scale_factor': avg_scale_factor,
                'output_zip_path': str(output_zip_path),
                'output_directory': str(job_output_dir),
                'results': results,
                'summary': {
                    'files_processed': total_files,
                    'files_successful': len(successful_thumbnails),
                    'files_failed': len(failed_thumbnails),
                    'artboard_size': f"{artboard_size[0]}x{artboard_size[1]}",
                    'scale_percentage': f"{scale_percent}%",
                    'average_size_reduction': f"{avg_reduction:.1f}%",
                    'average_scale_factor': f"{avg_scale_factor:.2f}x",
                    'output_zip_size': self.get_file_size(output_zip_path)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'job_id': job_id
            }

# Global processor instance
_image_processor = None

def get_image_processor() -> ImageProcessor:
    """Get or create global image processor instance"""
    global _image_processor
    if _image_processor is None:
        _image_processor = ImageProcessor()
    return _image_processor

def process_bulk_crop(zip_file, job_id: str, progress_callback=None) -> Dict:
    """Convenience function for bulk cropping"""
    processor = get_image_processor()
    return processor.process_bulk_crop(zip_file, job_id, progress_callback)

def process_bulk_resize(zip_file, job_id: str, target_size: Tuple[int, int], progress_callback=None) -> Dict:
    """Convenience function for bulk resizing"""
    processor = get_image_processor()
    return processor.process_bulk_resize(zip_file, job_id, target_size, progress_callback)

def process_bulk_thumbnail(zip_file, job_id: str, artboard_size: Tuple[int, int] = (1080, 1080),
                           scale_percent: float = 90.0, center_horizontal: bool = True,
                           center_vertical: bool = True, progress_callback=None) -> Dict:
    """Convenience function for bulk thumbnail creation"""
    processor = get_image_processor()
    return processor.process_bulk_thumbnail(zip_file, job_id, artboard_size, scale_percent, center_horizontal, center_vertical, progress_callback) 