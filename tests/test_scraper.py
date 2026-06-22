import os
import re

import responses

from arc.scraper import (
    ContentError,
    _build_session,
    _find_next_url,
    _parse_page_data,
    extract_chapter_number,
    extract_chapter_text,
    extract_chapter_title,
    get_chapter_urls_from_rss,
    get_novel_info,
)
from arc.types import AKKNOVEL_BASE


FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def _read_fixture(name):
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as f:
        return f.read()


def test_parse_page_data_series(series_html):
    data = _parse_page_data(series_html)
    assert "novelId" in data
    assert len(data["novelId"]) == 24


def test_parse_page_data_chapter(chapter_html):
    data = _parse_page_data(chapter_html)
    assert "chapterIndex" in data
    assert isinstance(data["chapterIndex"], int)


def test_parse_page_data_no_match():
    assert _parse_page_data("<html>no data</html>") == {}


@responses.activate
def test_get_novel_info(series_html):
    url = "https://www.akknovel.com/series/after-rebirth-i-was-forced-to-become-the-mafia-princess"
    responses.add(responses.GET, url, body=series_html, status=200)
    session = _build_session()
    info = get_novel_info(url, session)
    assert info.novel_id == "680ce072d6eced52d68d3059"
    assert "Mafia Princess" in info.title
    assert info.slug == "after-rebirth-i-was-forced-to-become-the-mafia-princess"


@responses.activate
def test_get_chapter_urls_from_rss(rss_xml):
    slug = "after-rebirth-i-was-forced-to-become-the-mafia-princess"
    rss_url = f"{AKKNOVEL_BASE}/series/{slug}/feed"
    responses.add(responses.GET, rss_url, body=rss_xml, status=200)
    session = _build_session()
    urls = get_chapter_urls_from_rss(
        f"https://www.akknovel.com/series/{slug}", session
    )
    assert len(urls) == 10
    assert all("/chapter-" in u for u in urls)


def test_find_next_url_non_last(chapter_html):
    next_url = _find_next_url(chapter_html)
    assert next_url is not None
    assert "/chapter-" in next_url


def test_find_next_url_last(last_chapter_html):
    next_url = _find_next_url(last_chapter_html)
    assert next_url is None


def test_extract_chapter_text(chapter_html):
    text = extract_chapter_text(chapter_html)
    assert len(text) > 100
    assert "<script>" not in text
    assert "<ins" not in text


def test_extract_chapter_text_no_ads(chapter_html):
    text = extract_chapter_text(chapter_html)
    assert "adsbygoogle" not in text
    assert "function(" not in text


def test_extract_chapter_text_empty(error_html):
    try:
        extract_chapter_text(error_html)
        assert False, "Should have raised ContentError"
    except ContentError:
        pass


def test_extract_chapter_title(chapter_html):
    title = extract_chapter_title(chapter_html)
    assert "Chapter" in title or "chapter" in title


def test_extract_chapter_number(chapter_html):
    num = extract_chapter_number(chapter_html)
    assert isinstance(num, int)
    assert num > 0


def test_extract_chapter_number_empty(error_html):
    try:
        extract_chapter_number(error_html)
        assert False, "Should have raised ContentError"
    except ContentError:
        pass
