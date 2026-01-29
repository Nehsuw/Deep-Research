"""
内容提取模块
解析网页并提取正文
"""
import logging
import time
import requests
from bs4 import BeautifulSoup
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import settings

logger = logging.getLogger(__name__)


class ContentExtractor:
    """网页内容提取类"""
    
    def __init__(self):
        """初始化内容提取器"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.cache = {}  # URL 缓存
        
    def extract_content(self, url: str) -> Optional[str]:
        """
        从 URL 提取网页正文内容
        
        Args:
            url: 网页 URL
            
        Returns:
            str: 提取的正文内容，失败返回 None
        """
        # 检查缓存
        if url in self.cache:
            logger.debug(f"从缓存获取内容: {url}")
            return self.cache[url]
        
        logger.info(f"正在提取内容: {url}")
        
        retry_count = 0
        while retry_count < settings.MAX_RETRIES:
            try:
                # 获取网页 HTML
                response = self.session.get(
                    url,
                    timeout=settings.REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                response.raise_for_status()
                
                # 检测编码
                response.encoding = response.apparent_encoding
                html = response.text
                
                # 解析 HTML
                soup = BeautifulSoup(html, 'lxml')
                
                # 移除无关标签
                for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
                    tag.decompose()
                
                # 尝试找到主要内容区域
                main_content = None
                
                # 优先查找常见的内容容器
                for selector in ['article', 'main', '[role="main"]', '.content', '.post', '.entry']:
                    main_content = soup.select_one(selector)
                    if main_content:
                        break
                
                # 如果没找到，使用 body
                if not main_content:
                    main_content = soup.body
                
                if not main_content:
                    logger.warning(f"无法找到主要内容: {url}")
                    return None
                
                # 提取文本
                text = main_content.get_text(separator='\n', strip=True)
                
                # 清理多余空行
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                content = '\n'.join(lines)
                
                # 限制长度
                if len(content) > settings.MAX_CONTENT_LENGTH:
                    content = content[:settings.MAX_CONTENT_LENGTH] + '...'
                
                # 缓存结果
                self.cache[url] = content
                
                logger.info(f"内容提取成功: {url} ({len(content)} 字符)")
                return content
                
            except requests.exceptions.RequestException as e:
                retry_count += 1
                logger.warning(
                    f"请求失败 (尝试 {retry_count}/{settings.MAX_RETRIES}): {url} - {str(e)}"
                )
                
                if retry_count < settings.MAX_RETRIES:
                    delay = settings.RETRY_DELAY * (2 ** (retry_count - 1))
                    time.sleep(delay)
                else:
                    logger.error(f"内容提取最终失败: {url}")
                    return None
                    
            except Exception as e:
                logger.error(f"解析失败: {url} - {str(e)}")
                return None
        
        return None
    
    def extract_multiple(self, urls: list, max_workers: int = None) -> dict:
        """
        并发提取多个 URL 的内容
        
        Args:
            urls: URL 列表
            max_workers: 最大并发数，默认使用配置值
            
        Returns:
            dict: URL 到内容的映射
        """
        if max_workers is None:
            max_workers = settings.MAX_CONCURRENT_REQUESTS
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_url = {
                executor.submit(self.extract_content, url): url 
                for url in urls
            }
            
            # 收集结果
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    content = future.result()
                    if content:
                        results[url] = content
                except Exception as e:
                    logger.error(f"提取失败: {url} - {str(e)}")
        
        return results
