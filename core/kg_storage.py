import json
import os

class KnowledgeStorage:
    def __init__(self, filepath="data/kg_data.json"):
        self.filepath = filepath
        # TBox (模式层/本体层)
        self.ontology = {
            "classes": set(),
            "subclasses": []
        }
        # ABox (数据层/实例层)
        self.knowledge_base = {
            "instances": {},        # 实体->类型
            "triples": []           # 事实三元组
        }
        self.load()

    def add_class(self, class_name):
        self.ontology["classes"].add(class_name)

    def add_instance(self, entity, class_name):
        self.knowledge_base["instances"][entity] = class_name
        self.add_class(class_name)

    def add_triple(self, head, relation, tail):
        triple = [head, relation, tail]
        if triple not in self.knowledge_base["triples"]:
            self.knowledge_base["triples"].append(triple)

    def save(self):
        """持久化存储到JSON"""
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        data = {
            "ontology": {
                "classes": list(self.ontology["classes"]),
                "subclasses": self.ontology["subclasses"]
            },
            "knowledge_base": self.knowledge_base
        }
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"[Storage] 知识图谱已保存至 {self.filepath}，当前三元组数量: {len(self.knowledge_base['triples'])}")

    def load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.ontology["classes"] = set(data["ontology"]["classes"])
                self.ontology["subclasses"] = data["ontology"]["subclasses"]
                self.knowledge_base = data["knowledge_base"]
            print("[Storage] 已加载历史知识图谱数据。")