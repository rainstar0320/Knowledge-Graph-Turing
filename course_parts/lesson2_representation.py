# ==========================================
# 进度：第2章 - 知识表示 (引入语义网概念：TBox, ABox, RDFS子类推理)
# ==========================================

class SemanticKnowledgeGraph:
    def __init__(self, name="图灵知识图谱-语义表示版"):
        self.name = name
        
        # TBox
        self.classes = set()             # 概念/类
        self.subclass_of = []            # 子类关系公理
        self.properties = set()          # 属性/关系定义
        
        # ABox
        self.instances = {}              # 个体实例声明
        self.facts = []                  # 事实断言三元组

    def add_class(self, class_name):
        self.classes.add(class_name)

    def add_subclass_axiom(self, sub_class, super_class):
        #添加子类公理 (rdfs:subClassOf)
        self.classes.add(sub_class)
        self.classes.add(super_class)
        self.subclass_of.append((sub_class, super_class))

    def add_instance(self, entity_name, class_name):
        #断言个体 (rdf:type)
        self.instances[entity_name] = class_name
        if class_name not in self.classes:
            self.classes.add(class_name)

    def add_fact(self, head, relation, tail):
        #添加事实断言三元组
        self.properties.add(relation)
        fact = (head, relation, tail)
        if fact not in self.facts:
            self.facts.append(fact)

    # 简单推理机
    def infer_types(self):
        #规则：如果 A 是 B 的子类，且 x 是 A 的实例，则 x 也是 B 的实例。
        inferred_types = []
        for entity, entity_type in self.instances.items():
            for sub_c, super_c in self.subclass_of:
                if entity_type == sub_c:
                    inferred_types.append((entity, super_c))
        return inferred_types

    def show_graph(self):
        print(f"语义表示：")
        print("\n【TBox】概念与本体定义:")
        print("  - 定义的类:", ", ".join(self.classes))
        for sub, sup in self.subclass_of:
            print(f"  - 子类公理: [{sub}] 是 [{sup}] 的子类")
            
        print("\n【ABox】事实与实例断言:")
        for ent, cls in self.instances.items():
            print(f"  - 个体声明: [{ent}] 属于 [{cls}] 类")
        for h, r, t in self.facts:
            print(f"  - 事实三元组: < {h} , {r} , {t} >")

        print("\n简单演绎推理:")
        inferred = self.infer_types()
        if inferred:
            for ent, sup_cls in inferred:
                print(f"  -> [推理得]: 因为 [{ent}] 是 {self.instances[ent]}, 所以其也是 [{sup_cls}]")


if __name__ == "__main__":
    kg = SemanticKnowledgeGraph()

    # 构建 TBox
    kg.add_class("Person")
    kg.add_class("Scientist")
    kg.add_class("Location")
    kg.add_class("Concept")
    
    # 建立类的层级关系
    kg.add_subclass_axiom("Scientist", "Person")

    # 构建 ABox
    kg.add_instance("阿兰·图灵", "Scientist")
    kg.add_instance("英国伦敦", "Location")
    kg.add_instance("图灵机", "Concept")
    kg.add_instance("图灵测试", "Concept")

    # 声明关系三元组
    kg.add_fact("阿兰·图灵", "出生于", "英国伦敦")
    kg.add_fact("阿兰·图灵", "提出", "图灵机")
    kg.add_fact("阿兰·图灵", "提出", "图灵测试")

    kg.show_graph()