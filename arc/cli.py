import argparse
import sys
import time

from arc.scraper import (
    ContentError,
    _build_session,
    extract_chapter_text,
    extract_chapter_number,
    extract_chapter_title,
    fetch_chapter,
    get_chapter_urls_from_rss,
    get_novel_info,
    walk_chapters,
)
from arc.output import ensure_output_dir, save_chapter
from arc.types import (
    DEFAULT_DELAY,
    DEFAULT_OUTPUT,
    EXIT_BAD_ARGS,
    EXIT_CONTENT_ERROR,
    EXIT_FILE_ERROR,
    EXIT_NETWORK_ERROR,
    EXIT_SUCCESS,
)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="python -m arc",
        description="A.R.C. — Automated Retrieval of Chapters",
    )
    parser.add_argument("series_url", help="URL of the series page on akknovel.com")
    parser.add_argument("--start", type=int, default=1, help="Starting chapter number (default: 1)")
    parser.add_argument("--end", type=int, default=None, help="Ending chapter number (default: all)")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT, help="Output directory (default: ./chapters)")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY, help="Delay between requests in seconds (default: 1.0)")
    parser.add_argument("--retries", type=int, default=3, help="Max retries per request (default: 3)")
    parser.add_argument("--force", "-f", action="store_true", help="Overwrite existing files")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    if args.start < 1:
        print("Error: --start must be >= 1", file=sys.stderr)
        return EXIT_BAD_ARGS

    if args.end is not None and args.end < args.start:
        print("Error: --end must be >= --start", file=sys.stderr)
        return EXIT_BAD_ARGS

    session = _build_session(retries=args.retries)

    try:
        rss_urls = get_chapter_urls_from_rss(args.series_url, session)
    except Exception as e:
        print(f"Error: Failed to fetch RSS feed: {e}", file=sys.stderr)
        return EXIT_NETWORK_ERROR

    if not rss_urls:
        print("Error: No chapters found in RSS feed", file=sys.stderr)
        return EXIT_CONTENT_ERROR

    start_url = None
    for url in rss_urls:
        parts = url.rstrip("/").split("/")
        for part in parts:
            if part.startswith("chapter-"):
                try:
                    nums = part.replace("chapter-", "").split("-")
                    ch_num = int(nums[0])
                    if ch_num == args.start:
                        start_url = url
                        break
                except (ValueError, IndexError):
                    continue
        if start_url:
            break

    if not start_url:
        print(f"Error: Could not find URL for chapter {args.start} in RSS feed", file=sys.stderr)
        print("Tip: RSS feed only contains recent chapters. Try --start with a higher number.", file=sys.stderr)
        return EXIT_CONTENT_ERROR

    ensure_output_dir(args.output)

    try:
        for chapter in walk_chapters(start_url, args.end, session, delay=args.delay):
            print(f"Chapter {chapter.number}: {chapter.title}")
            try:
                html = fetch_chapter(chapter.url, session)
                text = extract_chapter_text(html)
                title = extract_chapter_title(html)
                save_chapter(chapter.number, title, text, args.output, force=args.force)
            except ContentError as e:
                print(f"  Error: {e}", file=sys.stderr)
                return EXIT_CONTENT_ERROR
            if args.delay > 0 and not chapter.is_last:
                time.sleep(args.delay)
    except KeyboardInterrupt:
        print("\nInterrupted by user.", file=sys.stderr)
        return EXIT_SUCCESS
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return EXIT_NETWORK_ERROR

    print("Done.")
    return EXIT_SUCCESS
