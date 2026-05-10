#!/usr/bin/env python
"""Quick test script to verify CFG generation from Java code"""

import sys
sys.path.insert(0, '.')

from core.parser import JavaParser
from core.cfg_generator import CFGGeneratorVisitor
from core.types import NodeType, BranchType

# Read Java source code
java_file_path = "Pangkat.java"
with open(java_file_path, 'r', encoding='utf-8') as f:
    java_code = f.read()

print("=" * 60)
print("CFG GENERATION TEST")
print("=" * 60)
print(f"\n📄 Testing with: {java_file_path}")
print(f"Source code length: {len(java_code)} bytes")

# Parse Java code
parser = JavaParser()
tree = parser.parse_source_code(java_code)
print("\n✅ Java code parsed successfully")

# Extract methods
methods = parser.extract_all_methods(tree)
print(f"✅ Found {len(methods)} method(s)")

# Generate CFG for first method
if methods:
    method_node = methods[0]
    
    # Get method name
    method_name = "unknown"
    for child in method_node.children:
        if child.type == 'identifier':
            method_name = child.text.decode('utf8')
            break
    
    print(f"\n🔄 Generating CFG for method: {method_name}")
    
    # Generate CFG
    generator = CFGGeneratorVisitor()
    nodes, edges = generator.build_cfg(method_node)
    
    print(f"\n✅ CFG Generated Successfully!")
    print(f"   Total Nodes: {len(nodes)}")
    print(f"   Total Edges: {len(edges)}")
    
    print("\n📊 Node Types Distribution:")
    node_types_count = {}
    for node in nodes:
        node_type = node.node_type.value if isinstance(node.node_type, NodeType) else str(node.node_type)
        node_types_count[node_type] = node_types_count.get(node_type, 0) + 1
    
    for node_type, count in sorted(node_types_count.items()):
        print(f"   - {node_type}: {count}")
    
    print("\n📊 Branch Types Distribution:")
    branch_types_count = {}
    for edge in edges:
        branch_type = edge["branch_type"].value if isinstance(edge["branch_type"], BranchType) else str(edge["branch_type"])
        branch_types_count[branch_type] = branch_types_count.get(branch_type, 0) + 1
    
    for branch_type, count in sorted(branch_types_count.items()):
        print(f"   - {branch_type}: {count}")
    
    print("\n📝 Node Details (first 5):")
    for i, node in enumerate(nodes[:5]):
        print(f"   {i+1}. [{node.node_type.value}] {node.source_code[:50]}...")
    
    print("\n✅ CFG Generation Test PASSED!")
else:
    print("\n❌ No methods found in Java code")

print("\n" + "=" * 60)
