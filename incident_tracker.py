#!/usr/bin/env python3
import argparse, json, csv, os, sys, uuid
from datetime import datetime

STORE = "incidents.json"
NIST_PHASES = ["identify", "protect", "detect", "respond", "recover"]
STATUSES = ["open", "in_progress", "contained", "eradicated", "recovered", "closed"]
SEVERITIES = ["low", "medium", "high", "critical"]

def _load():
    if not os.path.exists(STORE):
        return []
    with open(STORE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def _save(data):
    with open(STORE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def init_store(args):
    if os.path.exists(STORE) and not args.force:
        print(f"{STORE} already exists. Use --force to overwrite.")
        return
    _save([])
    print(f"Initialized empty store at {STORE}")

def add_incident(args):
    data = _load()
    inc = {
        "id": str(uuid.uuid4())[:8],
        "title": args.title,
        "category": args.category.lower(),
        "severity": args.severity.lower(),
        "phase": args.phase.lower(),
        "status": "open",
        "reported_at": datetime.utcnow().isoformat() + "Z",
        "owner": args.owner or "",
        "notes": args.notes or ""
    }
    if inc["severity"] not in SEVERITIES:
        sys.exit(f"Invalid severity. Use one of: {', '.join(SEVERITIES)}")
    if inc["phase"] not in NIST_PHASES:
        sys.exit(f"Invalid phase. Use one of: {', '.join(NIST_PHASES)}")

    data.append(inc)
    _save(data)
    print(f"✅ Added incident {inc['id']} — {inc['title']}")

def list_incidents(args):
    data = _load()
    filtered = []
    for inc in data:
        if args.severity and inc["severity"] != args.severity.lower():
            continue
        if args.phase and inc["phase"] != args.phase.lower():
            continue
        if args.status and inc["status"] != args.status.lower():
            continue
        if args.owner and (inc.get("owner","").lower() != args.owner.lower()):
            continue
        filtered.append(inc)

    if not filtered:
        print("No incidents found.")
        return

    for inc in filtered:
        print(f"{inc['id']} | {inc['severity'].upper()} | {inc['phase']} | {inc['status']}"
              f" | {inc['title']} (owner: {inc.get('owner','-')})")

def update_incident(args):
    data = _load()
    for inc in data:
        if inc["id"] == args.id:
            if args.status:
                if args.status.lower() not in STATUSES:
                    sys.exit(f"Invalid status. Use: {', '.join(STATUSES)}")
                inc["status"] = args.status.lower()
            if args.phase:
                if args.phase.lower() not in NIST_PHASES:
                    sys.exit(f"Invalid phase. Use: {', '.join(NIST_PHASES)}")
                inc["phase"] = args.phase.lower()
            if args.owner is not None:
                inc["owner"] = args.owner
            if args.notes:
                inc["notes"] = (inc.get("notes","") + "\n" if inc.get("notes") else "") + args.notes
            inc["updated_at"] = datetime.utcnow().isoformat() + "Z"
            _save(data)
            print(f"🛠️ Updated {inc['id']}")
            return
    print(f"No incident with id {args.id} found.")

def export_csv(args):
    data = _load()
    if not data:
        print("No data to export.")
        return
    path = args.output or "incidents_export.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id","title","category","severity","phase","status",
            "reported_at","updated_at","owner","notes"
        ])
        writer.writeheader()
        for inc in data:
            writer.writerow(inc)
    print(f"📤 Exported {len(data)} incidents to {path}")

def stats(args):
    data = _load()
    if not data:
        print("No incidents yet.")
        return
    from collections import Counter
    by_sev = Counter([d["severity"] for d in data])
    by_phase = Counter([d["phase"] for d in data])
    by_status = Counter([d["status"] for d in data])

    print("== Severity ==")
    for k,v in by_sev.items():
        print(f"- {k}: {v}")
    print("\n== Phase (NIST 800-61 aligned) ==")
    for k,v in by_phase.items():
        print(f"- {k}: {v}")
    print("\n== Status ==")
    for k,v in by_status.items():
        print(f"- {k}: {v}")

def seed(args):
    """Optional: load sample incidents from sample_data.json"""
    if not os.path.exists("sample_data.json"):
        print("sample_data.json not found.")
        return
    with open("sample_data.json","r",encoding="utf-8") as f:
        sample = json.load(f)
    _save(sample)
    print(f"🌱 Seeded {len(sample)} incidents into {STORE}")

def main():
    p = argparse.ArgumentParser(
        description="Mini Incident Response Tracker (NIST 800-61 flavored)")
    sub = p.add_subparsers(dest="cmd")

    sp = sub.add_parser("init", help="Initialize empty incident store")
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=init_store)

    sp = sub.add_parser("add", help="Add a new incident")
    sp.add_argument("title")
    sp.add_argument("--category", required=True, help="e.g. phishing, malware, access, data_loss")
    sp.add_argument("--severity", required=True, choices=SEVERITIES)
    sp.add_argument("--phase", required=True, choices=NIST_PHASES)
    sp.add_argument("--owner", help="Person/team handling it")
    sp.add_argument("--notes", help="Freeform notes")
    sp.set_defaults(func=add_incident)

    sp = sub.add_parser("list", help="List incidents (filterable)")
    sp.add_argument("--severity", choices=SEVERITIES)
    sp.add_argument("--phase", choices=NIST_PHASES)
    sp.add_argument("--status", choices=STATUSES)
    sp.add_argument("--owner")
    sp.set_defaults(func=list_incidents)

    sp = sub.add_parser("update", help="Update an incident by id")
    sp.add_argument("id")
    sp.add_argument("--status", choices=STATUSES)
    sp.add_argument("--phase", choices=NIST_PHASES)
    sp.add_argument("--owner")
    sp.add_argument("--notes")
    sp.set_defaults(func=update_incident)

    sp = sub.add_parser("export", help="Export all incidents to CSV")
    sp.add_argument("--output", help="Filename (default incidents_export.csv)")
    sp.set_defaults(func=export_csv)

    sp = sub.add_parser("stats", help="Quick counts by severity/phase/status")
    sp.set_defaults(func=stats)

    sp = sub.add_parser("seed", help="Load sample_data.json into store")
    sp.set_defaults(func=seed)

    args = p.parse_args()
    if not hasattr(args, "func"):
        p.print_help()
        return
    args.func(args)

if __name__ == "__main__":
    main()
