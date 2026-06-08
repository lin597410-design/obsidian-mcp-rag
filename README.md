# 🧠 Obsidian Local RAG & MCP Server

基于 Anthropic MCP (Model Context Protocol) 标准协议的完全离线本地 Markdown 知识库增强检索中枢。

本项目旨在打破本地知识孤岛，将高度结构化的 Markdown 笔记库（如 Obsidian Vault）与主流大语言模型客户端无缝对接。通过提供精确的语义检索与标准化的工具调用接口，让大模型在断网环境下也能基于你的个人专业知识库进行深度问答与辅助生成。

---

## ✨ 核心特性 (Core Features)

* **无损语境切分 (Smart Chunking)** 弃用传统的暴力字数切分（TextSplitter），基于 `python-frontmatter` 引擎，按 Markdown 标题层级 (`#`, `##`) 进行智能切片，无损保留数学公式、代码块与上下文逻辑流。
* **图谱锚点提取 (Graph-Ready Metadata)**
  自动正则提取 Obsidian 特有的 `[[双向链接]]` 与 YAML Frontmatter 标签，并将其作为元数据（Metadata）深度绑定到每一个知识切片中，为后续的 GraphRAG 演进提供基础。
* **抗漂移混合检索 (Anti-Drift Retrieval)**
  在 ChromaDB 的高维语义检索基础之上，叠加基于标签（Tags）的元数据硬过滤策略，彻底解决跨领域相似概念导致的“检索漂移”问题，提升高优知识的召回精度。
* **工程级鲁棒性 (Engineering Robustness)**
  内置基于 `shutil` 的向量库生命周期管理（防数据堆叠重复）、UTF-8 强制定向编码（防跨平台乱码），以及空文件/异常格式拦截机制。
* **标准 MCP 协议挂载 (FastMCP Integration)**
  通过 Stdio 形式将复杂的 RAG 检索链路封装为大模型标准的 Tool。完全跨进程运行，兼容所有支持 MCP 协议的 AI 客户端（如 Cherry Studio, Claude Desktop）。

---

## 🚀 快速启动 (Quick Start)

### 1. 环境准备
确保本地已安装 Python 3.10+，并在本地运行了 Ollama（或其他兼容的本地模型引擎）。
```bash
# 克隆仓库
git clone [https://github.com/你的用户名/你的仓库名.git](https://github.com/你的用户名/你的仓库名.git)
cd 你的仓库名

# 安装依赖
pip install -r requirements.txt

# 拉取本地向量嵌入模型 (推荐 nomic-embed-text)
ollama pull nomic-embed-text

```
### 2. 构建本地知识库
在项目根目录的 sample_notes/ 文件夹中放入你的 Markdown 笔记（项目已自带部分演示数据），然后运行构建脚本：
```bash
python knowledge_base.py

```
> **提示:** 脚本会自动清空旧的索引并重新构建向量库，避免数据重复堆叠。生成的向量数据将持久化保存在 ./chroma_db 目录中。
> 
### 3. MCP 服务端接入 (以 Cherry Studio 为例)
无需手动运行 mcp_server.py，请在客户端中直接配置唤醒路径：
 1. 进入 Cherry Studio -> 设置 -> MCP
 2. 新增服务器配置：
   * **类型 (Transport):** 选择 stdio
   * **命令 (Command):** 填写你本地虚拟环境的 Python 绝对路径（例如：D:\miniconda\envs\rag\python.exe）
   * **参数 (Arguments):** 填写项目中 mcp_server.py 的绝对路径（例如：D:\projects\obsidian-rag\mcp_server.py）
 3. 激活服务器状态为“已连接”。
### 4. 开启对话
在对话框输入区域勾选 search_obsidian_knowledge 工具，向大模型提问即可自动触发本地知识检索与整合！
## 🛠️ 技术栈构成 (Tech Stack)
 * **通信层:** FastMCP (基于 Anthropic Model Context Protocol)
 * **向量数据库:** ChromaDB (本地轻量级持久化)
 * **嵌入引擎:** Ollama (nomic-embed-text)
 * **数据流编排:** LangChain Community
 * **文档解析:** python-frontmatter, re (Regular Expressions)
## ⚠️ 隐私声明
本项目致力于提供 100% 本地的隐私保护。向量数据的生成、存储与检索均在本地设备完成，不会向云端上传任何私人笔记内容（除非您手动配置了外部云端大模型 API 来处理检索后的上下文）。建议在 .gitignore 中严格屏蔽个人真实的笔记目录与 chroma_db 文件夹。
```
