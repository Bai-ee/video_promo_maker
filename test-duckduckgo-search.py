#!/usr/bin/env python3
"""
Test script to verify DuckDuckGo search integration
Tests the search functionality that will replace OpenAI URL generation
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_duckduckgo_search():
    """Test DuckDuckGo search functionality"""
    print("🔍 Testing DuckDuckGo Search Integration")
    print("=" * 50)
    
    try:
        from duckduckgo_search import DDGS
        print("✅ DuckDuckGo-search imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import duckduckgo-search: {e}")
        return False
    
    # Test queries
    test_queries = [
        "Rosita's Mexican Restaurant DeKalb Illinois",
        "DeKalb Illinois city information",
        "Chicago restaurants downtown",
        "Northern Illinois University campus"
    ]
    
    def search_for_urls(query, max_results=3):
        """Search DuckDuckGo and return URLs"""
        try:
            print(f"\n🔍 Searching: '{query}'")
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=max_results)
                urls = []
                for result in results:
                    if result.get('href'):
                        urls.append({
                            'url': result['href'],
                            'title': result.get('title', 'No title'),
                            'snippet': result.get('body', 'No snippet')[:100] + '...'
                        })
                return urls
        except Exception as e:
            print(f"❌ Search failed for '{query}': {e}")
            return []
    
    all_successful = True
    
    for query in test_queries:
        try:
            urls = search_for_urls(query, max_results=3)
            
            if urls:
                print(f"✅ Found {len(urls)} results:")
                for i, result in enumerate(urls, 1):
                    print(f"  {i}. {result['title']}")
                    print(f"     URL: {result['url']}")
                    print(f"     Snippet: {result['snippet']}")
                    print()
            else:
                print(f"⚠️ No results found for: {query}")
                all_successful = False
                
        except Exception as e:
            print(f"❌ Error testing query '{query}': {e}")
            all_successful = False
    
    print("\n" + "=" * 50)
    if all_successful:
        print("🎉 All DuckDuckGo search tests passed!")
        print("✅ Ready to integrate with deep research agent")
    else:
        print("⚠️ Some tests failed - check network connection")
    
    return all_successful

def test_integration_function():
    """Test the exact function we'll use in the deep research agent"""
    print("\n🔧 Testing Integration Function")
    print("-" * 30)
    
    def get_search_urls(search_query, max_urls=3):
        """Convert search query to list of URLs - exact function for integration"""
        try:
            from duckduckgo_search import DDGS
            print(f"🔍 Searching for: {search_query}")
            
            with DDGS() as ddgs:
                results = ddgs.text(search_query, max_results=max_urls)
                urls = [result['href'] for result in results if result.get('href')]
                
            print(f"🔗 Found {len(urls)} URLs:")
            for i, url in enumerate(urls, 1):
                print(f"  {i}. {url}")
            
            return urls
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    # Test the exact function
    test_query = "Rosita's Mexican Restaurant DeKalb Illinois"
    urls = get_search_urls(test_query)
    
    if urls:
        print(f"✅ Integration function working - returned {len(urls)} URLs")
        return True
    else:
        print("❌ Integration function failed")
        return False

if __name__ == "__main__":
    print("🚀 Starting DuckDuckGo Search Tests")
    print("🎯 This will replace OpenAI URL generation with real web search")
    print()
    
    # Test basic search functionality
    basic_test = test_duckduckgo_search()
    
    # Test integration function
    integration_test = test_integration_function()
    
    print("\n" + "=" * 60)
    if basic_test and integration_test:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Ready to replace OpenAI URL generation with DuckDuckGo search")
        print("🔧 Next step: Update deep_research.py with search integration")
    else:
        print("❌ Some tests failed")
        print("🔧 Check internet connection and try again") 