import os
import re
import shutil  # 【新增】用于物理删除旧的数据库文件夹
import frontmatter
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# ==========================================
# 1. Markdown 无损解析引擎
# ==========================================
def process_obsidian_note(md_text, file_name="unknown.md"):
    post = frontmatter.loads(md_text)
    frontmatter_data = post.metadata
    content_to_split = post.content

    wikilinks = re.findall(r'\[\[(.*?)\]\]', content_to_split)
    unique_links = list(set(wikilinks))

    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    splits = markdown_splitter.split_text(content_to_split)

    for chunk in splits:
        if 'tags' in frontmatter_data and frontmatter_data['tags']:
            chunk.metadata['tags'] = frontmatter_data['tags']
        if 'status' in frontmatter_data and frontmatter_data['status']:
            chunk.metadata['status'] = frontmatter_data['status']
            
        if unique_links:
            chunk.metadata['obsidian_links'] = unique_links
            
        chunk.metadata['source_file'] = file_name 

    return splits

# ==========================================
# 2. 动态目录扫描与向量库重建
# ==========================================
if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    NOTES_DIR = os.path.join(BASE_DIR, "sample_notes")
    DB_DIR = os.path.join(BASE_DIR, "chroma_db")

    if not os.path.exists(NOTES_DIR):
        print(f"📂 未找到目录 {NOTES_DIR}，已自动为您创建。请放入笔记后重试。")
        os.makedirs(NOTES_DIR)
        exit(0)

    # 在这里定义了 all_chunks 变量
    all_chunks = []
    print(f"🔍 正在扫描本地笔记目录: {NOTES_DIR}")
    
    # 扫描文件夹并填充 all_chunks
    for file_name in os.listdir(NOTES_DIR):
        if file_name.endswith(".md"):
            file_path = os.path.join(NOTES_DIR, file_name)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    md_content = f.read()
                
                if not md_content.strip():
                    print(f"  ⚠️ 警告: [{file_name}] 是空文件，已跳过。")
                    continue
                
                md_content = md_content.replace('\r\n', '\n')
                chunks = process_obsidian_note(md_content, file_name)
                
                if not chunks:
                    print(f"  ⚠️ 警告: [{file_name}] 未能拆分出有效内容。")
                else:
                    all_chunks.extend(chunks)
                    print(f"  ✅ 成功解析: [{file_name}] -> 拆分为 {len(chunks)} 个知识切片")
                
            except Exception as e:
                print(f"  ❌ 读取文件 [{file_name}] 失败: {str(e)}")

    # 边界检查
    if not all_chunks:
        print("\n🚨 致命错误: 最终未能获取到任何有效的文本切片。程序中止。")
        exit(1)

    print(f"\n📊 数据准备就绪：共收集到 {len(all_chunks)} 个 Chunk。")

    # ==========================================
    # 3. 向量库清理与重新写入
    # ==========================================
    
    # 核心防重复逻辑：写入前先销毁旧库
    if os.path.exists(DB_DIR):
        print(f"🗑️ 检测到旧的向量库索引，正在清空目录以防数据堆叠重复...")
        shutil.rmtree(DB_DIR)

    # 初始化嵌入模型
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    # 重新构建 ChromaDB（此时环境绝对干净）
    print("🚀 正在构建全新本地 Chroma 数据库并批量写入向量...")
    vector_db = Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    print("💾 向量数据库全新构建成功，索引已持久化到本地！\n")