from core.kg_storage import KnowledgeStorage
from core.kg_extraction import KnowledgeExtractor
from core.kg_disambiguation import EntityLinker
from core.kg_fusion import KnowledgeFuser
from core.kg_relation_extraction import RelationExtractor


def run_pipeline():
    print("====== 2026知识工程 知识图谱流水线 ======\n")

    # 1. 初始化
    storage = KnowledgeStorage()
    ner_extractor = KnowledgeExtractor()
    linker = EntityLinker()
    fuser = KnowledgeFuser(storage)
    relation_extractor = RelationExtractor()

    # 2. 模拟爬虫实时传来的纯文本流 (非结构化数据)
    raw_texts = [
        "阿兰·图灵在1936年提出了图灵机，它是现代计算机科学的基础。",
        "艾伦图灵曾在英国布莱切利园秘密破译密码。",
        "作为计算机科学的奠基人，图灵荣获了无数后人的赞誉。"
    ]

    # 3. 执行流水线
    for text in raw_texts:
        print(f"\n>>> 正在处理文本: '{text}'")

        # 命名实体识别
        entities = ner_extractor.extract_entities(text)
        if len(entities) < 2:
            print("  -> 实体数量不足以构成关系，跳过。")
            continue

        # 开放式关系抽取
        # 将文本和识别出的实体送入模型，抽取出实体间的动词关系
        raw_triples = relation_extractor.extract_open_relations(text, entities)

        # 实体消歧与链接
        for head_raw, rel, tail_raw in raw_triples:
            head_std = linker.link_entity(head_raw, context=text)
            tail_std = linker.link_entity(tail_raw, context=text)
            print(f"    [消歧] '{head_raw}' -> '{head_std}', '{tail_raw}' -> '{tail_std}'")

            # 结构化入库

            storage.add_instance(head_std, "Entity")
            storage.add_instance(tail_std, "Entity")
            storage.add_triple(head_std, rel, tail_std)

    # 知识融合与消冗
    print("\n>>> 执行全库实体对齐与融合 (Entity Alignment)...")
    fuser.fuse_entities(threshold=0.6)

    # 数据持久化
    print("\n>>> 保存至硬盘...")
    storage.save()
    print("\n====== 流水线执行完毕。 ======")


if __name__ == "__main__":
    run_pipeline()