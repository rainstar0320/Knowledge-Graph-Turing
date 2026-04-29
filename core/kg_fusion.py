
class KnowledgeFuser:
    def __init__(self, storage):
        self.storage = storage

    def _levenshtein(self, s1, s2):
        """计算编辑距离 """
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m + 1): dp[i][0] = i
        for j in range(n + 1): dp[0][j] = j
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                cost = 0 if s1[i-1] == s2[j-1] else 1
                dp[i][j] = min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+cost)
        return dp[m][n]

    def fuse_entities(self, threshold=0.7):
        """对 ABox 中的实例进行相似度对齐融合"""
        instances = list(self.storage.knowledge_base["instances"].keys())
        fusion_mapping = {}

        for i in range(len(instances)):
            for j in range(i + 1, len(instances)):
                e1, e2 = instances[i], instances[j]
                max_len = max(len(e1), len(e2))
                if max_len == 0: continue
                
                sim = 1.0 - (self._levenshtein(e1, e2) / max_len)
                if sim >= threshold:
                    # 保留较长的作为主实体
                    if len(e1) > len(e2):
                        fusion_mapping[e2] = e1
                    else:
                        fusion_mapping[e1] = e2

        # 如果发现需要融合的实体，更新底层三元组库
        if fusion_mapping:
            print(f"[Fusion] 发现相似实体，执行融合: {fusion_mapping}")
            new_triples = []
            for h, r, t in self.storage.knowledge_base["triples"]:
                new_h = fusion_mapping.get(h, h)
                new_t = fusion_mapping.get(t, t)
                new_triples.append([new_h, r, new_t])
            
            # 去重并写回
            self.storage.knowledge_base["triples"] = [list(x) for x in set(tuple(x) for x in new_triples)]
            
            # 清理废弃的实例定义
            for old_ent in fusion_mapping.keys():
                if old_ent in self.storage.knowledge_base["instances"]:
                    del self.storage.knowledge_base["instances"][old_ent]