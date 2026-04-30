# core/kg_storage.py
import re
from neo4j import GraphDatabase

class KnowledgeStorage:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="20050320txl"):
        # ⚠️ 请确认这里的 password 是你在 Neo4j 里设置的密码！
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
            print("[Storage] 🟢 成功连接到 Neo4j 图数据库！")
        except Exception as e:
            print(f"[Storage] 🟡 警告: 无法连接到 Neo4j (请检查是否在软件中点击了 Start 并且密码正确)。")
            print("[Storage] 🟡 已自动切入离线模拟模式，保证流水线不崩溃。")
            self.driver = None # 设为 None，进入容灾模式

    def close(self):
        if self.driver:
            self.driver.close()
            print("[Storage] 数据库连接已安全关闭。")

    def _clean_label(self, label):
        cleaned = re.sub(r'[^\w\u4e00-\u9fa5]', '_', label)
        return cleaned if cleaned else "Entity"

    def add_instance(self, entity_name, class_name):
        if not self.driver:
            # 容灾模式：只打印，不崩溃
            # print(f"    [Mock Storage] 实体入库 -> {entity_name} ({class_name})")
            return

        clean_class = self._clean_label(class_name)
        query = f"""
        MERGE (n:`{clean_class}` {{name: $name}})
        SET n.updated_at = timestamp()
        """
        with self.driver.session() as session:
            session.run(query, name=entity_name)

    def add_triple(self, head, relation, tail):
        if not self.driver:
            # 容灾模式：只打印，不崩溃
            print(f"    [Mock Storage] 事实入库 -> <{head}, {relation}, {tail}>")
            return

        clean_rel = self._clean_label(relation)
        query = f"""
        MERGE (h {{name: $head}})
        MERGE (t {{name: $tail}})
        MERGE (h)-[r:`{clean_rel}`]->(t)
        SET r.updated_at = timestamp()
        """
        with self.driver.session() as session:
            session.run(query, head=head, tail=tail)

    def save(self):
        if self.driver:
            print("[Storage] Neo4j 图数据库已实时落盘，无须额外 save 操作。")

    def get_graph_stats(self):
        if not self.driver:
            print("[Storage] 📊 当前处于离线模式，无法统计 Neo4j 数据库规模。")
            return

        query = """
        MATCH (n) WITH count(n) AS node_count
        MATCH ()-[r]->() RETURN node_count, count(r) AS edge_count
        """
        with self.driver.session() as session:
            result = session.run(query).single()
            if result:
                print(f"[Storage] 📊 Neo4j 数据库统计 -> 节点数: {result['node_count']} | 关系数: {result['edge_count']}")