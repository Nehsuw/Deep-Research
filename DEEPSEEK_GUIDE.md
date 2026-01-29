# DeepSeek API 使用指南

## 为什么选择 DeepSeek？

DeepSeek 是一个高性价比的 AI 服务提供商，提供与 OpenAI 兼容的 API 接口。相比 GPT-4：

- 💰 **价格优势**: 成本更低，性价比更高
- 🚀 **兼容性好**: API 格式完全兼容 OpenAI
- 🎯 **性能优秀**: 在多项任务上表现出色
- 🇨🇳 **国内友好**: 访问速度更快，无需额外配置

## 快速开始

### 1. 获取 DeepSeek API 密钥

1. 访问 [DeepSeek 平台](https://platform.deepseek.com/)
2. 注册并登录账号
3. 进入 API 密钥管理页面
4. 创建新的 API 密钥
5. 复制保存密钥（仅显示一次）

### 2. 配置环境变量

编辑项目根目录下的 `.env` 文件：

```bash
# DeepSeek API 配置
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 可选：模型选择
DEEPSEEK_MODEL=deepseek-chat  # 默认模型，适合大多数场景
# DEEPSEEK_MODEL=deepseek-reasoner  # 推理模型，适合复杂逻辑任务
```

### 3. 运行应用

```bash
# 安装依赖（首次运行）
pip install -r requirements.txt

# 启动应用
streamlit run app.py
```

应用会自动检测 DeepSeek API 密钥并将其作为默认选项。

## DeepSeek 模型说明

### deepseek-chat
- **适用场景**: 通用对话、内容分析、信息提取
- **特点**: 速度快、成本低
- **推荐用于**: 日常研究任务、快速原型开发

### deepseek-reasoner
- **适用场景**: 复杂推理、逻辑分析、深度思考
- **特点**: 推理能力强、适合复杂问题
- **推荐用于**: 需要深度分析的研究任务

## 使用示例

### 场景 1：快速信息研究

```python
# 配置使用 deepseek-chat
DEEPSEEK_MODEL=deepseek-chat
```

适合：
- 行业趋势调研
- 新闻事件分析
- 产品市场研究

### 场景 2：深度逻辑分析

```python
# 配置使用 deepseek-reasoner
DEEPSEEK_MODEL=deepseek-reasoner
```

适合：
- 学术问题研究
- 技术方案对比
- 复杂决策分析

## 费用说明

DeepSeek 采用按量计费模式：

- **输入 Token**: ￥0.001 / 1K tokens
- **输出 Token**: ￥0.002 / 1K tokens

示例计算（单次研究）：
- 3 轮搜索
- 每轮约 5000 tokens (输入) + 2000 tokens (输出)
- 总费用：约 ￥0.027

相比 GPT-4，成本降低约 **95%**！

## 常见问题

### Q1: DeepSeek API 是否稳定？
A: 是的，DeepSeek 提供企业级的稳定性保障，并有完善的文档支持。

### Q2: 可以同时配置多个 AI 服务吗？
A: 可以！你可以同时配置 DeepSeek、OpenAI 和 Claude，在应用中切换使用。

### Q3: 如何处理 API 限流？
A: DeepSeek 提供了较高的 RPM（每分钟请求数）限制。如遇限流，可在 `.env` 中调整：
```bash
MAX_CONCURRENT_REQUESTS=3  # 降低并发数
```

### Q4: 支持哪些地区？
A: DeepSeek 服务在全球可用，在中国大陆访问速度尤其快。

## 性能对比

| 模型 | 速度 | 成本 | 质量 | 推荐指数 |
|------|------|------|------|----------|
| DeepSeek Chat | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| DeepSeek Reasoner | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| GPT-4 | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Claude 3 | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 技术支持

- 官方文档: https://platform.deepseek.com/docs
- API 状态: https://status.deepseek.com/
- 社区支持: https://github.com/deepseek-ai

## 最佳实践

1. **混合使用**: 日常研究用 DeepSeek，关键任务用 GPT-4/Claude
2. **参数调优**: 根据任务类型选择合适的 `DEEPSEEK_MODEL`
3. **成本控制**: 使用 `MAX_RESEARCH_ROUNDS` 控制研究深度
4. **并发优化**: 调整 `MAX_CONCURRENT_REQUESTS` 平衡速度和稳定性

---

🎉 开始使用 DeepSeek，享受高性价比的 AI 研究体验！
