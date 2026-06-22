import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from arc.types import (
    AKKNOVEL_BASE,
    CHAPTER_CONTENT_SELECTOR,
    CHAPTER_TITLE_SELECTOR,
    NEXT_BUTTON_SELECTOR,
    PAGE_DATA_PATTERN,
    PARAGRAPH_SELECTOR,
    PREV_BUTTON_SELECTOR,
    random_user_agent,
    NovelInfo,
    ChapterInfo,
)


class ContentError(Exception):
    pass


def _build_session(retries=3):
    session = requests.Session()
    adapter = HTTPAdapter(
        max_retries=Retry(
            total=retries,
            backoff_factor=1.0,
            status_forcelist=[502, 503, 504],
            allowed_methods=["GET"],
        )
    )
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({
        "User-Agent": random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": AKKNOVEL_BASE + "/",
    })
    return session


def _parse_page_data(html):
    m = re.search(PAGE_DATA_PATTERN, html)
    if not m:
        return {}
    raw = m.group(1)
    decoded = raw.encode("utf-8").decode("unicode_escape")
    return json.loads(decoded)


def _extract_slug(series_url):
    path = urlparse(series_url).path.rstrip("/")
    parts = path.split("/")
    try:
        idx = parts.index("series")
        return parts[idx + 1]
    except (ValueError, IndexError):
        return parts[-1]


def get_novel_info(series_url, session=None):
    if session is None:
        session = _build_session()
    r = session.get(series_url, timeout=15)
    r.raise_for_status()
    data = _parse_page_data(r.text)
    slug = _extract_slug(series_url)
    return NovelInfo(
        novel_id=data.get("novelId", ""),
        title=data.get("name", ""),
        slug=slug,
    )


def get_chapter_urls_from_rss(series_url, session=None):
    if session is None:
        session = _build_session()
    slug = _extract_slug(series_url)
    rss_url = AKKNOVEL_BASE + f"/series/{slug}/feed"
    r = session.get(rss_url, timeout=15)
    r.raise_for_status()
    root = ET.fromstring(r.text)
    urls = []
    for item in root.iter("item"):
        link_el = item.find("link")
        if link_el is not None and link_el.text:
            url = link_el.text.strip()
            if "/chapter-" in url:
                urls.append(url)
    return urls


def get_next_chapter_url(chapter_url, session):
    r = session.get(chapter_url, timeout=15)
    r.raise_for_status()
    return _find_next_url(r.text), r.text


def _find_next_url(html):
    soup = BeautifulSoup(html, "html.parser")
    nav = soup.select(NEXT_BUTTON_SELECTOR)
    if not nav:
        return None
    btn = nav[0]
    href = btn.get("href", "")
    if not href or "btn-disabled" in (btn.get("class") or []):
        return None
    return href


def _find_prev_url(html):
    soup = BeautifulSoup(html, "html.parser")
    nav = soup.select(PREV_BUTTON_SELECTOR)
    if not nav:
        return None
    btn = nav[0]
    href = btn.get("href", "")
    if not href or "btn-disabled" in (btn.get("class") or []):
        return None
    return href


def get_chapter_info(chapter_url, session):
    r = session.get(chapter_url, timeout=15)
    r.raise_for_status()
    html = r.text
    data = _parse_page_data(html)
    chapter_index = data.get("chapterIndex", 0)
    number = chapter_index + 1

    soup = BeautifulSoup(html, "html.parser")
    title_el = soup.select_one(CHAPTER_TITLE_SELECTOR)
    title = title_el.get_text(strip=True) if title_el else f"Chapter {number}"

    next_url = _find_next_url(html)
    prev_url = _find_prev_url(html)

    return ChapterInfo(
        number=number,
        title=title,
        url=chapter_url,
        is_last=next_url is None,
    )


def fetch_chapter(url, session):
    r = session.get(url, timeout=15)
    r.raise_for_status()
    if "Just a moment..." in r.text:
        raise ContentError("Cloudflare challenge detected")
    return r.text


def extract_chapter_text(html):
    soup = BeautifulSoup(html, "html.parser")
    article = soup.select_one(CHAPTER_CONTENT_SELECTOR)
    if not article:
        raise ContentError("No chapter content found (no article#chapter-content)")

    for tag in article.find_all(["script", "ins"]):
        tag.decompose()

    paragraphs = article.select(PARAGRAPH_SELECTOR)
    if not paragraphs:
        paragraphs = article.find_all("p")

    texts = []
    for p in paragraphs:
        text = p.get_text(strip=True)
        if text:
            texts.append(text)

    if not texts:
        raise ContentError("No text paragraphs found in chapter content")

    return "\n\n".join(texts)


def extract_chapter_title(html):
    soup = BeautifulSoup(html, "html.parser")
    title_el = soup.select_one(CHAPTER_TITLE_SELECTOR)
    if title_el:
        return title_el.get_text(strip=True)
    data = _parse_page_data(html)
    if "chapterIndex" in data:
        return f"Chapter {data['chapterIndex'] + 1}"
    return "Unknown Chapter"


def extract_chapter_number(html):
    data = _parse_page_data(html)
    if "chapterIndex" in data:
        return data["chapterIndex"] + 1
    raise ContentError("Could not determine chapter number")


def walk_chapters(start_url, end_chapter, session, delay=1.0):
    url = start_url
    count = 0
    while url:
        html = fetch_chapter(url, session)
        data = _parse_page_data(html)
        chapter_index = data.get("chapterIndex", 0)
        number = chapter_index + 1

        if end_chapter is not None and number > end_chapter:
            return

        soup = BeautifulSoup(html, "html.parser")
        title_el = soup.select_one(CHAPTER_TITLE_SELECTOR)
        title = title_el.get_text(strip=True) if title_el else f"Chapter {number}"

        next_url = _find_next_url(html)

        yield ChapterInfo(
            number=number,
            title=title,
            url=url,
            is_last=next_url is None,
        )

        count += 1
        url = next_url
        if url and delay > 0:
            time.sleep(delay)
