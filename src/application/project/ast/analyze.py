from typing import Any

from tree_sitter import Language, Node, Parser, Query, QueryCursor
import tree_sitter_python as tsp


#
#
# with open("example.txt") as f:
#     source = f.read()


def get_node_text(node: Node, source: bytes) -> str:
    """Return the text of a tree-sitter node as a string."""
    return source[node.start_byte : node.end_byte].decode("utf-8")


def extract_docstring(class_body: Node, source: bytes) -> str | None:
    """
    Extract the docstring of a class if present.
    Docstring is the first expression_statement that is a string literal.
    """
    for child in class_body.children:
        if child.type == "expression_statement":
            # Look for a string literal inside the expression statement
            string_node = None
            for sub in child.children:
                if sub.type == "string":
                    string_node = sub
                    break
            if string_node:
                return get_node_text(string_node, source).strip('"')
    return None


def extract_methods(class_body: Node, source: bytes) -> list[dict[str, Any]]:
    """
    Extract methods defined directly inside the class body (not nested in other classes).
    Returns a list of dicts with 'name' and 'body' (the source code of the method).
    """
    methods = []
    for child in class_body.children:
        # Methods can be function_definition or decorated_definition (if they have decorators)
        # We'll handle both, but for simplicity we extract the function_definition child
        # if it's a decorated_definition, we descend to get the function_definition.
        if child.type == "function_definition":
            # Get method name
            name_node = child.child_by_field_name("name")
            if name_node is None:
                continue
            method_name = get_node_text(name_node, source)
            # The whole method body (from 'def' to end) is the node's text
            method_body = get_node_text(child, source)
            methods.append({"name": method_name, "body": method_body})
        elif child.type == "decorated_definition":
            # decorated_definition has a child which is the function_definition
            func_def = None
            for sub in child.children:
                if sub.type == "function_definition":
                    func_def = sub
                    break
            if func_def:
                name_node = func_def.child_by_field_name("name")
                if name_node is None:
                    continue
                method_name = get_node_text(name_node, source)
                # Include decorators in the method body? We'll include the whole decorated_definition.
                # If you want only the function definition, use func_def instead.
                method_body = get_node_text(child, source)
                methods.append({"name": method_name, "body": method_body})
    return methods


def extract_classes(source_code: str) -> list[dict[str, Any]]:
    """
    Parse the source code and return a list of classes with their name,
    docstring, and methods.
    """
    source_bytes = source_code.encode("utf-8")

    # Set up parser with Python language
    language = tsp.language()
    PY_LANGUAGE = Language(language)
    parser = Parser(PY_LANGUAGE)
    tree = parser.parse(source_bytes)
    root = tree.root_node

    # Query for all class definitions
    query = Query(
        PY_LANGUAGE,
        """
        (class_definition) @class
    """,
    )
    query_cursor = QueryCursor(query)
    captures = query_cursor.captures(root)

    classes = []
    for node_name, children in captures.items():
        node = captures[node_name][0]
        # Get class name
        name_node = node.child_by_field_name("name")
        if name_node is None:
            continue
        class_name = get_node_text(name_node, source_bytes)

        # Get class body (the block containing the class contents)
        body_node = node.child_by_field_name("body")
        if body_node is None:
            continue

        docstring = extract_docstring(body_node, source_bytes)
        methods = extract_methods(body_node, source_bytes)

        classes.append({"name": class_name, "docstring": docstring, "methods": methods})

    return classes


#
# classes = extract_classes(source)
#
# # Pretty print as JSON
# print(json.dumps(classes, indent=2, ensure_ascii=False))
