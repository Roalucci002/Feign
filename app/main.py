"""
REI-CHAN AI COMPANION SYSTEM
Main Entry Point - Application Startup & Component Initialization

This module handles:
- Environment configuration loading
- Component dependency wiring
- Application lifecycle management
- Error handling and fallback strategies
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Add src to path for existing modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from app.environment import load_env, get_env, validate_env
from app.logger import setup_logger, initialize_logging
from src.config_manager import ConfigManager, config_manager
from src.llm_manager import LLMManager
from src.memory_manager import MemoryManager
from src.search_manager import SearchManager
from src.emotion_manager import EmotionManager


# ===========================
# グローバルロガー
# ===========================
logger: Optional[logging.Logger] = None


class ApplicationContext:
    """アプリケーション全体のコンテキスト管理"""
    
    def __init__(self):
        self.config: Optional[ConfigManager] = None
        self.llm_manager: Optional[LLMManager] = None
        self.memory_manager: Optional[MemoryManager] = None
        self.search_manager: Optional[SearchManager] = None
        self.emotion_manager: Optional[EmotionManager] = None
        self.initialized: bool = False
        self.errors: list = []
    
    def log_error(self, component: str, error: Exception) -> None:
        """エラーを記録（他のコンポーネント失敗時の復旧可能性を保持）"""
        error_msg = f"{component}: {str(error)}"
        self.errors.append(error_msg)
        logger.error(f"Component initialization failed: {error_msg}")
    
    def get_status(self) -> Dict[str, Any]:
        """アプリケーション状態を取得"""
        return {
            'initialized': self.initialized,
            'components': {
                'config': self.config is not None,
                'llm': self.llm_manager is not None and self.llm_manager.available,
                'memory': self.memory_manager is not None,
                'search': self.search_manager is not None and self.search_manager.available,
                'emotion': self.emotion_manager is not None
            },
            'errors': self.errors
        }


# グローバルアプリケーションコンテキスト
app_context: ApplicationContext = ApplicationContext()


def initialize_environment() -> bool:
    """
    環境変数の初期化
    
    Returns:
        True if successful, False otherwise
    """
    global logger
    
    try:
        # .envファイルを読み込む
        env_loaded = load_env('.env')
        if not env_loaded:
            logger.warning("No .env file found, using system environment variables")
        
        # 必須環境変数を検証
        required_vars = [
            'OLLAMA_URL',
            'OLLAMA_MODEL',
            'MEMORY_DB_PATH',
            'LOG_LEVEL'
        ]
        
        if not validate_env(required_vars):
            logger.error("Missing required environment variables")
            return False
        
        logger.info("✓ Environment initialized")
        return True
    
    except Exception as e:
        logger.error(f"Environment initialization failed: {e}")
        return False


def initialize_config() -> bool:
    """
    設定システムの初期化
    
    Returns:
        True if successful, False otherwise
    """
    try:
        app_context.config = config_manager
        
        # 設定が正常に読み込まれたか確認
        if not app_context.config.configs:
            logger.warning("No configuration files loaded, using defaults")
        
        logger.info(f"✓ Configuration loaded: {len(app_context.config.configs)} files")
        return True
    
    except Exception as e:
        app_context.log_error("ConfigManager", e)
        return False


def initialize_llm() -> bool:
    """
    LLMマネージャーの初期化（失敗時も他のコンポーネントは継続）
    
    Returns:
        True if available, False otherwise (system continues)
    """
    try:
        llm_config = app_context.config.get('llm', {})
        base_url = llm_config.get('base_url', 'http://localhost:11434')
        model = llm_config.get('model', 'mistral')
        
        app_context.llm_manager = LLMManager(base_url=base_url, model=model)
        
        if app_context.llm_manager.available:
            logger.info(f"✓ LLM connected: {model}")
            return True
        else:
            logger.warning("LLM not available - chat will be offline")
            return False
    
    except Exception as e:
        app_context.log_error("LLMManager", e)
        logger.warning("LLM initialization failed - continuing without LLM")
        return False


def initialize_memory() -> bool:
    """
    メモリマネージャーの初期化
    
    Returns:
        True if successful, False otherwise
    """
    try:
        memory_config = app_context.config.get('memory', {})
        db_path = memory_config.get('database_path', './memory_db/rei_memory.db')
        
        app_context.memory_manager = MemoryManager(db_path=db_path)
        logger.info(f"✓ Memory initialized: {db_path}")
        return True
    
    except Exception as e:
        app_context.log_error("MemoryManager", e)
        logger.error("Memory system failed - cannot continue without memory")
        return False


def initialize_search() -> bool:
    """
    検索マネージャーの初期化（失敗時も他のコンポーネントは継続）
    
    Returns:
        True if available, False otherwise (system continues)
    """
    try:
        search_config = app_context.config.get('search', {})
        base_url = search_config.get('base_url', 'http://localhost:8888')
        timeout = search_config.get('timeout', 10)
        
        app_context.search_manager = SearchManager(base_url=base_url, timeout=timeout)
        
        if app_context.search_manager.available:
            logger.info("✓ Search engine connected")
            return True
        else:
            logger.warning("Search engine not available - search disabled")
            return False
    
    except Exception as e:
        app_context.log_error("SearchManager", e)
        logger.warning("Search initialization failed - continuing without search")
        return False


def initialize_emotion() -> bool:
    """
    感情マネージャーの初期化
    
    Returns:
        True if successful, False otherwise
    """
    try:
        app_context.emotion_manager = EmotionManager()
        logger.info("✓ Emotion system initialized")
        return True
    
    except Exception as e:
        app_context.log_error("EmotionManager", e)
        logger.warning("Emotion system failed")
        return False


def startup() -> bool:
    """
    アプリケーション起動シーケンス
    
    設計原則:
    - 一つのコンポーネント失敗 ≠ 全システム停止
    - 必須: Config, Memory
    - オプション: LLM, Search, Emotion
    
    Returns:
        True if critical components initialized, False otherwise
    """
    global logger
    
    try:
        # ロギングを初期化
        logger = setup_logger(
            'rei_system',
            log_level='INFO',
            log_file='./logs/rei_system.log',
            json_format=True,
            console_output=True
        )
        
        logger.info("=" * 60)
        logger.info("REI-CHAN AI COMPANION SYSTEM - Starting up")
        logger.info("=" * 60)
        
        # ステップ1: 環境変数
        if not initialize_environment():
            logger.critical("Environment initialization failed")
            return False
        
        # ステップ2: 設定（必須）
        if not initialize_config():
            logger.critical("Configuration initialization failed")
            return False
        
        # ステップ3: メモリ（必須）
        if not initialize_memory():
            logger.critical("Memory system initialization failed")
            return False
        
        # ステップ4: LLM（オプション）
        llm_ok = initialize_llm()
        
        # ステップ5: 検索（オプション）
        search_ok = initialize_search()
        
        # ステップ6: 感情（オプション）
        emotion_ok = initialize_emotion()
        
        # 起動完了
        app_context.initialized = True
        
        logger.info("=" * 60)
        logger.info("✓ REI-CHAN System Startup Complete")
        logger.info(f"Status: {app_context.get_status()}")
        logger.info("=" * 60)
        
        # 全コンポーネント起動していない場合は警告
        if not (llm_ok and search_ok and emotion_ok):
            logger.warning("Some optional components failed - system degraded")
        
        return True
    
    except Exception as e:
        logger.critical(f"Startup sequence failed: {e}", exc_info=True)
        return False


def shutdown() -> None:
    """
    アプリケーション終了処理
    """
    if logger:
        logger.info("=" * 60)
        logger.info("REI-CHAN System Shutting Down")
        logger.info("=" * 60)
    
    # クリーンアップ（今後拡張）
    # - メモリDB接続クローズ
    # - ログファイルフラッシュ
    # - キャッシュクリア


def main() -> int:
    """
    メインエントリーポイント
    
    Returns:
        Exit code (0 = success, 1 = failure)
    """
    try:
        # 起動
        if not startup():
            return 1
        
        # ここからアプリケーション本体が動く
        # （現在はプレースホルダー）
        if logger:
            logger.info("System ready for operation")
            logger.info(f"LLM: {'Available' if app_context.llm_manager and app_context.llm_manager.available else 'Offline'}")
            logger.info(f"Search: {'Available' if app_context.search_manager and app_context.search_manager.available else 'Offline'}")
            logger.info(f"Memory: {'Available' if app_context.memory_manager else 'Offline'}")
        
        return 0
    
    except KeyboardInterrupt:
        if logger:
            logger.info("Shutdown requested by user")
        return 0
    
    except Exception as e:
        if logger:
            logger.critical(f"Unexpected error: {e}", exc_info=True)
        return 1
    
    finally:
        shutdown()


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
