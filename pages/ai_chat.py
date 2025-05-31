import streamlit as st
import sys
import os
import logging
import time
from datetime import datetime
import json
import uuid
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import content feed components
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "components"))
    from content_feed import render_content_feed, add_job, update_job, complete_job, fail_job
    CONTENT_FEED_AVAILABLE = True
except ImportError as e:
    CONTENT_FEED_AVAILABLE = False
    print(f"Content feed not available: {e}")

# Import image processor
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "components"))
    from image_processor import get_image_processor, process_bulk_crop, process_bulk_resize, process_bulk_thumbnail
    IMAGE_PROCESSOR_AVAILABLE = True
except ImportError as e:
    IMAGE_PROCESSOR_AVAILABLE = False
    print(f"Image processor not available: {e}")

# Import deep research components
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "components"))
    from deep_research import conduct_dynamic_research
    DEEP_RESEARCH_AVAILABLE = True
except ImportError as e:
    DEEP_RESEARCH_AVAILABLE = False
    print(f"Deep Research not available: {e}")

# Configure debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def log_debug(message):
    """Debug logging function"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    logger.debug(f"[{timestamp}] {message}")

# Import CommandExecutor (this works without CrewAI)
EXECUTOR_AVAILABLE = False
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "streamlit_crew", "tools"))
    from command_executor import CommandExecutor
    EXECUTOR_AVAILABLE = True
    log_debug("✅ CommandExecutor imported successfully")
except ImportError as e:
    log_debug(f"❌ CommandExecutor import failed: {e}")
    EXECUTOR_AVAILABLE = False

def initialize_session_state():
    """Initialize session state variables for chat"""
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    if "crew_active" not in st.session_state:
        st.session_state.crew_active = False
        
    if "current_task" not in st.session_state:
        st.session_state.current_task = None
        
    if "execution_mode" not in st.session_state:
        st.session_state.execution_mode = "real"  # "real" or "simulation"
        
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False
        
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None

def parse_user_intent(user_input, uploaded_file=None):
    """Parse user input to detect intent and extract parameters"""
    log_debug(f"🔍 Starting intent parsing...")
    log_debug(f"🔍 Parsing user input: '{user_input}'")
    log_debug(f"📁 Uploaded file: {uploaded_file.name if uploaded_file else 'None'}")
    
    # Convert to lowercase for analysis
    lower_input = user_input.lower()
    log_debug(f"📝 Processing lowercase input: '{lower_input}'")
    
    # Video generation keywords
    video_keywords = ['create', 'generate', 'make', 'build', 'produce', 'video', 'render']
    layout_keywords = ['balanced', 'artist-focused', 'logo-focused', 'artist focused', 'logo focused']
    
    # Image processing keywords - ENHANCED
    image_keywords = ['crop', 'resize', 'process', 'edit', 'thumbnail', 'artboard']
    crop_keywords = ['crop', 'trim', 'remove empty', 'viewable pixel', 'transparent', 'padding']
    resize_keywords = ['resize', 'scale', 'size', 'dimension']
    thumbnail_keywords = ['thumbnail', 'artboard', 'frame', 'canvas', 'center']
    
    # Bulk processing keywords
    bulk_edit_keywords = ['bulk', 'batch', 'all images', 'multiple', 'zip', 'folder']
    artboard_keywords = ['artboard', 'canvas', 'frame', 'background']
    scaling_keywords = ['scale', 'scaling', 'percent', '%']
    centering_keywords = ['center', 'centered', 'middle', 'align']
    
    # Deep research keywords - FIXED
    research_keywords = ['research', 'analyze', 'investigate', 'study', 'examine', 'explore', 'deep dive']
    festival_keywords = ['festival', 'event', 'concert', 'show', 'organizer', 'promoter']
    market_keywords = ['market', 'industry', 'competitor', 'trends', 'analysis']
    restaurant_keywords = ['restaurant', 'dining', 'food', 'eatery', 'cuisine', 'chef']
    
    log_debug(f"🔍 Checking for research intent...")
    
    # Check for deep research intent first - FIXED to detect ANY research query
    has_research_keywords = any(keyword in lower_input for keyword in research_keywords)
    has_festival_keywords = any(keyword in lower_input for keyword in festival_keywords)
    has_market_keywords = any(keyword in lower_input for keyword in market_keywords)
    has_restaurant_keywords = any(keyword in lower_input for keyword in restaurant_keywords)
    
    # ANY research keyword should trigger research intent
    if has_research_keywords:
        log_debug("✅ INTENT: Deep Research Detected!")
        
        # Extract research parameters
        research_params = {
            'query': user_input,
            'depth': 3,  # Default depth
            'breadth': 5,  # Default breadth
            'focus_area': 'general'
        }
        
        # Detect specific research focus areas
        if has_festival_keywords and 'chicago' in lower_input:
            research_params['focus_area'] = 'chicago_festivals'
            log_debug("🎵 Detected Chicago festival research focus")
        elif has_restaurant_keywords:
            research_params['focus_area'] = 'restaurants'
            log_debug("🍽️ Detected restaurant research focus")
        elif has_market_keywords:
            research_params['focus_area'] = 'market_analysis'
            log_debug("📊 Detected market analysis focus")
        elif 'competitor' in lower_input:
            research_params['focus_area'] = 'competitor_analysis'
            log_debug("🏛️ Detected competitor analysis focus")
        
        # Extract depth and breadth if specified
        import re
        depth_match = re.search(r'depth[:\s]*(\d+)', lower_input)
        if depth_match:
            research_params['depth'] = int(depth_match.group(1))
            
        breadth_match = re.search(r'breadth[:\s]*(\d+)', lower_input)
        if breadth_match:
            research_params['breadth'] = int(breadth_match.group(1))
        
        intent_data = {
            'intent': 'deep_research',
            'parameters': research_params,
            'confidence': 0.9
        }
        log_debug(f"🎯 Research intent data: {intent_data}")
        return intent_data
    
    # Check for bulk edit commands FIRST (higher priority)
    has_bulk_edit = any(keyword in lower_input for keyword in bulk_edit_keywords)
    has_image_keywords = any(keyword in lower_input for keyword in image_keywords)
    has_crop_keywords = any(keyword in lower_input for keyword in crop_keywords)
    has_resize_keywords = any(keyword in lower_input for keyword in resize_keywords)
    has_thumbnail_keywords = any(keyword in lower_input for keyword in thumbnail_keywords)
    has_artboard_keywords = any(keyword in lower_input for keyword in artboard_keywords)
    has_scaling_keywords = any(keyword in lower_input for keyword in scaling_keywords)
    has_centering_keywords = any(keyword in lower_input for keyword in centering_keywords)
    
    # ENHANCED: Check for bulk image processing with uploaded file OR bulk edit keywords
    if (uploaded_file and (has_image_keywords or has_crop_keywords or has_resize_keywords or has_thumbnail_keywords)) or (has_bulk_edit and uploaded_file):
        log_debug("✅ INTENT: Bulk Image Processing Detected!")
        
        # Determine operation type - Enhanced to include thumbnails
        if has_thumbnail_keywords or has_artboard_keywords or (has_crop_keywords and has_artboard_keywords):
            operation_type = "thumbnail"
            log_debug("🔍 Detected thumbnail/artboard operation")
            
            # Extract artboard size
            import re
            artboard_size = (1080, 1080)  # Default
            size_patterns = [
                r'(\d+)x(\d+)',
                r'(\d+)\s*by\s*(\d+)',
                r'(\d+)\s*×\s*(\d+)',
                r'artboard.*?(\d+).*?(\d+)',
                r'canvas.*?(\d+).*?(\d+)',
                r'frame.*?(\d+).*?(\d+)'
            ]
            
            for pattern in size_patterns:
                size_match = re.search(pattern, lower_input)
                if size_match:
                    groups = size_match.groups()
                    sizes = [g for g in groups if g is not None]
                    if len(sizes) >= 2:
                        artboard_size = (int(sizes[0]), int(sizes[1]))
                        log_debug(f"📐 Extracted artboard size: {artboard_size}")
                        break
            
            # Extract scaling percentage
            scale_percent = 90.0  # Default
            scale_patterns = [
                r'(\d+)%',
                r'(\d+)\s*percent',
                r'fill\s*(\d+)%',
                r'scale.*?(\d+)%',
                r'(\d+)%.*?fill'
            ]
            
            for pattern in scale_patterns:
                scale_match = re.search(pattern, lower_input)
                if scale_match:
                    scale_percent = float(scale_match.group(1))
                    log_debug(f"📊 Extracted scale percentage: {scale_percent}%")
                    break
            
            # Extract centering options
            center_horizontal = True  # Default
            center_vertical = True    # Default
            
            if 'horizontal' in lower_input and 'center' in lower_input:
                center_horizontal = True
            if 'vertical' in lower_input and 'center' in lower_input:
                center_vertical = True
                
            log_debug(f"🎯 Centering: H={center_horizontal}, V={center_vertical}")
            
        elif has_crop_keywords or 'crop' in lower_input:
            operation_type = "crop"
            log_debug("🔍 Detected crop operation")
        elif has_resize_keywords or 'resize' in lower_input:
            operation_type = "resize"
            log_debug("🔍 Detected resize operation")
            
            # Try to extract target size
            import re
            size_pattern = r'(\d+)x(\d+)|(\d+)\s*by\s*(\d+)|(\d+)\s*×\s*(\d+)'
            size_match = re.search(size_pattern, lower_input)
            target_size = None
            
            if size_match:
                groups = size_match.groups()
                # Extract non-None groups
                sizes = [g for g in groups if g is not None]
                if len(sizes) >= 2:
                    target_size = (int(sizes[0]), int(sizes[1]))
                    log_debug(f"📐 Extracted target size: {target_size}")
            
            if not target_size:
                # Default size if not specified
                target_size = (1024, 1024)
                log_debug(f"📐 Using default target size: {target_size}")
        else:
            operation_type = "crop"  # Default to crop for bulk edit
            log_debug("🔍 Defaulting to crop operation for bulk edit")
        
        # Build parameters based on operation type
        parameters = {
            'operation_type': operation_type,
            'uploaded_file': uploaded_file
        }
        
        if operation_type == "thumbnail":
            parameters.update({
                'artboard_size': artboard_size,
                'scale_percent': scale_percent,
                'center_horizontal': center_horizontal,
                'center_vertical': center_vertical
            })
        elif operation_type == "resize":
            parameters['target_size'] = target_size
        
        intent_data = {
            'intent': 'bulk_image_processing',
            'parameters': parameters,
            'confidence': 0.95
        }
        
        log_debug("🎯 Final bulk image processing intent:")
        return intent_data
    
    # Check if this is a video generation request (ONLY if not bulk image processing)
    has_video_keywords = any(keyword in lower_input for keyword in video_keywords)
    log_debug(f"🎬 Video keywords detected: {has_video_keywords}")
    
    if has_video_keywords and not has_bulk_edit:  # Exclude bulk edit from video generation
        log_debug("✅ INTENT: Video Generation Detected!")
        
        # Extract artist name (look for patterns like "for Artist Name")
        artist_name = None
        if ' for ' in lower_input:
            parts = lower_input.split(' for ')
            if len(parts) >= 2:
                artist_part = parts[1].strip()
                
                # Remove layout type descriptions from artist name
                layout_stopwords = ['that is', 'with', 'using', 'in', 'artist focused', 'logo focused', 'balanced']
                for stopword in layout_stopwords:
                    if stopword in artist_part:
                        artist_part = artist_part.split(stopword)[0].strip()
                        break
                
                # Clean up the artist name - just take first few words that look like a name
                artist_words = artist_part.split()
                if len(artist_words) >= 2:
                    # Take first 2-3 words as likely to be the artist name
                    artist_name = ' '.join(artist_words[:3])
                else:
                    artist_name = artist_part
                    
                log_debug(f"🎤 Artist extracted (pattern 'for'): '{artist_name}'")
        
        if artist_name:
            log_debug(f"✅ Final artist name: '{artist_name}'")
        else:
            log_debug("❌ No artist name found")
            artist_name = "Unknown Artist"
        
        # Extract layout type
        layout_type = "balanced"  # default
        for layout in layout_keywords:
            if layout in lower_input:
                if 'artist' in layout:
                    layout_type = "artist-focused"
                elif 'logo' in layout:
                    layout_type = "logo-focused"
                else:
                    layout_type = layout
                break
        
        log_debug(f"🎨 Layout type determined: '{layout_type}'")
        
        intent_data = {
            'intent': 'video_generation',
            'parameters': {
                'artist_name': artist_name,
                'layout_type': layout_type
            },
            'confidence': 0.9
        }
        
        log_debug("🎯 Final video generation intent:")
        
    else:
        log_debug("ℹ️ INTENT: General chat (no specific intent detected)")
        intent_data = {
            'intent': 'general_chat',
            'parameters': {},
            'confidence': 0.5
        }
    
    log_debug(f"🎯 Final intent data: {intent_data}")
    return intent_data

def handle_bulk_image_processing(operation_type, uploaded_file, target_size=None, 
                                artboard_size=(1080, 1080), scale_percent=90.0, 
                                center_horizontal=True, center_vertical=True, mode="real"):
    """Handle bulk image processing operations including thumbnail creation"""
    log_debug(f"🖼️ Routing to bulk image processing handler...")
    log_debug(f"🔧 Operation: {operation_type}")
    log_debug(f"📁 File: {uploaded_file.name}")
    log_debug(f"📐 Target size: {target_size}")
    log_debug(f"🖼️ Artboard size: {artboard_size}")
    log_debug(f"📊 Scale percent: {scale_percent}")
    log_debug(f"🎯 Centering: H={center_horizontal}, V={center_vertical}")
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())[:8]
    
    # Check file type
    if not uploaded_file.name.lower().endswith('.zip'):
        st.error("❌ Please upload a ZIP file containing PNG images")
        return {'success': False, 'error': 'Invalid file type - ZIP required'}
    
    # Add job to content feed immediately
    if CONTENT_FEED_AVAILABLE:
        add_job(
            job_id, 
            agent_name="Image Processing Agent",
            task_type=f"bulk_{operation_type}",
            job_type="image_processing",
            operation_type=operation_type,
            file_name=uploaded_file.name,
            artboard_size=f"{artboard_size[0]}x{artboard_size[1]}" if operation_type == "thumbnail" else None,
            scale_percent=f"{scale_percent}%" if operation_type == "thumbnail" else None
        )
        log_debug(f"📱 Added job {job_id} to content feed")
    
    if mode == "simulation":
        log_debug("🔵 Using SIMULATION mode")
        
        # Simulation with visible progress
        with st.status(f"🖼️ Simulating bulk {operation_type}...", expanded=True) as status:
            st.write("📦 Extracting ZIP file...")
            if CONTENT_FEED_AVAILABLE:
                update_job(job_id, 20, status_message="Extracting ZIP file...")
            time.sleep(1)
            
            st.write("🔍 Finding PNG files...")
            if CONTENT_FEED_AVAILABLE:
                update_job(job_id, 40, status_message="Finding PNG files...")
            time.sleep(1)
            
            st.write(f"✂️ {operation_type.title()}ping images...")
            if CONTENT_FEED_AVAILABLE:
                update_job(job_id, 80, status_message=f"{operation_type.title()}ping images...")
            time.sleep(2)
            
            st.write("📦 Creating output ZIP...")
            if CONTENT_FEED_AVAILABLE:
                update_job(job_id, 95, status_message="Creating output ZIP...")
            time.sleep(1)
            
            st.write("✅ Processing completed!")
            status.update(label=f"✅ Bulk {operation_type} simulation completed!", state="complete")
            
            # Complete the job in feed
            if CONTENT_FEED_AVAILABLE:
                output_path = f"output/processed_images/{job_id}_{operation_type}ped.zip"
                complete_job(job_id, output_path, summary={
                    'files_processed': 25,
                    'files_successful': 25,
                    'files_failed': 0
                })
        
        # Add final result to chat
        st.success(f"✅ **Simulation completed successfully!**\n\nBulk {operation_type} would process the uploaded images.")
        
        return {
            'success': True,
            'message': f'Simulated bulk {operation_type} processing',
            'mode': 'simulation',
            'job_id': job_id
        }
    
    else:
        log_debug("🔴 Using REAL EXECUTION mode")
        
        if not IMAGE_PROCESSOR_AVAILABLE:
            st.error("❌ **Image Processor not available** - Cannot execute real image processing")
            if CONTENT_FEED_AVAILABLE:
                fail_job(job_id, "Image processor not available")
            return {
                'success': False,
                'message': 'Image processor not available for real execution',
                'mode': 'real',
                'job_id': job_id
            }
        
        # Real execution with comprehensive status tracking
        processor = get_image_processor()
        
        # Start the status display that will show all steps
        with st.status(f"🖼️ Starting bulk {operation_type} workflow...", expanded=True) as status:
            
            # Progress callback for real-time updates
            def progress_callback(message, progress):
                st.write(f"📊 **Progress {progress}%**: {message}")
                if CONTENT_FEED_AVAILABLE:
                    update_job(job_id, progress, status_message=message)
            
            try:
                # Execute the image processing
                if operation_type == "crop":
                    result = process_bulk_crop(uploaded_file, job_id, progress_callback)
                elif operation_type == "resize":
                    result = process_bulk_resize(uploaded_file, job_id, target_size, progress_callback)
                elif operation_type == "thumbnail":
                    result = process_bulk_thumbnail(uploaded_file, job_id, artboard_size, scale_percent, 
                                                  center_horizontal, center_vertical, progress_callback)
                else:
                    raise ValueError(f"Unknown operation type: {operation_type}")
                
                if result['success']:
                    # Success
                    st.write("🎉 **Processing completed successfully!**")
                    
                    summary = result.get('summary', {})
                    st.write(f"📁 Processed: {summary.get('files_successful', 0)}/{summary.get('files_processed', 0)} files")
                    st.write(f"💾 Output size: {summary.get('output_zip_size', 'Unknown')}")
                    
                    if operation_type == "crop":
                        avg_reduction = summary.get('average_size_reduction', '0%')
                        st.write(f"📏 Average size reduction: {avg_reduction}")
                    elif operation_type == "resize":
                        target_size_str = summary.get('target_size', 'Unknown')
                        st.write(f"📐 Target size: {target_size_str}")
                    elif operation_type == "thumbnail":
                        artboard_size_str = summary.get('artboard_size', 'Unknown')
                        scale_percentage = summary.get('scale_percentage', 'Unknown')
                        avg_scale_factor = summary.get('average_scale_factor', 'Unknown')
                        avg_reduction = summary.get('average_size_reduction', '0%')
                        st.write(f"🖼️ Artboard size: {artboard_size_str}")
                        st.write(f"📊 Scale percentage: {scale_percentage}")
                        st.write(f"🔍 Average scale factor: {avg_scale_factor}")
                        st.write(f"📏 Average size reduction: {avg_reduction}")
                    
                    status.update(label=f"✅ Bulk {operation_type} completed successfully!", state="complete")
                    
                    # Complete job in feed with actual output path
                    if CONTENT_FEED_AVAILABLE:
                        complete_job(job_id, result['output_zip_path'], summary=summary)
                    
                    # Show final success message
                    st.success(f"""
                    🎉 **Bulk {operation_type.title()} Completed Successfully!**
                    
                    **Results:**
                    • Operation: {operation_type.title()}
                    • Files processed: {summary.get('files_processed', 0)}
                    • Files successful: {summary.get('files_successful', 0)}
                    • Output ZIP: Available in Content Feed below
                    """)
                    
                else:
                    # Show error details
                    st.write(f"❌ **Bulk {operation_type} failed**")
                    error_msg = result.get('error', 'Unknown error')
                    st.write(f"🔍 Error: {error_msg}")
                    
                    # Fail job in feed
                    if CONTENT_FEED_AVAILABLE:
                        fail_job(job_id, error_msg)
                    
                    status.update(label=f"❌ Bulk {operation_type} failed", state="error")
                    
                    # Show error message
                    st.error(f"""
                    ❌ **Bulk {operation_type.title()} Failed**
                    
                    **Error Details:**
                    • Operation: {operation_type}
                    • Error: {error_msg}
                    • Job ID: {job_id}
                    """)
                
                return result
                
            except Exception as e:
                st.write(f"❌ **Unexpected error occurred**")
                error_msg = str(e)
                st.write(f"🔍 Error: {error_msg}")
                
                # Fail job in feed
                if CONTENT_FEED_AVAILABLE:
                    fail_job(job_id, error_msg)
                
                status.update(label=f"❌ Unexpected error during bulk {operation_type}", state="error")
                
                st.error(f"""
                ❌ **Unexpected Error**
                
                **Details:**
                • Operation: {operation_type}
                • Error: {error_msg}
                • Job ID: {job_id}
                """)
                
                return {
                    'success': False,
                    'error': error_msg,
                    'mode': 'real',
                    'job_id': job_id
                }

def handle_video_generation(artist_name, layout_type, mode="real"):
    """Handle video generation with real-time status updates and feed integration"""
    log_debug(f"🎬 Routing to video generation handler...")
    log_debug(f"🎤 Artist: {artist_name}")
    log_debug(f"🎨 Layout: {layout_type}")
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())[:8]
    
    # Add job to content feed immediately
    if CONTENT_FEED_AVAILABLE:
        add_job(job_id, agent_name=artist_name, task_type=layout_type, job_type="video")
        log_debug(f"📱 Added job {job_id} to content feed")
    
    if mode == "simulation":
        log_debug("🔵 Using SIMULATION mode")
        
        # Simulation with visible progress
        with st.status("🎬 Simulating video generation...", expanded=True) as status:
            st.write("📝 Parsing parameters...")
            if CONTENT_FEED_AVAILABLE:
                update_job(job_id, 20)
            time.sleep(1)
            
            st.write("🎨 Setting up video composition...")
            if CONTENT_FEED_AVAILABLE:
                update_job(job_id, 50)
            time.sleep(1)
            
            st.write(f"🎬 Generating video for {artist_name}...")
            if CONTENT_FEED_AVAILABLE:
                update_job(job_id, 80)
            time.sleep(2)
            
            st.write("✅ Video generation completed!")
            status.update(label="✅ Video generation simulation completed!", state="complete")
            
            # Complete the job in feed
            if CONTENT_FEED_AVAILABLE:
                # Simulate output path
                output_path = f"output/simulated_{artist_name.replace(' ', '_')}_{layout_type}.mp4"
                complete_job(job_id, output_path)
        
        # Add final result to chat
        st.success(f"✅ **Simulation completed successfully!**\n\nA {layout_type} video for **{artist_name}** would be generated.")
        
        return {
            'success': True,
            'message': f'Simulated video generation for {artist_name} with {layout_type} layout',
            'mode': 'simulation',
            'job_id': job_id
        }
    
    else:
        log_debug("🔴 Using REAL EXECUTION mode")
        
        if not EXECUTOR_AVAILABLE:
            st.error("❌ **CommandExecutor not available** - Cannot execute real video generation")
            if CONTENT_FEED_AVAILABLE:
                fail_job(job_id, "CommandExecutor not available")
            return {
                'success': False,
                'message': 'CommandExecutor not available for real execution',
                'mode': 'real',
                'job_id': job_id
            }
        
        # Real execution with comprehensive status tracking
        executor = CommandExecutor()
        
        # Start the status display that will show all steps
        with st.status("🎬 Starting video generation workflow...", expanded=True) as status:
            
            # Step 1: System Check
            st.write("🔍 **Step 1/5**: Checking system prerequisites...")
            if CONTENT_FEED_AVAILABLE:
                update_job(job_id, 10)
            
            prerequisites = executor.check_prerequisites()
            missing_tools = [tool for tool, available in prerequisites.items() if not available]
            
            if missing_tools:
                st.write(f"⚠️ Missing tools: {', '.join(missing_tools)}")
                st.write("⚠️ Some features may not work properly")
            else:
                st.write("✅ All prerequisites available:")
                for tool, available in prerequisites.items():
                    st.write(f"  • {tool}: {'✅' if available else '❌'}")
            
            # Step 2: Command Preparation
            st.write("⚙️ **Step 2/5**: Preparing video generation command...")
            if CONTENT_FEED_AVAILABLE:
                update_job(job_id, 20)
            
            command_name = f"hierarchy-{layout_type.replace('_', '-')}"
            full_command = f"npm run {command_name} {artist_name}"
            st.write(f"📝 Command: `{full_command}`")
            
            # Step 3: Validation
            st.write("✅ **Step 3/5**: Validating configuration...")
            if CONTENT_FEED_AVAILABLE:
                update_job(job_id, 30)
            
            st.write(f"  • Artist: **{artist_name}**")
            st.write(f"  • Layout: **{layout_type}**")
            st.write(f"  • Mode: Real Execution")
            
            # Step 4: Execution
            st.write("🚀 **Step 4/5**: Executing video generation...")
            st.write("⏳ This may take 1-3 minutes depending on complexity...")
            if CONTENT_FEED_AVAILABLE:
                update_job(job_id, 40)
            
            # Create a placeholder for execution feedback
            execution_placeholder = st.empty()
            
            try:
                # Update status to show we're executing
                status.update(label="🚀 Executing video generation command...", state="running")
                
                # Execute the video generation
                with execution_placeholder.container():
                    st.info("📡 **Running command now** - Please wait while the video is generated...")
                    st.info("⏳ This may take 1-3 minutes depending on complexity...")
                    
                    # Simple progress indicator without threading
                    progress_bar = st.progress(0)
                    progress_text = st.empty()
                    
                    # Show initial progress
                    progress_bar.progress(10)
                    progress_text.text("🔄 Initializing video generation...")
                    
                    # Update feed progress
                    if CONTENT_FEED_AVAILABLE:
                        update_job(job_id, 50, status_message="Executing video generation...")
                
                # Execute the actual command
                result = executor.execute_video_generation_sync(
                    artist_name=artist_name,
                    layout_type=layout_type
                )
                
                # Clear the progress display
                execution_placeholder.empty()
                
                if result['success']:
                    # Step 5: Success
                    st.write("🎉 **Step 5/5**: Video generation completed successfully!")
                    duration_min = result.get('duration', 0) / 60
                    st.write(f"⏱️ Total time: {duration_min:.1f} minutes")
                    
                    # Show output details
                    output_path = result.get('output_path', '')
                    if output_path:
                        st.write(f"📁 Output: `{output_path}`")
                        
                        # Complete job in feed with actual output path
                        if CONTENT_FEED_AVAILABLE:
                            complete_job(job_id, output_path)
                    else:
                        if CONTENT_FEED_AVAILABLE:
                            complete_job(job_id, f"output/{artist_name}_{layout_type}.mp4")
                    
                    status.update(label="✅ Video generation completed successfully!", state="complete")
                    
                    # Show final success message
                    st.success(f"""
                    🎉 **Video Generated Successfully!**
                    
                    **Results:**
                    • Artist: **{artist_name}**
                    • Layout: {layout_type}
                    • Duration: {duration_min:.1f} minutes
                    • Command: `{result.get('command', 'N/A')}`
                    """)
                    
                else:
                    # Show error details
                    st.write("❌ **Step 5/5**: Video generation failed")
                    error_msg = result.get('error', 'Unknown error')
                    st.write(f"🔍 Error: {error_msg}")
                    
                    # Fail job in feed
                    if CONTENT_FEED_AVAILABLE:
                        fail_job(job_id, error_msg)
                    
                    if result.get('stderr'):
                        st.write("📄 Error details:")
                        st.code(result['stderr'][:500])
                    
                    status.update(label="❌ Video generation failed", state="error")
                    
                    # Show error message
                    st.error(f"""
                    ❌ **Video Generation Failed**
                    
                    **Error Details:**
                    • Artist: {artist_name}
                    • Layout: {layout_type}
                    • Error: {error_msg}
                    • Command: `{result.get('command', 'N/A')}`
                    """)
                
                return result
                
            except Exception as e:
                execution_placeholder.empty()
                st.write(f"❌ **Step 5/5**: Unexpected error occurred")
                error_msg = str(e)
                st.write(f"🔍 Error: {error_msg}")
                
                # Fail job in feed
                if CONTENT_FEED_AVAILABLE:
                    fail_job(job_id, error_msg)
                
                status.update(label="❌ Unexpected error during video generation", state="error")
                
                st.error(f"""
                ❌ **Unexpected Error**
                
                **Details:**
                • Artist: {artist_name}
                • Layout: {layout_type}
                • Error: {error_msg}
                """)
                
                return {
                    'success': False,
                    'error': error_msg,
                    'mode': 'real',
                    'job_id': job_id
                }

def handle_deep_research(research_params, mode="real"):
    """Handle deep research requests with real WebcrawlerAPI web scraping"""
    log_debug("🔬 DEEP RESEARCH AGENT ACTIVATED")
    log_debug(f"📊 Research parameters: {research_params}")
    
    query = research_params.get('query', 'Unknown query')
    depth = research_params.get('depth', 2)
    breadth = research_params.get('breadth', 4)
    
    # Initialize variables at the start
    research_data = {'sources_analyzed': 0, 'insights_generated': 0}
    pdf_path = None
    
    # Show detailed agent status
    with st.chat_message("assistant"):
        st.markdown("### 🔬 **Deep Research Agent Status**")
        
        # Agent assignment details
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                **🤖 Agent:** Deep Research Agent
                **📝 Query:** `{query}`
                **🎯 Mode:** {mode.title()}
                **📊 Scope:** {depth} depth × {breadth} breadth = {depth * breadth} total research cycles
                """)
            
            with col2:
                st.markdown(f"""
                **⚙️ Configuration:**
                - WebcrawlerAPI: {'✅' if mode == 'real' else '🔵 Simulated'}
                - OpenAI Analysis: {'✅' if mode == 'real' else '🔵 Simulated'}
                - PDF Generation: ✅
                """)
        
        st.markdown("---")
        st.write(f"🔍 **Research Target:** {query}")
        
        progress_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                queries_metric = st.metric("Search Queries", "0")
            with col2:
                sources_metric = st.metric("Sources Found", "0") 
            with col3:
                learnings_metric = st.metric("Learnings", "0")
        
        try:
            # Import and run real research
            from components.deep_research import conduct_dynamic_research
            
            status_text.text("🌐 Conducting REAL research with WebcrawlerAPI web scraping...")
            
            try:
                # Execute research with real WebcrawlerAPI
                research_results = conduct_dynamic_research(
                    query=query,
                    depth=depth,
                    breadth=breadth
                )
                
                # Extract data from result
                if isinstance(research_results, dict):
                    # Handle the actual result format from our research function
                    research_data = research_results.get('analysis', {})
                    pdf_path = research_results.get('presentation_path')
                    
                    # Update metrics using the actual data structure
                    analysis = research_results.get('analysis', {})
                    queries_metric.metric("Search Queries", analysis.get('breadth', 0))
                    sources_metric.metric("Sources Found", analysis.get('sources_analyzed', 0))
                    learnings_metric.metric("Learnings", analysis.get('insights_generated', 0))
                else:
                    # Fallback structure
                    research_data = {'sources_analyzed': 0, 'insights_generated': 0}
                
                progress_bar.progress(100)
                status_text.text("✅ Research Complete!")
                
                # Show download button
                if pdf_path and Path(pdf_path).exists():
                    with open(pdf_path, "rb") as pdf_file:
                        pdf_data = pdf_file.read()
                    
                    st.download_button(
                        label="📄 Download Professional Research Report",
                        data=pdf_data,
                        file_name=Path(pdf_path).name,
                        mime="application/pdf",
                        type="primary"
                    )
                    
                    # Add to job tracking
                    if CONTENT_FEED_AVAILABLE:
                        job_id = f"research_{int(time.time())}"
                        add_job(
                            job_id=job_id,
                            agent_name="Deep Research Agent",
                            task_type="web_research",
                            job_type="research",
                            query=query,
                            depth=depth,
                            breadth=breadth,
                            sources_found=research_data.get('sources_analyzed', 0),
                            learnings_extracted=research_data.get('insights_generated', 0)
                        )
                        
                        complete_job(job_id, output_path=pdf_path)
                    
                    log_debug(f"✅ Deep research completed: {pdf_path}")
                else:
                    st.warning("📊 Research completed but report file not available")
                
            except NotImplementedError as e:
                # Clear, honest error message about missing real implementation
                status_text.text("❌ Research system not fully implemented")
                progress_bar.progress(0)
                
                st.error("🚫 **Real Research System Not Available**")
                st.markdown(f"""
                **Error Details:**
                ```
                {str(e)}
                ```
                
                **What this means:**
                - The system is configured to use **real web scraping** with WebcrawlerAPI
                - **Mock/fake data has been completely removed** to prevent misleading results
                - The research system needs proper WebcrawlerAPI integration to work
                
                **Next Steps:**
                1. Implement real WebcrawlerAPI integration
                2. Add OpenAI content analysis
                3. Test with real web sources
                
                **Status: Refusing to return fake data - this is intentional to ensure data integrity**
                """)
                
                # Set fallback values for error case
                research_data = {'sources_analyzed': 0, 'insights_generated': 0}
            
        except ValueError as e:
            # API key or configuration issues
            status_text.text("❌ Configuration error")
            progress_bar.progress(0)
            
            st.error("🔑 **Configuration Required**")
            st.markdown(f"""
            **Error Details:**
            ```
            {str(e)}
            ```
            
            **Required Setup:**
            - Add `WEB_CRAWLER_API_KEY=your_webcrawler_api_key` to .env file  
            - Add `OPENAI_API_KEY=your_openai_key` to .env file
            - Restart the application
            
            **What's happening:**
            The research system is trying to use real web scraping but missing required API keys.
            """)
            
            # Set fallback values for error case
            research_data = {'sources_analyzed': 0, 'insights_generated': 0}
            
        except Exception as e:
            st.error(f"❌ Unexpected research error: {str(e)}")
            log_debug(f"❌ Deep research error: {str(e)}")
            # Set fallback values for error case
            research_data = {'sources_analyzed': 0, 'insights_generated': 0}
    
    # Add assistant response - use safe access to research_data
    sources_count = research_data.get('sources_analyzed', 0)
    insights_count = research_data.get('insights_generated', 0)
    
    st.session_state.chat_messages.append({
        "role": "assistant", 
        "content": f"✅ **Deep Research Complete!** Professional analysis on: {query}\\n\\n📊 Found {sources_count} sources with {insights_count} key insights.\\n📄 Download the comprehensive PDF report above."
    })
    
    # DON'T call st.rerun() - it clears the download button!
    log_debug("🔄 Deep research completed without rerun to preserve download button")
    return "deep_research_completed"

