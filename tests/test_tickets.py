import tempfile
import unittest
from datetime import timezone, datetime
from pathlib import Path
from itsupport_lab.tickets import Ticket, load_tickets, make_report, parse_time, render_html


class TicketTests(unittest.TestCase):
    def setUp(self):
        self.ts = parse_time("2026-11-19T12:00:00Z")
        self.path = Path(__file__).resolve().parents[1] / "sample-data" / "incidents.csv"

    def test_sample_size_and_summary(self):
        report = make_report(load_tickets(self.path), self.ts)
        self.assertEqual(report["tickets_total"], 8)
        self.assertEqual(report["completed_total"], 6)
        self.assertEqual(report["open_total"], 2)
        self.assertIn("INC-1003", report["breached_ticket_ids"])
        self.assertEqual(report["scope"], "SYNTHETIC LAB DATA ONLY")

    def test_timezone_required(self):
        with self.assertRaises(ValueError):
            parse_time("2026-11-19T12:00:00")

    def test_invalid_status_and_priority(self):
        row = {"ticket_id": "X", "category": "Identity", "priority": "P7", "status": "Closed", "opened_at": "2026-11-19T10:00:00Z", "resolved_at": "2026-11-19T11:00:00Z", "summary": "example"}
        with self.assertRaises(ValueError):
            Ticket.from_row(row)
        row["priority"] = "P2"
        row["status"] = "Missing"
        with self.assertRaises(ValueError):
            Ticket.from_row(row)

    def test_breach_boundary(self):
        base = dict(ticket_id="LAB-1", category="Identity", priority="P1", status="Resolved", summary="mock")
        start = parse_time("2026-11-19T08:00:00Z")
        deadline = parse_time("2026-11-19T12:00:00Z")
        ticket = Ticket(opened_at=start, resolved_at=deadline, **base)
        self.assertFalse(ticket.assessment(self.ts)["breached"])

    def test_early_as_of_fails(self):
        ticket = load_tickets(self.path)[-1]
        with self.assertRaises(ValueError):
            ticket.assessment(parse_time("2026-11-18T00:00:00Z"))

    def test_duplicate_ids_rejected(self):
        raw = self.path.read_text(encoding="utf-8").splitlines()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "dups.csv"
            p.write_text("\n".join(raw[:2] + [raw[1]]) + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_tickets(p)

    def test_html_report(self):
        html = render_html(make_report(load_tickets(self.path), self.ts))
        self.assertIn("SYNTHETIC LAB DATA", html)
        self.assertIn("INC-1003", html)
        self.assertIn("<!doctype html>", html)

    def test_resolved_needs_resolution_time(self):
        row = {"ticket_id": "Y", "category": "Endpoints", "priority": "P3", "status": "Resolved", "opened_at": "2026-11-19T10:00:00Z", "resolved_at": "", "summary": "mock"}
        with self.assertRaises(ValueError):
            Ticket.from_row(row)

if __name__ == "__main__":
    unittest.main()
