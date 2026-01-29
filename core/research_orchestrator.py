"""
研究流程编排模块
协调搜索、提取、分析的完整研究流程
"""
import logging
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .search_engine import SearchEngine
from .content_extractor import ContentExtractor
from .ai_analyzer import AIAnalyzer, AIProvider
from config import settings

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """搜索结果数据类"""
    title: str
    url: str
    snippet: str
    content: Optional[str] = None


@dataclass
class ResearchRound:
    """研究轮次数据类"""
    round_number: int
    queries: List[str]
    search_results: List[Dict[str, str]] = field(default_factory=list)
    extracted_contents: Dict[str, str] = field(default_factory=dict)
    analysis: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchResult:
    """研究结果数据类"""
    topic: str
    final_report: str
    rounds: List[ResearchRound]
    all_sources: List[str]
    timestamp: datetime
    total_rounds: int


class ResearchOrchestrator:
    """研究流程编排器"""
    
    def __init__(self, ai_provider: AIProvider = AIProvider.OPENAI):
        """
        初始化研究编排器
        
        Args:
            ai_provider: AI 提供商
        """
        self.search_engine = SearchEngine()
        self.content_extractor = ContentExtractor()
        self.ai_analyzer = AIAnalyzer(provider=ai_provider)
        
    def conduct_research(
        self,
        topic: str,
        max_rounds: int = None,
        results_per_search: int = None,
        progress_callback: Callable[[str, int, int], None] = None
    ) -> ResearchResult:
        """
        执行完整的研究流程
        
        Args:
            topic: 研究主题
            max_rounds: 最大研究轮数
            results_per_search: 每次搜索的结果数量
            progress_callback: 进度回调函数 (message, current_round, total_rounds)
            
        Returns:
            ResearchResult: 完整的研究结果
        """
        if max_rounds is None:
            max_rounds = settings.MAX_RESEARCH_ROUNDS
        if results_per_search is None:
            results_per_search = settings.RESULTS_PER_SEARCH
        
        logger.info(f"开始研究: {topic} (最多 {max_rounds} 轮)")
        
        rounds = []
        all_sources = set()
        
        # 第一轮: 初始搜索
        current_query = topic
        
        for round_num in range(max_rounds):
            logger.info(f"=== 第 {round_num + 1} 轮研究 ===")
            
            if progress_callback:
                progress_callback(
                    f"第 {round_num + 1}/{max_rounds} 轮: 搜索中...",
                    round_num + 1,
                    max_rounds
                )
            
            # 如果是后续轮次，生成新的查询
            queries = [current_query] if round_num == 0 else self._generate_queries(
                topic, rounds[-1].analysis, round_num
            )
            
            if not queries:
                logger.info("没有更多查询，提前结束")
                break
            
            # 创建新轮次
            round_data = ResearchRound(
                round_number=round_num + 1,
                queries=queries
            )
            
            # 执行搜索
            all_search_results = []
            for query in queries:
                if progress_callback:
                    progress_callback(
                        f"第 {round_num + 1}/{max_rounds} 轮: 搜索 '{query}'",
                        round_num + 1,
                        max_rounds
                    )
                
                results = self.search_engine.search(query, results_per_search)
                all_search_results.extend(results)
                
                # 收集来源
                for result in results:
                    if result.get('url'):
                        all_sources.add(result['url'])
            
            round_data.search_results = all_search_results
            logger.info(f"搜索完成，共 {len(all_search_results)} 条结果")
            
            # 提取内容
            if progress_callback:
                progress_callback(
                    f"第 {round_num + 1}/{max_rounds} 轮: 提取网页内容...",
                    round_num + 1,
                    max_rounds
                )
            
            urls_to_extract = [r['url'] for r in all_search_results[:10]]  # 限制数量
            extracted = self.content_extractor.extract_multiple(urls_to_extract)
            round_data.extracted_contents = extracted
            logger.info(f"内容提取完成，成功 {len(extracted)} 个")
            
            # AI 分析
            if progress_callback:
                progress_callback(
                    f"第 {round_num + 1}/{max_rounds} 轮: AI 分析中...",
                    round_num + 1,
                    max_rounds
                )
            
            analysis = self.ai_analyzer.analyze_search_results(
                queries[0],  # 使用主要查询
                all_search_results,
                extracted
            )
            round_data.analysis = analysis
            logger.info("分析完成")
            
            rounds.append(round_data)
            
            # 判断是否需要继续
            if round_num >= max_rounds - 1:
                logger.info("达到最大轮数")
                break
            
            # 检查是否还有信息缺口
            gaps = analysis.get('gaps', [])
            if not gaps:
                logger.info("没有信息缺口，提前结束")
                break
        
        # 生成最终报告
        if progress_callback:
            progress_callback(
                "正在生成最终报告...",
                max_rounds,
                max_rounds
            )
        
        logger.info("正在生成最终报告...")
        
        # 准备所有轮次的数据
        all_rounds_data = []
        for round_data in rounds:
            all_rounds_data.append({
                'round_number': round_data.round_number,
                'queries': round_data.queries,
                'search_results': round_data.search_results,
                'analysis': round_data.analysis
            })
        
        final_report = self.ai_analyzer.synthesize_research(
            topic,
            all_rounds_data
        )
        
        # 构建结果
        result = ResearchResult(
            topic=topic,
            final_report=final_report,
            rounds=rounds,
            all_sources=sorted(list(all_sources)),
            timestamp=datetime.now(),
            total_rounds=len(rounds)
        )
        
        logger.info(f"研究完成! 共 {len(rounds)} 轮，{len(all_sources)} 个来源")
        
        return result
    
    def _generate_queries(
        self,
        topic: str,
        previous_analysis: Dict[str, Any],
        round_num: int
    ) -> List[str]:
        """生成后续查询"""
        try:
            return self.ai_analyzer.generate_follow_up_queries(
                topic,
                previous_analysis,
                round_num
            )
        except Exception as e:
            logger.error(f"生成查询失败: {str(e)}")
            return []
