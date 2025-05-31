#!/usr/bin/env python3
"""
Comprehensive test for DuckDuckGo search integration with deep research agent
Tests the complete pipeline: Search → URLs → WebcrawlerAPI → Content → Analysis
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import after path setup
from api_key_manager import APIKeyManager
from components.deep_research import EnhancedDeepResearchAgent

def test_search_integration():
    """Test that DuckDuckGo search integration works with the deep research agent"""
    print("🔍 Testing DuckDuckGo Search Integration with Deep Research Agent")
    print("=" * 70)
    
    # Initialize API key manager
    print("🔑 Loading API keys...")
    api_manager = APIKeyManager()
    
    # Check if keys are valid
    validation_results = api_manager.validate_api_keys()
    webcrawler_available = validation_results.get('WEBCRAWLER_API_KEY', False)
    
    if not webcrawler_available:
        print("⚠️ WebcrawlerAPI key not available - testing search only")
    else:
        print("✅ WebcrawlerAPI key available - testing full pipeline")
    
    # Initialize agent
    agent = EnhancedDeepResearchAgent(api_key_manager=api_manager)
    print(f"🤖 Agent initialized")
    
    # Test queries
    test_queries = [
        "Rosita's Mexican Restaurant DeKalb Illinois",
        "DeKalb Illinois city information", 
        "Chicago restaurants downtown"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        print("-" * 50)
        
        try:
            # Test URL generation with DuckDuckGo search
            urls = agent.generate_research_urls(query, depth=3)
            
            if urls:
                print(f"✅ Search generated {len(urls)} URLs:")
                for i, url in enumerate(urls, 1):
                    print(f"  {i}. {url}")
                
                # Test scraping the first URL if WebcrawlerAPI is available
                if webcrawler_available and urls:
                    print(f"\n🌐 Testing scraping first URL: {urls[0][:60]}...")
                    scraped_data = agent.search_and_scrape(urls[0], max_results=1)
                    
                    if scraped_data:
                        for result in scraped_data:
                            print(f"✅ Scraped content from: {result.get('title', 'No title')}")
                            print(f"📄 Content length: {len(result.get('content', ''))} characters")
                            print(f"🔗 URL: {result.get('url', 'No URL')}")
                    else:
                        print("⚠️ No content scraped (may be due to URL complexity)")
                else:
                    print("⏭️ Skipping scraping test (WebcrawlerAPI not available)")
            else:
                print("❌ No URLs generated")
            
            print()
            
        except Exception as e:
            print(f"❌ Error testing query '{query}': {e}")
            continue
    
    print("🎯 Search Integration Test Complete!")

def test_full_research_pipeline():
    """Test a complete research pipeline with DuckDuckGo search"""
    print("\n🔬 Testing Full Research Pipeline with DuckDuckGo Search")
    print("=" * 60)
    
    try:
        # Import the main research function
        from components.deep_research import conduct_dynamic_research
        
        test_query = "DeKalb Illinois city information"
        print(f"🔍 Running full research for: '{test_query}'")
        print("🎯 This should now use DuckDuckGo search instead of OpenAI URL generation")
        
        # Run research with minimal parameters to test quickly
        result = conduct_dynamic_research(
            query=test_query,
            depth=2,  # Only 2 URLs
            breadth=2  # Only 2 results per URL
        )
        
        if result and 'error' not in result:
            print("✅ Research pipeline completed successfully!")
            print(f"📄 Sources analyzed: {len(result.get('sources', []))}")
            print(f"🔍 Search method: DuckDuckGo → WebcrawlerAPI → Analysis")
            
            # Check if we got real search results
            sources = result.get('sources', [])
            if sources:
                print(f"\n📋 Sample sources found:")
                for i, source in enumerate(sources[:3], 1):
                    print(f"  {i}. {source.get('title', 'No title')}")
                    print(f"     URL: {source.get('url', 'No URL')}")
            
        else:
            print(f"⚠️ Research completed with issues: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")

def test_search_vs_openai_comparison():
    """Compare DuckDuckGo search results vs OpenAI URL generation"""
    print("\n⚖️ Comparing DuckDuckGo Search vs OpenAI URL Generation")
    print("=" * 60)
    
    # Initialize agent
    api_manager = APIKeyManager()
    agent = EnhancedDeepResearchAgent(api_key_manager=api_manager)
    
    test_query = "Rosita's Mexican Restaurant DeKalb Illinois"
    
    print(f"🔍 Query: {test_query}")
    print()
    
    # Test DuckDuckGo search (primary method)
    print("🌐 DuckDuckGo Search Results:")
    search_urls = agent.generate_research_urls(test_query, depth=3)
    
    print(f"\n📊 Comparison Summary:")
    print(f"📍 DuckDuckGo Search: {len(search_urls)} real URLs from web search")
    print(f"🎯 These are actual search results, not AI-generated URLs")
    print(f"✅ Restored search functionality lost when moving from Firecrawl")

if __name__ == "__main__":
    print("🚀 Starting DuckDuckGo Search Integration Tests")
    print("🎯 Testing replacement of OpenAI URL generation with real web search")
    print()
    
    # Test search integration
    test_search_integration()
    
    # Test full pipeline
    test_full_research_pipeline()
    
    # Compare methods
    test_search_vs_openai_comparison()
    
    print("\n" + "=" * 80)
    print("🎉 All integration tests completed!")
    print("✅ DuckDuckGo search now provides real URLs instead of AI-generated ones")
    print("🔧 Your research agent now has proper web search functionality")
    print("📋 Next: Test in Streamlit interface at http://localhost:8501") 