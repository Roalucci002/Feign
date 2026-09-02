"""
Unified logging system for REI-CHAN Python modules
Supports file and console output with JSON formatting
"""

import logging
import logging.handlers
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import os


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


class PlainFormatter(logging.Formatter):
    """Format logs as human-readable text"""
    
    def format(self, record: logging.LogRecord) -> str:
        return (
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"[{record.levelname}] "
            f"{record.name}: {record.getMessage()}"
        )


def setup_logger(
    name: str,
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    json_format: bool = True,
    console_output: bool = True
) -> logging.Logger:
    """
    セットアップ統一ロギング
    
    Args:
        name: Logger name (usually __name__)
        log_level: ログレベル (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: ログファイルパス (None=ファイルなし)
        json_format: JSON形式で出力するか (default=True)
        console_output: コンソール出力するか (default=True)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # ロガーレベルを設定
    log_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # フォーマッターを選択
    formatter = JSONFormatter() if json_format else PlainFormatter()
    
    # コンソールハンドラ
    if console_output and not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # ファイルハンドラ
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=100 * 1024 * 1024,  # 100MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # 他のロガーからの伝播を防止
    logger.propagate = False
    
    return logger


# グローバルロガー設定
def initialize_logging(config: dict) -> None:
    """
    設定からロギングシステムを初期化
    
    Args:
        config: Configuration dict with logging settings
    """
    logging_config = config.get('logging', {})
    log_level = logging_config.get('level', 'INFO')
    log_file = logging_config.get('output_path', './logs/rei_system.log')
    json_format = logging_config.get('format', 'json') == 'json'
    
    # ルートロガーを設定
    root_logger = setup_logger(
        'rei_system',
        log_level=log_level,
        log_file=log_file,
        json_format=json_format,
        console_output=True
    )
    
    return root_logger
