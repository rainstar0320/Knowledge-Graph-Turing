# main_pipeline.py
import wikipedia
from core.kg_storage import KnowledgeStorage
from core.kg_extraction import DeepKnowledgeExtractor
from core.kg_disambiguation import EntityLinker
from core.kg_fusion import DeepKnowledgeFuser


def fetch_wiki_summary(keyword):
    """解除封印的网络爬虫：抓取完整的百科摘要"""
    wikipedia.set_lang("zh")
    print(f"\n[Spider] 正在实时爬取网络数据: '{keyword}'...")
    try:
        # 取完整的摘要内容 (不再限制前两句！)
        text = wikipedia.summary(keyword)
        # 简单清洗一下文本，去掉换行符
        text = text.replace('\n', ' ').replace('\r', '')
        print(f"[Spider] 🟢 爬取成功！获取文本长度: {len(text)} 字符")
        return text
    except Exception as e:
        print(f"[Spider] 🔴 爬取失败: {e}")
        return ""


def run_pipeline():
    print("====== 2026知识工程(AI) - 自动化知识图谱流水线 (火力全开版) ======\n")

    storage = KnowledgeStorage()
    dl_extractor = DeepKnowledgeExtractor()
    linker = EntityLinker()
    dl_fuser = DeepKnowledgeFuser(storage)

    # 🚀 扩充我们的种子库！让系统去爬取几十个相关词条
    targets = [
        "阿兰·图灵", "约翰·冯·诺伊曼", "姚期智", "吴恩达", "李飞飞",
        "计算机科学", "人工智能", "机器学习", "深度学习", "图灵奖",
        "清华大学", "麻省理工学院", "斯坦福大学", "剑桥大学",
        "苹果公司", "微软", "谷歌", "OpenAI",
        "第二次世界大战", "密码学", "诺贝尔奖"
    ]

    raw_texts = []
    for t in targets:
        txt = fetch_wiki_summary(t)
        if txt:
            raw_texts.append(txt)

    # 2. 核心大模型处理流 (因为文本变多了，这里会跑几分钟，请让 CPU 飞一会儿)
    print(f"\n>>> 准备处理 {len(raw_texts)} 篇长文本，大模型全速运转中...")
    for text in raw_texts:
        entities = dl_extractor.extract_entities(text)
        if len(entities) < 2: continue

        raw_triples = dl_extractor.joint_relation_extraction(text, entities)

        for head_raw, rel, tail_raw in raw_triples:
            head_std = linker.link_entity(head_raw, context=text)
            tail_std = linker.link_entity(tail_raw, context=text)

            storage.add_instance(head_std, "Entity")
            storage.add_instance(tail_std, "Entity")
            storage.add_triple(head_std, rel, tail_std)

    # 3. 大模型向量融合
    print("\n>>> 开始全库实体对齐与融合 (清理垃圾节点)...")
    dl_fuser.deep_entity_alignment(similarity_threshold=0.85)

    storage.get_graph_stats()
    storage.close()
    print("\n====== 流水线执行完毕！快去刷新网页看看！ ======")


if __name__ == "__main__":
    run_pipeline()