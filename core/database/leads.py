import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from core.models.lead_model import Lead

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "leads.sqlite3"

@contextmanager
def connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                location TEXT NOT NULL,
                website TEXT,
                phone TEXT,
                social_profiles TEXT NOT NULL DEFAULT '[]',
                score REAL NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'new',
                created_at TEXT NOT NULL
            )
        """)

def get_statistics() -> dict:
    with connection() as conn:
        summary = dict(conn.execute("""
            SELECT
                COUNT(*) AS total,
                COALESCE(SUM(
                    CASE WHEN TRIM(COALESCE(website, '')) != ''
                    THEN 1 ELSE 0 END
                ), 0) AS with_website,
                COALESCE(SUM(
                    CASE WHEN TRIM(COALESCE(phone, '')) != ''
                    THEN 1 ELSE 0 END
                ), 0) AS with_phone,
                COALESCE(SUM(
                    CASE
                        WHEN TRIM(COALESCE(website, '')) != ''
                         AND TRIM(COALESCE(phone, '')) != ''
                        THEN 1 ELSE 0
                    END
                ), 0) AS with_both,
                COALESCE(AVG(score), 0) AS average_score
            FROM leads
        """).fetchone())

        statuses = [
            dict(row)
            for row in conn.execute("""
                SELECT status, COUNT(*) AS total
                FROM leads
                GROUP BY status
                ORDER BY total DESC, status
            """).fetchall()
        ]

        category_rows = conn.execute("""
            SELECT category, COUNT(*) AS total
            FROM leads
            GROUP BY category
        """).fetchall()

    categories = {}

    for row in category_rows:
        labels = {
            label.strip()
            for label in row["category"].split(",")
            if label.strip()
        }

        for label in labels:
            categories[label] = categories.get(label, 0) + row["total"]

    summary["without_website"] = (
        summary["total"] - summary["with_website"]
    )
    summary["without_phone"] = (
        summary["total"] - summary["with_phone"]
    )
    summary["without_contact"] = (
        summary["total"]
        - summary["with_website"]
        - summary["with_phone"]
        + summary["with_both"]
    )

    return {
        "summary": summary,
        "statuses": statuses,
        "categories": sorted(
            categories.items(),
            key=lambda item: (-item[1], item[0]),
        ),
    }

def save_leads(leads: list[Lead]) -> int:
    """Salva uma busca inteira em uma única transação."""
    rows = [
        (
            lead.name,
            lead.category,
            lead.location,
            lead.website,
            lead.phone,
            json.dumps(lead.social_profiles, ensure_ascii=False),
            lead.score,
            lead.status,
            lead.created_at.isoformat(),
        )
        for lead in leads
    ]

    with connection() as conn:
        conn.executemany("""
            INSERT INTO leads (
                name, category, location, website, phone,
                social_profiles, score, status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)

    return len(rows)

def list_leads() -> list[Lead]:
    with connection() as conn:
        rows = conn.execute("""
            SELECT *
            FROM leads
            ORDER BY id DESC
        """).fetchall()

    return [
        Lead(
            name=row["name"],
            category=row["category"],
            location=row["location"],
            website=row["website"],
            phone=row["phone"],
            social_profiles=json.loads(row["social_profiles"]),
            score=row["score"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
        for row in rows
    ]