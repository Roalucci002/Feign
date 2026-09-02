import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class SearchManager:
    """Web検索管理（SearXNG統合）"""
    
    def __init__(self, base_url: str = "http://localhost:8888", timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.available = False
        self._check_connection()
    
    def _check_connection(self) -> bool:
        """SearXNG への接続確認"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            self.available = response.status_code == 200
            if self.available:
                logger.info("✓ Connected to SearXNG")
            return self.available
        except Exception as e:
            logger.warning(f"SearXNG not available: {e}")
            self.available = False
            return False
    
    def search(self, query: str, language: str = "ja", max_results: int = 10) -> List[Dict]:
        """Web検索を実行"""
        if not self.available:
            logger.warning("Search not available")
            return []
        
        try:
            params = {
                'q': query,
                'format': 'json',
                'language': language,
                'pageno': 1
            }
            
            response = requests.get(
                f"{self.base_url}/search",
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                for result in data.get('results', [])[:max_results]:
                    results.append({
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'content': result.get('content', ''),
                        'engine': result.get('engine', []),
                        'timestamp': datetime.now().isoformat()
                    })
                logger.info(f"Search results: {len(results)} items")
                return results
            else:
                logger.error(f"Search error: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error performing search: {e}")
            return []
    
    def rate_source(self, result: Dict) -> Dict[str, any]:
        """情報源の信頼度を評価"""
        url = result.get('url', '')
        
        score = 0.5
        if 'official' in url.lower() or 'github.com' in url:
            score = 0.95
        elif 'wikipedia' in url or 'wiki' in url:
            score = 0.8
        elif 'reddit' in url or 'twitter' in url:
            score = 0.5
        elif 'blog' in url:
            score = 0.4
        
        confidence = 'MEDIUM'
        if score > 0.9:
            confidence = 'HIGH'
        elif score < 0.5:
            confidence = 'LOW'
        
        return {
            'url': url,
            'credibility_score': score,
            'confidence': confidence,
            'verified': score > 0.8
        }

search_manager = SearchManager()
