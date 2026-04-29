# ==========================================
#第1章 - 知识图谱概述 (基于 G=(E, R, S) 结构)
# ==========================================

class KnowledgeGraphBase:
    def __init__(self, name="通用知识图谱"):
        self.name = name
        self.E = set()  # 实体集合 (E)
        self.R = set()  # 关系集合 (R)
        self.S = []     # 三元组集合 , S ⊆ E x R x E

    def add_triple(self, head_entity, relation, tail_entity):
        # 将实体加入实体集合 E
        self.E.add(head_entity)
        self.E.add(tail_entity)
        # 将关系加入关系集合 R
        self.R.add(relation)
        # 将三元组加入集合 S
        triple = (head_entity, relation, tail_entity)
        if triple not in self.S:
            self.S.append(triple)

    def summary(self):
        print(f"【{self.name}】 概览：")
        print(f"实体总数 (|E|): {len(self.E)}")
        print(f"关系总数 (|R|): {len(self.R)}")
        print(f"三元组数 (|S|): {len(self.S)}")

    def print_triples(self):
        print("当前图谱包含的事实 (三元组):")
        for i, (h, r, t) in enumerate(self.S, 1):
            print(f"  {i}. < {h} , {r} , {t} >")
        print("\n")

if __name__ == "__main__":
    # 1. 实例化知识图谱对象
    turing_kg = KnowledgeGraphBase(name="阿兰·图灵 (Alan Turing) 初始概念图谱")

    # 2. 手动构建并添加图灵相关的基础事实
    # 头实体: 阿兰·图灵
    turing = "阿兰·图灵"
    
    turing_kg.add_triple(turing, "出生年份", "1912年")
    turing_kg.add_triple(turing, "职业", "计算机科学家")
    turing_kg.add_triple(turing, "职业", "数学家")
    turing_kg.add_triple(turing, "提出概念", "图灵机")
    turing_kg.add_triple(turing, "提出概念", "图灵测试")
    turing_kg.add_triple(turing, "毕业院校", "剑桥大学国王学院")

    # 3. 输出图谱的概述信息
    turing_kg.summary()
    turing_kg.print_triples()
