#!/usr/bin/env python3
"""
Debug script to test URL generation for the failing query
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api_key_manager import APIKeyManager
from components.deep_research import EnhancedDeepResearchAgent

def debug_url_generation():
    """Debug the exact URL generation issue"""
    print("🐛 Debugging URL Generation Issue")
    print("=" * 50)
    
    # Initialize agent exactly like the failed query
    api_manager = APIKeyManager()
    agent = EnhancedDeepResearchAgent(api_key_manager=api_manager)
    
    # Test the exact query that failed
    test_query = "deep research tony kongton in hawaii"
    print(f"🔍 Testing query: '{test_query}'")
    print()
    
    # Check what method is being called
    print("🔧 Calling generate_research_urls() directly...")
    try:
        urls = agent.generate_research_urls(test_query, depth=3)
        print(f"📋 URLs returned: {urls}")
        print(f"📊 Number of URLs: {len(urls) if urls else 0}")
        
        if urls:
            print("✅ URL generation working!")
            for i, url in enumerate(urls, 1):
                print(f"  {i}. {url}")
        else:
            print("❌ No URLs generated - this is the issue!")
            
    except Exception as e:
        print(f"💥 Error in URL generation: {e}")
        import traceback
        traceback.print_exc()

def test_duckduckgo_directly():
    """Test DuckDuckGo search directly"""
    print("\n🔍 Testing DuckDuckGo Search Directly")
    print("=" * 40)
    
    try:
        from duckduckgo_search import DDGS
        print("✅ DuckDuckGo import successful")
        
        query = "tony kongton hawaii"
        print(f"🔍 Searching for: {query}")
        
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=3)
            urls = [result['href'] for result in results if result.get('href')]
            
        print(f"📋 Found {len(urls)} URLs:")
        for i, url in enumerate(urls, 1):
            print(f"  {i}. {url}")
            
        return urls
        
    except Exception as e:
        print(f"❌ DuckDuckGo search failed: {e}")
        return []

def check_openai_fallback():
    """Check if OpenAI fallback is working"""
    print("\n🤖 Testing OpenAI Fallback")
    print("=" * 30)
    
    try:
        api_manager = APIKeyManager()
        agent = EnhancedDeepResearchAgent(api_key_manager=api_manager)
        
        if agent.ai_available:
            print("✅ OpenAI client available")
            
            # Test OpenAI fallback manually
            print("🔄 Testing OpenAI URL generation...")
            query = "tony kongton hawaii"
            
            response = agent.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a research expert. Generate 3 real URLs for research."
                    },
                    {
                        "role": "user", 
                        "content": f"Generate 3 real URLs about: {query}. Return only URLs, one per line."
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            urls_text = response.choices[0].message.content.strip()
            print(f"📄 OpenAI response: {urls_text}")
            
            urls = [url.strip() for url in urls_text.split('\n') if url.strip().startswith('http')]
            print(f"📋 Extracted URLs: {urls}")
            
        else:
            print("❌ OpenAI client not available")
            
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")

if __name__ == "__main__":
    debug_url_generation()
    test_duckduckgo_directly()
    check_openai_fallback()
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSIS COMPLETE")
    print("Check the output above to identify where the issue is occurring.") 