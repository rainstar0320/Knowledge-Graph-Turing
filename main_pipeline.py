from core.kg_storage import KnowledgeStorage
from core.kg_extraction import KnowledgeExtractor
from core.kg_disambiguation import EntityLinker
from core.kg_fusion import KnowledgeFuser
from core.kg_relation_extraction import RelationExtractor


def run_pipeline():
    print("====== 2026知识工程 - 自动化知识图谱 ======\n")

    # 1. 初始化全生命周期组件
    storage = KnowledgeStorage()
    ner_extractor = KnowledgeExtractor()
    linker = EntityLinker()
    fuser = KnowledgeFuser(storage)
    relation_extractor = RelationExtractor()
    # 2. 模拟网络爬虫实时传来的纯文本流
    raw_texts = [
        "阿兰·图灵在1936年提出了图灵机，它是现代计算机科学的基础。",
        "艾伦图灵曾在英国布莱切利园秘密破译密码。",
        "作为计算机科学的奠基人，图灵荣获了无数后人的赞誉。"
    ]
    # 3. 执行流水线
    for text in raw_texts:
        print(f"\n>>> 正在处理文本: '{text}'")

        entities = ner_extractor.extract_entities(text)
        if len(entities) < 2:
            print("  -> 实体数量不足以构成关系，跳过。")
            continue

        raw_triples = relation_extractor.extract_open_relations(text, entities)

        for head_raw, rel, tail_raw in raw_triples:
            # 消歧
            head_std = linker.link_entity(head_raw, context=text)
            tail_std = linker.link_entity(tail_raw, context=text)
            print(f"    [消歧] '{head_raw}' -> '{head_std}', '{tail_raw}' -> '{tail_std}'")

            # 入库 (现在实时写入Neo4j了)
            storage.add_instance(head_std, "Entity")
            storage.add_instance(tail_std, "Entity")
            storage.add_triple(head_std, rel, tail_std)

    # 知识融合 (暂略，因为 Neo4j 内部需要使用专门的 Graph Refactoring 算法融合，我们后续用图算法实现)
    # fuser.fuse_entities(threshold=0.6)

    print("\n>>> 处理完毕！查询当前图谱状态...")
    storage.get_graph_stats()
    storage.close()
    print("\n====== 流水线执行完毕 ======")

if __name__ == "__main__":
    run_pipeline()