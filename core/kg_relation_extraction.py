import re


class RelationExtractor:
    def __init__(self):
        # 停用词/无意义字符表，用于清洗抽取出的原始开放关系短语
        self.stop_words = ["了", "的", "在", "被", "将", "把", "是", "一", "个", "年", "月", "日"]
        
    def _clean_relation(self, raw_relation):
        """清洗提取到的关系短语，提取核心动词谓词"""
        cleaned = raw_relation
        for word in self.stop_words:
            # 简单去除边缘的停用词
            cleaned = re.sub(f"^{word}|{word}$", "", cleaned).strip()
        return cleaned if cleaned else "关联"

    def extract_open_relations(self, text, entities):
        """基于 Open IE 思想的开放式关系抽取。"""
        triples = []
        n = len(entities)
        
        # 遍历句子中出现的任意两个实体
        for i in range(n):
            for j in range(i + 1, n):
                ent1 = entities[i]["entity"]
                ent2 = entities[j]["entity"]
                
                # 在文本中定位两个实体的位置
                idx1 = text.find(ent1)
                idx2 = text.find(ent2)
                
                if idx1 == -1 or idx2 == -1:
                    continue

                if idx1 > idx2:
                    ent1, ent2 = ent2, ent1
                    idx1, idx2 = idx2, idx1
                
                # 截取两个实体中间的文本作为“潜在关系短语”
                start = idx1 + len(ent1)
                end = idx2
                raw_between = text[start:end].strip()
                
                # 如果两个实体距离适中
                if 1 <= len(raw_between) <= 15:
                    # 过滤掉纯标点符号
                    if not re.match(r'^[^\w\s]+$', raw_between):
                        relation = self._clean_relation(raw_between)
                        # 生成事实三元组
                        triples.append((ent1, relation, ent2))
                        print(f"    [Relation Extractor] 成功抽取关系: <{ent1}, {relation}, {ent2}>")
                        
        return triples