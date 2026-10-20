import json
import sqlite3
from pathlib import Path
from opspilot.config import settings

def connect():
    root=Path(settings.data_dir); root.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(root/"opspilot.db",timeout=10); db.row_factory=sqlite3.Row; return db

def initialize():
    with connect() as db:
        db.execute("CREATE TABLE IF NOT EXISTS incidents(id TEXT PRIMARY KEY, service TEXT, state TEXT, score REAL, payload TEXT)")
        db.execute("CREATE TABLE IF NOT EXISTS actions(key TEXT PRIMARY KEY, plan_id TEXT, status TEXT, result TEXT)")

def save_incident(incident):
    with connect() as db: db.execute("INSERT OR REPLACE INTO incidents VALUES(?,?,?,?,?)",(incident.incident_id,incident.service,incident.state,incident.anomaly_score,incident.model_dump_json()))

def get_incident(incident_id):
    with connect() as db: row=db.execute("SELECT payload FROM incidents WHERE id=?",(incident_id,)).fetchone()
    return json.loads(row[0]) if row else None

def list_incidents():
    with connect() as db: rows=db.execute("SELECT payload FROM incidents ORDER BY rowid DESC LIMIT 50").fetchall()
    return [json.loads(r[0]) for r in rows]

def claim_action(key,plan_id):
    with connect() as db:
        try: db.execute("INSERT INTO actions VALUES(?,?,?,?)",(key,plan_id,"executed","simulated")); return True
        except sqlite3.IntegrityError: return False
