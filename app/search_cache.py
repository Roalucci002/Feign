"""
Search Result Caching System
キャッシュにより不要な検索を削減し、応答速度を向上
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class SearchCache:
    """検索結果のキャッシング管理"""
    
    def __init__(self, cache_dir: str = "./cache/search", ttl_hours: int = 24):
        """
        Initialize search cache
        
        Args:
            cache_dir: キャッシュディレクトリ
            ttl_hours: キャッシュの有効期限（時間）
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        self.memory_cache: Dict[str, Dict[str, Any]] = {}  # 高速アクセス用
    
    def _hash_query(self, query: str, language: str = "ja") -> str:
        """クエリをハッシュ化"""
        key = f"{query}:{language}".encode('utf-8')
        return hashlib.md5(key).hexdigest()
    
    def _get_cache_path(self, query_hash: str) -> Path:
        """キャッシュファイルパスを取得"""
        return self.cache_dir / f"{query_hash}.json"
    
    def get(self, query: str, language: str = "ja") -> Optional[Dict[str, Any]]:
        """
        キャッシュから検索結果を取得
        
        Args:
            query: 検索クエリ
            language: 言語
        
        Returns:
            キャッシュされた結果、または None
        """
        query_hash = self._hash_query(query, language)
        
        # メモリキャッシュを確認
        if query_hash in self.memory_cache:
            cached = self.memory_cache[query_hash]
            if self._is_valid(cached['timestamp']):
                logger.debug(f"Cache HIT (memory): {query}")
                return cached['results']
            else:
                del self.memory_cache[query_hash]
        
        # ファイルキャッシュを確認
        cache_path = self._get_cache_path(query_hash)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                
                if self._is_valid(cached['timestamp']):
                    logger.debug(f"Cache HIT (file): {query}")
                    # メモリキャッシュにも保存
                    self.memory_cache[query_hash] = cached
                    return cached['results']
                else:
                    # 期限切れキャッシュを削除
                    cache_path.unlink()
                    logger.debug(f"Cache expired: {query}")
            
            except Exception as e:
                logger.error(f"Error reading cache: {e}")
        
        return None
    
    def set(self, query: str, results: List[Dict], language: str = "ja") -> bool:
        """
        検索結果をキャッシュに保存
        
        Args:
            query: 検索クエリ
            results: 検索結果
            language: 言語
        
        Returns:
            True if successful
        """
        query_hash = self._hash_query(query, language)
        
        cached_data = {
            'query': query,
            'language': language,
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
        
        # メモリキャッシュに保存
        self.memory_cache[query_hash] = cached_data
        
        # ファイルに保存
        try:
            cache_path = self._get_cache_path(query_hash)
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cached_data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Cached: {query}")
            return True
        
        except Exception as e:
            logger.error(f"Error writing cache: {e}")
            return False
    
    def _is_valid(self, timestamp_str: str) -> bool:
        """キャッシュが有効か確認"""
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            return datetime.now() - timestamp < self.ttl
        except:
            return False
    
    def clear(self) -> None:
        """すべてのキャッシュを削除"""
        self.memory_cache.clear()
        
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """キャッシュの統計情報を取得"""
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files) / 1024  # KB
        
        return {
            'memory_cache_size': len(self.memory_cache),
            'file_cache_count': len(cache_files),
            'total_size_kb': round(total_size, 2),
            'ttl_hours': self.ttl.total_seconds() / 3600
        }


class SearchDecisionEngine:
    """検索が必要か判断するロジック"""
    
    def __init__(self):
        """Initialize decision rules"""
        self.time_indicators = [
            '今', '現在', '最新', 'latest', 'current', 'today',
            'yesterday', 'tomorrow', 'this week', 'this month',
            '昨日', '明日', '今週', '今月', 'news', 'ニュース',
            'update', 'updated', '更新', 'release', 'リリース'
        ]
        
        self.change_indicators = [
            'changed', '変わった', 'patch', 'パッチ', 'fix', '修正',
            'new', '新', 'deprecated', '廃止', 'removed', '削除',
            'added', '追加', 'version', 'バージョン'
        ]
        
        self.realtime_topics = [
            'price', '価格', 'stock', '在庫', 'available', '利用可能',
            'event', 'イベント', 'schedule', 'スケジュール', 'weather', '天気',
            'status', 'サービス状態', 'down', '障害', 'error', 'エラー'
        ]
        
        self.no_search_patterns = [
            'feel', '感じ', 'think', '思う', 'opinion', '意見',
            'joke', 'ジョーク', 'funny', '面白', 'like', 'が好き',
            'hate', 'が嫌', 'personal', '個人的', 'preference', '好み'
        ]
    
    def should_search(self, query: str, conversation_context: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        検索の必要性を判定
        
        Args:
            query: ユーザー質問
            conversation_context: 会話履歴（オプション）
        
        Returns:
            {
                'should_search': bool,
                'reason': str,
                'priority': int (0-10),
                'type': str ('realtime', 'factual', 'optional', 'unnecessary')
            }
        """
        query_lower = query.lower()
        
        # 1. 検索不要なパターンをチェック
        for pattern in self.no_search_patterns:
            if pattern in query_lower:
                return {
                    'should_search': False,
                    'reason': f'Personal opinion/feeling detected: "{pattern}"',
                    'priority': 0,
                    'type': 'unnecessary'
                }
        
        # 2. リアルタイム情報（最優先）
        for indicator in self.realtime_topics:
            if indicator in query_lower:
                return {
                    'should_search': True,
                    'reason': f'Realtime topic detected: "{indicator}"',
                    'priority': 10,
                    'type': 'realtime'
                }
        
        # 3. 時間指標（最新情報が必要）
        for indicator in self.time_indicators:
            if indicator in query_lower:
                return {
                    'should_search': True,
                    'reason': f'Time indicator detected: "{indicator}"',
                    'priority': 9,
                    'type': 'factual'
                }
        
        # 4. 変更情報（パッチ、アップデート等）
        for indicator in self.change_indicators:
            if indicator in query_lower:
                return {
                    'should_search': True,
                    'reason': f'Change indicator detected: "{indicator}"',
                    'priority': 8,
                    'type': 'factual'
                }
        
        # 5. URLが含まれている？
        if 'http' in query_lower or 'www' in query_lower:
            return {
                'should_search': False,
                'reason': 'URL reference detected',
                'priority': 0,
                'type': 'unnecessary'
            }
        
        # 6. 会話からの判断
        if conversation_context and len(conversation_context) > 0:
            last_messages = conversation_context[-3:]  # 直近3メッセージ
            if any('searched' in msg.lower() or 'found' in msg.lower() 
                   for msg in last_messages):
                return {
                    'should_search': False,
                    'reason': 'Recent search context exists',
                    'priority': 2,
                    'type': 'optional'
                }
        
        # デフォルト: 判断留保（キャッシュで十分かもしれない）
        return {
            'should_search': False,
            'reason': 'No clear search indicators',
            'priority': 3,
            'type': 'optional'
        }
    
    def get_urgency_score(self, decision: Dict[str, Any]) -> float:
        """
        検索の緊急度スコアを計算（0.0-1.0）
        
        Args:
            decision: search_decision 結果
        
        Returns:
            Urgency score
        """
        priority = decision.get('priority', 0)
        return min(1.0, priority / 10.0)
