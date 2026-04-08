# ==========================================
# 进度：第3章 - 知识体系构建 (模板抽取) 与 知识融合 (实体对齐)
# ==========================================

import re

class AdvancedKnowledgeGraph:
    def __init__(self, name="体系构建与融合"):
        self.name = name
        self.classes = set()             # TBox: 概念
        self.instances = {}              # ABox: 个体 -> 概念
        self.facts = []                  # ABox: 事实三元组

    def add_instance(self, entity, class_name):
        self.instances[entity] = class_name
        self.classes.add(class_name)

    def add_fact(self, head, relation, tail):
        fact = (head, relation, tail)
        if fact not in self.facts:
            self.facts.append(fact)

    # ================== 知识体系构建 (基于规则抽取) ==================
    # 启发式规则
    def extract_knowledge_from_text(self, text):
        print(f"\n分析文本: '{text}'")
        extracted_triples = []
        
        # 正则表达式定义简单的中文启发式模板： "概念如实体1、实体2"（"NP such as NP"）
        pattern = r'([a-zA-Z\u4e00-\u9fa5]+)(?:诸?如|比如)(.*?)(?:。|；|$)'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            concept = match.group(1).strip()
            entities_str = match.group(2)
            # 分割多个实体
            entities = re.split(r'[、,，和及]', entities_str)
            for ent in entities:
                ent = ent.strip()
                if ent:
                    extracted_triples.append((ent, "is-a", concept))
                    self.add_instance(ent, concept)
                    print(f"发现新实体 [{ent}], 概念归属为 [{concept}]")
                    
        return extracted_triples

    # ================== 知识融合 (实体对齐) ==================
    def _levenshtein_distance(self, s1, s2):
        #计算两个字符串的编辑距离 (动态规划)
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m + 1): dp[i][0] = i
        for j in range(n + 1): dp[0][j] = j
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                cost = 0 if s1[i - 1] == s2[j - 1] else 1
                dp[i][j] = min(dp[i - 1][j] + 1,      # 删除
                               dp[i][j - 1] + 1,      # 插入
                               dp[i - 1][j - 1] + cost) # 替换
        return dp[m][n]

    def _string_similarity(self, s1, s2):
        #转化为相似度
        max_len = max(len(s1), len(s2))
        if max_len == 0: return 1.0
        dist = self._levenshtein_distance(s1, s2)
        return 1.0 - (dist / max_len)

    def knowledge_fusion_entity_alignment(self, similarity_threshold=0.6):
        #计算编辑距离相似度进行实体对齐，相似度超过阈值则将它们融合为一个实体
        print(f"\n实体对齐 (相似度阈值: {similarity_threshold})...")
        entities = list(self.instances.keys())
        fusion_map = {}

        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                e1, e2 = entities[i], entities[j]
                sim = self._string_similarity(e1, e2)
                if sim >= similarity_threshold:
                    print(f"[融合共指实体]: '{e1}' 与 '{e2}' 相似度为 {sim:.2f}")
                    # 简单策略：保留较长的名字
                    if len(e1) > len(e2):
                        fusion_map[e2] = e1
                    else:
                        fusion_map[e1] = e2

        # 图谱数据的融合/更新
        new_facts = []
        for h, r, t in self.facts:
            new_h = fusion_map.get(h, h)
            new_t = fusion_map.get(t, t)
            new_facts.append((new_h, r, new_t))
        self.facts = list(set(new_facts))

        for old_ent, new_ent in fusion_map.items():
            if old_ent in self.instances:
                del self.instances[old_ent]
        print("融合完成")

    def show_graph(self):
        print(f"\n【{self.name}】 当前状态：")
        print(f"共有 {len(self.instances)} 个独立实体， {len(self.facts)} 条事实三元组。")
        for h, r, t in self.facts:
            print(f"  < {h} , {r} , {t} >")


if __name__ == "__main__":
    kg = AdvancedKnowledgeGraph()

    # 现有的知识库 (存在冗余)
    print("加载数据：")
    kg.add_instance("阿兰·图灵", "Person")
    kg.add_fact("阿兰·图灵", "国籍", "英国")
    kg.add_instance("艾伦·图灵", "Person")
    kg.add_fact("艾伦·图灵", "毕业于", "剑桥大学")
    kg.add_instance("图灵", "Person")
    kg.add_fact("图灵", "提出", "图灵机")
    kg.show_graph()

    # 抽取知识
    print("\n构建知识体系：")
    text_data = "20世纪诞生了许多杰出的计算机科学家如阿兰·图灵、冯·诺依曼和姚期智。"
    kg.extract_knowledge_from_text(text_data)

    # 执行知识融合/实体对齐
    print("\n知识融合：")
    kg.knowledge_fusion_entity_alignment(similarity_threshold=0.4)

    kg.show_graph()