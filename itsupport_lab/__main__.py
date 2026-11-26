"""Usage: python -m itsupport_lab report --file sample-data/incidents.csv --as-of ..."""
import argparse
import json
from datetime import datetime, timezone
from .tickets import load_tickets, make_report, parse_time, render_html


def main() -> int:
    p = argparse.ArgumentParser(description="Offline help-desk SLA report")
    p.add_argument("command", choices=["report"])
    p.add_argument("--file", default="sample-data/incidents.csv", help="CSV path")
    p.add_argument("--as-of", help="ISO8601 timestamp with timezone (defaults to now)")
    p.add_argument("--output", help="Optional JSON/HTML output file")
    p.add_argument("--format", choices=["json", "html"], default="json")
    args = p.parse_args()
    as_of = parse_time(args.as_of) if args.as_of else datetime.now(timezone.utc)
    report = make_report(load_tickets(args.file), as_of)
    encoded = render_html(report) if args.format == "html" else json.dumps(report, indent=2)
    if args.output:
        from pathlib import Path
        Path(args.output).write_text(encoded + "\n", encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
