import os
import tempfile

from arc.output import (
    build_output_path,
    chapter_exists,
    ensure_output_dir,
    save_chapter,
)


def test_build_output_path_basic():
    assert build_output_path(1, "./out") == os.path.join("./out", "chapter_001.txt")


def test_build_output_path_double_digit():
    assert build_output_path(12, "./out") == os.path.join("./out", "chapter_012.txt")


def test_build_output_path_triple_digit():
    assert build_output_path(123, "./out") == os.path.join("./out", "chapter_123.txt")


def test_ensure_output_dir_creates_directory():
    with tempfile.TemporaryDirectory() as tmp:
        d = os.path.join(tmp, "sub", "dir")
        ensure_output_dir(d)
        assert os.path.isdir(d)


def test_save_chapter_creates_file():
    with tempfile.TemporaryDirectory() as tmp:
        path = save_chapter(1, "Chapter 1", "Hello world", tmp)
        assert os.path.isfile(path)
        content = open(path, encoding="utf-8").read()
        assert content == "# Chapter 1\n\nHello world\n"


def test_save_chapter_content_format():
    with tempfile.TemporaryDirectory() as tmp:
        path = save_chapter(3, "Chapter 3: The Beginning", "Once upon a time...", tmp)
        content = open(path, encoding="utf-8").read()
        assert content.startswith("# Chapter 3: The Beginning\n\n")
        assert "Once upon a time..." in content


def test_save_chapter_skips_existing():
    with tempfile.TemporaryDirectory() as tmp:
        p1 = save_chapter(1, "Chapter 1", "First version", tmp)
        save_chapter(1, "Chapter 1", "Second version", tmp)
        content = open(p1, encoding="utf-8").read()
        assert "First version" in content
        assert "Second version" not in content


def test_save_chapter_force_overwrites():
    with tempfile.TemporaryDirectory() as tmp:
        p1 = save_chapter(1, "Chapter 1", "First", tmp)
        save_chapter(1, "Chapter 1", "Second", tmp, force=True)
        content = open(p1, encoding="utf-8").read()
        assert "Second" in content
        assert "First" not in content


def test_chapter_exists_true():
    with tempfile.TemporaryDirectory() as tmp:
        save_chapter(1, "Chapter 1", "text", tmp)
        assert chapter_exists(1, tmp) is True


def test_chapter_exists_false():
    with tempfile.TemporaryDirectory() as tmp:
        assert chapter_exists(1, tmp) is False


def test_save_chapter_uses_utf8():
    with tempfile.TemporaryDirectory() as tmp:
        save_chapter(1, "Chapter 1", "\u4e2d\u6587\u6d4b\u8bd5", tmp)
        path = build_output_path(1, tmp)
        with open(path, encoding="utf-8") as f:
            assert "\u4e2d\u6587\u6d4b\u8bd5" in f.read()
