"""
Multi-Engine Search Provider
複数の検索エンジンを統合し、最適なものを自動選択
"""

import logging
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class SearchProvider(ABC):
    """検索エンジンの基底クラス"""
    
    def __init__(self, name: str, base_url: str, timeout: int = 10):
        self.name = name
        self.base_url = base_url
        self.timeout = timeout
        self.available = False
        self._check_connection()
    
    @abstractmethod
    def search(self, query: str, language: str = "ja", max_results: int = 10) -> List[Dict]:
        """検索を実行"""
        pass
    
    @abstractmethod
    def _check_connection(self) -> bool:
        """接続確認"""
        pass
    
    def format_result(self, title: str, url: str, content: str, engine: str) -> Dict:
        """結果をフォーマット"""
        return {
            'title': title,
            'url': url,
            'content': content,
            'engine': engine,
            'timestamp': datetime.now().isoformat()
        }


class SearXNGProvider(SearchProvider):
    """SearXNG統合プロバイダー"""
    
    def __init__(self, base_url: str = "http://localhost:8888", timeout: int = 10):
        super().__init__("SearXNG", base_url, timeout)
    
    def _check_connection(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            self.available = response.status_code == 200
            if self.available:
                logger.info(f"✓ {self.name} connected")
            else:
                logger.warning(f"✗ {self.name} connection failed")
            return self.available
        except Exception as e:
            logger.warning(f"{self.name} error: {e}")
            self.available = False
            return False
    
    def search(self, query: str, language: str = "ja", max_results: int = 10) -> List[Dict]:
        """SearXNGで検索"""
        if not self.available:
            return []
        
        try:
            params = {
                'q': query,
                'format': 'json',
                'language': language,
                'pageno': 1,
                'safesearch': 0
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
                    formatted = self.format_result(
                        title=result.get('title', 'Unknown'),
                        url=result.get('url', ''),
                        content=result.get('content', ''),
                        engine=self.name
                    )
                    # エンジン情報を追加
                    formatted['sources'] = result.get('engines', [])
                    results.append(formatted)
                
                logger.info(f"{self.name}: {len(results)} results")
                return results
            else:
                logger.error(f"{self.name} error: {response.status_code}")
                return []
        
        except Exception as e:
            logger.error(f"{self.name} search error: {e}")
            return []


class MetaSearchEngine:
    """複数エンジンを統合する検索エンジン"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize meta search engine
        
        Args:
            config: 検索設定（config/search.jsonから）
        """
        self.config = config or {}
        self.providers: Dict[str, SearchProvider] = {}
        self.primary_provider = "searxng_local"
        self._initialize_providers()
    
    def _initialize_providers(self):
        """プロバイダーを初期化"""
        # SearXNG
        searxng_config = self.config.get('searxng_local', {})
        if searxng_config.get('enabled', True):
            provider = SearXNGProvider(
                base_url=searxng_config.get('base_url', 'http://localhost:8888'),
                timeout=searxng_config.get('timeout', 10)
            )
            self.providers['searxng_local'] = provider
        
        logger.info(f"Initialized {len(self.providers)} search provider(s)")
    
    def search(self, query: str, language: str = "ja", max_results: int = 10) -> Dict[str, Any]:
        """
        統合検索を実行
        
        Args:
            query: 検索クエリ
            language: 言語
            max_results: 最大結果数
        
        Returns:
            {
                'query': str,
                'results': List[Dict],
                'total_results': int,
                'engines_used': List[str],
                'timestamp': str
            }
        """
        if not self.providers:
            logger.error("No search providers available")
            return {
                'query': query,
                'results': [],
                'total_results': 0,
                'engines_used': [],
                'timestamp': datetime.now().isoformat()
            }
        
        all_results = []
        engines_used = []
        
        # プライマリプロバイダーで検索
        if self.primary_provider in self.providers:
            provider = self.providers[self.primary_provider]
            if provider.available:
                results = provider.search(query, language, max_results)
                all_results.extend(results)
                engines_used.append(self.primary_provider)
        
        # 結果が少ない場合は他のプロバイダーも試す
        if len(all_results) < max_results // 2:
            for name, provider in self.providers.items():
                if name != self.primary_provider and provider.available:
                    results = provider.search(query, language, max_results)
                    all_results.extend(results)
                    engines_used.append(name)
                    if len(all_results) >= max_results:
                        break
        
        # 重複を削除（URL比較）
        unique_results = []
        seen_urls = set()
        for result in all_results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                unique_results.append(result)
                seen_urls.add(url)
        
        return {
            'query': query,
            'results': unique_results[:max_results],
            'total_results': len(unique_results),
            'engines_used': engines_used,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_provider_status(self) -> Dict[str, bool]:
        """プロバイダーの状態を取得"""
        return {name: provider.available 
                for name, provider in self.providers.items()}
    
    def set_primary_provider(self, provider_name: str) -> bool:
        """プライマリプロバイダーを変更"""
        if provider_name in self.providers:
            self.primary_provider = provider_name
            logger.info(f"Primary provider set to: {provider_name}")
            return True
        else:
            logger.error(f"Provider not found: {provider_name}")
            return False
