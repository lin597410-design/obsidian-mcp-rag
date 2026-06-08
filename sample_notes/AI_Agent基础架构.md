---
tags: [AI, Agent, 架构体系]
status: review
---
# AI Agent 基础架构与核心组件
## 什么是真正的 AI Agent？
区别于传统的单一问答模型（Chatbot），AI Agent（智能体）是将大语言模型（LLM）作为大脑，辅以感知、记忆和执行模块的完整系统。它的核心价值在于“自主决策与行动”。

### Agent 的四大核心支柱
1. **控制中心 (LLM Brain)**: 负责理解复杂指令、逻辑推理与决策规划。
2. **规划能力 (Planning)**: 包含任务分解（Task Decomposition）和自我反思（Self-Reflection）。业界常用的规划框架可以参考 [[ReAct 提示词工程]]。
3. **记忆系统 (Memory)**: 
   - 短期记忆：即当前的会话上下文（Context Window）。
   - 长期记忆：通常借助向量数据库来实现，具体落地可参考 [[RAG 检索增强架构]]。
4. **工具调用 (Tools/Actions)**: 允许大模型突破文本边界，与真实世界交互。例如通过 API 搜索网页、执行 Python 代码或读取本地文件。我们正在使用的 [[MCP 标准协议]] 便是统一工具接口的前沿方案。