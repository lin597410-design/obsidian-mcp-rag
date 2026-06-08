import os
import sys
from fastmcp import FastMCP
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# 1. 初始化 FastMCP 服务
mcp = FastMCP("Obsidian 本地知识库中枢")

# ==========================================
# 修复核心区：绝对路径与安全日志
# ==========================================
# 获取当前脚本所在的绝对路径，确保 ChromaDB 不会“迷路”
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "chroma_db")

# 绝对不能使用普通 print()，必须将其重定向到 stderr，否则会污染 JSON-RPC 通信通道
if not os.path.exists(DB_DIR):
    print(f"⚠️ 警告: 未找到本地向量文件夹 {DB_DIR}，请先运行 knowledge_base.py！", file=sys.stderr)

# 初始化嵌入模型
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# 加载数据库
vector_db = Chroma(
    persist_directory=DB_DIR,
    embedding_function=embeddings
)

# ==========================================
# 注册标准 MCP 工具
# ==========================================
@mcp.tool(
    name="search_obsidian_knowledge",
    description="本地知识库检索引擎。当用户询问关于专业领域的具体细节、推导过程或笔记记录时，调用此工具。"
)
def search_obsidian_knowledge(query: str, tag_filter: str = None) -> str:
    """
    通过语义搜索本地向量库，可选传入标签进行硬过滤。
    """
    filter_condition = None
    if tag_filter:
        filter_condition = {"tags": {"$contains": tag_filter}}
    
    try:
        results = vector_db.similarity_search_with_score(
            query, 
            k=3, 
            filter=filter_condition
        )
    except Exception as e:
        # 错误信息作为字符串返回给大模型，而不是 print 出来
        return f"检索数据库时发生错误: {str(e)}"
    
    if not results:
        return f"未在本地知识库中找到关于 '{query}' 且匹配标签 '{tag_filter}' 的相关内容。"
    
    formatted_context = ["【已为您找到以下本地知识库上下文支撑】:\n"]
    for i, (doc, score) in enumerate(results):
        source_file = doc.metadata.get("source_file", "未知文件")
        headers = [doc.metadata.get(f"Header {j}") for j in range(1, 4) if doc.metadata.get(f"Header {j}")]
        title_path = " -> ".join(headers) if headers else "正文片段"
        
        formatted_context.append(
            f"--- 支撑材料 {i+1} ---\n"
            f"📄 出处: {source_file} ({title_path})\n"
            f"🔍 相关度得分: {score:.4f}\n"
            f"📝 核心内容:\n{doc.page_content.strip()}\n"
        )
        
    return "\n".join(formatted_context)

if __name__ == "__main__":
    mcp.run(transport="stdio")