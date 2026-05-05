from collections.abc import Callable
from pathlib import Path


def is_dir(p: Path) -> bool:
    try:
        return p.is_dir()
    except OSError:
        return False


def path_tree(
    root: Path,
    *,
    follow_symlinks: bool = False,
    include: Callable[[Path], bool] = lambda _: True,
) -> str:
    root = root.resolve()
    lines: list[str] = [str(root)]

    def iter_children(d: Path) -> list[Path]:
        try:
            children = list(d.iterdir())
        except OSError:
            return []
        children.sort(key=lambda p: (not is_dir(p), p.name.casefold()))
        return children

    def rec(d: Path, prefix: str) -> None:
        children = [c for c in iter_children(d) if include(c)]
        n = len(children)

        for i, child in enumerate(children):
            last = i == n - 1
            branch = "└── " if last else "├── "
            lines.append(prefix + branch + child.name)

            if is_dir(child):
                ext = "    " if last else "│   "
                if follow_symlinks or not child.is_symlink():
                    rec(child, prefix + ext)

    rec(root, "")
    return "\n".join(lines)
