import os
import sys


def build_output_path(chapter_number, output_dir):
    filename = f"chapter_{chapter_number:03d}.txt"
    return os.path.join(output_dir, filename)


def chapter_exists(chapter_number, output_dir):
    return os.path.isfile(build_output_path(chapter_number, output_dir))


def ensure_output_dir(output_dir):
    os.makedirs(output_dir, exist_ok=True)


def save_chapter(chapter_number, title, text, output_dir, force=False):
    path = build_output_path(chapter_number, output_dir)
    if os.path.exists(path) and not force:
        print(f"  Skipping chapter {chapter_number} (already exists): {path}", file=sys.stderr)
        return path
    content = f"# {title}\n\n{text}\n"
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    return path
