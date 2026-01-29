"""
日志配置模块
"""
import logging
import sys
from pathlib import Path

from config import settings


def setup_logger(name: str = None) -> logging.Logger:
    """
    配置并返回 logger
    
    Args:
        name: logger 名称，默认为根 logger
        
    Returns:
        logging.Logger: 配置好的 logger
    """
    logger = logging.getLogger(name)
    
    # 避免重复配置
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器 (可选)
    if settings.LOG_FILE:
        try:
            file_handler = logging.FileHandler(
                settings.LOG_FILE,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"无法创建日志文件: {str(e)}")
    
    return logger
