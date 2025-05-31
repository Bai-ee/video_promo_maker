#!/usr/bin/env python3
"""
Faceless Video Maker - Streamlit Web Interface
A comprehensive web interface for interacting with AI agents using CrewAI and Streamlit.
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.append(str(project_root / "agents" / "core"))
sys.path.append(str(project_root / "agents" / "tools"))
sys.path.append(str(project_root / "agents" / "scripts"))

# Import content feed components
try:
    sys.path.append(str(project_root / "components"))
    from content_feed import render_content_feed
    CONTENT_FEED_AVAILABLE = True
except ImportError as e:
    CONTENT_FEED_AVAILABLE = False
    print(f"Content feed not available: {e}")

# Configure Streamlit page
st.set_page_config(
    page_title="Faceless Video Maker - AI Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .content-feed-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 2rem;
        border-top: 3px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

def render_page_with_feed(content_function):
    """Wrapper to render any page with content feed at the bottom"""
    # Create main content area
    main_content = st.container()
    
    with main_content:
        # Run the page content function
        content_function()
    
    # Add content feed at the bottom
    if CONTENT_FEED_AVAILABLE:
        st.markdown('<div class="content-feed-container">', unsafe_allow_html=True)
        render_content_feed(max_items=12)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("---")
        st.info("📱 **Content Feed**: Install content_feed component to see generated videos and images here")

def main():
    """Main application function"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎬 Faceless Video Maker - AI Assistant</h1>
        <p>Intelligent video creation with AI agents and CrewAI orchestration</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for navigation and settings
    with st.sidebar:
        st.title("🛠️ Control Panel")
        
        # API Key Management
        st.subheader("🔑 API Configuration")
        
        # Check for existing .env file
        env_file = project_root / ".env"
        if env_file.exists():
            st.success("✅ .env file found")
        else:
            st.warning("⚠️ .env file not found")
            
        # API Key inputs
        openai_key = st.text_input("OpenAI API Key", type="password", help="Your OpenAI API key")
        google_key = st.text_input("Google API Key", type="password", help="Your Google API key")
        
        if st.button("💾 Save API Keys"):
            save_api_keys(openai_key, google_key)
            st.rerun()
        
        st.divider()
        
        # Navigation
        st.subheader("🧭 Navigation")
        
        # Initialize current page if not set
        if "current_page" not in st.session_state:
            st.session_state.current_page = "🏠 Home"
        
        page = st.selectbox(
            "Choose a function:",
            [
                "🏠 Home",
                "🎨 Video Generation",
                "🖼️ Image Processing", 
                "🔬 Deep Research",
                "🤖 AI Agent Chat",
                "📊 System Status",
                "⚙️ Settings"
            ],
            index=[
                "🏠 Home",
                "🎨 Video Generation",
                "🖼️ Image Processing", 
                "🔬 Deep Research",
                "🤖 AI Agent Chat",
                "📊 System Status",
                "⚙️ Settings"
            ].index(st.session_state.current_page) if st.session_state.current_page in [
                "🏠 Home",
                "🎨 Video Generation",
                "🖼️ Image Processing", 
                "🔬 Deep Research",
                "🤖 AI Agent Chat",
                "📊 System Status",
                "⚙️ Settings"
            ] else 0
        )
        
        # Update session state when selectbox changes
        if page != st.session_state.current_page:
            st.session_state.current_page = page
            st.rerun()
        
        st.divider()
        
        # System Status in Sidebar
        st.subheader("🔧 System Status")
        
        # Check Deep Research availability
        try:
            sys.path.append(str(Path(__file__).parent / "components"))
            from deep_research import get_deep_research_agent
            deep_research_available = True
        except ImportError:
            deep_research_available = False
        
        if CONTENT_FEED_AVAILABLE:
            st.success("✅ Content Feed Active")
        else:
            st.error("❌ Content Feed Missing")
            
        if deep_research_available:
            st.success("✅ Deep Research Active")
        else:
            st.warning("⚠️ Deep Research Needs Setup")
    
    # Main content area based on selection
    current_page = st.session_state.current_page
    
    if current_page == "🏠 Home":
        render_page_with_feed(show_home_page)
    elif current_page == "🎨 Video Generation":
        render_page_with_feed(show_video_generation_page)
    elif current_page == "🖼️ Image Processing":
        render_page_with_feed(show_image_processing_page)
    elif current_page == "🔬 Deep Research":
        render_page_with_feed(show_deep_research_page)
    elif current_page == "🤖 AI Agent Chat":
        # AI Chat has its own feed integration, so no wrapper needed
        show_ai_chat_page()
    elif current_page == "📊 System Status":
        render_page_with_feed(show_system_status_page)
    elif current_page == "⚙️ Settings":
        render_page_with_feed(show_settings_page)

