#!/usr/bin/env python3
"""
Instagram-style Content Feed Component
Shows generated videos/images with placeholders during job execution
Enhanced with downloadable zip files and bulk processing support
"""

import streamlit as st
import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import glob
from typing import List, Dict, Optional
import base64

class ContentFeed:
    """Instagram-style content feed for generated videos and images"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.feed_data_file = self.project_root / "content_feed_data.json"
        self.load_feed_data()
    
    def load_feed_data(self):
        """Load feed data from JSON file"""
        if self.feed_data_file.exists():
            try:
                with open(self.feed_data_file, 'r') as f:
                    self.feed_data = json.load(f)
            except:
                self.feed_data = {"jobs": [], "completed": []}
        else:
            self.feed_data = {"jobs": [], "completed": []}
    
    def save_feed_data(self):
        """Save feed data to JSON file"""
        try:
            with open(self.feed_data_file, 'w') as f:
                json.dump(self.feed_data, f, indent=2, default=str)
        except Exception as e:
            st.error(f"Error saving feed data: {e}")
    
    def add_running_job(self, job_id: str, artist_name: str, layout_type: str, job_type: str = "video", **kwargs):
        """Add a running job to show placeholder"""
        job_data = {
            "id": job_id,
            "artist_name": artist_name,
            "layout_type": layout_type,
            "job_type": job_type,
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "progress": 0,
            **kwargs  # Additional data like file_count, operation_type, etc.
        }
        
        # Remove any existing job with same ID
        self.feed_data["jobs"] = [j for j in self.feed_data["jobs"] if j["id"] != job_id]
        self.feed_data["jobs"].insert(0, job_data)
        self.save_feed_data()
    
    def update_job_progress(self, job_id: str, progress: int, status: str = "running", status_message: str = ""):
        """Update job progress"""
        for job in self.feed_data["jobs"]:
            if job["id"] == job_id:
                job["progress"] = progress
                job["status"] = status
                job["updated_at"] = datetime.now().isoformat()
                if status_message:
                    job["status_message"] = status_message
                break
        self.save_feed_data()
    
    def complete_job(self, job_id: str, output_path: str, thumbnail_path: Optional[str] = None, **kwargs):
        """Mark job as completed and move to completed list"""
        # Find and remove from jobs
        job_data = None
        for i, job in enumerate(self.feed_data["jobs"]):
            if job["id"] == job_id:
                job_data = self.feed_data["jobs"].pop(i)
                break
        
        if job_data:
            job_data["status"] = "completed"
            job_data["completed_at"] = datetime.now().isoformat()
            job_data["output_path"] = output_path
            job_data["thumbnail_path"] = thumbnail_path
            job_data["progress"] = 100
            
            # Add any additional completion data
            job_data.update(kwargs)
            
            # Add to completed list at the beginning
            self.feed_data["completed"].insert(0, job_data)
            
            # Keep only last 50 completed items
            self.feed_data["completed"] = self.feed_data["completed"][:50]
            
            self.save_feed_data()
    
    def fail_job(self, job_id: str, error_message: str):
        """Mark job as failed"""
        for job in self.feed_data["jobs"]:
            if job["id"] == job_id:
                job["status"] = "failed"
                job["error"] = error_message
                job["failed_at"] = datetime.now().isoformat()
                break
        self.save_feed_data()
    
    def scan_for_existing_content(self):
        """Scan output directories for existing content"""
        content_paths = []
        
        # Scan common output directories
        output_dirs = [
            self.project_root / "output" / "artist-promo",
            self.project_root / "output" / "processed_images",
            self.project_root / "outputs",
            self.project_root,  # Root level videos
        ]
        
        for output_dir in output_dirs:
            if output_dir.exists():
                # Look for video files
                for ext in ["*.mp4", "*.mov", "*.avi", "*.webm"]:
                    content_paths.extend(glob.glob(str(output_dir / "**" / ext), recursive=True))
                
                # Look for image files
                for ext in ["*.png", "*.jpg", "*.jpeg", "*.gif"]:
                    content_paths.extend(glob.glob(str(output_dir / "**" / ext), recursive=True))
                
                # Look for zip files
                for ext in ["*.zip"]:
                    content_paths.extend(glob.glob(str(output_dir / "**" / ext), recursive=True))
        
        # Add root level videos that match naming pattern
        root_videos = glob.glob(str(self.project_root / "*_enhanced_*.mp4"))
        content_paths.extend(root_videos)
        
        return content_paths
    
    def get_file_thumbnail(self, file_path: str) -> Optional[str]:
        """Generate or get thumbnail for file"""
        file_path = Path(file_path)
        
        if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
            # Image file - use as thumbnail
            try:
                with open(file_path, 'rb') as f:
                    return base64.b64encode(f.read()).decode()
            except:
                return None
        
        elif file_path.suffix.lower() in ['.mp4', '.mov', '.avi', '.webm']:
            # Video file - could generate thumbnail but for now return None
            return None
        
        return None
    
    def create_download_button(self, file_path: str, label: str, mime_type: str = "application/octet-stream") -> bool:
        """Create a download button for a file"""
        try:
            file_path = Path(file_path)
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                return st.download_button(
                    label=label,
                    data=file_data,
                    file_name=file_path.name,
                    mime=mime_type,
                    use_container_width=True
                )
            else:
                st.error(f"File not found: {file_path}")
                return False
        except Exception as e:
            st.error(f"Error creating download button: {e}")
            return False
    
    def render_feed(self, max_items: int = 12):
        """Render the Instagram-style content feed"""
        st.markdown("---")
        st.subheader("📱 Content Feed")
        
        # Refresh button
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("🔄 Refresh", key="feed_refresh"):
                self.load_feed_data()
                st.rerun()
        
        with col2:
            show_completed = st.checkbox("Show All", value=True, key="show_completed")
        
        # Combine running jobs and completed content
        all_items = []
        
        # Add running jobs (these show as placeholders)
        for job in self.feed_data.get("jobs", []):
            all_items.append({
                "type": "job",
                "data": job,
                "timestamp": job.get("started_at", "")
            })
        
        # Add completed content if enabled
        if show_completed:
            for item in self.feed_data.get("completed", []):
                all_items.append({
                    "type": "completed",
                    "data": item,
                    "timestamp": item.get("completed_at", "")
                })
            
            # Add existing content from file system
            existing_content = self.scan_for_existing_content()
            for file_path in existing_content[:20]:  # Limit to prevent too many
                file_info = os.stat(file_path)
                all_items.append({
                    "type": "file",
                    "data": {
                        "path": file_path,
                        "name": os.path.basename(file_path),
                        "size": file_info.st_size,
                        "modified": datetime.fromtimestamp(file_info.st_mtime).isoformat()
                    },
                    "timestamp": datetime.fromtimestamp(file_info.st_mtime).isoformat()
                })
        
        # Sort by timestamp (newest first)
        all_items.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Limit items
        all_items = all_items[:max_items]
        
        if not all_items:
            st.info("🎬 No content yet. Generate some videos or process some images to see them here!")
            return
        
        # Create grid layout (3 columns for Instagram-style)
        cols_per_row = 3
        rows_needed = (len(all_items) + cols_per_row - 1) // cols_per_row
        
        for row in range(rows_needed):
            cols = st.columns(cols_per_row)
            
            for col_idx in range(cols_per_row):
                item_idx = row * cols_per_row + col_idx
                
                if item_idx < len(all_items):
                    item = all_items[item_idx]
                    
                    with cols[col_idx]:
                        self.render_feed_item(item)
    
    def render_feed_item(self, item: Dict):
        """Render a single feed item"""
        item_type = item["type"]
        data = item["data"]
        
        # Create container for the item
        container = st.container()
        
        with container:
            if item_type == "job":
                # Running job - show placeholder
                self.render_job_placeholder(data)
                
            elif item_type == "completed":
                # Completed job
                self.render_completed_item(data)
                
            elif item_type == "file":
                # Existing file
                self.render_file_item(data)
    
    def render_job_placeholder(self, job_data: Dict):
        """Render placeholder for running job"""
        status = job_data.get("status", "running")
        progress = job_data.get("progress", 0)
        job_type = job_data.get("job_type", "video")
        
        # Different icons for different job types
        if job_type == "image_processing":
            icon = "🖼️"
            type_label = "Image Processing"
        elif job_type == "bulk_crop":
            icon = "✂️"
            type_label = "Bulk Crop"
        elif job_type == "bulk_resize":
            icon = "🔄"
            type_label = "Bulk Resize"
        elif job_type == "bulk_thumbnail":
            icon = "🎨"
            type_label = "Thumbnail Creation"
        elif job_type == "deep_research":
            icon = "🔬"
            type_label = "Deep Research"
        else:
            icon = "🎬"
            type_label = "Video Generation"
        
        # Create placeholder image
        placeholder_html = f"""
        <div style="
            width: 100%;
            height: 200px;
            background: linear-gradient(45deg, #f0f0f0, #e0e0e0);
            border-radius: 10px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            border: 2px dashed #ccc;
            margin-bottom: 10px;
            position: relative;
        ">
            <div style="font-size: 24px; margin-bottom: 10px;">
                {icon}
            </div>
            <div style="font-size: 14px; color: #666; text-align: center;">
                <strong>{job_data.get('artist_name', 'Processing')}</strong><br>
                {type_label}<br>
                {'⏳ Processing...' if status == 'running' else ('❌ Failed' if status == 'failed' else '✅ Done')}
            </div>
        </div>
        """
        
        st.markdown(placeholder_html, unsafe_allow_html=True)
        
        if status == "running":
            st.progress(progress / 100.0)
            status_msg = job_data.get("status_message", f"Progress: {progress}%")
            st.caption(status_msg)
            
            # Show additional info for bulk jobs
            if job_type in ["bulk_crop", "bulk_resize", "image_processing"]:
                file_count = job_data.get("file_count", "Unknown")
                st.caption(f"📁 Files: {file_count}")
                
        elif status == "failed":
            st.error(f"❌ Failed: {job_data.get('error', 'Unknown error')}")
        
        # Show timestamp
        started_time = job_data.get("started_at", "")
        if started_time:
            try:
                dt = datetime.fromisoformat(started_time.replace('Z', '+00:00'))
                time_ago = self.time_ago(dt)
                st.caption(f"⏰ {time_ago}")
            except:
                pass
    
    def render_completed_item(self, item_data: Dict):
        """Render completed job item"""
        output_path = item_data.get("output_path", "")
        thumbnail_path = item_data.get("thumbnail_path")
        job_type = item_data.get("job_type", "video")
        
        # Try to show thumbnail or file info
        if thumbnail_path and os.path.exists(thumbnail_path):
            st.image(thumbnail_path, use_container_width=True)
        elif output_path and os.path.exists(output_path):
            file_ext = Path(output_path).suffix.lower()
            if file_ext in ['.png', '.jpg', '.jpeg']:
                st.image(output_path, use_container_width=True)
            elif file_ext in ['.mp4', '.mov', '.avi', '.webm']:
                st.video(output_path)
            elif file_ext == '.zip':
                # Show zip file placeholder with download option
                st.markdown("""
                <div style="
                    width: 100%;
                    height: 150px;
                    background: linear-gradient(45deg, #e3f2fd, #bbdefb);
                    border-radius: 10px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    border: 2px solid #2196f3;
                    margin-bottom: 10px;
                ">
                    <div style="font-size: 48px; margin-bottom: 10px;">📦</div>
                    <div style="font-size: 14px; color: #1976d2; text-align: center;">
                        <strong>ZIP Archive</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Create download button
                self.create_download_button(
                    output_path, 
                    f"📥 Download {Path(output_path).name}",
                    "application/zip"
                )
            else:
                # Show file info
                st.info(f"📁 {os.path.basename(output_path)}")
        else:
            # Show placeholder
            job_name = item_data.get('artist_name', 'Unknown')
            layout = item_data.get('layout_type', 'unknown')
            st.info(f"✅ {job_name} - {layout}")
        
        # Show metadata
        st.caption(f"🎯 {item_data.get('artist_name', 'Unknown')}")
        
        # Show specific metadata based on job type
        if job_type in ["bulk_crop", "bulk_resize", "bulk_thumbnail", "image_processing"]:
            summary = item_data.get("summary", {})
            files_processed = summary.get("files_processed", "Unknown")
            files_successful = summary.get("files_successful", "Unknown")
            st.caption(f"📁 Processed: {files_successful}/{files_processed} files")
            
            if job_type == "bulk_crop":
                avg_reduction = summary.get("average_size_reduction", "0%")
                st.caption(f"📏 Avg reduction: {avg_reduction}")
            elif job_type == "bulk_resize":
                target_size = summary.get("target_size", "Unknown")
                st.caption(f"📐 Target size: {target_size}")
            elif job_type == "bulk_thumbnail":
                artboard_size = summary.get("artboard_size", "Unknown")
                scale_percent = summary.get("scale_percent", "Unknown")
                st.caption(f"🎨 Artboard: {artboard_size}, Scale: {scale_percent}%")
        
        elif job_type == "deep_research":
            summary = item_data.get("summary", {})
            sources_analyzed = summary.get("sources_analyzed", "Unknown")
            insights_generated = summary.get("insights_generated", "Unknown")
            research_focus = summary.get("research_focus", "general").replace("_", " ").title()
            recommendations_count = summary.get("recommendations_count", 0)
            
            st.caption(f"🔍 Sources: {sources_analyzed} | 💡 Insights: {insights_generated}")
            st.caption(f"🎯 Focus: {research_focus} | 📋 Recommendations: {recommendations_count}")
        
        else:
            # Video generation metadata
            artist_name = item_data.get("metadata", {}).get("artist_name", "Unknown Artist")
            layout_type = item_data.get("metadata", {}).get("layout_type", "Unknown Layout")
            st.caption(f"🎤 Artist: {artist_name}")
            st.caption(f"🎨 Layout: {layout_type}")
        
        # Show timestamp
        completed_time = item_data.get("completed_at", "")
        if completed_time:
            try:
                dt = datetime.fromisoformat(completed_time.replace('Z', '+00:00'))
                time_ago = self.time_ago(dt)
                st.caption(f"⏰ {time_ago}")
            except:
                pass
    
    def render_file_item(self, file_data: Dict):
        """Render existing file item"""
        file_path = file_data["path"]
        file_name = file_data["name"]
        
        # Try to show the file
        file_ext = Path(file_path).suffix.lower()
        try:
            if file_ext in ['.png', '.jpg', '.jpeg']:
                st.image(file_path, use_container_width=True)
            elif file_ext in ['.mp4', '.mov', '.avi', '.webm']:
                st.video(file_path)
            elif file_ext == '.zip':
                # Show zip file with download option
                st.markdown("""
                <div style="
                    width: 100%;
                    height: 150px;
                    background: linear-gradient(45deg, #fff3e0, #ffe0b2);
                    border-radius: 10px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    border: 2px solid #ff9800;
                    margin-bottom: 10px;
                ">
                    <div style="font-size: 48px; margin-bottom: 10px;">📦</div>
                    <div style="font-size: 14px; color: #f57c00; text-align: center;">
                        <strong>ZIP File</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Create download button
                self.create_download_button(
                    file_path, 
                    f"📥 Download {file_name}",
                    "application/zip"
                )
            else:
                st.info(f"📁 {file_name}")
        except:
            st.warning(f"⚠️ {file_name}")
        
        # Show file info
        st.caption(f"📁 {file_name}")
        
        # Format file size
        size_mb = file_data["size"] / (1024 * 1024)
        st.caption(f"💾 {size_mb:.1f} MB")
        
        # Show timestamp
        modified_time = file_data.get("modified", "")
        if modified_time:
            try:
                dt = datetime.fromisoformat(modified_time)
                time_ago = self.time_ago(dt)
                st.caption(f"⏰ {time_ago}")
            except:
                pass
    
    def time_ago(self, dt: datetime) -> str:
        """Calculate time ago string"""
        now = datetime.now()
        if dt.tzinfo:
            # Make now timezone aware
            import pytz
            now = now.replace(tzinfo=pytz.UTC)
        
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"

# Global feed instance
_content_feed = None

def get_content_feed() -> ContentFeed:
    """Get or create global content feed instance"""
    global _content_feed
    if _content_feed is None:
        _content_feed = ContentFeed()
    return _content_feed

def render_content_feed(max_items: int = 12):
    """Convenience function to render the content feed"""
    feed = get_content_feed()
    feed.render_feed(max_items)

def add_job(job_id: str, agent_name: str = "AI Agent", task_type: str = "general", job_type: str = "processing", **kwargs):
    """
    Flexible function to add any type of agent job to the content feed
    
    Args:
        job_id: Unique identifier for the job
        agent_name: Name of the agent handling this task (replaces artist_name)
        task_type: Type of task being performed (replaces layout_type) 
        job_type: Category of job (video, image_processing, research, etc.)
        **kwargs: Any additional job-specific parameters
    """
    feed = get_content_feed()
    # Map new parameters to old for backward compatibility
    feed.add_running_job(job_id, agent_name, task_type, job_type, **kwargs)

def update_job(job_id: str, progress: int, status: str = "running", status_message: str = ""):
    """Convenience function to update job progress"""
    feed = get_content_feed()
    feed.update_job_progress(job_id, progress, status, status_message)

def complete_job(job_id: str, output_path: str, thumbnail_path: Optional[str] = None, **kwargs):
    """Convenience function to complete a job"""
    feed = get_content_feed()
    feed.complete_job(job_id, output_path, thumbnail_path, **kwargs)

def fail_job(job_id: str, error_message: str):
    """Convenience function to fail a job"""
    feed = get_content_feed()
    feed.fail_job(job_id, error_message) 