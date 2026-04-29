# ==========================================
# 架构升级：引入 Neo4j 图数据库作为底层存储引擎
# 机制：使用 Cypher 的 MERGE 语句实现“存在则更新，不存在则创建”
# ==========================================

from neo4j import GraphDatabase
import re


class KnowledgeStorage:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="20050320txl"):
        # 请将这里的 password 改为你刚才在 Neo4j Desktop 中设置的密码
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
            print("[Storage] 成功连接到 Neo4j 图数据库！")
        except Exception as e:
            print(f"[Storage] 连接 Neo4j 失败，请检查数据库是否启动以及密码是否正确。\n错误信息: {e}")

    def close(self):
        """关闭数据库连接"""
        if self.driver:
            self.driver.close()
            print("[Storage] 数据库连接已安全关闭。")

    def _clean_label(self, label):
        """清洗标签名称，因为 Neo4j 的 Label 和 Relation 类别不支持空格和特殊符号"""
        cleaned = re.sub(r'[^\w\u4e00-\u9fa5]', '_', label)
        return cleaned if cleaned else "Entity"

    def add_instance(self, entity_name, class_name):
        """向图中添加实体节点 (ABox) 和 标签类型 (TBox)"""
        clean_class = self._clean_label(class_name)

        # ⚠️ 注意这里 n: 的后面加上了反引号 ` `，防止非标准字符报错
        query = f"""
        MERGE (n:`{clean_class}` {{name: $name}})
        SET n.updated_at = timestamp()
        """
        with self.driver.session() as session:
            session.run(query, name=entity_name)

    def add_triple(self, head, relation, tail):
        """向图中添加事实关系边"""
        clean_rel = self._clean_label(relation)

        # ⚠️ 注意这里 r: 的后面加上了反引号 ` `，允许关系名以数字开头！
        query = f"""
        MERGE (h {{name: $head}})
        MERGE (t {{name: $tail}})
        MERGE (h)-[r:`{clean_rel}`]->(t)
        SET r.updated_at = timestamp()
        """
        with self.driver.session() as session:
            session.run(query, head=head, tail=tail)

    def save(self):
        """保留此接口为兼容流水线"""
        print("[Storage] Neo4j 图数据库已实时落盘，无须额外 save 操作。")

    def get_graph_stats(self):
        """获取当前数据库的统计信息"""
        query = """
        MATCH (n) WITH count(n) AS node_count
        MATCH ()-[r]->() RETURN node_count, count(r) AS edge_count
        """
        with self.driver.session() as session:
            result = session.run(query).single()
            if result:
                print(f"[Storage] 数据库统计 -> 节点数: {result['node_count']} | 关系数: {result['edge_count']}")