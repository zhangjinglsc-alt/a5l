"""
A5L Knowledge Graph - Visualizer
Phase 4: Interactive graph visualization

Features:
- Interactive network visualization
- Path highlighting
- Subgraph extraction
- Export to HTML
"""

import os
import json
from typing import List, Dict, Optional, Tuple
from knowledge_graph_core import KnowledgeGraph


class KGVisualizer:
    """知识图谱可视化器"""
    
    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg
        self.colors = {
            'Stock': '#FF6B6B',      # 红色
            'Industry': '#4ECDC4',   # 青色
            'Concept': '#45B7D1',    # 蓝色
            'Event': '#FFA07A',      # 橙色
            'Person': '#98D8C8',     # 绿色
            'Report': '#F7DC6F',     # 黄色
        }
        self.shapes = {
            'Stock': 'dot',
            'Industry': 'box',
            'Concept': 'diamond',
            'Event': 'star',
            'Person': 'triangle',
            'Report': 'square',
        }
    
    def to_visjs_data(self, center_node: str = None, depth: int = 2) -> Dict:
        """转换为Vis.js数据格式"""
        if not self.kg._loaded:
            self.kg.load_to_memory()
        
        nodes = []
        edges = []
        
        # 确定要显示的节点
        if center_node:
            # 获取子图
            if center_node in self.kg.graph:
                node_set = {center_node}
                current_level = {center_node}
                
                for _ in range(depth):
                    next_level = set()
                    for node in current_level:
                        neighbors = list(self.kg.graph.neighbors(node))
                        predecessors = list(self.kg.graph.predecessors(node))
                        next_level.update(neighbors)
                        next_level.update(predecessors)
                    node_set.update(next_level)
                    current_level = next_level
                
                subgraph = self.kg.graph.subgraph(node_set)
            else:
                subgraph = self.kg.graph
        else:
            subgraph = self.kg.graph
        
        # 构建节点
        for node_id, data in subgraph.nodes(data=True):
            node_type = data.get('type', 'Unknown')
            nodes.append({
                'id': node_id,
                'label': data.get('name', node_id),
                'title': f"Type: {node_type}<br>ID: {node_id}",
                'color': self.colors.get(node_type, '#CCCCCC'),
                'shape': self.shapes.get(node_type, 'dot'),
                'size': 30 if node_type == 'Stock' else 20,
            })
        
        # 构建边
        for source, target, data in subgraph.edges(data=True):
            relation_type = data.get('type', 'related')
            edges.append({
                'from': source,
                'to': target,
                'label': relation_type,
                'title': f"Type: {relation_type}<br>Confidence: {data.get('confidence', 1.0)}",
                'arrows': 'to',
                'color': {'color': '#848484', 'highlight': '#FF6B6B'},
            })
        
        return {'nodes': nodes, 'edges': edges}
    
    def render_html(self, output_path: str, center_node: str = None, depth: int = 2, title: str = "A5L Knowledge Graph") -> str:
        """渲染为HTML文件"""
        data = self.to_visjs_data(center_node, depth)
        
        html_template = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        #mynetwork {{
            width: 100%;
            height: 800px;
            border: 1px solid lightgray;
        }}
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }}
        h1 {{
            color: #333;
        }}
        .legend {{
            margin-top: 10px;
            padding: 10px;
            background: #f5f5f5;
            border-radius: 5px;
        }}
        .legend-item {{
            display: inline-block;
            margin-right: 20px;
        }}
        .color-box {{
            display: inline-block;
            width: 20px;
            height: 20px;
            margin-right: 5px;
            vertical-align: middle;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div id="mynetwork"></div>
    <div class="legend">
        <strong>图例:</strong>
        <div class="legend-item"><span class="color-box" style="background: #FF6B6B;"></span>股票</div>
        <div class="legend-item"><span class="color-box" style="background: #4ECDC4;"></span>行业</div>
        <div class="legend-item"><span class="color-box" style="background: #45B7D1;"></span>概念</div>
        <div class="legend-item"><span class="color-box" style="background: #FFA07A;"></span>事件</div>
        <div class="legend-item"><span class="color-box" style="background: #98D8C8;"></span>人物</div>
        <div class="legend-item"><span class="color-box" style="background: #F7DC6F;"></span>研报</div>
    </div>
    <script type="text/javascript">
        // 数据
        var nodes = new vis.DataSet({json.dumps(data['nodes'], ensure_ascii=False)});
        var edges = new vis.DataSet({json.dumps(data['edges'], ensure_ascii=False)});
        
        // 创建网络
        var container = document.getElementById('mynetwork');
        var data = {{
            nodes: nodes,
            edges: edges
        }};
        var options = {{
            nodes: {{
                font: {{
                    size: 14,
                    color: '#333'
                }},
                borderWidth: 2,
                shadow: true
            }},
            edges: {{
                width: 2,
                shadow: true,
                smooth: {{
                    type: 'continuous'
                }},
                font: {{
                    size: 12,
                    align: 'middle'
                }}
            }},
            physics: {{
                stabilization: false,
                barnesHut: {{
                    gravitationalConstant: -8000,
                    springConstant: 0.04,
                    springLength: 200
                }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200,
                hideEdgesOnDrag: true
            }}
        }};
        
        var network = new vis.Network(container, data, options);
        
        // 点击事件
        network.on("click", function (params) {{
            if (params.nodes.length > 0) {{
                var nodeId = params.nodes[0];
                console.log("Clicked node:", nodeId);
            }}
        }});
    </script>
</body>
</html>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        return output_path
    
    def render_subgraph(self, center_node: str, depth: int = 2, output_dir: str = None) -> str:
        """渲染子图为HTML"""
        if output_dir is None:
            output_dir = os.path.dirname(os.path.abspath(__file__))
        
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'subgraph_{center_node}.html')
        
        return self.render_html(
            output_path=output_path,
            center_node=center_node,
            depth=depth,
            title=f"Knowledge Graph - {center_node}"
        )
    
    def render_full_graph(self, output_path: str = None) -> str:
        """渲染完整图谱"""
        if output_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            output_path = os.path.join(base_dir, 'visualization', 'full_graph.html')
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        return self.render_html(
            output_path=output_path,
            center_node=None,
            depth=10,  # 显示所有
            title="A5L Knowledge Graph - Full View"
        )
    
    def get_path_visualization_data(self, start_id: str, end_id: str) -> Dict:
        """获取路径可视化数据"""
        if not self.kg._loaded:
            self.kg.load_to_memory()
        
        # 查找路径
        paths = self.kg.find_path(start_id, end_id)
        
        if not paths:
            return {'nodes': [], 'edges': [], 'paths': []}
        
        # 收集路径上的所有节点和边
        path_nodes = set()
        path_edges = []
        
        for path in paths:
            for i in range(0, len(path), 2):  # 每隔一个是节点
                if 'entity_id' in path[i]:
                    path_nodes.add(path[i]['entity_id'])
            
            for i in range(1, len(path), 2):  # 每隔一个是边
                if 'relation_type' in path[i]:
                    # 找到对应的源和目标
                    source = path[i-1]['entity_id']
                    target = path[i+1]['entity_id'] if i+1 < len(path) else None
                    if target:
                        path_edges.append((source, target, path[i]['relation_type']))
        
        # 构建Vis.js数据
        nodes = []
        edges = []
        
        for node_id in path_nodes:
            if node_id in self.kg.graph:
                data = self.kg.graph.nodes[node_id]
                node_type = data.get('type', 'Unknown')
                nodes.append({
                    'id': node_id,
                    'label': data.get('name', node_id),
                    'color': self.colors.get(node_type, '#CCCCCC'),
                    'shape': self.shapes.get(node_type, 'dot'),
                    'size': 35 if node_id in [start_id, end_id] else 25,  # 起点终点更大
                })
        
        for source, target, relation_type in path_edges:
            edges.append({
                'from': source,
                'to': target,
                'label': relation_type,
                'arrows': 'to',
                'color': {'color': '#FF6B6B', 'highlight': '#FF0000'},  # 路径用红色
                'width': 3,
            })
        
        return {'nodes': nodes, 'edges': edges, 'paths': paths}


# ========== 快捷函数 ==========

def visualize_stock_network(kg: KnowledgeGraph, stock_code: str, output_path: str = None) -> str:
    """可视化股票关系网络"""
    visualizer = KGVisualizer(kg)
    stock_id = f"stock_{stock_code}"
    
    if output_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(base_dir, 'visualization', f'{stock_code}_network.html')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    return visualizer.render_subgraph(stock_id, depth=2, output_dir=os.path.dirname(output_path))


def visualize_industry_chain(kg: KnowledgeGraph, industry_name: str, output_path: str = None) -> str:
    """可视化产业链"""
    visualizer = KGVisualizer(kg)
    industry_id = f"industry_{industry_name}"
    
    if output_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(base_dir, 'visualization', f'{industry_name}_chain.html')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    return visualizer.render_html(
        output_path=output_path,
        center_node=industry_id,
        depth=3,
        title=f"{industry_name} Industry Chain"
    )


# ========== 测试代码 ==========

if __name__ == "__main__":
    from knowledge_graph_core import KnowledgeGraph, create_stock_entity, create_industry_entity
    from entity_extractor import FeishuDocumentProcessor
    
    print("=" * 60)
    print("A5L 知识图谱 - 可视化测试")
    print("=" * 60)
    
    # 使用已有的知识图谱
    kg = KnowledgeGraph()
    
    # 添加一些测试数据
    print("\n1. 添加测试数据...")
    test_text = """
    NVIDIA (NVDA)是AI算力龙头，与AMD在GPU市场竞争激烈。
    半导体行业包括芯片设计、晶圆代工、封测等环节。
    新能源汽车产业链包括锂电池、电机、电控、整车制造。
    """
    
    processor = FeishuDocumentProcessor(kg)
    result = processor.process_text(test_text, doc_id="test_doc", doc_title="Test Document")
    print(f"  添加了 {result['entity_count']} 个实体")
    
    # 创建可视化器
    print("\n2. 生成可视化...")
    visualizer = KGVisualizer(kg)
    
    # 生成完整图谱
    output_path = visualizer.render_full_graph()
    print(f"  完整图谱: {output_path}")
    
    # 生成NVDA子图
    if 'stock_NVDA' in [n['entity_id'] for n in kg.get_related_entities('stock_NVDA', depth=0)] or True:
        try:
            nvda_path = visualizer.render_subgraph('stock_NVDA', depth=2)
            print(f"  NVDA子图: {nvda_path}")
        except:
            print(f"  NVDA子图: 节点不存在或无法生成")
    
    print("\n" + "=" * 60)
    print("✅ Phase 4 可视化测试完成!")
    print("  请在浏览器中打开生成的HTML文件查看")
    print("=" * 60)
