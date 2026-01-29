"""
AI 分析模块
集成 OpenAI/Claude API 进行内容分析和查询生成
"""
import logging
import json
from typing import List, Dict, Any, Optional
from enum import Enum

from config import settings

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """AI 提供商枚举"""
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class AIAnalyzer:
    """AI 分析类"""
    
    def __init__(self, provider: AIProvider = AIProvider.DEEPSEEK):
        """
        初始化 AI 分析器
        
        Args:
            provider: AI 提供商 (DEEPSEEK, OPENAI 或 ANTHROPIC)
        """
        self.provider = provider
        
        if provider == AIProvider.DEEPSEEK:
            if not settings.DEEPSEEK_API_KEY:
                raise ValueError("未配置 DEEPSEEK_API_KEY")
            from openai import OpenAI
            # DeepSeek 使用兼容 OpenAI 的 API
            self.client = OpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL
            )
            self.model = settings.DEEPSEEK_MODEL
        elif provider == AIProvider.OPENAI:
            if not settings.OPENAI_API_KEY:
                raise ValueError("未配置 OPENAI_API_KEY")
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL
        else:
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("未配置 ANTHROPIC_API_KEY")
            from anthropic import Anthropic
            self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = settings.ANTHROPIC_MODEL
    
    def _call_api(self, messages: List[Dict[str, str]], system_prompt: str = None) -> str:
        """
        调用 AI API
        
        Args:
            messages: 消息列表
            system_prompt: 系统提示词
            
        Returns:
            str: AI 响应内容
        """
        try:
            if self.provider in [AIProvider.DEEPSEEK, AIProvider.OPENAI]:
                # DeepSeek 和 OpenAI 使用相同的 API 格式
                if system_prompt:
                    messages = [{"role": "system", "content": system_prompt}] + messages
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=settings.TEMPERATURE,
                    max_tokens=settings.MAX_TOKENS
                )
                return response.choices[0].message.content
                
            else:
                # Anthropic API 调用
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=settings.MAX_TOKENS,
                    temperature=settings.TEMPERATURE,
                    system=system_prompt or "",
                    messages=messages
                )
                return response.content[0].text
                
        except Exception as e:
            logger.error(f"AI API 调用失败: {str(e)}")
            raise
    
    def analyze_search_results(
        self, 
        query: str, 
        results: List[Dict[str, str]],
        extracted_contents: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        分析搜索结果并提取关键信息
        
        Args:
            query: 原始查询
            results: 搜索结果列表
            extracted_contents: 提取的网页内容 (URL -> 内容)
            
        Returns:
            Dict: 包含分析结果和关键发现
        """
        logger.info(f"正在分析搜索结果: {query}")
        
        # 构建分析提示
        system_prompt = """你是一个专业的研究分析助手。你的任务是分析搜索结果和网页内容，提取关键信息。"""
        
        content_summary = ""
        if extracted_contents:
            content_summary = "\n\n### 网页内容摘要:\n"
            for url, content in list(extracted_contents.items())[:5]:  # 限制数量
                content_summary += f"\n**URL**: {url}\n**内容**: {content[:500]}...\n"
        
        user_message = f"""
请分析以下搜索结果，提取关键信息和主要发现。

**查询**: {query}

**搜索结果**:
{json.dumps(results[:10], ensure_ascii=False, indent=2)}

{content_summary}

请以 JSON 格式返回分析结果，包含以下字段:
- key_findings: 主要发现列表 (字符串数组)
- summary: 整体摘要 (字符串)
- topics: 识别的主题列表 (字符串数组)
- gaps: 信息缺口或需要进一步研究的方向 (字符串数组)
"""
        
        messages = [{"role": "user", "content": user_message}]
        
        try:
            response = self._call_api(messages, system_prompt)
            
            # 尝试解析 JSON
            # 移除可能的 markdown 代码块标记
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            analysis = json.loads(response.strip())
            logger.info(f"分析完成: {len(analysis.get('key_findings', []))} 个主要发现")
            return analysis
            
        except json.JSONDecodeError:
            logger.warning("AI 响应不是有效的 JSON，使用原始响应")
            return {
                "key_findings": [response],
                "summary": response,
                "topics": [],
                "gaps": []
            }
    
    def generate_follow_up_queries(
        self, 
        initial_query: str, 
        analysis: Dict[str, Any],
        round_number: int = 1
    ) -> List[str]:
        """
        根据分析结果生成后续搜索查询
        
        Args:
            initial_query: 初始查询
            analysis: 分析结果
            round_number: 当前轮数
            
        Returns:
            List[str]: 后续查询列表
        """
        logger.info(f"正在生成第 {round_number + 1} 轮搜索查询")
        
        system_prompt = """你是一个专业的研究策略专家。你的任务是根据已有的分析结果，生成深入的后续搜索查询。"""
        
        user_message = f"""
基于以下研究进展，生成 2-3 个更深入的搜索查询，以填补信息缺口。

**原始主题**: {initial_query}

**当前发现**:
{json.dumps(analysis.get('key_findings', []), ensure_ascii=False, indent=2)}

**信息缺口**:
{json.dumps(analysis.get('gaps', []), ensure_ascii=False, indent=2)}

**要求**:
1. 查询应该更具体、更深入
2. 避免重复已有信息
3. 关注信息缺口和未探索的角度
4. 每个查询应该简洁明确

请以 JSON 数组格式返回查询列表，例如: ["查询1", "查询2", "查询3"]
"""
        
        messages = [{"role": "user", "content": user_message}]
        
        try:
            response = self._call_api(messages, system_prompt)
            
            # 解析 JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            queries = json.loads(response.strip())
            logger.info(f"生成 {len(queries)} 个后续查询")
            return queries[:3]  # 限制最多 3 个
            
        except json.JSONDecodeError:
            logger.warning("无法解析后续查询，使用默认策略")
            # 使用信息缺口作为查询
            gaps = analysis.get('gaps', [])
            return gaps[:3] if gaps else []
    
    def synthesize_research(
        self, 
        topic: str,
        all_rounds: List[Dict[str, Any]]
    ) -> str:
        """
        整合所有研究轮次的信息，生成最终报告
        
        Args:
            topic: 研究主题
            all_rounds: 所有轮次的数据
            
        Returns:
            str: Markdown 格式的最终报告
        """
        logger.info(f"正在整合研究结果: {topic}")
        
        system_prompt = """你是一个专业的研究报告撰写专家。你的任务是将多轮研究的信息整合成一份结构清晰、内容丰富的研究报告。"""
        
        # 构建研究数据摘要
        rounds_summary = ""
        all_sources = set()
        
        for i, round_data in enumerate(all_rounds, 1):
            rounds_summary += f"\n### 第 {i} 轮研究\n"
            rounds_summary += f"**查询**: {', '.join(round_data.get('queries', []))}\n"
            
            analysis = round_data.get('analysis', {})
            if analysis:
                rounds_summary += f"**主要发现**:\n"
                for finding in analysis.get('key_findings', [])[:5]:
                    rounds_summary += f"- {finding}\n"
            
            # 收集来源
            for result in round_data.get('search_results', []):
                if result.get('url'):
                    all_sources.add(result['url'])
        
        user_message = f"""
请基于以下多轮研究数据，撰写一份全面的研究报告。

**研究主题**: {topic}

**研究数据**:
{rounds_summary}

**要求**:
1. 使用 Markdown 格式
2. 包含以下部分:
   - # 研究主题标题
   - ## 概述 (Executive Summary)
   - ## 核心发现 (Key Findings)
   - ## 详细分析 (Detailed Analysis)
   - ## 结论与展望 (Conclusions and Outlook)
   - ## 参考来源 (References)
3. 内容要结构清晰、逻辑连贯
4. 使用项目符号和编号列表增强可读性
5. 在参考来源部分列出所有 URL

请生成完整的 Markdown 报告。
"""
        
        messages = [{"role": "user", "content": user_message}]
        
        try:
            report = self._call_api(messages, system_prompt)
            
            # 确保包含参考来源
            if "## 参考来源" not in report and "## References" not in report:
                report += "\n\n## 参考来源 (References)\n\n"
                for i, url in enumerate(sorted(all_sources), 1):
                    report += f"{i}. {url}\n"
            
            logger.info("研究报告生成完成")
            return report
            
        except Exception as e:
            logger.error(f"报告生成失败: {str(e)}")
            # 返回简单的汇总
            simple_report = f"# {topic}\n\n## 研究摘要\n\n"
            for i, round_data in enumerate(all_rounds, 1):
                simple_report += f"### 第 {i} 轮\n"
                analysis = round_data.get('analysis', {})
                simple_report += analysis.get('summary', '无摘要') + "\n\n"
            return simple_report
