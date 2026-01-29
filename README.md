# Deep Research - AI-Powered Research Assistant

🔍 一个基于 AI 的智能深度研究工具，通过多轮搜索和智能分析帮助你快速完成深度研究。

## ✨ 功能特性

- 🤖 **AI 智能分析**: 集成 OpenAI GPT-4 和 Anthropic Claude，智能分析和整合信息
- 🔎 **多轮深度搜索**: 自动生成后续查询，进行多轮深度信息检索
- 🌐 **网页内容提取**: 自动提取和清洗网页正文内容
- 📊 **实时进度展示**: 可视化展示研究进度和中间结果
- 📄 **多格式导出**: 支持 Markdown 和 PDF 格式导出研究报告
- 🎨 **现代化界面**: 基于 Streamlit 的美观交互界面

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd deep-research
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API 密钥

复制 `.env.example` 为 `.env` 并填入你的 API 密钥:

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入至少一个 AI API 密钥:

```
OPENAI_API_KEY=sk-xxxxx
# 或
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### 4. 运行应用

```bash
streamlit run app.py
```

应用将在浏览器中自动打开 (默认地址: http://localhost:8501)

## 📖 使用方法

1. **输入研究主题**: 在文本框中输入你想研究的主题
2. **选择 AI 模型**: 选择使用 OpenAI 或 Claude 进行分析
3. **配置参数**: 设置研究轮数和每轮搜索结果数量
4. **开始研究**: 点击"开始研究"按钮，系统将自动执行多轮搜索和分析
5. **查看结果**: 实时查看研究进度和分析结果
6. **导出报告**: 研究完成后，下载 Markdown 或 PDF 格式报告

## 🛠️ 技术栈

- **前端界面**: Streamlit
- **AI 模型**: OpenAI GPT-4 / Anthropic Claude
- **搜索引擎**: DuckDuckGo Search API
- **网页解析**: BeautifulSoup4 + Requests
- **文档生成**: Python-Markdown + WeasyPrint
- **环境管理**: python-dotenv

## 📁 项目结构

```
deep-research/
├── app.py                    # Streamlit 应用主入口
├── requirements.txt          # Python 依赖
├── .env.example             # 环境变量模板
├── .gitignore               # Git 忽略配置
├── README.md                # 项目文档
├── config/
│   ├── __init__.py
│   └── settings.py          # 配置管理
├── core/
│   ├── __init__.py
│   ├── search_engine.py     # 搜索引擎封装
│   ├── ai_analyzer.py       # AI 分析模块
│   ├── content_extractor.py # 内容提取模块
│   └── research_orchestrator.py # 研究流程编排
├── utils/
│   ├── __init__.py
│   ├── export_manager.py    # 导出管理
│   └── logger.py            # 日志配置
└── outputs/                 # 导出文件目录
```

## ⚙️ 配置说明

在 `.env` 文件中可配置以下参数:

- `OPENAI_API_KEY`: OpenAI API 密钥
- `ANTHROPIC_API_KEY`: Anthropic Claude API 密钥
- `MAX_RESEARCH_ROUNDS`: 最大研究轮数 (默认: 3)
- `RESULTS_PER_SEARCH`: 每轮搜索结果数 (默认: 10)
- `MAX_CONCURRENT_REQUESTS`: 最大并发请求数 (默认: 5)

## 📝 示例

**研究主题示例**:
- "量子计算的最新进展和应用前景"
- "2024年人工智能行业发展趋势"
- "气候变化对全球经济的影响"
- "区块链技术在供应链管理中的应用"

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [Streamlit](https://streamlit.io/) - 强大的 Python Web 应用框架
- [OpenAI](https://openai.com/) - GPT 系列模型
- [Anthropic](https://www.anthropic.com/) - Claude 模型
- [DuckDuckGo](https://duckduckgo.com/) - 隐私友好的搜索引擎
