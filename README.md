# 🛡️ Mini Incident Response Tracker (NIST 800-61)

A zero-dependency, command-line tool to log incidents, track phases, export reports, and produce quick GRC-friendly stats.

## ✅ Why this exists
- Shows practical **GRC + Incident Response** skills (NIST SP 800-61).
- Lightweight portfolio piece: pure Python, no database required.
- Useful starter for small orgs / labs.

## 🔧 Install & Run
```bash
git clone https://github.com/YOUR-USERNAME/incident-response-tracker.git
cd incident-response-tracker
python3 incident_tracker.py init

➕ Add an incident
python3 incident_tracker.py add "Phishing email reported" \
  --category phishing --severity medium --phase detect --owner "SOC Tier 1" \
  --notes "User forwarded suspicious O365 login page."

📋 List (with filters)
python3 incident_tracker.py list
python3 incident_tracker.py list --phase respond
python3 incident_tracker.py list --severity high --status in_progress

🛠 Update
python3 incident_tracker.py update <ID_FROM_LIST> --status contained --phase respond --notes "Blocked domain; reset user creds."

📤 Export CSV
python3 incident_tracker.py export --output incidents_YYYYMM.csv

📈 Stats
python3 incident_tracker.py stats

🌱 Seed sample data (optional)
python3 incident_tracker.py seed
