# ==========================================
# 进度：第5章 - 实体消歧与实体链接 (Entity Disambiguation & Linking)
# 考点：候选实体生成(P39), 先验概率 P(e|m)(P48), 词袋模型上下文相似度(P60), NIL处理(P117)
# ==========================================

import math

class EntityLinkingEngine:
    def __init__(self):
        # 1.模拟后台知识库包含每个标准实体的先验概率和词袋特征
        self.kb_entities = {
            "Michael_Jordan_(Basketball)": {
                "prior": 0.85, 
                "bow": {"篮球", "nba", "公牛队", "体育", "得分", "扣篮", "退役"}
            },
            "Michael_Jordan_(Professor)": {
                "prior": 0.15, 
                "bow": {"计算机", "机器学习", "ai", "伯克利", "教授", "学者", "模型"}
            },
            "Apple_(Company)": {
                "prior": 0.70, 
                "bow": {"科技", "手机", "电脑", "乔布斯", "硅谷", "发布会", "数码"}
            },
            "Apple_(Fruit)": {
                "prior": 0.30, 
                "bow": {"水果", "种植", "果园", "营养", "吃", "维生素", "口感"}
            }
        }
        
        # 2.指称项->候选实体的映射词典
        self.mention_dict = {
            "乔丹": ["Michael_Jordan_(Basketball)", "Michael_Jordan_(Professor)"],
            "Michael Jordan": ["Michael_Jordan_(Basketball)", "Michael_Jordan_(Professor)"],
            "苹果": ["Apple_(Company)", "Apple_(Fruit)"]
        }

    def _calculate_cosine_similarity(self, text_context, entity_bow):
        #基于词袋模型计算余弦相似度（简化处理：直接检查实体词袋中的词是否在上下文中出现。在真实系统中应使用 Jieba 等分词工具）
        overlap_count = 0
        for word in entity_bow:
            if word in text_context:
                overlap_count += 1
                
        # 简化版余弦相似度 = 相同词数 / (上下文长度 * 实体词袋长度的平方根)
        if len(text_context) == 0 or len(entity_bow) == 0:
            return 0.0
        return overlap_count / math.sqrt(len(entity_bow))

    def disambiguate(self, mention, context, similarity_threshold=0.1):
        """
        实体消歧核心算法
        :param mention: 待消歧的实体指称项 (如 "乔丹")
        :param context: 该实体所处的文本上下文 (如 "乔丹提出了新的机器学习模型")
        :param similarity_threshold: NIL (无链接实体) 的判定阈值
        """
        print(f"\n[实体消歧引擎] 开始处理指称项: '{mention}'")
        print(f"  -> 所处上下文: '{context}'")
        
        # 步骤 1：候选实体发现 (Candidate Generation)
        candidates = self.mention_dict.get(mention, [])
        if not candidates:
            # 对应课件 P117-118: NIL 问题 (无链接实体预测)
            print(f"  -> [NIL预测]: 知识库中未找到候选, 预测为新实体 NIL.")
            return f"NIL_{mention}"
            
        print(f"  -> 找到候选实体: {candidates}")
        
        best_entity = None
        highest_score = -1.0
        
        # 步骤 2：对每个候选实体进行打分 (Ranking)
        for candidate in candidates:
            entity_data = self.kb_entities[candidate]
            
            # 特征A：先验概率 P(entity|mention) (参考课件 P48)
            prior_score = entity_data["prior"]
            
            # 特征B：基于词袋的上下文相似度 (参考课件 P60)
            context_score = self._calculate_cosine_similarity(context, entity_data["bow"])
            
            # 综合打分：假设先验占 30%，上下文占 70% (线性融合，参考课件P132)
            final_score = (0.3 * prior_score) + (0.7 * context_score)
            print(f"     * 候选 [{candidate}] - 先验得分: {prior_score:.2f}, 上下文得分: {context_score:.2f}, 综合得分: {final_score:.2f}")
            
            if final_score > highest_score:
                highest_score = final_score
                best_entity = candidate

        # 步骤 3：NIL 判定阈值
        if highest_score < similarity_threshold:
            print(f"  -> [NIL预测]: 最高得分 {highest_score:.2f} 低于阈值, 预测为新实体 NIL.")
            return f"NIL_{mention}"
            
        print(f"  => [消歧成功]: '{mention}' 成功链接到标准实体库 ID: 【{best_entity}】")
        return best_entity


if __name__ == "__main__":
    el_engine = EntityLinkingEngine()
    
    # 场景 1
    text1 = "昨天的NBA总决赛中，乔丹完成了一个不可思议的扣篮得分！"
    el_engine.disambiguate("乔丹", text1)
    text2 = "加州大学伯克利分校的乔丹教授最近在机器学习顶会上发表了关于AI的新论文。"
    el_engine.disambiguate("乔丹", text2)
    
    # 场景 2
    text3 = "专家建议每天吃一个新鲜的苹果，可以补充维生素，非常有营养。"
    el_engine.disambiguate("苹果", text3)
    text4 = "硅谷的苹果公司昨天晚上举行了秋季发布会，发布了最新款的手机和电脑。"
    el_engine.disambiguate("苹果", text4)
    
    # 场景 3：NIL (未登录词) 测试
    text5 = "这辆特斯拉电动车的自动驾驶技术很不错。"
    el_engine.disambiguate("特斯拉", text5)
