import os
import tempfile

import responses

from arc.scraper import _build_session
from arc.types import (
    EXIT_BAD_ARGS,
    EXIT_CONTENT_ERROR,
    EXIT_NETWORK_ERROR,
    EXIT_SUCCESS,
    AKKNOVEL_BASE,
)

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
SLUG = "after-rebirth-i-was-forced-to-become-the-mafia-princess"
CH703_URL = f"{AKKNOVEL_BASE}/series/{SLUG}/chapter-703-703-a-slap-thank-you-tianwei-yuedu-for-the-great-god-certification"
CH704_URL = f"{AKKNOVEL_BASE}/series/{SLUG}/chapter-704-704-dust-settles-thanks-to-ailuo-who-loves-eating-nyonya-dried-meat-for-the-generous-big-health-gift"


def _read_fixture(name):
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as f:
        return f.read()


@responses.activate
def test_full_pipeline_with_mocked_requests():
    rss_url = f"{AKKNOVEL_BASE}/series/{SLUG}/feed"
    responses.add(responses.GET, rss_url, body=_read_fixture("rss_feed.xml"), status=200)
    responses.add(responses.GET, CH703_URL, body=_read_fixture("chapter_page.html"), status=200)
    responses.add(responses.GET, CH704_URL, body=_read_fixture("last_chapter_page.html"), status=200)

    from arc.cli import main
    with tempfile.TemporaryDirectory() as tmp:
        result = main([
            f"https://www.akknovel.com/series/{SLUG}",
            "--start", "703",
            "--end", "704",
            "--output", tmp,
            "--delay", "0",
        ])

        assert result == EXIT_SUCCESS
        files = os.listdir(tmp)
        assert len(files) == 2, f"Expected 2 files, got: {files}"
        for f in files:
            path = os.path.join(tmp, f)
            content = open(path, encoding="utf-8").read()
            assert content.startswith("# Chapter"), f"Bad header in {f}"


@responses.activate
def test_cli_exit_codes_invalid_url():
    from arc.cli import main
    result = main(["https://example.com/series/fake", "--start", "1", "--end", "1", "--delay", "0"])
    assert result in (EXIT_NETWORK_ERROR, EXIT_CONTENT_ERROR)


@responses.activate
def test_cli_network_error():
    from arc.cli import main
    slug = "test-slug"
    rss_url = f"{AKKNOVEL_BASE}/series/{slug}/feed"
    responses.add(responses.GET, rss_url, body="Server Error", status=500)
    responses.add(responses.GET, rss_url, body="Server Error", status=500)
    responses.add(responses.GET, rss_url, body="Server Error", status=500)
    responses.add(responses.GET, rss_url, body="Server Error", status=500)
    result = main([f"https://www.akknovel.com/series/{slug}", "--delay", "0", "--retries", "1"])
    assert result == EXIT_NETWORK_ERROR


@responses.activate
def test_force_flag_overwrites():
    rss_url = f"{AKKNOVEL_BASE}/series/{SLUG}/feed"
    responses.add(responses.GET, rss_url, body=_read_fixture("rss_feed.xml"), status=200)
    responses.add(responses.GET, CH704_URL, body=_read_fixture("last_chapter_page.html"), status=200)

    from arc.cli import main
    with tempfile.TemporaryDirectory() as tmp:
        main([f"https://www.akknovel.com/series/{SLUG}", "--start", "704", "--end", "704", "--output", tmp, "--delay", "0"])
        files1 = os.listdir(tmp)

        responses.add(responses.GET, CH704_URL, body=_read_fixture("last_chapter_page.html"), status=200)
        main([f"https://www.akknovel.com/series/{SLUG}", "--start", "704", "--end", "704", "--output", tmp, "--delay", "0", "--force"])
        files2 = os.listdir(tmp)
        assert len(files2) == len(files1)
