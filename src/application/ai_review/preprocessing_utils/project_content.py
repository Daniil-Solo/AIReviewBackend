from collections.abc import Callable
from pathlib import Path

from src.application.ai_review.preprocessing_utils.file_handlers import DEFAULT_FILE_HANDLERS, FileHandler


def is_binary_file(path: Path, *, sample_size: int = 8192) -> bool:
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")

    with path.open("rb") as f:
        sample = f.read(sample_size)

    if b"\x00" in sample:
        return True

    text_bytes = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(32, 127)))
    non_text = sum(b not in text_bytes for b in sample)
    return non_text / max(len(sample), 1) > 0.30


def path_content(
    root: Path,
    *,
    follow_symlinks: bool = False,
    include: Callable[[Path], bool] = lambda _: True,
    encoding: str = "utf-8",
    errors: str = "raise",
    file_handlers: dict[str, FileHandler] | None = None,
) -> str:
    root = root.resolve()
    blocks: list[str] = []
    handlers = DEFAULT_FILE_HANDLERS.copy()
    if file_handlers:
        handlers.update(file_handlers)

    def should_follow(p: Path) -> bool:
        return follow_symlinks or not p.is_symlink()

    def get_handler(p: Path) -> FileHandler | None:
        ext = "." + p.name.rsplit(".", 1)[-1]
        return handlers.get(ext)

    def safe_add_file(p: Path) -> None:
        try:
            handler = get_handler(p)
            content = handler(p) if handler is not None else p.read_text(encoding=encoding)
            relative_path = p.resolve().relative_to(root.resolve()).as_posix()
            blocks.append(f"===== FILE: {relative_path} =====\n{content}\n===== END FILE =====")
        except (OSError, UnicodeDecodeError):
            if errors == "skip":
                return
            raise

    if root.is_file():
        if include(root) and should_follow(root):
            safe_add_file(root)
        return "\n\n".join(blocks)

    if not root.is_dir():
        raise ValueError(f"Not a file or directory: {root}")

    for dirpath, dirnames, filenames in root.walk(follow_symlinks=follow_symlinks):
        kept = [name for name in dirnames if include(dirpath / name) and should_follow(dirpath / name)]
        dirnames[:] = sorted(kept, key=str.casefold)

        for name in sorted(filenames, key=str.casefold):
            p = dirpath / name
            if not include(p) or not should_follow(p):
                continue
            safe_add_file(p)

    return "\n\n".join(blocks)