def handle_user_input(user_input, uploaded_file=None):
    """Main function to handle user input and route to appropriate handlers"""
    log_debug(f"💬 USER INPUT RECEIVED: '{user_input}'")
    log_debug(f"📁 UPLOADED FILE: {uploaded_file.name if uploaded_file else 'None'}")
    
    # Add user message to chat history
    if uploaded_file:
        st.session_state.chat_messages.append({
            "role": "user", 
            "content": f"{user_input}\n📎 Attached: {uploaded_file.name}"
        })
    else:
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
    log_debug("📝 User message added to chat history")
    
    # Parse intent
    intent_data = parse_user_intent(user_input, uploaded_file)
    log_debug(f"🎯 Intent parsing completed. Result: {intent_data}")
    
    intent = intent_data['intent']
    parameters = intent_data['parameters']
    confidence = intent_data['confidence']
    
    log_debug(f"🚀 HANDLING INTENT: '{intent}' (confidence: {confidence})")
    log_debug(f"📊 Parameters: {parameters}")
    log_debug(f"⚙️ Execution mode: {'🔴 Real Execution' if st.session_state.execution_mode == 'real' else '🔵 Simulation Mode'}")
    
    if intent == 'bulk_image_processing':
        operation_type = parameters.get('operation_type', 'crop')
        uploaded_file = parameters.get('uploaded_file')
        target_size = parameters.get('target_size')
        artboard_size = parameters.get('artboard_size', (1080, 1080))
        scale_percent = parameters.get('scale_percent', 90.0)
        center_horizontal = parameters.get('center_horizontal', True)
        center_vertical = parameters.get('center_vertical', True)
        
        # Show a brief confirmation, then start the process
        if operation_type == "thumbnail":
            st.info(f"🖼️ **Request understood**: Creating thumbnails from **{uploaded_file.name}** with {artboard_size[0]}x{artboard_size[1]} artboards at {scale_percent}% scale")
        else:
            st.info(f"🖼️ **Request understood**: {operation_type.title()} operation on **{uploaded_file.name}**")
        
        time.sleep(1)  # Brief pause for user to see confirmation
        
        # Execute the operation
        return handle_bulk_image_processing(
            operation_type, uploaded_file, target_size, artboard_size, 
            scale_percent, center_horizontal, center_vertical, st.session_state.execution_mode
        )
    
    elif intent == 'deep_research':
        research_params = parameters
        
        # Show a brief confirmation, then start the process
        st.success(f"🔬 **DEEP RESEARCH AGENT ACTIVATED**")
        st.info(f"📊 **Research Focus**: {research_params.get('focus_area', 'General')} analysis")
        st.info(f"📊 **Scope**: Depth {research_params.get('depth', 3)}, Breadth {research_params.get('breadth', 5)}")
        
        # Add detailed logging about what's happening
        with st.expander("🔍 **Research Agent Handoff Details**", expanded=True):
            st.markdown(f"""
            **🤖 Agent Assignment:** Deep Research Agent
            **📝 Query:** `{research_params.get('query', 'Unknown')}`
            **🎯 Intent Confidence:** {confidence:.1%}
            **⚙️ Processing Mode:** {st.session_state.execution_mode.title()}
            **🔧 Parameters:**
            - Focus Area: `{research_params.get('focus_area', 'general')}`
            - Research Depth: `{research_params.get('depth', 3)}` iterations
            - Research Breadth: `{research_params.get('breadth', 5)}` queries per iteration
            
            **🚀 Starting handoff to Deep Research Agent...**
            """)
        
        time.sleep(1)  # Brief pause for user to see confirmation
        
        # Execute the research
        return handle_deep_research(research_params, st.session_state.execution_mode)
    
    elif intent == 'video_generation':
        artist_name = parameters.get('artist_name', 'Unknown Artist')
        layout_type = parameters.get('layout_type', 'balanced')
        
        # Show a brief confirmation, then start the process
        st.info(f"🎯 **Request understood**: Creating {layout_type} video for **{artist_name}**")
        
        # Execute video generation (this will show comprehensive real-time progress)
        result = handle_video_generation(
            artist_name=artist_name,
            layout_type=layout_type,
            mode=st.session_state.execution_mode
        )
        
        # The handler now shows all progress and results directly
        
    else:
        # Handle general chat
        log_debug(f"💭 GENERAL CHAT - No specific intent detected for: '{user_input}'")
        
        # Provide helpful guidance
        if uploaded_file:
            response = f"I see you've uploaded '{uploaded_file.name}'. To process this file, try asking me to:\n\n• 'Crop all PNGs to remove empty space'\n• 'Resize all images to 1024x1024'\n• 'Process the uploaded images'"
        else:
            response = f"I understand you're asking about: '{user_input}'. I can help you with:\n\n• **Video Generation**: 'Create a video for [Artist Name]'\n• **Bulk Image Processing**: Upload a ZIP of PNGs and ask me to crop or resize them\n• **System Status**: Check my capabilities and status"
        
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        log_debug(f"📤 Helpful response sent: '{response}'")
    
    log_debug("🔄 Triggering Streamlit rerun...")

