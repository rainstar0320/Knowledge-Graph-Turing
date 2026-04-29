import math

class EntityLinker:
    def __init__(self):
        # 模拟后台标准概念库
        self.standard_kb = {
            "Alan_Turing_(Person)": {
                "prior": 0.9, 
                "bow": {"计算机", "密码", "数学", "诞生", "破解", "科学家"}
            },
            "Turing_Award_(Award)": {
                "prior": 0.5, 
                "bow": {"奖项", "诺贝尔", "获得", "颁发", "学者"}
            }
        }
        self.mention_map = {
            "图灵": ["Alan_Turing_(Person)", "Turing_Award_(Award)"]
        }

    def link_entity(self, mention, context):
        """实体链接引擎：输入文本指称项和上下文，返回标准实体ID"""
        candidates = self.mention_map.get(mention, [])
        if not candidates:
            return f"NIL_{mention}" # NIL无链接实体预测
            
        best_entity = None
        best_score = -1
        
        for cand in candidates:
            kb_info = self.standard_kb[cand]
            prior = kb_info["prior"]
            # 计算简单的词袋重合度
            overlap = sum(1 for word in kb_info["bow"] if word in context)
            context_score = overlap / math.sqrt(len(kb_info["bow"]) + 1)
            
            # 综合打分 (先验 + 上下文)
            score = 0.4 * prior + 0.6 * context_score
            if score > best_score:
                best_score = score
                best_entity = cand
                
        # 设定阈值，防止错误链接
        if best_score < 0.2:
            return f"NIL_{mention}"
        return best_entity