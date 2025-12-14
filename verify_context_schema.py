import json
import os
import glob

files = glob.glob('context_cache/*.json')
if not files:
    print("No files found!")
    exit(1)

# Pick a file that likely has stats (not the first one)
f = files[-1]

try:
    data = json.load(open(f))
    print(f"Checking {f}")
    print(json.dumps(data, indent=2))

    expected = ['game_id', 'is_playoff', 'home_record', 'visitor_record', 'narrative_notes']
    missing = [k for k in expected if k not in data]
    if missing:
        print(f"FAIL: Missing keys {missing}")
    else:
        print("PASS: Top-level keys present")

    if 'regular' not in data['home_record']:
        print("FAIL: Missing home_record.regular")
    else:
        print("PASS: Nested record structure valid")

except Exception as e:
    print(f"ERROR: {e}")
