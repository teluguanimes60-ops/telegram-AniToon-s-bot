# =========================
# Simple User DB (JSON)
# =========================

import json
import os

DB_FILE = "users.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    return json.load(open(DB_FILE, "r"))

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

def get_user(uid):
    db = load_db()
    return db.get(str(uid), {})

def set_user(uid, data):
    db = load_db()
    db[str(uid)] = data
    save_db(db)
