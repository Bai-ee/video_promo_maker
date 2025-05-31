import streamlit as st
import sys
import os
import asyncio
import time
from datetime import datetime
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import deep research components
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "components"))
    from deep_research import conduct_dynamic_research, EnhancedDeepResearchAgent
    DEEP_RESEARCH_AVAILABLE = True
except ImportError as e:
    DEEP_RESEARCH_AVAILABLE = False
    print(f"Deep Research not available: {e}")

# Import content feed for integration
try:
    from content_feed import render_content_feed, add_job, update_job, complete_job, fail_job
    CONTENT_FEED_AVAILABLE = True
except ImportError as e:
    CONTENT_FEED_AVAILABLE = False
    print(f"Content feed not available: {e}")

# Import API key manager for enhanced functionality
try:
    from api_key_manager import APIKeyManager
    API_KEY_MANAGER_AVAILABLE = True
except ImportError:
    API_KEY_MANAGER_AVAILABLE = False

# Custom CSS for professional styling
st.markdown("""
<style>
.research-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}

.research-card {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    border: 1px solid #e1e5e9;
    margin-bottom: 1rem;
}

.status-running {
    background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: bold;
}

.status-completed {
    background: linear-gradient(90deg, #43e97b 0%, #38f9d7 100%);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: bold;
}

.research-metric {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
    border-left: 4px solid #667eea;
}

.download-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 10px;
    color: white;
    margin-top: 2rem;
}

.query-preset {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #28a745;
    margin: 0.5rem 0;
    cursor: pointer;
}

.query-preset:hover {
    background: #e9ecef;
}
</style>
""", unsafe_allow_html=True)

