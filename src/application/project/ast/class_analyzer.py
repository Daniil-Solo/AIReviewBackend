from dataclasses import dataclass
from pprint import pprint

from tree_sitter import Node, Query, QueryCursor

from src.services.project.ast.base_analyzer import BaseASTAnalyzer
from src.services.project.ast.utils import print_node_fields


@dataclass
class ClassMethodInfo:
    name: str
    decorators: list[str]
    docstring: str | None
    body: str


@dataclass
class ClassInfo:
    name: str
    parent_names: list[str]
    docstring: str | None
    methods: list[ClassMethodInfo]


class ClassASTAnalyzer(BaseASTAnalyzer[list[ClassInfo]]):
    """
    Usage:
    ```python
    with open("example.txt", "rb") as f:
        source_code = f.read()

    analyzer = ClassASTAnalyzer()
    result = analyzer.analyze(source_code)
    pprint(result)  # noqa: T203
    ```
    """

    def __init__(self) -> None:
        super().__init__()

    def extract_classes(self, root_node: Node) -> list[tuple[str, Node]]:
        classes = []
        query = Query(
            self._language,
            """
            (class_definition) @class
        """,
        )
        query_cursor = QueryCursor(query)
        captures = query_cursor.captures(root_node)
        for class_node in captures["class"]:
            class_name_node = class_node.child_by_field_name("name")
            if class_name_node is None:
                continue
            class_name = class_name_node.text.decode("utf-8")
            class_body_node = class_node.child_by_field_name("body")
            if class_body_node is None:
                continue
            classes.append((class_name, class_node))
        return classes

    @staticmethod
    def extract_docstring(node: Node) -> str | None:
        body_node = node.child_by_field_name("body")
        expression_statement_node = body_node.children[0]
        if expression_statement_node.type != "expression_statement":
            return None
        string_node = expression_statement_node.children[0]
        if string_node.type != "string":
            return None
        string_content_node = next(ch for ch in string_node.children if ch.type == "string_content")
        return string_content_node.text.decode("utf-8").strip()

    @staticmethod
    def extract_parent_names(class_node: Node) -> list[str]:
        parent_classes_node = class_node.child_by_field_name("superclasses")
        if parent_classes_node is None:
            return []
        parent_names = []
        for child in parent_classes_node.children:
            if child.type == "identifier" or child.type == "attribute":
                parent_names.append(child.text.decode("utf-8"))
        return parent_names

    def extract_method_info_list(self, class_node: Node) -> list[ClassMethodInfo]:
        method_info_list = []
        body_node = class_node.child_by_field_name("body")
        for child in body_node.children:
            decorators = []
            if child.type == "function_definition":
                name_node = child.child_by_field_name("name")
                if name_node is None:
                    continue
                method_name = name_node.text.decode("utf-8")
                docstring = self.extract_docstring(child)
            elif child.type == "decorated_definition":
                print_node_fields(child)
                func_definition_node = None
                for sub in child.children:
                    if sub.type == "decorator":
                        decorators.append(sub.text.decode("utf-8").lstrip("@"))
                    elif sub.type == "function_definition":
                        func_definition_node = sub
                        break
                if func_definition_node is None:
                    continue
                name_node = func_definition_node.child_by_field_name("name")
                if name_node is None:
                    continue
                method_name = name_node.text.decode("utf-8")
                docstring = self.extract_docstring(func_definition_node)
            else:
                continue
            method_body = child.text.decode("utf-8")
            method_info_list.append(
                ClassMethodInfo(
                    name=method_name,
                    decorators=decorators,
                    docstring=docstring,
                    body=method_body,
                )
            )
        return method_info_list

    def analyze(self, source: bytes) -> list[ClassInfo]:
        class_info_list = []

        tree = self._parser.parse(source)
        classes = self.extract_classes(tree.root_node)
        for class_name, class_node in classes:
            class_info = ClassInfo(
                name=class_name,
                parent_names=self.extract_parent_names(class_node),
                docstring=self.extract_docstring(class_node),
                methods=self.extract_method_info_list(class_node),
            )
            class_info_list.append(class_info)
        return class_info_list

#
# with open("example.txt", "rb") as f:
#     source_code = f.read()
#
# analyzer = ClassASTAnalyzer()
# result = analyzer.analyze(source_code)
# pprint(result)  # noqa: T203
