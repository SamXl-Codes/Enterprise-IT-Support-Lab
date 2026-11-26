"""Deterministic service-desk ticket analysis for fictional lab incident data."""
from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

SLA_HOURS = {"P1": 4, "P2": 8, "P3": 48, "P4": 120}
STATUSES = {"Open", "In Progress", "Resolved", "Closed"}


def parse_time(value: str) -> datetime:
    """Require timezone-aware ISO8601. All elapsed intervals are clock hours."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"Timezone missing: {value}")
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class Ticket:
    ticket_id: str
    category: str
    priority: str
    status: str
    opened_at: datetime
    resolved_at: datetime | None
    summary: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "Ticket":
        priority = row["priority"].strip().upper()
        status = row["status"].strip()
        if priority not in SLA_HOURS:
            raise ValueError(f"Unknown priority {priority!r}")
        if status not in STATUSES:
            raise ValueError(f"Unknown status {status!r}")
        resolved_at = parse_time(row["resolved_at"]) if row.get("resolved_at", "").strip() else None
        opened_at = parse_time(row["opened_at"])
        if status in {"Resolved", "Closed"} and resolved_at is None:
            raise ValueError("Resolved/Closed tickets need resolved_at")
        if status in {"Open", "In Progress"} and resolved_at is not None:
            raise ValueError("Open tickets cannot have resolved_at")
        if resolved_at and resolved_at < opened_at:
            raise ValueError("Resolution precedes opening")
        ticket_id = row["ticket_id"].strip()
        if not ticket_id:
            raise ValueError("ticket_id must not be empty")
        return cls(ticket_id, row["category"].strip(), priority, status,
                   opened_at, resolved_at, row["summary"].strip())

    def assessment(self, as_of: datetime) -> dict:
        if as_of < self.opened_at:
            raise ValueError(f"as_of predates ticket {self.ticket_id}")
        completed = self.resolved_at is not None and self.resolved_at <= as_of
        end = self.resolved_at if completed else as_of
        elapsed = round((end - self.opened_at).total_seconds() / 3600, 2)
        target = SLA_HOURS[self.priority]
        return {"ticket_id": self.ticket_id,
                "priority": self.priority, "status": self.status,
                "elapsed_clock_hours": elapsed, "resolution_target_clock_hours": target,
                "breached": elapsed > target,
                "completed": completed}


def load_tickets(path: str | Path) -> list[Ticket]:
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        tickets = [Ticket.from_row(row) for row in csv.DictReader(handle)]
    ids = [t.ticket_id for t in tickets]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate ticket_id in input")
    return tickets


def make_report(tickets: list[Ticket], as_of: datetime) -> dict:
    if as_of.tzinfo is None:
        raise ValueError("as_of must include timezone")
    evaluated = [t.assessment(as_of) for t in tickets]
    completed = [t for t in evaluated if t["completed"]]
    active = [t for t in evaluated if not t["completed"]]
    breaches = [t for t in evaluated if t["breached"]]
    counts = Counter(t.status for t in tickets)
    return {
        "scope": "SYNTHETIC LAB DATA ONLY",
        "as_of_utc": as_of.astimezone(timezone.utc).isoformat(),
        "sla_basis": "elapsed clock hours, not business-hours SLA",
        "tickets_total": len(tickets),
        "status_counts": dict(sorted(counts.items())),
        "completed_total": len(completed),
        "open_total": len(active),
        "breached_total": len(breaches),
        "resolved_within_target": sum(not t["breached"] for t in completed),
        "breached_ticket_ids": [t["ticket_id"] for t in breaches],
        "tickets": evaluated,
    }


def render_html(report: dict) -> str:
    """Single-file, escaped HTML view of an offline report. No remote assets."""
    from html import escape
    summary = [
        ("Total tickets", report["tickets_total"]),
        ("Resolved/closed", report["completed_total"]),
        ("Open", report["open_total"]),
        ("SLA breaches", report["breached_total"]),
    ]
    cards = "".join(
        f'<div class="metric"><span>{escape(label)}</span><strong>{value}</strong></div>'
        for label, value in summary
    )
    rows = "".join(
        "<tr>" + "".join(f"<td>{escape(str(ticket[key]))}</td>" for key in (
            "ticket_id", "priority", "status", "elapsed_clock_hours",
            "resolution_target_clock_hours", "breached"
        )) + "</tr>"
        for ticket in report["tickets"]
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lab Service Desk Report</title>
<style>
:root{{color-scheme:light}}*{{box-sizing:border-box}}
body{{font-family:system-ui,-apple-system,Segoe UI,sans-serif;color:#1b1d22;background:#f5f4ef;margin:0;padding:36px 18px}}
main{{max-width:1040px;margin:auto}}h1{{margin:6px 0 8px;font-size:clamp(1.75rem,4vw,2.6rem)}}
.subtitle{{color:#555;line-height:1.6}}.scope{{background:#141b22;color:#fff;border-radius:7px;padding:7px 10px;display:inline-block;font-size:12px;font-weight:600}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:28px 0}}
.metric{{background:#fff;border:1px solid #dadada;border-radius:12px;padding:20px}}
.metric span{{display:block;color:#666;font-size:13px}}.metric strong{{font-size:32px}}
table{{border-collapse:collapse;width:100%;font-size:14px;background:#fff}}th,td{{text-align:left;padding:12px;border-bottom:1px solid #e5e5e5}}
th{{background:#f1f1ef}}.table-wrap{{overflow:auto;border:1px solid #ddd;border-radius:12px}}
footer{{margin-top:20px;color:#777;font-size:12px}}
</style></head><body><main>
<p class="scope">SYNTHETIC LAB DATA</p><h1>Service desk incident report</h1>
<p class="subtitle">As of {escape(report['as_of_utc'])}. Target times are elapsed clock hours and illustrative only.</p>
<section class="stats" aria-label="Incident summary">{cards}</section>
<div class="table-wrap"><table><thead><tr><th>ID</th><th>Priority</th><th>Status</th>
<th>Elapsed hours</th><th>Target hours</th><th>Breached</th></tr></thead><tbody>{rows}</tbody></table></div>
<footer>Generated from fictional sample incidents. Not employer or production service desk metrics.</footer>
</main></body></html>"""