def render_research_header():
    """Render the main research page header"""
    st.markdown("""
    <div class="research-header">
        <h1>🔬 Deep Research Intelligence</h1>
        <p style="font-size: 1.2rem; margin-bottom: 0;">
            Professional AI-powered research system for comprehensive market analysis
        </p>
        <p style="margin-top: 0.5rem; opacity: 0.9;">
            Analyze industries, competitors, events, and market trends with Fortune-500 level insights
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_quick_start_templates():
    """Render quick start research templates"""
    st.markdown("### 🚀 Quick Start Templates")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="research-card">
            <h4>🎵 Electronic Music Festivals</h4>
            <p>Research upcoming electronic music festivals in Chicago, analyze organizers with 2+ years experience, and identify success patterns.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎵 Research Chicago EDM Festivals", key="edm_research", use_container_width=True):
            return "chicago_edm"
    
    with col2:
        st.markdown("""
        <div class="research-card">
            <h4>🏢 Industry Analysis</h4>
            <p>Comprehensive market research on any industry including key players, trends, opportunities, and competitive landscape.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🏢 Industry Analysis", key="industry_research", use_container_width=True):
            return "industry"
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div class="research-card">
            <h4>🏛️ Competitor Analysis</h4>
            <p>Deep dive into competitor strategies, market positioning, strengths, weaknesses, and strategic opportunities.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🏛️ Competitor Analysis", key="competitor_research", use_container_width=True):
            return "competitor"
    
    with col4:
        st.markdown("""
        <div class="research-card">
            <h4>📈 Market Trends</h4>
            <p>Analyze current and emerging market trends, consumer behavior, and future predictions for strategic planning.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📈 Market Trends", key="trends_research", use_container_width=True):
            return "trends"
    
    return None

def render_custom_research_form():
    """Render custom research query form"""
    st.markdown("### 🔍 Custom Research Query")
    
    with st.form("custom_research_form"):
        st.markdown("""
        <div class="research-card">
            <h4>Design Your Research Project</h4>
            <p>Create a custom research query for comprehensive analysis on any topic.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Research query input
        research_query = st.text_area(
            "Research Query",
            placeholder="Example: Research upcoming electronic music festivals happening in Chicago this summer, return back a large breadth of events...",
            height=100,
            help="Describe what you want to research. Be specific about the scope, depth, and desired outcomes."
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            research_depth = st.slider(
                "Research Depth",
                min_value=1,
                max_value=5,
                value=3,
                help="How many iterations of research refinement (1=basic, 5=comprehensive)"
            )
        
        with col2:
            research_breadth = st.slider(
                "Research Breadth", 
                min_value=3,
                max_value=10,
                value=5,
                help="Number of search queries per iteration (3=focused, 10=comprehensive)"
            )
        
        with col3:
            output_format = st.selectbox(
                "Output Format",
                ["Professional PDF Report", "Markdown Report", "JSON Data Export", "All Formats"],
                help="Choose the format for your research output"
            )
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            col1, col2 = st.columns(2)
            
            with col1:
                use_ai_analysis = st.checkbox(
                    "Use AI Analysis",
                    value=True,
                    help="Enable AI-powered content analysis (requires OpenAI API key)"
                )
                
                include_visualizations = st.checkbox(
                    "Include Data Visualizations",
                    value=True,
                    help="Generate charts and graphs in the report"
                )
            
            with col2:
                custom_output_dir = st.text_input(
                    "Output Directory",
                    value="research_output",
                    help="Directory to save research outputs"
                )
                
                openai_api_key = st.text_input(
                    "OpenAI API Key (Optional)",
                    type="password",
                    help="For enhanced AI analysis capabilities"
                )
        
        # Submit button
        submitted = st.form_submit_button(
            "🚀 Start Deep Research",
            use_container_width=True,
            type="primary"
        )
        
        if submitted and research_query:
            return {
                "query": research_query,
                "depth": research_depth,
                "breadth": research_breadth,
                "output_format": output_format,
                "use_ai": use_ai_analysis,
                "visualizations": include_visualizations,
                "output_dir": custom_output_dir,
                "openai_key": openai_api_key
            }
    
    return None

def run_async_research(research_config):
    """Run research asynchronously with progress tracking"""
    
    # Create progress tracking
    progress_container = st.container()
    
    with progress_container:
        st.markdown("### 🔬 Research In Progress")
        
        # Progress tracking elements
        overall_progress = st.progress(0)
        status_text = st.empty()
        phase_text = st.empty()
        
        # Metrics display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="research-metric">
                <h4>Research Depth</h4>
                <h2>{}</h2>
            </div>
            """.format(research_config["depth"]), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="research-metric">
                <h4>Research Breadth</h4>
                <h2>{}</h2>
            </div>
            """.format(research_config["breadth"]), unsafe_allow_html=True)
        
        with col3:
            sources_analyzed = st.empty()
            sources_analyzed.markdown("""
            <div class="research-metric">
                <h4>Sources Analyzed</h4>
                <h2 id="sources-count">0</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            insights_generated = st.empty()
            insights_generated.markdown("""
            <div class="research-metric">
                <h4>Insights Generated</h4>
                <h2 id="insights-count">0</h2>
            </div>
            """, unsafe_allow_html=True)
    
    # Progress callback function
    def progress_callback(message, progress):
        status_text.info(f"🔄 {message}")
        overall_progress.progress(progress / 100)
        
        # Update phase based on progress
        if progress < 20:
            phase_text.markdown("**Phase:** Initialization & Query Generation")
        elif progress < 60:
            phase_text.markdown("**Phase:** Data Collection & Analysis")
        elif progress < 85:
            phase_text.markdown("**Phase:** Comprehensive Analysis")
        elif progress < 95:
            phase_text.markdown("**Phase:** Report Generation")
        else:
            phase_text.markdown("**Phase:** Finalizing Results")
    
    try:
        # Actually conduct enhanced multi-provider research
        try:
            # Initialize API key manager if available
            api_key_manager = None
            if API_KEY_MANAGER_AVAILABLE:
                try:
                    api_key_manager = APIKeyManager()
                    api_key_manager.auto_setup()  # Ensure all keys are configured
                except Exception as e:
                    st.warning(f"⚠️ API key manager setup issue: {e}")
            
            # Use the enhanced research system with multi-provider support
            research_results = conduct_dynamic_research(
                query=research_config["query"],
                depth=research_config["depth"],
                breadth=research_config["breadth"],
                api_key_manager=api_key_manager
            )
            
            # Check if research was successful
            if research_results.get("success", False):
                # Update results to match expected format for backwards compatibility
                session_id = f"research_{int(time.time())}"
                research_results["session_id"] = session_id
                
                # Update sources count display
                total_sources = research_results.get("provider_stats", {}).get("total_sources", 0)
                sources_analyzed.markdown(f"""
                <div class="research-metric">
                    <h4>Sources Analyzed</h4>
                    <h2>{total_sources}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Update insights count (estimate based on analysis length)
                analysis_text = research_results.get("analysis", {}).get("analysis", "")
                insights_count = len(analysis_text.split('\n\n')) if analysis_text else 0
                insights_generated.markdown(f"""
                <div class="research-metric">
                    <h4>Insights Generated</h4>
                    <h2>{insights_count}</h2>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                # Research failed - show comprehensive error information
                st.error("❌ **ENHANCED RESEARCH SYSTEM - REAL DATA COLLECTION FAILED**")
                st.markdown(f"""
                **Error Details:**
                ```
                {research_results.get('error', 'Unknown error')}
                ```
                
                **🔧 Troubleshooting Information:**
                {research_results.get('troubleshooting', 'Please check your API configuration')}
                
                **🌐 System Status:**
                - ✅ **WebcrawlerAPI**: Primary web crawler (unlimited trial)
                - ✅ **OpenAI**: Content analysis engine
                
                **💡 What you can do:**
                1. **Try a simpler query** - Very specific queries may have limited web results
                2. **Wait and retry** - API quotas reset periodically
                3. **Check internet connection** - Ensure stable connectivity
                4. **Verify API keys** - Make sure all keys are properly configured
                
                🚫 **This system uses only REAL web data** - No mock/fake data is returned to ensure data integrity.
                """)
                return None
            
        except Exception as e:
            # System-level error - show detailed troubleshooting
            st.error("❌ **ENHANCED RESEARCH SYSTEM ERROR**")
            st.markdown(f"""
            **System Error:**
            ```
            {str(e)}
            ```
            
            **What happened:**
            - The enhanced multi-provider research system encountered an unexpected error
            - This system uses **WebcrawlerAPI (primary)** for real web data
            - **No mock/fake data** is returned to prevent misleading results
            
            **System Components:**
            - 🔍 **WebcrawlerAPI**: Primary web scraping (b0a58413f6d2d8acb2bd)
            - 🧠 **OpenAI**: Content analysis and synthesis
            
            **Troubleshooting:**
            1. **API Configuration**: Check that API keys are properly set
            2. **Network Connectivity**: Ensure stable internet connection
            3. **Query Simplification**: Try a broader, simpler search query
            4. **Service Status**: Verify external API services are operational
            
            🔒 **Data Integrity**: This system refuses to return fake data to maintain research quality.
            """)
            return None
        
        # Add to content feed if available
        if CONTENT_FEED_AVAILABLE:
            job_id = session_id[:8]
            add_job(
                job_id,
                agent_name="Deep Research Agent",
                task_type=research_config.get("query", "research")[:20],
                job_type="research",
                query=research_config["query"],
                depth=research_config["depth"],
                breadth=research_config["breadth"],
                status="completed"
            )
            
            complete_job(
                job_id,
                research_results.get("presentation_path", "research_presentation.pdf"),
                summary={
                    "sources_analyzed": research_results["analysis"]["sources_analyzed"],
                    "insights_generated": research_results["analysis"]["insights_generated"],
                    "research_depth": research_config["depth"],
                    "research_breadth": research_config["breadth"]
                }
            )
        
        return research_results
        
    except Exception as e:
        st.error(f"Research failed: {str(e)}")
        return None

def generate_mock_executive_summary(query):
    """Generate realistic executive summary for demo"""
    if "chicago" in query.lower() and "electronic music" in query.lower():
        return """
BULLSHIT SUMMARY

Research Objective: Chicago Electronic Music Festival Market Analysis

This comprehensive analysis examines the Chicago electronic music festival landscape, focusing on established organizers with 2+ years of operational history. Our research reveals a dynamic market characterized by strong growth potential, established players, and clear success patterns.

Key Market Dynamics:
• Chicago maintains a vibrant electronic music ecosystem with multiple successful annual festivals
• Established organizers demonstrate significantly higher success rates and operational consistency  
• Market leaders like React Presents command premium positioning through consistent execution
• Venue partnerships and community engagement emerge as critical differentiating factors

Strategic Implications:
The research indicates favorable conditions for new entrants who demonstrate strong operational planning, established industry relationships, and differentiated programming approaches. Success patterns emphasize the importance of multi-year strategic planning over opportunistic event execution.

Data Sources: 45 comprehensive data points analyzed across multiple market segments and operational timeframes.
        """.strip()
    
    return f"""
EXECUTIVE SUMMARY

Research Objective: {query}

This comprehensive analysis provides strategic insights and market intelligence based on extensive research across multiple data sources and industry segments. Our methodology combines web-based research, pattern analysis, and strategic assessment to deliver actionable intelligence.

Key Findings:
• Market demonstrates strong fundamentals with established player ecosystem
• Clear differentiation patterns emerge among successful versus struggling entities
• Strategic opportunities exist for well-positioned new entrants
• Risk mitigation strategies are clearly identifiable from industry patterns

Strategic Implications:
The research indicates specific strategic pathways for success, supported by data-driven insights and industry best practices. Recommended approaches emphasize systematic planning over opportunistic execution.

Data Sources: Multiple industry sources analyzed with comprehensive pattern recognition and strategic assessment.
    """.strip()

def generate_mock_findings(query):
    """Generate realistic key findings"""
    if "chicago" in query.lower() and "electronic music" in query.lower():
        return [
            "Chicago's electronic music festival market shows strong growth with multiple established organizers",
            "React Presents dominates the market with 8+ years of experience and multiple successful annual events",
            "Successful festivals maintain consistent venue partnerships and build year-round community engagement",
            "Attendance figures range from 15,000 (boutique events) to 75,000+ (major festivals)",
            "Ticket pricing typically ranges from $199 GA to $899 VIP, indicating strong market demand",
            "Success factors include diverse lineup curation, strong logistics, and weather contingency planning",
            "Market leaders demonstrate 85%+ success rates compared to 45% for newcomers",
            "Venue commitments of 2-3 years correlate strongly with event profitability",
            "Social media engagement (50K+ followers) is critical for major festival success",
            "Weather contingency planning is the #1 differentiator between successful and failed events"
        ]
    
    return [
        "Market demonstrates strong growth trajectory with established competitive dynamics",
        "Key players show consistent performance patterns over multi-year timeframes", 
        "Success factors cluster around operational excellence and strategic partnerships",
        "Market entry barriers exist but are surmountable with proper strategic approach",
        "Differentiation opportunities exist in underserved market segments",
        "Technology adoption patterns show clear competitive advantages",
        "Customer acquisition costs vary significantly by strategic approach",
        "Partnership strategies emerge as critical success differentiators",
        "Market timing considerations significantly impact success probability",
        "Risk mitigation approaches show clear correlation with long-term success"
    ]

def generate_mock_organizer_analysis():
    """Generate realistic organizer analysis"""
    return {
        "React Presents": {
            "years_active": 8,
            "total_events": 24,
            "success_rate": 0.85,
            "avg_attendance": 45000,
            "assessment": "HIGHLY RECOMMENDED: Strong strategic partner candidate with proven track record. Factors: Highly established (5+ years), High success rate (80%+), High event volume (10+ events)"
        },
        "LiveStyle": {
            "years_active": 5,
            "total_events": 12,
            "success_rate": 0.75,
            "avg_attendance": 28000,
            "assessment": "RECOMMENDED: Solid operational capability with room for growth. Factors: Highly established (5+ years), Moderate success rate (60-79%), Moderate event volume (5-9 events)"
        },
        "C3 Presents": {
            "years_active": 12,
            "total_events": 36,
            "success_rate": 0.90,
            "avg_attendance": 65000,
            "assessment": "HIGHLY RECOMMENDED: Industry leader with exceptional track record. Factors: Highly established (5+ years), High success rate (80%+), High event volume (10+ events)"
        }
    }

def generate_mock_recommendations():
    """Generate strategic recommendations"""
    return [
        "PARTNERSHIP STRATEGY: Engage with React Presents for co-promotion opportunities leveraging their 8-year market presence",
        "VENUE STRATEGY: Secure 2-3 year venue commitments to reduce operational costs and improve logistics planning",
        "PROGRAMMING STRATEGY: Develop diverse lineup curation balancing mainstream appeal with niche electronic subgenres",
        "TIMING STRATEGY: Target shoulder seasons (June, September) to avoid peak summer competition",
        "COMMUNITY STRATEGY: Build year-round engagement through monthly events and social media presence",
        "CONTINGENCY STRATEGY: Implement comprehensive weather backup plans for outdoor events",
        "PRICING STRATEGY: Position tickets in $199-449 range to balance accessibility with premium experience",
        "MARKETING STRATEGY: Achieve 50K+ social media followers before major event announcements"
    ]

def render_research_results(research_results):
    """Render comprehensive research results"""
    
    st.markdown("### 📊 Research Results")
    
    # Status banner
    st.markdown(f"""
    <div class="status-completed">
        ✅ Research Completed Successfully - Session ID: {research_results['session_id']}
    </div>
    """, unsafe_allow_html=True)
    
    # Results summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    analysis = research_results.get("analysis", {})
    
    with col1:
        st.metric(
            "Sources Analyzed",
            analysis.get("sources_analyzed", 0),
            help="Number of web sources researched and analyzed"
        )
    
    with col2:
        st.metric(
            "Insights Generated", 
            analysis.get("insights_generated", 0),
            help="Key insights and findings extracted"
        )
    
    with col3:
        st.metric(
            "Research Depth",
            research_results["parameters"]["depth"],
            help="Number of research iteration rounds completed"
        )
    
    with col4:
        st.metric(
            "Research Breadth",
            research_results["parameters"]["breadth"], 
            help="Number of queries analyzed per iteration"
        )
    
    # Tabbed results display
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Executive Summary", 
        "🔍 Key Findings", 
        "🏢 Organizer Analysis", 
        "💡 Recommendations",
        "📁 Download Reports"
    ])
    
    with tab1:
        st.markdown("#### Executive Summary")
        st.markdown(f"""
        <div class="research-card">
            <pre style="white-space: pre-wrap; font-family: 'Georgia', serif; line-height: 1.6;">
{analysis.get("executive_summary", "No executive summary available.")}
            </pre>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("#### Key Research Findings")
        findings = analysis.get("key_findings", [])
        
        for i, finding in enumerate(findings, 1):
            st.markdown(f"""
            <div class="research-card">
                <strong>{i}.</strong> {finding}
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("#### Organizer Analysis")
        
        organizer_analysis = analysis.get("organizer_analysis", {})
        
        if organizer_analysis:
            # Create data for table
            org_data = []
            for org_name, org_info in organizer_analysis.items():
                org_data.append({
                    "Organizer": org_name,
                    "Years Active": org_info.get("years_active", "N/A"),
                    "Total Events": org_info.get("total_events", "N/A"),
                    "Success Rate": f"{org_info.get('success_rate', 0):.1%}",
                    "Avg Attendance": f"{org_info.get('avg_attendance', 0):,}"
                })
            
            # Display as dataframe
            import pandas as pd
            df = pd.DataFrame(org_data)
            st.dataframe(df, use_container_width=True)
            
            # Detailed assessments
            st.markdown("##### Detailed Assessments")
            for org_name, org_info in organizer_analysis.items():
                with st.expander(f"📊 {org_name} Assessment"):
                    st.write(org_info.get("assessment", "No assessment available."))
        else:
            st.info("No organizer analysis available for this research query.")
    
    with tab4:
        st.markdown("#### Strategic Recommendations")
        recommendations = analysis.get("recommendations", [])
        
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"""
            <div class="research-card">
                <strong>{i}.</strong> {rec}
            </div>
            """, unsafe_allow_html=True)
    
    with tab5:
        st.markdown("#### Download Research Reports")
        
        st.markdown("""
        <div class="download-section">
            <h4>📁 Professional Fortune-500 Level Presentation</h4>
            <p>Your research has been compiled into a board-ready presentation with comprehensive graphics and strategic analysis:</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if we have the actual presentation file
        presentation_path = research_results.get("presentation_path")
        
        if presentation_path and Path(presentation_path).exists():
            # Show download for actual Fortune-500 presentation
            st.success("📊 **Professional Fortune-500 Level Presentation Created!**")
            
            with st.container():
                st.markdown("### 📋 **DELIVERABLE: Board-Level Research Presentation**")
                
                try:
                    with open(presentation_path, 'rb') as f:
                        presentation_data = f.read()
                    
                    file_name = Path(presentation_path).name
                    file_ext = Path(presentation_path).suffix.lower()
                    
                    if file_ext == '.pdf':
                        mime_type = 'application/pdf'
                        icon = "📄"
                        description = "Professional PDF with charts, graphs, and executive analysis"
                    else:
                        mime_type = 'text/markdown'
                        icon = "📝"
                        description = "Comprehensive markdown report with strategic insights"
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.download_button(
                            label=f"{icon} **Download Professional Research Presentation**",
                            data=presentation_data,
                            file_name=file_name,
                            mime=mime_type,
                            use_container_width=True
                        )
                    
                    with col2:
                        st.info(f"📁 **File**: `{file_name}`\n💾 **Size**: {len(presentation_data)/1024:.1f} KB\n📊 **Type**: {description}")
                        
                except Exception as e:
                    st.error(f"Error creating download: {e}")
                    st.info(f"📁 **Presentation created at**: `{presentation_path}`")
        
        else:
            # Fallback for mock results
            st.warning("📊 Research completed but Fortune-500 presentation file not available")
            st.info("The research was completed using mock data. For full Fortune-500 level presentations with professional graphics and charts, ensure all dependencies are installed.")
            
            # Show mock download options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class="research-card">
                    <h5>📄 Fortune-500 PDF</h5>
                    <p>Professional presentation with charts and executive summary</p>
                </div>
                """, unsafe_allow_html=True)
                st.button("📄 Download PDF (Mock)", key="download_pdf_mock", disabled=True)
            
            with col2:
                st.markdown("""
                <div class="research-card">
                    <h5>📝 Strategic Report</h5>
                    <p>Comprehensive analysis in markdown format</p>
                </div>
                """, unsafe_allow_html=True)
                st.button("📝 Download Report (Mock)", key="download_md_mock", disabled=True)
            
            with col3:
                st.markdown("""
                <div class="research-card">
                    <h5>📊 Data Export</h5>
                    <p>Raw research data for further analysis</p>
                </div>
                """, unsafe_allow_html=True)
                st.button("📊 Download Data (Mock)", key="download_json_mock", disabled=True)

def main():
    """Main Deep Research page function"""
    
    st.title("🔍 Deep Research Agent")
    st.markdown("**Professional AI-powered research with real web scraping using WebcrawlerAPI**")
    
    # System status check
    if not DEEP_RESEARCH_AVAILABLE:
        st.error("🚨 Deep Research system is not available. Please check dependencies.")
        st.info("Required: bs4, requests-html, reportlab, openai (optional)")
        return
    
    # Session state for research results
    if "research_results" not in st.session_state:
        st.session_state.research_results = None
    
    if "research_running" not in st.session_state:
        st.session_state.research_running = False
    
    # Main interface
    if not st.session_state.research_running and st.session_state.research_results is None:
        
        # Quick start templates
        template_choice = render_quick_start_templates()
        
        # Handle template selection
        if template_choice == "chicago_edm":
            # Auto-populate Chicago EDM research
            st.session_state.research_running = True
            
            # Chicago EDM specific configuration
            research_config = {
                "query": ("Research upcoming electronic music festivals happening in Chicago this summer. "
                         "Find organizers who have been throwing events for more than 2 years and analyze "
                         "their past event success patterns to identify what works and what doesn't. "
                         "Focus on attendance data, success rates, venue partnerships, and provide "
                         "strategic recommendations for new event organizers."),
                "depth": 3,
                "breadth": 5,
                "output_format": "All Formats",
                "use_ai": True,
                "visualizations": True,
                "output_dir": "research_output",
                "openai_key": ""
            }
            
            # Run the research
            results = run_async_research(research_config)
            if results:
                st.session_state.research_results = results
                st.session_state.research_running = False
                st.rerun()
        
        elif template_choice:
            st.info(f"Template '{template_choice}' selected. Implementation coming soon!")
        
        # Custom research form
        st.markdown("---")
        custom_config = render_custom_research_form()
        
        if custom_config:
            st.session_state.research_running = True
            
            # Run custom research
            results = run_async_research(custom_config)
            if results:
                st.session_state.research_results = results
                st.session_state.research_running = False
                st.rerun()
    
    elif st.session_state.research_results:
        # Display results
        render_research_results(st.session_state.research_results)
        
        # Reset button
        if st.button("🔄 Start New Research", type="primary", use_container_width=True):
            st.session_state.research_results = None
            st.session_state.research_running = False
            st.rerun()
    
    # Sidebar with recent research
    with st.sidebar:
        st.markdown("### 🕒 Recent Research")
        
        if CONTENT_FEED_AVAILABLE:
            # Display recent research jobs from content feed
            st.markdown("Recent research sessions will appear here...")
        else:
            st.info("Content feed integration not available")
        
        st.markdown("### ℹ️ About Deep Research")
        st.markdown("""
        **Deep Research** uses advanced AI and web scraping to conduct comprehensive market research:
        
        - **Multi-depth Analysis**: Iterative research refinement
        - **Comprehensive Sources**: Web scraping across multiple platforms  
        - **AI Analysis**: Pattern recognition and insight extraction
        - **Professional Reports**: PDF, Markdown, and JSON outputs
        - **Strategic Intelligence**: Actionable recommendations
        
        Perfect for:
        - Market analysis
        - Competitor research  
        - Industry trends
        - Event planning
        - Strategic planning
        """)

if __name__ == "__main__":
    main() 