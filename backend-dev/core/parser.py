import tree_sitter_java as tsjava
from tree_sitter import Language, Parser
from core.types import AstNodeType

class JavaParser:
    def __init__(self):
        self.JAVA_LANGUAGE = Language(tsjava.language())
        self.parser = Parser(self.JAVA_LANGUAGE)

    def parse_source_code(self, source_code: str):
        if isinstance(source_code, str):
            source_code_bytes = source_code.encode('utf8')
        else:
            source_code_bytes = source_code
            
        tree = self.parser.parse(source_code_bytes)
        return tree

    def extract_all_methods(self, tree):
        methods = []
        def traverse(node):
            if node.type == AstNodeType.METHOD_DECLARATION:
                methods.append(node)
            for child in node.children:
                traverse(child)

        traverse(tree.root_node)
        return methods

    def find_method_by_name(self, tree, target_name: str):
        methods = self.extract_all_methods(tree)
        for method in methods:
            for child in method.children:
                if child.type == AstNodeType.IDENTIFIER:
                    method_name = child.text.decode('utf8')
                    if method_name == target_name:
                        return method
        return None
