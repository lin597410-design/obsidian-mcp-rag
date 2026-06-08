---
tags: [Prompt, 算法框架, Agent]
status: completed
---
# ReAct 提示词工程揭秘
## 思考与行动的交织范式
ReAct (Reason + Act) 是一种让大模型在解决复杂问题时，交替进行“逻辑推理”和“工具调用”的交互范式。它通过强制模型输出内部思考过程，有效缓解了大型模型常见的“幻觉”现象。

### ReAct 的基本运转流
一次完整的 ReAct 周期包含以下三个步骤，缺一不可，这构成了 [[AI_Agent基础架构]] 中“规划”能力的核心：

* **Thought (思考)**: 模型分析当前现状，决定下一步需要什么信息。
* **Action (行动)**: 模型按照规定格式，选择调用一个外部工具。
* **Observation (观察)**: 系统拦截工具输出，将真实执行结果返回给大模型。

### 经典 Prompt 模板示例
在实际开发中，我们通常会在 System Prompt 中规定如下的运行格式：

```text
Question: {用户输入的复杂问题}
Thought: 我需要查阅关于 AI Agent 组件的详细资料。
Action: search_obsidian_knowledge
Action Input: {"query": "Agent 的四大组件", "tag_filter": "架构体系"}
Observation: {工具返回的本地笔记切片}
Thought: 我已经掌握了相关知识，可以开始回答了。
Final Answer: 你的最终回答...