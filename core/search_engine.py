"""
搜索引擎模块
封装 DuckDuckGo Search API
"""
import logging
import time
from typing import List, Dict, Optional
from duckduckgo_search import DDGS

from config import settings

logger = logging.getLogger(__name__)


class SearchEngine:
    """搜索引擎封装类"""
    
    def __init__(self):
        """初始化搜索引擎"""
        self.ddgs = DDGS()
        
    def search(self, query: str, max_results: int = None) -> List[Dict[str, str]]:
        """
        执行搜索并返回结果列表
        
        Args:
            query: 搜索查询字符串
            max_results: 最大结果数量，默认使用配置值
            
        Returns:
            List[Dict]: 每个结果包含 'title', 'url', 'snippet'
        """
        if max_results is None:
            max_results = settings.RESULTS_PER_SEARCH
            
        logger.info(f"正在搜索: {query} (最多 {max_results} 条结果)")
        
        results = []
        retry_count = 0
        
        while retry_count < settings.MAX_RETRIES:
            try:
                # 使用 DuckDuckGo 搜索
                search_results = self.ddgs.text(
                    query,
                    max_results=max_results
                )
                
                # 转换为标准格式
                for result in search_results:
                    results.append({
                        'title': result.get('title', ''),
                        'url': result.get('href', ''),
                        'snippet': result.get('body', '')
                    })
                
                logger.info(f"搜索成功，获取 {len(results)} 条结果")
                return results
                
            except Exception as e:
                retry_count += 1
                logger.warning(
                    f"搜索失败 (尝试 {retry_count}/{settings.MAX_RETRIES}): {str(e)}"
                )
                
                if retry_count < settings.MAX_RETRIES:
                    # 指数退避
                    delay = settings.RETRY_DELAY * (2 ** (retry_count - 1))
                    logger.info(f"等待 {delay} 秒后重试...")
                    time.sleep(delay)
                else:
                    logger.error(f"搜索最终失败: {query}")
                    return []
        
        return results
    
    def search_multiple(self, queries: List[str], max_results: int = None) -> Dict[str, List[Dict[str, str]]]:
        """
        执行多个搜索查询
        
        Args:
            queries: 搜索查询列表
            max_results: 每个查询的最大结果数量
            
        Returns:
            Dict: 查询到结果的映射
        """
        results = {}
        
        for query in queries:
            results[query] = self.search(query, max_results)
            # 避免请求过快
            time.sleep(0.5)
        
        return results
