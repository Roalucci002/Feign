"""
Environment variable management
Loads .env files and provides configuration bridge
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


def load_env(env_path: str = ".env") -> bool:
    """
    .env ファイルを読み込む
    
    Args:
        env_path: .env file path
    
    Returns:
        True if loaded successfully, False if file not found
    """
    env_file = Path(env_path)
    
    if not env_file.exists():
        logger.warning(f".env file not found at {env_path}")
        return False
    
    try:
        load_dotenv(env_file)
        logger.info(f"✓ Loaded environment from {env_path}")
        return True
    except Exception as e:
        logger.error(f"Error loading .env: {e}")
        return False


def get_env(key: str, default: Optional[Any] = None, required: bool = False) -> Any:
    """
    環境変数を取得（型変換対応）
    
    Args:
        key: Environment variable name
        default: Default value if not set
        required: Raise error if not set (default=False)
    
    Returns:
        Environment variable value with type conversion
    
    Raises:
        ValueError: If required and not set
    """
    value = os.getenv(key, default)
    
    if value is None and required:
        raise ValueError(f"Required environment variable '{key}' not set")
    
    # 型推論: 'true'/'false' → bool, 数字 → int
    if isinstance(value, str):
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        elif value.isdigit():
            return int(value)
        elif value.replace('.', '', 1).isdigit():
            return float(value)
    
    return value


def validate_env(required_vars: list) -> bool:
    """
    必須環境変数が設定されているか検証
    
    Args:
        required_vars: List of required variable names
    
    Returns:
        True if all required vars are set, False otherwise
    """
    missing = []
    for var in required_vars:
        if os.getenv(var) is None:
            missing.append(var)
    
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        return False
    
    return True


def get_env_dict() -> Dict[str, str]:
    """
    すべての環境変数を辞書で取得
    
    Returns:
        Dictionary of all environment variables
    """
    return dict(os.environ)


def print_env_status(sensitive_keys: list = None) -> None:
    """
    環境変数の状態をログに出力（機密情報を隠す）
    
    Args:
        sensitive_keys: Keys to mask in output
    """
    if sensitive_keys is None:
        sensitive_keys = ['KEY', 'SECRET', 'PASSWORD', 'TOKEN']
    
    logger.info("=== Environment Status ===")
    for key, value in os.environ.items():
        if any(sensitive in key.upper() for sensitive in sensitive_keys):
            logger.info(f"{key}=***MASKED***")
        else:
            logger.info(f"{key}={value}")
