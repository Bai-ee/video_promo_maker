#!/usr/bin/env python3
"""
Video Generation Page - Direct Interface with Content Feed Integration
"""

import streamlit as st
import sys
import uuid
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "streamlit_crew" / "tools"))

# Import content feed components
try:
    sys.path.append(str(project_root / "components"))
    from content_feed import add_job, update_job, complete_job, fail_job
    CONTENT_FEED_AVAILABLE = True
except ImportError:
    CONTENT_FEED_AVAILABLE = False

try:
    from command_executor import CommandExecutor
    EXECUTOR_AVAILABLE = True
except ImportError:
    EXECUTOR_AVAILABLE = False

# Remove duplicate st.set_page_config - only main app should set this
# st.set_page_config(
#     page_title="Video Generation", 
#     page_icon="🎬",
#     layout="wide"
# )

def main():
    st.title("🎬 Video Generation Studio")
    st.markdown("*Generate professional videos with your hierarchical design system*")
    
    if not EXECUTOR_AVAILABLE:
        st.error("❌ Command executor not available. Please check your setup.")
        return
    
    # Show quick stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Available Layouts", "3", help="balanced, artist-focused, logo-focused")
    
    with col2:
        st.metric("Queue Status", "Ready", help="System ready for new jobs")
    
    with col3:
        st.metric("Content Feed", "Active" if CONTENT_FEED_AVAILABLE else "Disabled")
    
    st.markdown("---")
    
    # Video generation form
    with st.form("video_generation_form"):
        st.subheader("🎯 Video Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            artist_name = st.text_input(
                "🎤 Artist Name", 
                placeholder="e.g., ACIDMAN, John Simmons, Blue J",
                help="Enter the artist name for the video"
            )
            
        with col2:
            layout_type = st.selectbox(
                "🎨 Layout Type",
                ["balanced", "artist-focused", "logo-focused"],
                help="Choose the video layout style"
            )
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            col1, col2 = st.columns(2)
            
            with col1:
                quality_preset = st.selectbox("Quality", ["Standard", "High", "Ultra"])
                include_audio = st.checkbox("Include Audio", value=True)
                
            with col2:
                duration = st.slider("Duration (seconds)", 10, 60, 30)
                add_to_feed = st.checkbox("Track in Content Feed", value=CONTENT_FEED_AVAILABLE)
        
        submitted = st.form_submit_button("🚀 Generate Video", use_container_width=True)
        
        if submitted:
            if not artist_name:
                st.error("❌ Please enter an artist name")
                return
            
            # Generate unique job ID
            job_id = str(uuid.uuid4())[:8]
            
            st.info(f"🎬 **Starting video generation**\n\n**Artist:** {artist_name}\n**Layout:** {layout_type}\n**Job ID:** {job_id}")
            
            # Add to content feed if enabled
            if add_to_feed and CONTENT_FEED_AVAILABLE:
                add_job(job_id, artist_name, layout_type, "video")
                st.success(f"📱 Added to content feed with ID: {job_id}")
            
            # Initialize executor
            executor = CommandExecutor()
            
            # Create progress containers
            progress_container = st.container()
            status_container = st.container()
            
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
                output_text = st.empty()
            
            # Progress callback for real-time updates
            def progress_callback(message):
                with output_text:
                    st.text(message)
                    
                # Update feed progress if available
                if add_to_feed and CONTENT_FEED_AVAILABLE:
                    # Extract progress from message if possible
                    progress = 50  # Default progress
                    if "%" in message:
                        try:
                            progress = int(message.split("%")[0].split()[-1])
                        except:
                            pass
                    update_job(job_id, progress)
            
            try:
                # Update initial progress
                progress_bar.progress(0.1)
                status_text.text("🔄 Initializing video generation...")
                
                if add_to_feed and CONTENT_FEED_AVAILABLE:
                    update_job(job_id, 10)
                
                # Execute video generation
                result = executor.execute_video_generation(
                    artist_name=artist_name,
                    layout_type=layout_type,
                    progress_callback=progress_callback
                )
                
                # Update final progress
                progress_bar.progress(1.0)
                status_text.text("✅ Video generation completed!")
                
                if result.get("success"):
                    st.success("🎉 **Video generation completed successfully!**")
                    
                    # Get output path from result
                    output_path = result.get('output_path', f"output/{artist_name}_{layout_type}.mp4")
                    
                    # Complete job in feed
                    if add_to_feed and CONTENT_FEED_AVAILABLE:
                        complete_job(job_id, output_path)
                    
                    # Show results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.info(f"""
                        **Generation Summary:**
                        • Artist: **{artist_name}**
                        • Layout: {layout_type}
                        • Quality: {quality_preset}
                        • Duration: ~{duration}s
                        • Job ID: `{job_id}`
                        """)
                    
                    with col2:
                        st.info(f"""
                        **Output Details:**
                        • Path: `{output_path}`
                        • Command: `{result.get('command', 'N/A')}`
                        • Execution Time: {result.get('duration', 0):.1f}s
                        • Status: ✅ Success
                        """)
                    
                    # Show detailed execution info
                    with st.expander("📊 Detailed Execution Log"):
                        st.write(f"**Full Command:** `{result.get('command')}`")
                        st.write(f"**Execution Duration:** {result.get('duration', 0):.1f} seconds")
                        st.write(f"**Return Code:** {result.get('return_code')}")
                        
                        if result.get('output'):
                            st.write("**Recent Output Lines:**")
                            output_lines = result['output'][-15:] if len(result['output']) > 15 else result['output']
                            for line in output_lines:
                                st.code(line, language="bash")
                                
                else:
                    st.error("❌ **Video generation failed!**")
                    
                    error_msg = result.get('error', 'Unknown error occurred')
                    
                    # Fail job in feed
                    if add_to_feed and CONTENT_FEED_AVAILABLE:
                        fail_job(job_id, error_msg)
                    
                    st.error(f"**Error:** {error_msg}")
                    
                    with st.expander("🔍 Error Details & Troubleshooting"):
                        if result.get('stderr'):
                            st.write("**Error Output:**")
                            st.code(result['stderr'], language="bash")
                        
                        if result.get('errors'):
                            st.write("**Error Messages:**")
                            for error in result['errors']:
                                st.error(error)
                        
                        # Troubleshooting tips
                        st.markdown("""
                        **Common Solutions:**
                        - Check that the artist name doesn't contain special characters
                        - Ensure npm dependencies are installed (`npm install`)
                        - Verify that FFmpeg is available in your system
                        - Check that all required asset files exist
                        """)
                                
            except Exception as e:
                error_msg = str(e)
                st.error(f"**Unexpected Error:** {error_msg}")
                
                # Fail job in feed
                if add_to_feed and CONTENT_FEED_AVAILABLE:
                    fail_job(job_id, error_msg)
                
                with st.expander("🐛 Debug Information"):
                    st.code(f"Exception: {error_msg}", language="python")
            
            finally:
                # Clean up progress indicators
                progress_bar.empty()
                status_text.empty()
                output_text.empty()
    
    # Show tips and help
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 💡 **Tips for Best Results**
        
        - **Artist Names**: Use clear, simple names without special characters
        - **Balanced Layout**: Good for general promotional videos
        - **Artist-Focused**: Emphasizes the artist prominently
        - **Logo-Focused**: Highlights branding elements
        """)
    
    with col2:
        st.markdown("""
        ### ⚡ **Quick Commands**
        
        - Generate multiple videos for A/B testing
        - Use different layouts to compare styles
        - Check the Content Feed below for progress
        - Monitor system status in the sidebar
        """)

if __name__ == "__main__":
    main() 