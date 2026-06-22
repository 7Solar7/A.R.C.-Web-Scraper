from arc.types import (
    EXIT_SUCCESS,
    EXIT_BAD_ARGS,
    EXIT_NETWORK_ERROR,
    EXIT_CONTENT_ERROR,
    EXIT_FILE_ERROR,
    DEFAULT_DELAY,
    DEFAULT_OUTPUT,
    AKKNOVEL_BASE,
    RSS_PATH,
    CHAPTER_CONTENT_SELECTOR,
    PARAGRAPH_SELECTOR,
    NovelInfo,
    ChapterInfo,
    random_user_agent,
)


def test_exit_codes_are_distinct_integers():
    codes = [EXIT_SUCCESS, EXIT_BAD_ARGS, EXIT_NETWORK_ERROR, EXIT_CONTENT_ERROR, EXIT_FILE_ERROR]
    assert codes == sorted(codes)
    assert len(set(codes)) == 5


def test_exit_success_is_zero():
    assert EXIT_SUCCESS == 0


def test_default_delay():
    assert DEFAULT_DELAY == 1.0


def test_default_output():
    assert DEFAULT_OUTPUT == "./chapters"


def test_akknovel_base():
    assert AKKNOVEL_BASE == "https://www.akknovel.com"


def test_rss_path_format():
    assert "{slug}" in RSS_PATH


def test_css_selectors():
    assert CHAPTER_CONTENT_SELECTOR == "article#chapter-content"
    assert "mb-4" in PARAGRAPH_SELECTOR


def test_novel_info_dataclass():
    n = NovelInfo(novel_id="abc123", title="Test Novel", slug="test-novel")
    assert n.novel_id == "abc123"
    assert n.title == "Test Novel"
    assert n.slug == "test-novel"
    assert n.total_chapters is None


def test_chapter_info_dataclass():
    c = ChapterInfo(number=5, title="Chapter 5", url="https://example.com/ch5", is_last=False)
    assert c.number == 5
    assert c.is_last is False


def test_chapter_info_is_last_default():
    c = ChapterInfo(number=1, title="Ch1", url="u")
    assert c.is_last is False


def test_random_user_agent_returns_string():
    ua = random_user_agent()
    assert isinstance(ua, str)
    assert "Mozilla" in ua
