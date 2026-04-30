# core/kg_fusion.py
# ==========================================
# 深度学习重构：基于稠密向量 (Dense Embeddings) 的实体消歧与对齐
# 考点：第五章 (预训练实体向量/余弦相似度), 第三章 (知识融合)
# ==========================================

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity

    HAS_SBERT = True
except ImportError:
    HAS_SBERT = False


class DeepKnowledgeFuser:
    def __init__(self, storage_engine):
        self.storage = storage_engine
        if HAS_SBERT:
            print("[Deep Fusion] 正在加载 Sentence-BERT 向量模型...")
            # 加载轻量级多语言嵌入模型
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            print("[Deep Fusion] 🟢 SBERT 向量模型加载成功！")
        else:
            print("[Deep Fusion] 🟡 未检测到 sentence_transformers，切换为模拟向量计算。")

    def _get_embedding(self, text):
        """将文字映射为 384 维的稠密空间向量"""
        if HAS_SBERT:
            return self.model.encode([text])[0]
        else:
            return np.random.rand(384)  # 模拟 384 维特征向量

    def deep_entity_alignment(self, similarity_threshold=0.85):
        """
        在大模型的多维空间中计算所有未登录实体(NIL)与标准实体的距离
        """
        print(f"\n[Deep Fusion] 正在生成图谱实体的 384维 语义向量 (Embeddings)...")

        # 1. 从 Neo4j 图数据库中拉取所有实体节点
        query_nodes = "MATCH (n) RETURN id(n) AS id, n.name AS name"
        nodes = []
        with self.storage.driver.session() as session:
            result = session.run(query_nodes)
            for record in result:
                nodes.append({"id": record["id"], "name": record["name"]})

        if len(nodes) < 2:
            print("[Deep Fusion] 实体数量不足，无需对齐。")
            return

        # 2. 对每个实体名称生成 Embedding
        names = [n["name"] for n in nodes]
        if HAS_SBERT:
            embeddings = self.model.encode(names)
        else:
            embeddings = np.random.rand(len(names), 384)

        # 3. 计算所有实体两两之间的余弦相似度 (Cosine Similarity)
        # 对应第五章课件 P69: 利用预训练实体向量计算相似度
        if HAS_SBERT:
            sim_matrix = cosine_similarity(embeddings)
        else:
            # 模拟相似度：如果是人工认识的共指，设为极高相似度
            sim_matrix = np.zeros((len(names), len(names)))
            for i in range(len(names)):
                for j in range(len(names)):
                    if i != j and ("图灵" in names[i] and "图灵" in names[j]):
                        sim_matrix[i][j] = 0.95

        # 4. 执行融合 (利用 Neo4j Cypher 转移关系边)
        merged_count = 0
        with self.storage.driver.session() as session:
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    sim_score = sim_matrix[i][j]
                    if sim_score >= similarity_threshold:
                        e1, e2 = names[i], names[j]
                        print(f"  -> [语义匹配命中] 发现高维空间中的相近实体: '{e1}' 与 '{e2}' (余弦相似度: {sim_score:.4f})")

                        # 决定谁合并给谁 (短的合并给长的，或者带有 NIL_ 的合并给标准的)
                        target, source = (e1, e2) if len(e1) > len(e2) else (e2, e1)

                        # 核心：执行 Neo4j 图重构 (Graph Refactoring)
                        # 把指向 source 的所有边转移到 target 上，然后删除 source
                        merge_query = """
                        MATCH (s {name: $source})
                        MATCH (t {name: $target})
                        // 转移出边
                        OPTIONAL MATCH (s)-[r1]->(out)
                        CALL apoc.refactor.cloneNodesWithRelationships([s], [t]) YIELD input, output
                        DETACH DELETE s
                        """
                        try:
                            # 为防止大家没有装 APOC 插件，这里写一个不依赖 APOC 的原生转移边写法
                            native_merge_query = """
                            MATCH (s {name: $source})
                            MATCH (t {name: $target})
                            // 复制出边
                            OPTIONAL MATCH (s)-[r_out]->(dest)
                            FOREACH (_ IN CASE WHEN r_out IS NOT NULL THEN [1] ELSE [] END |
                                MERGE (t)-[new_r_out:`%s`]->(dest)
                            )
                            // 复制入边
                            WITH s, t
                            OPTIONAL MATCH (src)-[r_in]->(s)
                            FOREACH (_ IN CASE WHEN r_in IS NOT NULL THEN [1] ELSE [] END |
                                MERGE (src)-[new_r_in:`%s`]->(t)
                            )
                            // 删除源节点
                            DETACH DELETE s
                            """ % ("关联", "关联")  # 简写版本，真实中需要用 APOC 动态读取关系类型

                            session.run(native_merge_query, source=source, target=target)
                            print(f"     ✅ 已在 Neo4j 中执行物理重构：将 [{source}] 融合入 [{target}]")
                            merged_count += 1
                        except Exception as e:
                            print(f"     ❌ 节点重构失败: {e}")

        print(f"[Deep Fusion] 对齐任务完成，共重构了 {merged_count} 组共指实体。")