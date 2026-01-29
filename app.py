"""
Deep Research - AI 深度研究助手
Streamlit 应用主入口
"""
import streamlit as st
import logging
from pathlib import Path

from config import settings
from core import ResearchOrchestrator, AIProvider
from utils import ExportManager, setup_logger

# 设置日志
setup_logger()
logger = logging.getLogger(__name__)

# 页面配置
st.set_page_config(
    page_title="Deep Research - AI 深度研究助手",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        color: #155724;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.25rem;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """初始化会话状态"""
    if 'research_result' not in st.session_state:
        st.session_state.research_result = None
    if 'is_researching' not in st.session_state:
        st.session_state.is_researching = False
    if 'progress_message' not in st.session_state:
        st.session_state.progress_message = ""
    if 'progress_value' not in st.session_state:
        st.session_state.progress_value = 0


def validate_api_keys():
    """验证 API 密钥配置"""
    try:
        settings.validate()
        return True
    except ValueError as e:
        st.error(f"⚠️ {str(e)}")
        st.info("""
        **配置步骤**:
        1. 复制 `.env.example` 为 `.env`
        2. 在 `.env` 中填入至少一个 API 密钥:
           - `OPENAI_API_KEY` 或
           - `ANTHROPIC_API_KEY`
        3. 重启应用
        """)
        return False


def main():
    """主函数"""
    initialize_session_state()
    
    # 标题
    st.markdown('<div class="main-header">🔍 Deep Research</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI 驱动的智能深度研究助手</div>', unsafe_allow_html=True)
    
    # 验证配置
    if not validate_api_keys():
        st.stop()
    
    # 侧边栏配置
    with st.sidebar:
        st.header("⚙️ 配置")
        
        # AI 提供商选择
        ai_options = []
        if settings.OPENAI_API_KEY:
            ai_options.append("OpenAI GPT-4")
        if settings.ANTHROPIC_API_KEY:
            ai_options.append("Anthropic Claude")
        
        if not ai_options:
            st.error("未配置任何 AI API 密钥")
            st.stop()
        
        ai_choice = st.selectbox(
            "AI 模型",
            ai_options,
            help="选择用于分析的 AI 模型"
        )
        
        ai_provider = AIProvider.OPENAI if "OpenAI" in ai_choice else AIProvider.ANTHROPIC
        
        # 研究参数
        st.subheader("研究参数")
        
        max_rounds = st.slider(
            "研究轮数",
            min_value=1,
            max_value=5,
            value=settings.MAX_RESEARCH_ROUNDS,
            help="执行多少轮搜索和分析"
        )
        
        results_per_search = st.slider(
            "每轮搜索结果数",
            min_value=5,
            max_value=20,
            value=settings.RESULTS_PER_SEARCH,
            help="每次搜索返回的结果数量"
        )
        
        st.divider()
        
        # 说明
        st.subheader("📖 使用说明")
        st.markdown("""
        1. 输入研究主题
        2. 配置研究参数
        3. 点击"开始研究"
        4. 等待 AI 完成分析
        5. 下载研究报告
        """)
        
        st.divider()
        
        # 示例主题
        st.subheader("💡 示例主题")
        example_topics = [
            "量子计算的最新进展",
            "2024年人工智能趋势",
            "气候变化的经济影响",
            "区块链在供应链中的应用"
        ]
        
        for topic in example_topics:
            if st.button(topic, key=f"example_{topic}", use_container_width=True):
                st.session_state.example_topic = topic
    
    # 主界面
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 研究主题输入
        default_topic = st.session_state.get('example_topic', '')
        research_topic = st.text_input(
            "🎯 研究主题",
            value=default_topic,
            placeholder="例如: 量子计算的最新进展和应用前景",
            help="输入你想深入研究的主题"
        )
        
        # 清除示例主题
        if 'example_topic' in st.session_state:
            del st.session_state.example_topic
    
    with col2:
        st.write("")  # 对齐
        st.write("")
        start_button = st.button(
            "🚀 开始研究",
            type="primary",
            disabled=st.session_state.is_researching or not research_topic,
            use_container_width=True
        )
    
    # 执行研究
    if start_button and research_topic:
        st.session_state.is_researching = True
        st.session_state.research_result = None
        
        # 进度显示
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_callback(message: str, current: int, total: int):
            """进度回调函数"""
            progress = current / total
            progress_bar.progress(progress)
            status_text.info(f"📊 {message}")
        
        try:
            # 创建研究编排器
            orchestrator = ResearchOrchestrator(ai_provider=ai_provider)
            
            # 执行研究
            with st.spinner("🔬 研究进行中..."):
                result = orchestrator.conduct_research(
                    topic=research_topic,
                    max_rounds=max_rounds,
                    results_per_search=results_per_search,
                    progress_callback=progress_callback
                )
            
            st.session_state.research_result = result
            progress_bar.progress(1.0)
            status_text.success("✅ 研究完成!")
            
        except Exception as e:
            logger.error(f"研究失败: {str(e)}", exc_info=True)
            st.error(f"❌ 研究失败: {str(e)}")
        
        finally:
            st.session_state.is_researching = False
    
    # 显示结果
    if st.session_state.research_result:
        result = st.session_state.research_result
        
        st.divider()
        st.success("✅ 研究完成!")
        
        # 统计信息
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("研究轮数", result.total_rounds)
        with col2:
            st.metric("参考来源", len(result.all_sources))
        with col3:
            st.metric("完成时间", result.timestamp.strftime("%H:%M:%S"))
        with col4:
            st.metric("AI 模型", ai_choice.split()[0])
        
        st.divider()
        
        # 结果展示
        tabs = st.tabs(["📄 最终报告", "🔍 研究过程", "🔗 参考来源"])
        
        with tabs[0]:
            st.markdown(result.final_report)
        
        with tabs[1]:
            for round_data in result.rounds:
                with st.expander(f"第 {round_data.round_number} 轮研究", expanded=False):
                    st.write(f"**查询**: {', '.join(round_data.queries)}")
                    st.write(f"**搜索结果数**: {len(round_data.search_results)}")
                    st.write(f"**内容提取数**: {len(round_data.extracted_contents)}")
                    
                    if round_data.analysis:
                        st.subheader("分析结果")
                        
                        if 'summary' in round_data.analysis:
                            st.write("**摘要**:")
                            st.info(round_data.analysis['summary'])
                        
                        if 'key_findings' in round_data.analysis:
                            st.write("**主要发现**:")
                            for finding in round_data.analysis['key_findings']:
                                st.write(f"- {finding}")
        
        with tabs[2]:
            st.write(f"共 {len(result.all_sources)} 个参考来源:")
            for i, source in enumerate(result.all_sources, 1):
                st.write(f"{i}. [{source}]({source})")
        
        st.divider()
        
        # 导出选项
        st.subheader("📥 导出报告")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("💾 导出 Markdown", use_container_width=True):
                try:
                    export_manager = ExportManager()
                    md_path = export_manager.export_markdown(
                        result.final_report,
                        result.topic
                    )
                    st.success(f"已保存到: {md_path}")
                    
                    # 提供下载
                    with open(md_path, 'r', encoding='utf-8') as f:
                        st.download_button(
                            label="⬇️ 下载 Markdown",
                            data=f.read(),
                            file_name=md_path.name,
                            mime="text/markdown",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"导出失败: {str(e)}")
        
        with col2:
            if st.button("📄 导出 PDF", use_container_width=True):
                try:
                    with st.spinner("正在生成 PDF..."):
                        export_manager = ExportManager()
                        pdf_path = export_manager.export_pdf(
                            result.final_report,
                            result.topic
                        )
                        st.success(f"已保存到: {pdf_path}")
                        
                        # 提供下载
                        with open(pdf_path, 'rb') as f:
                            st.download_button(
                                label="⬇️ 下载 PDF",
                                data=f.read(),
                                file_name=pdf_path.name,
                                mime="application/pdf",
                                use_container_width=True
                            )
                except Exception as e:
                    st.error(f"导出失败: {str(e)}")
    
    # 页脚
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        Made with ❤️ by Deep Research | Powered by AI
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
