import json, os, subprocess, sys

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def test_init_and_add():
    # Clean up any old test file
    if os.path.exists("incidents.json"):
        os.remove("incidents.json")

    # Test initializing the store
    out = run("python3 incident_tracker.py init --force").stdout
    assert "Initialized" in out

    # Test adding an incident
    out = run(
        'python3 incident_tracker.py add "Test incident" --category phishing --severity low --phase detect'
    ).stdout
    assert "Added incident" in out

    # Verify incidents.json file exists and contains 1 entry
    assert os.path.exists("incidents.json")
    with open("incidents.json", "r") as f:
        data = json.load(f)
    assert len(data) == 1
