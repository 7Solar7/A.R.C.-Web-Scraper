import sys

from arc.cli import parse_args
from arc.types import (
    DEFAULT_DELAY,
    DEFAULT_OUTPUT,
    EXIT_BAD_ARGS,
    EXIT_SUCCESS,
)


def test_parse_args_basic():
    args = parse_args(["https://example.com/series/test"])
    assert args.series_url == "https://example.com/series/test"
    assert args.start == 1
    assert args.end is None


def test_parse_args_defaults():
    args = parse_args(["https://example.com"])
    assert args.output == DEFAULT_OUTPUT
    assert args.delay == DEFAULT_DELAY
    assert args.retries == 3
    assert args.force is False


def test_parse_args_custom():
    args = parse_args([
        "https://example.com",
        "--start", "5",
        "--end", "10",
        "--output", "./mydir",
        "--delay", "0.5",
        "--retries", "5",
        "--force",
    ])
    assert args.start == 5
    assert args.end == 10
    assert args.output == "./mydir"
    assert args.delay == 0.5
    assert args.retries == 5
    assert args.force is True


def test_parse_args_short_flags():
    args = parse_args(["https://example.com", "-o", "./out", "-f"])
    assert args.output == "./out"
    assert args.force is True


def test_main_bad_args_start():
    from arc.cli import main
    result = main(["https://example.com", "--start", "0"])
    assert result == EXIT_BAD_ARGS


def test_main_bad_args_end_before_start():
    from arc.cli import main
    result = main(["https://example.com", "--start", "5", "--end", "3"])
    assert result == EXIT_BAD_ARGS
