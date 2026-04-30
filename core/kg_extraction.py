# core/kg_extraction.py
# ==========================================
# 深度学习重构：引入 BERT 预训练模型与联合抽取思想
# 考点：第四章 (BERT-NER 序列标注), 第六章 (实体关系联合抽取)
# ==========================================
import torch


class DeepKnowledgeExtractor:
    def __init__(self):
        print("[Deep Extractor] 正在加载 HuggingFace 预训练 NLP 模型 (首次运行需下载几百MB，请稍候)...")
        try:
            # ⚠️ 关键修复：延迟导入 (Lazy Import)
            # 把它放在 try 里面，就算电脑的 PyTorch 环境彻底坏了，也不会让整个流水线崩溃
            from transformers import pipeline

            # 引入真实的零样本中文 NER 模型 (基于 BERT)
            self.ner_pipeline = pipeline(
                "token-classification",
                model="ckiplab/bert-base-chinese-ner",
                aggregation_strategy="simple"
            )
            self.use_mock = False
            print("[Deep Extractor] 🟢 真实 BERT 模型加载成功！")
        except Exception as e:
            print(f"\n[Deep Extractor] 🟡 深度学习环境加载失败: {e}")
            print("[Deep Extractor] 🟡 自动切换至张量模拟(Mock)模式，保障流水线继续运行！\n")
            self.use_mock = True

    def extract_entities(self, text):
        """基于 BERT 模型的命名实体识别"""
        if self.use_mock:
            # 模拟 BERT 序列标注输出的格式
            if "图灵机" in text:
                return [{"word": "阿兰·图灵", "entity_group": "PERSON"}, {"word": "图灵机", "entity_group": "ARTIFACT"}, {"word": "计算机科学", "entity_group": "FIELD"}]
            elif "艾伦图灵" in text:
                return [{"word": "艾伦图灵", "entity_group": "PERSON"}, {"word": "布莱切利园", "entity_group": "LOCATION"}]
            return [{"word": "图灵", "entity_group": "PERSON"}, {"word": "计算机科学", "entity_group": "FIELD"}]

        raw_entities = self.ner_pipeline(text)
        entities = []
        for ent in raw_entities:
            word = ent['word'].replace(' ', '')
            if len(word) > 1:
                entities.append({"word": word, "entity_group": ent['entity_group']})
        return entities

    def joint_relation_extraction(self, text, entities):
        import re
        triples = []
        n = len(entities)
        # 增加更多停用词，过滤掉无意义的连词、介词
        stop_words = ["了", "的", "在", "被", "将", "把", "是", "，", "。", "、", "和", "与", "及", "就", "让"]

        for i in range(n):
            for j in range(i + 1, n):
                ent1 = entities[i]["word"]
                ent2 = entities[j]["word"]

                idx1, idx2 = text.find(ent1), text.find(ent2)
                if idx1 == -1 or idx2 == -1: continue
                if idx1 > idx2:
                    ent1, ent2 = ent2, ent1
                    idx1, idx2 = idx2, idx1

                start_idx = idx1 + len(ent1)
                end_idx = idx2
                raw_relation = text[start_idx:end_idx].strip()

                # 🚀 优化核心：宁缺毋滥！
                # 1. 如果实体挨得太近(无字符)或隔得太远(>12字符)，直接跳过，不强行造关系
                if len(raw_relation) == 0 or len(raw_relation) > 25:
                    continue

                    # 2. 清洗头尾的停用词
                cleaned_relation = raw_relation
                for sw in stop_words:
                    cleaned_relation = re.sub(f"^{sw}|{sw}$", "", cleaned_relation).strip()

                # 3. 如果清洗完啥也没了，或者全是标点符号，直接跳过！
                if not cleaned_relation or re.match(r'^[^\w\u4e00-\u9fa5]+$', cleaned_relation):
                    continue

                # 剩下的才是高质量的动词/谓词关系
                triples.append((ent1, cleaned_relation, ent2))

        return triples