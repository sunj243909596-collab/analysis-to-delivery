# Draw.io 流程图生成

> 适用于阶段 2 业务流程图的可视化
> 来源：MXGraph XML 格式

## 何时用 Draw.io

- 业务流程复杂（10+ 节点）
- 需要可视化分享给非技术干系人
- 用户明确要求 `.drawio` 文件

简单流程用 ASCII 即可（详见 [flow-chart-ascii.md](flow-chart-ascii.md)）

## 文件结构

`.drawio` 文件本质是：
```xml
<mxfile>
  <diagram name="流程图">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>  <!-- 根节点 -->
        <mxCell id="1" parent="0"/>  <!-- 容器 -->
        <!-- 业务节点 -->
        <mxCell id="node1" value="节点1" style="..." vertex="1" parent="1">
          <mxGeometry x="100" y="100" width="120" height="60"/>
        </mxCell>
        <!-- 边 -->
        <mxCell id="edge1" style="..." edge="1" parent="1" source="node1" target="node2"/>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## 关键规则

### ⛔ 严禁

- 空的 `<Array as="points"/>`（导致 `a.push is not a function`）
- 嵌套 `mxCell`（同上）
- 全局 ID 不唯一（架构/流程/状态机边 ID 用不同前缀）

### ✅ 必须

- 用 Python `ElementTree` 构建 XML
- 复杂脚本优先 `write_file → terminal python3`：`execute_code` 在 50+ 行脚本中易遇 f-string 限制
- 节点间距 ≥ 80px
- 主流程垂直居中，分支左右分列
- 边标签用 `value` 属性，不要嵌套 mxCell

## Python 生成脚本模板

```python
import xml.etree.ElementTree as ET

# 创建根节点
mxfile = ET.Element('mxfile')
diagram = ET.SubElement(mxfile, 'diagram', name='业务流程图')
graph = ET.SubElement(diagram, 'mxGraphModel')
root = ET.SubElement(graph, 'root')

# 容器
ET.SubElement(root, 'mxCell', id='0')
ET.SubElement(root, 'mxCell', id='1', parent='0')

# 节点
node1 = ET.SubElement(root, 'mxCell',
    id='node1', value='开始',
    style='rounded=1;fillColor=#67CE91;',
    vertex='1', parent='1')
ET.SubElement(node1, 'mxGeometry', x='100', y='100', width='120', height='60')

# 边
ET.SubElement(root, 'mxCell',
    id='edge1', style='endArrow=classic;',
    edge='1', parent='1',
    source='node1', target='node2')

# 写入文件
ET.ElementTree(mxfile).write('flow.drawio', encoding='utf-8', xml_declaration=True)
```

## 验证

生成后必须检查：
- ID 无重复
- 无 `Array` 标签
- XML 合法（用 `xmllint --noout flow.drawio`）