def main():
    """Main chat interface"""
    log_debug("Attempting to import CommandExecutor...")
    
    st.title("🤖 AI Agent Chat")
    st.markdown("Chat with your AI agent to generate videos, process images, and manage your workflow.")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar controls
    with st.sidebar:
        st.header("🔧 Controls")
        
        # File upload section
        st.subheader("📎 File Upload")
        uploaded_file = st.file_uploader(
            "Upload ZIP of PNG images for bulk processing",
            type=['zip'],
            help="Upload a ZIP file containing PNG images for batch processing operations like cropping or resizing"
        )
        
        if uploaded_file:
            st.success(f"📁 File uploaded: {uploaded_file.name}")
            st.session_state.uploaded_file = uploaded_file
        else:
            st.session_state.uploaded_file = None
        
        st.divider()
        
        # Execution mode toggle
        mode = st.radio(
            "Execution Mode",
            ["🔴 Real Execution", "🔵 Simulation Mode"],
            index=0 if st.session_state.execution_mode == "real" else 1
        )
        st.session_state.execution_mode = "real" if "Real" in mode else "simulation"
        
        # Debug mode toggle
        st.session_state.debug_mode = st.checkbox("Enable Debug Logging", value=st.session_state.debug_mode)
        
        if st.session_state.debug_mode:
            st.success("🐛 Debug mode active - detailed logs will be shown")
        
        st.divider()
        
        # Status information
        st.subheader("📊 System Status")
        if EXECUTOR_AVAILABLE:
            st.success("✅ CommandExecutor Available")
        else:
            st.error("❌ CommandExecutor Not Available")
            
        if IMAGE_PROCESSOR_AVAILABLE:
            st.success("✅ Image Processor Available")
        else:
            st.error("❌ Image Processor Not Available")
            
        if CONTENT_FEED_AVAILABLE:
            st.success("✅ Content Feed Available")
        else:
            st.error("❌ Content Feed Not Available")
            
        st.info(f"Mode: {st.session_state.execution_mode.title()}")
        st.info(f"Messages: {len(st.session_state.chat_messages)}")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # Debug output
    if st.session_state.debug_mode:
        with st.expander("🐛 Debug Information", expanded=False):
            st.json({
                "session_state": {
                    "messages_count": len(st.session_state.chat_messages),
                    "execution_mode": st.session_state.execution_mode,
                    "executor_available": EXECUTOR_AVAILABLE,
                    "image_processor_available": IMAGE_PROCESSOR_AVAILABLE,
                    "content_feed_available": CONTENT_FEED_AVAILABLE,
                    "uploaded_file": uploaded_file.name if uploaded_file else None
                }
            })
    
    # Chat input
    if prompt := st.chat_input("Ask me to generate videos, process images, or help with your workflow..."):
        # Show user message immediately
        with st.chat_message("user"):
            if st.session_state.uploaded_file:
                st.write(f"{prompt}\n📎 Attached: {st.session_state.uploaded_file.name}")
            else:
                st.write(prompt)
        
        # Show debug info if enabled
        if st.session_state.debug_mode:
            debug_container = st.container()
            with debug_container:
                st.text(f"🐛 [{datetime.now().strftime('%H:%M:%S')}] 💬 USER INPUT RECEIVED: '{prompt}'")
                st.text(f"🐛 [{datetime.now().strftime('%H:%M:%S')}] 🔍 Starting intent parsing...")
        
        # Check intent before processing to avoid clearing download buttons
        intent_data = parse_user_intent(prompt, st.session_state.uploaded_file)
        is_deep_research = intent_data.get('intent') == 'deep_research'
        
        # Process the input
        handle_user_input(prompt, st.session_state.uploaded_file)
        
        # Clear uploaded file after processing
        if st.session_state.uploaded_file:
            st.session_state.uploaded_file = None
        
        # Only rerun for non-deep research to avoid clearing download buttons
        if not is_deep_research:
            st.rerun()
    
    # Render content feed at the bottom
    if CONTENT_FEED_AVAILABLE:
        render_content_feed(max_items=12)
    else:
        st.warning("📱 Content feed not available - install content_feed component")

if __name__ == "__main__":
    main()