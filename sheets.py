import csv, datetime, json, os

CSV_FILE = "leads_backup.csv"

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        csv.writer(f).writerow(
            ["ts","tg_id","first","username","phone","source","payload"]
        )

def save_lead(user: dict, source: str, payload: dict):
    with open(CSV_FILE, "a", newline="") as f:
        csv.writer(f).writerow([
            datetime.datetime.utcnow().isoformat(timespec="seconds"),
            user["id"],
            user["first_name"],
            user["username"],
            user["phone"],
            source,
            json.dumps(payload, ensure_ascii=False)
        ])