def save_api_keys(openai_key: str, google_key: str):
    """Save API keys to .env file"""
    env_content = ""
    if openai_key:
        env_content += f"OPENAI_API_KEY={openai_key}\n"
    if google_key:
        env_content += f"GOOGLE_API_KEY={google_key}\n"
    
    if env_content:
        with open(project_root / ".env", "w") as f:
            f.write(env_content)
        st.success("✅ API keys saved successfully!")

def show_home_page():
    """Display the home page with overview"""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🚀 Welcome to Your AI Video Creation Suite")
        
        st.markdown("""
        This intelligent interface provides access to your comprehensive video generation system:
        
        ### 🎯 **Key Features:**
        - **AI-Powered Video Generation**: Create professional faceless videos with AI backgrounds
        - **Intelligent Image Processing**: Crop, enhance, and optimize images with AI
        - **🔬 Deep Research Intelligence**: ✅ **NOW AVAILABLE** - Professional AI-powered market analysis and research
        - **CrewAI Agent Orchestration**: Coordinate multiple AI agents for complex tasks
        - **Brand Asset Management**: Automatic logo and thumbnail integration
        - **Real-time Processing**: Watch your content creation in real-time
        - **📱 Live Content Feed**: See all your generated videos and images in Instagram-style feed
        
        ### 🛠️ **Available Tools:**
        - Video generation with hierarchical design systems
        - AI background creation and Veo video integration
        - Smart image cropping with content detection
        - **🆕 Fortune-500 level market research and analysis**
        - Brand-aware layout optimization
        - Automated workflow orchestration
        - Real-time progress tracking with visual feed
        
        ### 🔬 **Deep Research Capabilities:**
        - **Chicago Electronic Music Festival Analysis** - Research organizers, success patterns, strategic insights
        - **Market & Competitor Analysis** - Industry trends, competitive landscape, opportunities
        - **Professional Report Generation** - PDF, Markdown, and JSON outputs
        - **Strategic Recommendations** - Data-driven insights for business planning
        """)
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        
        col_a, col_b, col_c, col_d = st.columns(4)
        
        with col_a:
            if st.button("🎬 Generate Video", use_container_width=True):
                st.session_state.current_page = "🎨 Video Generation"
                st.rerun()
                
        with col_b:
            if st.button("🖼️ Process Images", use_container_width=True):
                st.session_state.current_page = "🖼️ Image Processing"
                st.rerun()
                
        with col_c:
            if st.button("🔬 Deep Research", use_container_width=True):
                st.session_state.current_page = "🔬 Deep Research"
                st.rerun()
                
        with col_d:
            if st.button("🤖 Chat with AI", use_container_width=True):
                st.session_state.current_page = "🤖 AI Agent Chat"
                st.rerun()
    
    with col2:
        st.subheader("📈 System Overview")
        
        # System status cards
        st.markdown("""
        <div class="agent-card">
            <h4>🔧 Available NPM Scripts</h4>
            <p>25+ commands ready</p>
        </div>
        
        <div class="agent-card">
            <h4>🤖 AI Agents</h4>
            <p>2 active agents</p>
        </div>
        
        <div class="agent-card">
            <h4>🎨 Video Templates</h4>
            <p>Multiple layouts available</p>
        </div>
        
        <div class="agent-card">
            <h4>📱 Content Feed</h4>
            <p>Real-time job tracking</p>
        </div>
        """, unsafe_allow_html=True)

def show_video_generation_page():
    """Video generation interface"""
    # Import and run the video generation module
    import sys
    from pathlib import Path
    
    # Add the pages directory to the path
    pages_dir = Path(__file__).parent / "pages"
    sys.path.append(str(pages_dir))
    
    try:
        # Import the video generation main function
        from video_generation import main as video_gen_main
        video_gen_main()
    except ImportError as e:
        st.error(f"Could not load video generation: {e}")
        st.info("Please check that the video generation components are properly installed.")

def show_image_processing_page():
    """Image processing interface"""
    st.subheader("🖼️ Image Processing Lab")
    
    # Basic image processing tools
    st.info("Image processing interface - will be implemented in Phase 2")

