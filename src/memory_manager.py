import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib

logger = logging.getLogger(__name__)

class MemoryManager:
    """長期記憶管理システム"""
    
    def __init__(self, db_path: str = "./memory_db/rei_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_hash TEXT UNIQUE,
                memory_type TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_accessed DATETIME,
                access_count INTEGER DEFAULT 0,
                weight REAL DEFAULT 0.5,
                namespace TEXT DEFAULT 'rei',
                tags TEXT
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT,
                ai_response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                emotion_state TEXT,
                namespace TEXT DEFAULT 'rei'
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS emotion_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                affection REAL DEFAULT 0.5,
                trust REAL DEFAULT 0.5,
                mood REAL DEFAULT 0.5,
                energy REAL DEFAULT 0.7,
                loneliness REAL DEFAULT 0.3,
                playfulness REAL DEFAULT 0.5,
                curiosity REAL DEFAULT 0.6,
                namespace TEXT DEFAULT 'rei'
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✓ Memory database initialized")
    
    def add_memory(self, memory_type: str, content: str, tags: List[str] = None, 
                   weight: float = 0.5, namespace: str = 'rei') -> bool:
        """記憶を追加"""
        try:
            memory_hash = hashlib.sha256(f"{memory_type}:{content}".encode()).hexdigest()
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            tags_str = json.dumps(tags) if tags else None
            
            c.execute('''
                INSERT OR IGNORE INTO memories 
                (memory_hash, memory_type, content, weight, namespace, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (memory_hash, memory_type, content, weight, namespace, tags_str))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            return False
    
    def get_memories(self, query: str, limit: int = 5, namespace: str = 'rei') -> List[Dict]:
        """関連記憶を検索"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                SELECT id, memory_type, content, weight, timestamp 
                FROM memories 
                WHERE namespace = ? AND content LIKE ?
                ORDER BY timestamp DESC LIMIT ?
            ''', (namespace, f"%{query}%", limit))
            
            memories = []
            for row in c.fetchall():
                memories.append({
                    'id': row[0],
                    'type': row[1],
                    'content': row[2],
                    'weight': row[3],
                    'timestamp': row[4]
                })
            conn.close()
            return memories
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            return []
    
    def delete_memory(self, memory_id: int) -> bool:
        """記憶を削除"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('DELETE FROM memories WHERE id = ?', (memory_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error deleting memory: {e}")
            return False
    
    def add_conversation(self, user_message: str, ai_response: str, 
                        emotion_state: Dict = None, namespace: str = 'rei') -> bool:
        """会話履歴を記録"""
        try:
            emotion_str = json.dumps(emotion_state) if emotion_state else None
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                INSERT INTO conversations (user_message, ai_response, emotion_state, namespace)
                VALUES (?, ?, ?, ?)
            ''', (user_message, ai_response, emotion_str, namespace))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding conversation: {e}")
            return False

memory_manager = MemoryManager()
