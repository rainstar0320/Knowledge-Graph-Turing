from core.kg_storage import KnowledgeStorage
from core.kg_extraction import KnowledgeExtractor
from core.kg_disambiguation import EntityLinker
from core.kg_fusion import KnowledgeFuser

def run_pipeline():
    print("====== 2026知识工程 知识图谱 ======\n")

    # 1. 初始化模块
    storage = KnowledgeStorage()
    extractor = KnowledgeExtractor()
    linker = EntityLinker()
    fuser = KnowledgeFuser(storage)

    # 2. 模拟网络爬虫传来的实时纯文本 (非结构化数据)
    raw_texts = [
        "计算机科学家包括图灵、冯·诺依曼和姚期智。",
        "艾伦图灵曾在英国布莱切利园工作。",
        "图灵在1950年发表了划时代的论文。"
    ]

    # 3. 执行流水线处理
    for text in raw_texts:
        print(f"\n>>> 正在处理文本: '{text}'")

        # 知识抽取
        entities = extractor.extract_entities(text)
        new_triples = extractor.extract_relations_hearst(text)

        # 实体消歧
        for triple in new_triples:
            head_raw, rel, tail_raw = triple
            head_standard = linker.link_entity(head_raw, context=text)
            tail_standard = linker.link_entity(tail_raw, context=text)

            print(f"    [EL 消歧] '{head_raw}' -> 链接至 '{head_standard}'")

            # 存入知识库
            storage.add_instance(head_standard, "Entity")
            storage.add_instance(tail_standard, "Concept")
            storage.add_triple(head_standard, rel, tail_standard)

        # 针对单纯抽取的实体添加入库
        for ent in entities:
            ent_std = linker.link_entity(ent["entity"], context=text)
            storage.add_instance(ent_std, ent["type"])

    # 知识融合与对齐
    print("\n>>> 执行知识库一致性检查与融合对齐...")
    fuser.fuse_entities(threshold=0.6)

    # 数据持久化保存
    print("\n>>> 保存至硬盘...")
    storage.save()
    print("\n====== 执行完毕。 ======")

if __name__ == "__main__":
    run_pipeline()