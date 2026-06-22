from dataclasses import dataclass
import random

EXIT_SUCCESS = 0
EXIT_BAD_ARGS = 1
EXIT_NETWORK_ERROR = 2
EXIT_CONTENT_ERROR = 3
EXIT_FILE_ERROR = 4

DEFAULT_DELAY = 1.0
DEFAULT_OUTPUT = "./chapters"

AKKNOVEL_BASE = "https://www.akknovel.com"
SERIES_PATH = "/series/{slug}"
RSS_PATH = "/series/{slug}/feed"

CHAPTER_CONTENT_SELECTOR = "article#chapter-content"
PARAGRAPH_SELECTOR = "p.mb-4.para"
CHAPTER_TITLE_SELECTOR = "h1"
NEXT_BUTTON_SELECTOR = "div.grid.grid-cols-2 a.btn:last-of-type"
PREV_BUTTON_SELECTOR = "div.grid.grid-cols-2 a.btn:first-of-type"
PAGE_DATA_PATTERN = r"window\._pageData\s*=\s*JSON\.parse\(\x60(.+?)\x60\)"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]


def random_user_agent():
    return random.choice(USER_AGENTS)


@dataclass
class NovelInfo:
    novel_id: str
    title: str
    slug: str
    total_chapters: int | None = None


@dataclass
class ChapterInfo:
    number: int
    title: str
    url: str
    is_last: bool = False
