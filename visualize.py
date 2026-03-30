import json
from pyvis.network import Network

def generate_html_graph(json_path, output_html):
    print(f"正在读取数据: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        triplets = json.load(f)

    # 1. 初始化一个 PyVis 网络画布
    # directed=True 表示有向图（带箭头）
    # notebook=False 表示生成独立的 HTML 文件
    net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white", directed=True)
    
    # 设置力导向图的物理引力模型，让节点散开得更漂亮
    net.repulsion(node_distance=150, central_gravity=0.2, spring_length=200)

    # 2. 遍历数据，添加节点和边
    print(f"正在绘制图谱，共 {len(triplets)} 条关系...")
    for item in triplets:
        head = item['head']
        relation = item['relation']
        tail = item['tail']

        # 添加头节点和尾节点（PyVis 会自动去重，名字相同的节点不会重复创建）
        # 这里给图灵本人设置一个大一点的 size 和不同的颜色
        if head == "艾伦·图灵":
            net.add_node(head, label=head, title="核心人物", color="#ff5722", size=40)
        else:
            net.add_node(head, label=head, title=head, color="#4caf50", size=20)
            
        net.add_node(tail, label=tail, title=tail, color="#2196f3", size=20)

        # 添加连线（关系）
        net.add_edge(head, tail, label=relation, title=relation, color="#aaaaaa")

    # 3. 生成并保存为 HTML 网页
    net.save_graph(output_html)
    print(f"\n🎉 知识图谱已生成！请在浏览器中双击打开文件: {output_html}")

if __name__ == "__main__":
    generate_html_graph(
        json_path="E:\VscodePractice\knowlodge_graph\\turing_final_graph_ready.json",  # 你上一步精修好的文件
        output_html="E:\VscodePractice\knowlodge_graph\\turing_knowledge_graph.html"
    )