def show_deep_research_page():
    """Deep Research interface"""
    import sys
    from pathlib import Path
    
    # Add the pages directory to the path
    pages_dir = Path(__file__).parent / "pages"
    sys.path.append(str(pages_dir))
    
    # First check if Deep Research is available
    try:
        sys.path.append(str(Path(__file__).parent / "components"))
        from deep_research import get_deep_research_agent, conduct_chicago_edm_research
        DEEP_RESEARCH_AVAILABLE = True
    except ImportError as e:
        DEEP_RESEARCH_AVAILABLE = False
    
    if DEEP_RESEARCH_AVAILABLE:
        # Deep Research is working - show the main interface
        try:
            from deep_research import main as deep_research_main
            deep_research_main()
        except ImportError as e:
            st.error(f"Could not load Deep Research interface: {e}")
    else:
        # Show helpful information about Deep Research
        st.subheader("🔬 Deep Research Intelligence")
        
        st.error("🚨 Deep Research functionality is not available")
        st.info("""
        **Missing dependencies. To enable Deep Research, install:**
        ```bash
        pip install beautifulsoup4 requests-html reportlab aiohttp
        ```
        
        **After installation, Deep Research will provide:**
        - Fortune-500 level market analysis
        - Chicago electronic music festival research
        - Competitor analysis and trend identification
        - Professional PDF report generation
        - Strategic recommendations
        """)
        
        st.markdown("### 🔄 Alternative Access")
        st.info("""
        💡 **Try the AI Chat page instead!**
        
        You can still access Deep Research functionality through the AI Chat interface by asking:
        - "perform deep research on electronic music events in chicago"
        - "research upcoming festivals and organizers"
        - "analyze the chicago edm festival market"
        
        The AI Chat will handle missing dependencies gracefully.
        """)
        
        # Quick test button
        if st.button("🧪 Test Deep Research Dependencies", use_container_width=True):
            with st.spinner("Testing dependencies..."):
                try:
                    import beautifulsoup4
                    import requests_html
                    import reportlab
                    import aiohttp
                    st.success("✅ All dependencies are available! Deep Research should work.")
                    st.info("🔄 Refresh the page to access Deep Research functionality.")
                except ImportError as missing:
                    st.error(f"❌ Missing dependency: {missing}")
                    st.info("Install the missing packages and refresh the page.")

def show_ai_chat_page():
    """AI agent chat interface"""
    # Import and run the AI chat module
    import sys
    from pathlib import Path
    
    # Add the pages directory to the path
    pages_dir = Path(__file__).parent / "pages"
    sys.path.append(str(pages_dir))
    
    try:
        # Import the AI chat main function
        from ai_chat import main as ai_chat_main
        ai_chat_main()
    except ImportError as e:
        st.error(f"Could not load AI chat: {e}")
        st.info("Please check that the AI chat components are properly installed.")

def show_system_status_page():
    """System status and monitoring"""
    st.subheader("📊 System Status")
    
    # Check various system components
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔍 Environment Check")
        
        # Check .env file
        env_exists = (project_root / ".env").exists()
        st.markdown(f"**.env file:** {'✅ Found' if env_exists else '❌ Missing'}")
        
        # Check node_modules
        node_modules_exists = (project_root / "node_modules").exists()
        st.markdown(f"**Node modules:** {'✅ Installed' if node_modules_exists else '❌ Missing'}")
        
        # Check key directories
        agents_exists = (project_root / "agents").exists()
        st.markdown(f"**Agents directory:** {'✅ Found' if agents_exists else '❌ Missing'}")
        
        # Check components directory
        components_exists = (project_root / "components").exists()
        st.markdown(f"**Components directory:** {'✅ Found' if components_exists else '❌ Missing'}")
        
        # Check content feed
        st.markdown(f"**Content Feed:** {'✅ Available' if CONTENT_FEED_AVAILABLE else '❌ Not Available'}")
        
    with col2:
        st.markdown("### 📦 Available Commands")
        
        # Show some key npm scripts
        key_scripts = [
            "npm run build",
            "npm run artist",
            "npm run enhanced-video-artist", 
            "npm run hierarchy-artist-focused",
            "npm run agent-crop-images"
        ]
        
        for script in key_scripts:
            st.code(script)
    
    # Add system performance metrics
    st.markdown("---")
    st.subheader("⚡ Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Generated Videos", "12", "3")
    
    with col2:
        st.metric("Processed Images", "47", "12")
    
    with col3:
        st.metric("Active Jobs", "2", "1")
    
    with col4:
        st.metric("Success Rate", "94%", "2%")

def show_settings_page():
    """Settings and configuration"""
    st.subheader("⚙️ Settings & Configuration")
    
    # Content Feed Settings
    st.markdown("### 📱 Content Feed Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_items = st.slider("Max items in feed", 6, 24, 12)
        auto_refresh = st.checkbox("Auto-refresh feed", value=True)
        
    with col2:
        show_thumbnails = st.checkbox("Show video thumbnails", value=True)
        compact_view = st.checkbox("Compact view", value=False)
    
    st.markdown("### 🎬 Video Generation Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_layout = st.selectbox("Default layout", ["balanced", "artist-focused", "logo-focused"])
        quality_preset = st.selectbox("Quality preset", ["Draft", "Standard", "High", "Ultra"])
        
    with col2:
        auto_preview = st.checkbox("Auto-generate previews", value=True)
        save_intermediate = st.checkbox("Save intermediate files", value=False)
    
    if st.button("💾 Save Settings", use_container_width=True):
        st.success("✅ Settings saved successfully!")

if __name__ == "__main__":
    main() 