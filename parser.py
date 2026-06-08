import re
import frontmatter
from langchain_text_splitters import MarkdownHeaderTextSplitter

def process_obsidian_note(md_text):
    """
    无损解析 Obsidian Markdown 笔记，提取元数据并按层级切分
    """
    # 1. 提取 YAML Frontmatter 和 干净的正文 (告别脆弱的正则表达式)
    post = frontmatter.loads(md_text)
    frontmatter_data = post.metadata # 自动解析为字典
    content_to_split = post.content  # 自动剥离 YAML 后的纯正文

    # 2. 提取全文的双向链接 [[xxx]]
    wikilinks = re.findall(r'\[\[(.*?)\]\]', content_to_split)
    unique_links = list(set(wikilinks)) # 去重

    # 3. 按 Markdown 标题层级切分 (Smart Chunking)
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    splits = markdown_splitter.split_text(content_to_split)

    # 4. 将提取到的元数据注入到每个 Chunk 中
    for chunk in splits:
        # 注入分类标签
        if 'tags' in frontmatter_data:
            chunk.metadata['tags'] = frontmatter_data['tags']
        if 'status' in frontmatter_data:
            chunk.metadata['status'] = frontmatter_data['status']
            
        # 注入双向链接
        chunk.metadata['obsidian_links'] = unique_links

    return splits

# ==========================================
# 测试运行区域
# ==========================================
if __name__ == "__main__":
    sample_note = """---
tags: [教学设计, 数列, 高中数学]
status: draft
---
# 数列教学策略与优化方案
## 新高考背景下的考点分析
在新高考中，数列不再仅仅是公式的套用，更强调与不等式、函数思想的结合。我们可以参考 [[不等式放缩技巧]] 来加深理解。

### 等差数列的教学痛点
学生容易死记硬背通项公式 $a_n = a_1 + (n-1)d$，而忽略了其本质是一次函数在离散状态下的表现。
为了解决这个问题，在导入环节可以引入 [[运筹学基础]] 中的一些资源分配模型，让学生感受到数列的实际应用价值。
"""

    chunks = process_obsidian_note(sample_note)

    print(f"成功将笔记切分为 {len(chunks)} 个 Chunk！\n")
    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i+1} ---")
        print(f"📖 内容 (Content):\n{chunk.page_content}")
        print(f"🏷️ 元数据 (Metadata): {chunk.metadata}\n")