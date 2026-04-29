# ==========================================
# 进度：第4章 - 实体识别和扩展 (Information Extraction Pipeline)
# ==========================================

import re

class KnowledgeExtractionPipeline:
    def __init__(self):
        # 预置的基础领域词典
        self.lexicon = {
            "阿兰·图灵": "PER", "冯·诺依曼": "PER",
            "剑桥大学": "ORG", "布莱切利园": "LOC"
        }
        self.extracted_entities = set(self.lexicon.keys())

    # 模块 1：命名实体识别
    def ner_bio_tagging(self, sentence):
        """
        基于词典的正向最大匹配，输出 BIO 标签序列。
        后续会被替换为加载训练好的 BiLSTM-CRF 或 BERT 模型。
        """
        print(f"\n正在处理句子: '{sentence}'")
        n = len(sentence)
        tags = ['O'] * n
        i = 0
        
        while i < n:
            matched = False
            for length in range(min(n - i, 6), 0, -1): 
                word = sentence[i:i+length]
                if word in self.lexicon:
                    entity_type = self.lexicon[word]
                    tags[i] = f'B-{entity_type}'
                    for j in range(1, length):
                        tags[i+j] = f'I-{entity_type}'
                    
                    print(f"  ->识别到命名实体: [{word}], 赋予类型: {entity_type}")
                    i += length
                    matched = True
                    break
            if not matched:
                i += 1
                
        print("  ->BIO 序列标注底层结果:")
        for char, tag in zip(sentence, tags):
            print(f"     {char}\t{tag}")
        return tags

    # 模块 2：开放域实体扩展 (Bootstrapping)
    def open_domain_expansion(self, seeds, corpus, max_iters=2):
        #机制：种子 -> 模板 -> 新候选 -> 验证
        print(f"  初始种子实体: {seeds}")
        current_entities = set(seeds)
        
        for iteration in range(max_iters):
            print(f"\n  >>>第 {iteration + 1} 轮迭代 ")
            learned_patterns = set()
            
            # 利用已知实体，去语料库中挖掘上下文模板
            for text in corpus:
                for entity in current_entities:
                    if entity in text:
                        idx = text.find(entity)
                        # 提取实体前面的3个字符和后面的1个标点作为上下文模板
                        if idx >= 3 and idx + len(entity) < len(text):
                            prefix = text[idx-3 : idx]
                            suffix = text[idx+len(entity) : idx+len(entity)+1]
                            pattern = (prefix, suffix)
                            if pattern not in learned_patterns:
                                learned_patterns.add(pattern)
                                print(f"   -学到新模板: '{prefix}[X]{suffix}' (驱动种子: '{entity}')")
                            
            # 利用挖掘到的模板，去语料库中寻找新候选实体
            new_found = set()
            for text in corpus:
                for prefix, suffix in learned_patterns:
                    # 构造正则表达式来匹配模板中心的 [X]
                    regex_pattern = f"{re.escape(prefix)}([\\u4e00-\\u9fa5]{{2,5}}){re.escape(suffix)}"
                    for match in re.finditer(regex_pattern, text):
                        candidate = match.group(1)
                        if candidate not in current_entities:
                            new_found.add(candidate)
                            print(f"    -发现新实体: [{candidate}] (命中: '{prefix}[X]{suffix}')")

            if not new_found:
                print("  >>>本轮未发现新实体，Bootstrapping 收敛结束。")
                break
                
            # 将新发现的实体加入集合
            current_entities.update(new_found)
            self.extracted_entities.update(new_found)
            
        print(f"\n  =>系统完成开放域扩展，当前实体总库: {self.extracted_entities}")


if __name__ == "__main__":
    pipeline = KnowledgeExtractionPipeline()

    #命名实体识别 NER
    sample_text = "阿兰·图灵曾在布莱切利园进行密码破译工作。"
    pipeline.ner_bio_tagging(sample_text)

    # 开放域实体扩展
    # 预设一些非结构化网页文本
    web_corpus = [
        "计算机科学的奠基人包括阿兰·图灵，他提出了图灵测试。",
        "计算机科学的奠基人包括姚期智，他是唯一获图灵奖的华人学者。",
        "计算机科学的奠基人包括吴恩达，他在人工智能领域贡献卓著。"
    ]
    seed_list = ["阿兰·图灵"]
    pipeline.open_domain_expansion(seeds=seed_list, corpus=web_corpus)