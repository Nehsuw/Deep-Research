"""
配置管理模块
加载环境变量并定义系统参数
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings:
    """应用配置类"""
    
    # 项目根目录
    BASE_DIR = Path(__file__).parent.parent
    
    # API 密钥
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    SERP_API_KEY = os.getenv("SERP_API_KEY", "")
    
    # 研究参数
    MAX_RESEARCH_ROUNDS = int(os.getenv("MAX_RESEARCH_ROUNDS", "3"))
    RESULTS_PER_SEARCH = int(os.getenv("RESULTS_PER_SEARCH", "10"))
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
    
    # 导出配置
    OUTPUT_DIR = BASE_DIR / "outputs"
    
    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = BASE_DIR / "app.log"
    
    # HTTP 请求配置
    REQUEST_TIMEOUT = 30  # 秒
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # 秒
    
    # AI 模型配置
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")  # 或 deepseek-reasoner
    OPENAI_MODEL = "gpt-4-turbo-preview"
    ANTHROPIC_MODEL = "claude-3-opus-20240229"
    MAX_TOKENS = 4000
    TEMPERATURE = 0.7
    
    # 内容提取配置
    MAX_CONTENT_LENGTH = 5000  # 每个网页提取的最大字符数
    
    @classmethod
    def validate(cls):
        """验证必要的配置"""
        if not cls.DEEPSEEK_API_KEY and not cls.OPENAI_API_KEY and not cls.ANTHROPIC_API_KEY:
            raise ValueError(
                "至少需要配置 DEEPSEEK_API_KEY、OPENAI_API_KEY 或 ANTHROPIC_API_KEY。"
                "请复制 .env.example 为 .env 并填入 API 密钥。"
            )
        
        # 确保输出目录存在
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        return True

# 全局配置实例
settings = Settings()
