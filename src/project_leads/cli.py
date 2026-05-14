from __future__ import annotations

import argparse
import os

from .pipeline import run_collection


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect global infrastructure project leads.")
    parser.add_argument("--sources", default="sources.csv", help="Path to sources.csv")
    parser.add_argument("--output-dir", default="reports", help="Directory for generated reports")
    parser.add_argument(
        "--timezone",
        default=os.getenv("RUN_TZ", "Asia/Shanghai"),
        help="Timezone used for report date",
    )
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout in seconds")
    parser.add_argument(
        "--max-items-per-source",
        type=int,
        default=50,
        help="Maximum matching links to keep per source",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = run_collection(
        sources_path=args.sources,
        output_dir=args.output_dir,
        timezone=args.timezone,
        timeout=args.timeout,
        max_items_per_source=args.max_items_per_source,
    )

    print(f"Run date: {summary.run_date}")
    print(f"Sources: {summary.source_count}")
    print(f"Leads: {summary.lead_count}")
    print(f"Errors: {summary.error_count}")
    print(f"Excel: {summary.excel_path}")
    print(f"Markdown: {summary.markdown_path}")
    return 0
