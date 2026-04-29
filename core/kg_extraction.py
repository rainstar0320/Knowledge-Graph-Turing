import re

class KnowledgeExtractor:
    def __init__(self):
        # 预置的基础词典 (未来可替换为深度学习模型，如BiLSTM-CRF)
        self.dict_ner = {"阿兰·图灵": "Person", "人工智能": "Field", "英国": "Location"}

    def extract_entities(self, text):
        """基于词典的快速 NER"""
        extracted = []
        for word, ent_type in self.dict_ner.items():
            if word in text:
                extracted.append({"entity": word, "type": ent_type})
        return extracted

    def extract_relations_hearst(self, text):
        """基于 Hearst 模板的上下位关系抽取"""
        triples = []
        # 模拟中文模板: "概念[诸]如实体1、实体2"
        pattern = r'([a-zA-Z\u4e00-\u9fa5]+)(?:诸?如|比如|包括)(.*?)(?:。|；|$)'
        matches = re.finditer(pattern, text)
        for match in matches:
            concept = match.group(1).strip()
            entities = re.split(r'[、,，和及]', match.group(2))
            for ent in entities:
                if ent.strip():
                    # 抽取出 (实体, Is-A, 概念)
                    triples.append((ent.strip(), "Is-A", concept))
        return triples