#!/usr/bin/env python3
"""
🌐 Enhanced Web Crawler with WebcrawlerAPI ONLY
Primary: WebcrawlerAPI (unlimited trial) - SINGLE PROVIDER
"""

import os
import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class CrawlResult:
    """Structured result from web crawling"""
    url: str
    title: str
    content: str
    success: bool
    provider: str
    error_message: Optional[str] = None

class EnhancedWebCrawler:
    """Single-provider web crawler using WebcrawlerAPI ONLY"""
    
    def __init__(self, api_key_manager=None):
        self.setup_logging()
        
        # API Key - WebcrawlerAPI ONLY
        self.webcrawler_api_key = os.getenv("WEBCRAWLER_API_KEY", "b0a58413f6d2d8acb2bd")
        
        # Single provider system
        self.provider = "webcrawlerapi"
        self.api_key_manager = api_key_manager
        
        self.logger.info("🌐 Enhanced Web Crawler initialized")
        self.logger.info(f"📡 WebcrawlerAPI: {'✅ Available' if self.webcrawler_api_key else '❌ Missing'}")
    
    def setup_logging(self):
        """Configure logging for web crawler operations"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def search_and_scrape(self, query: str, max_results: int = 5) -> List[CrawlResult]:
        """
        Search and scrape web content using WebcrawlerAPI ONLY
        
        Args:
            query: Search query string or URL
            max_results: Maximum number of results to return
            
        Returns:
            List of CrawlResult objects with scraped content
        """
        self.logger.info(f"🌐 Searching: {query}")
        
        try:
            results = self._search_webcrawlerapi(query, max_results)
            
            if results and any(r.success for r in results):
                self.logger.info(f"✅ Success with webcrawlerapi: {len([r for r in results if r.success])} results")
                return results
            elif results:
                # Provider returned results but they failed
                failed_results = [r for r in results if not r.success]
                if failed_results:
                    self.logger.warning(f"⚠️ webcrawlerapi returned failed results: {failed_results[0].error_message}")
            
        except Exception as e:
            self.logger.error(f"❌ webcrawlerapi failed: {e}")
            
            # Try automatic key rotation if quota exhausted
            if self.api_key_manager and "402" in str(e):
                self.logger.info(f"💳 Attempting webcrawlerapi key rotation...")
                self.api_key_manager.rotate_api_key("WEBCRAWLER_API_KEY")
        
        self.logger.error(f"❌ WebcrawlerAPI failed for query: {query}")
        return []
    
    def _search_webcrawlerapi(self, query: str, max_results: int) -> List[CrawlResult]:
        """Search using WebcrawlerAPI - ONLY provider"""
        if not self.webcrawler_api_key:
            raise Exception("WebcrawlerAPI key not available")
        
        self.logger.info(f"🔍 WebcrawlerAPI: Searching '{query}'...")
        
        # Use direct crawling for specific URLs or general search
        if query.startswith("http"):
            return self._crawl_webcrawlerapi_url(query)
        else:
            return self._search_webcrawlerapi_general(query, max_results)
    
    def _search_webcrawlerapi_general(self, query: str, max_results: int) -> List[CrawlResult]:
        """General search using WebcrawlerAPI - try multiple relevant URLs"""
        # For general queries, construct relevant URLs to crawl
        search_urls = []
        
        # Wikipedia URLs
        clean_query = query.replace(' ', '_')
        search_urls.append(f"https://en.wikipedia.org/wiki/{clean_query}")
        
        # Business-specific URLs
        if any(word in query.lower() for word in ['restaurant', 'cafe', 'bar', 'food', 'business']):
            # Extract business name and location
            words = query.lower().split()
            location = None
            business_name = query
            
            # Find location
            location_words = ['chicago', 'dekalb', 'illinois', 'il']
            for word in words:
                if word in location_words:
                    location = word
                    break
            
            if location:
                # Clean business name
                business_name = query.lower()
                for loc_word in location_words:
                    business_name = business_name.replace(loc_word, '').strip()
                
                # Add Yelp URL
                yelp_name = business_name.replace(' ', '-')
                search_urls.append(f"https://www.yelp.com/biz/{yelp_name}-{location}")
                
                # Add TripAdvisor URL
                search_urls.append(f"https://www.tripadvisor.com/Restaurant_Review-g{location}")
        
        # Local business directory URLs
        if any(word in query.lower() for word in ['dekalb', 'chicago']):
            location = 'dekalb' if 'dekalb' in query.lower() else 'chicago'
            search_urls.append(f"https://www.yellowpages.com/search?search_terms={query.replace(' ', '+')}&geo_location_terms={location}")
        
        results = []
        for url in search_urls[:max_results]:
            try:
                result = self._crawl_webcrawlerapi_url(url)
                if result and result[0].success:
                    results.extend(result)
                    if len(results) >= max_results:
                        break
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to crawl {url}: {e}")
                continue
        
        return results[:max_results]
    
    def _crawl_webcrawlerapi_url(self, url: str) -> List[CrawlResult]:
        """Crawl URL using WebcrawlerAPI v1/crawl endpoint"""
        headers = {
            "Authorization": f"Bearer {self.webcrawler_api_key}",
            "Content-Type": "application/json"
        }
        
        # Use v1/crawl endpoint with proper parameters
        payload = {
            "url": url,
            "scrape_type": "markdown",
            "items_limit": 1  # For single URL crawling
        }
        
        try:
            # Step 1: Start crawl job
            response = requests.post(
                "https://api.webcrawlerapi.com/v1/crawl",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            self.logger.debug(f"WebcrawlerAPI crawl response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                job_id = data.get("id")
                
                if not job_id:
                    raise Exception("No job ID returned from crawl request")
                
                # Step 2: Poll for job completion
                return self._wait_for_webcrawler_job(job_id, url)
                
            elif response.status_code == 402:
                raise Exception("Payment Required: WebcrawlerAPI quota exhausted")
            elif response.status_code == 400:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('error_message', f'Bad Request: {response.text[:200]}')
                raise Exception(f"Bad Request: {error_msg}")
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"WebcrawlerAPI request failed: {e}")
    
    def _wait_for_webcrawler_job(self, job_id: str, original_url: str, max_wait: int = 60) -> List[CrawlResult]:
        """Wait for WebcrawlerAPI job completion and retrieve results"""
        headers = {
            "Authorization": f"Bearer {self.webcrawler_api_key}"
        }
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(
                    f"https://api.webcrawlerapi.com/v1/job/{job_id}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")
                    
                    if status == "done":
                        # Extract crawled content
                        job_items = data.get("job_items", [])
                        results = []
                        
                        for item in job_items:
                            # Get content from clean_content_url, raw_content_url, or markdown_content_url
                            content_url = (item.get("clean_content_url") or 
                                         item.get("raw_content_url") or 
                                         item.get("markdown_content_url"))
                            if content_url:
                                try:
                                    content_response = requests.get(content_url, timeout=10)
                                    content = content_response.text if content_response.status_code == 200 else ""
                                except:
                                    content = ""
                            else:
                                content = ""
                            
                            results.append(CrawlResult(
                                url=item.get("original_url", original_url),
                                title=item.get("page_title", "Untitled"),
                                content=content,
                                success=bool(content),
                                provider="webcrawlerapi"
                            ))
                        
                        return results
                    
                    elif status == "failed":
                        error_msg = data.get("error_message", "Job failed")
                        return [CrawlResult(
                            url=original_url,
                            title="Error",
                            content="",
                            success=False,
                            provider="webcrawlerapi",
                            error_message=error_msg
                        )]
                    
                    elif status in ["pending", "running", "in_progress"]:
                        # Job still processing, wait and retry
                        self.logger.debug(f"Job {job_id} status: {status}, waiting...")
                        time.sleep(2)
                        continue
                    
                else:
                    raise Exception(f"HTTP {response.status_code}: {response.text[:200]}")
                    
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Error checking job status: {e}")
                time.sleep(2)
                continue
        
        # Timeout reached
        return [CrawlResult(
            url=original_url,
            title="Timeout",
            content="",
            success=False,
            provider="webcrawlerapi",
            error_message="Job timeout after 60 seconds"
        )]

    def _generate_urls_for_query(self, query: str) -> List[str]:
        """Generate specific URLs to crawl based on the query"""
        urls = []
        
        # Clean query for URL generation
        clean_query = query.lower().replace(' ', '_')
        query_words = query.lower().split()
        
        # Wikipedia URLs - try different variations
        urls.append(f"https://en.wikipedia.org/wiki/{clean_query}")
        
        # For business queries, try multiple approaches
        if any(word in query.lower() for word in ['restaurant', 'cafe', 'bar', 'food', 'business']):
            # Extract business name and location
            location = None
            business_name = query.lower()
            
            # Find location words
            location_words = ['chicago', 'dekalb', 'illinois', 'il', 'in']
            for word in query_words:
                if word in location_words:
                    location = word
                    business_name = business_name.replace(word, '').strip()
                    break
            
            # Clean business name
            business_name = business_name.replace('restaurant', '').replace('cafe', '').replace('bar', '').strip()
            business_name = business_name.replace('"', '').replace("'s", 's').strip()
            
            if location and business_name:
                # Yelp URLs - multiple formats
                yelp_name = business_name.replace(' ', '-')
                urls.append(f"https://www.yelp.com/biz/{yelp_name}-{location}")
                urls.append(f"https://www.yelp.com/biz/{yelp_name}-{location}-il")
                
                # Google Business listings
                google_query = f"{business_name} {location}".replace(' ', '+')
                urls.append(f"https://www.google.com/search?q={google_query}")
                
                # TripAdvisor
                urls.append(f"https://www.tripadvisor.com/Restaurant_Review-{location}")
                
                # For DeKalb specifically, try NIU/local sites
                if location in ['dekalb', 'de kalb']:
                    urls.append(f"https://www.cityofdekalb.com")
                    urls.append(f"https://www.niu.edu")
                    
        # Location-based searches
        if any(word in query.lower() for word in ['dekalb', 'chicago', 'illinois']):
            location = 'dekalb' if 'dekalb' in query.lower() else 'chicago'
            search_term = query.replace(' ', '+')
            urls.append(f"https://www.yellowpages.com/search?search_terms={search_term}&geo_location_terms={location}")
            
            # City websites
            if 'dekalb' in query.lower():
                urls.append("https://www.cityofdekalb.com")
                urls.append("https://www.niu.edu/dining")
            elif 'chicago' in query.lower():
                urls.append("https://www.chicago.gov")
        
        # Fallback: Try constructing simple domain names
        if len(query_words) >= 2:
            # Try domain variations
            domain_name = ''.join(query_words[:2])
            urls.append(f"https://www.{domain_name}.com")
            urls.append(f"https://{domain_name}.com")
        
        # Remove duplicates and return limited set
        unique_urls = []
        for url in urls:
            if url not in unique_urls and len(unique_urls) < 5:
                unique_urls.append(url)
        
        return unique_urls

def create_enhanced_crawler(api_key_manager=None) -> EnhancedWebCrawler:
    """Factory function to create enhanced web crawler"""
    return EnhancedWebCrawler(api_key_manager=api_key_manager) 