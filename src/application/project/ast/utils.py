from tree_sitter import Node


def print_node_fields(node: Node, indent: int = 0) -> None:
    node_type = node.type
    text = node.text.decode("utf-8")[:50]

    print(f"{'  ' * indent}{node_type}: {text!r}")  # noqa: T201

    for child in node.children:
        print_node_fields(child, indent + 1)
