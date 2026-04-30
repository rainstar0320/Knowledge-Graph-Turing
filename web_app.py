# web_app.py
from flask import Flask, render_template, jsonify
from neo4j import GraphDatabase

app = Flask(__name__)

# ⚠️ 注意修改为你的真实密码！
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "20050320txl"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/graph')
def get_graph_data():
    """从 Neo4j 查询图谱数据并转为 ECharts 格式"""
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

    # 限制返回100条边，防止前端卡死
    query = """
    MATCH (n)-[r]->(m)
    RETURN id(n) AS src_id, n.name AS src_name, labels(n)[0] AS src_category,
           id(m) AS tgt_id, m.name AS tgt_name, labels(m)[0] AS tgt_category,
           type(r) AS rel_name
    LIMIT 100
    """

    nodes_dict = {}
    links = []
    categories_set = set()

    with driver.session() as session:
        results = session.run(query)
        for record in results:
            # 处理节点
            for prefix in ['src_', 'tgt_']:
                n_id = str(record[prefix + 'id'])
                if n_id not in nodes_dict:
                    cat = record[prefix + 'category'] or 'Unknown'
                    categories_set.add(cat)

                    # 🚀 优化核心：前端展示时，隐去 NIL_ 前缀，让界面更美观
                    raw_name = record[prefix + 'name']
                    display_name = raw_name.replace("NIL_", "")  # 截掉 NIL_

                    nodes_dict[n_id] = {
                        "id": n_id,
                        "name": display_name,  # 使用清洗后的名字
                        "category": list(categories_set).index(cat),
                        "symbolSize": 40 if "NIL" not in raw_name else 25  # 未知实体圈小一点
                    }

            # 处理边
            links.append({
                "source": str(record['src_id']),
                "target": str(record['tgt_id']),
                "value": record['rel_name']
            })

    driver.close()

    graph_data = {
        "nodes": list(nodes_dict.values()),
        "links": links,
        "categories": [{"name": c} for c in categories_set]
    }

    return jsonify(graph_data)


if __name__ == '__main__':
    print("启动知识图谱可视化服务: http://127.0.0.1:5000")
    app.run(port=5000, debug=True)