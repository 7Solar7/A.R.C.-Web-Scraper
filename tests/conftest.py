import os
import pytest

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def _read_fixture(name):
    path = os.path.join(FIXTURES_DIR, name)
    with open(path, encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def series_html():
    return _read_fixture("series_page.html")


@pytest.fixture
def chapter_html():
    return _read_fixture("chapter_page.html")


@pytest.fixture
def last_chapter_html():
    return _read_fixture("last_chapter_page.html")


@pytest.fixture
def error_html():
    return _read_fixture("error_404.html")


@pytest.fixture
def rss_xml():
    return _read_fixture("rss_feed.xml")
