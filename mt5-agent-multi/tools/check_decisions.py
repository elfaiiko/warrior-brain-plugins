"""Controlla che l'ultimo giro in decisions.jsonl abbia una riga per ciascun simbolo.

Uso:  python check_decisions.py C:\\n8n\\mt5-agent-bot\\decisions.jsonl
Exit code 0 = tutti e 5 presenti, 1 = mancano simboli o formato vecchio.
"""
import json
import sys

WANTED = {"XAUUSD", "EURUSD", "GBPUSD", "BTCUSD", "ETHUSD"}

rows = []
with open(sys.argv[1], encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass

with_run = [r for r in rows if r.get("run_id")]
if not with_run:
    raise SystemExit("Nessuna riga con run_id: il giro di prova non usa ancora il nuovo formato.")

last_run = with_run[-1]["run_id"]
seen = {r.get("symbol") for r in with_run if r["run_id"] == last_run}
print(f"Ultimo run_id: {last_run}")
for r in (r for r in with_run if r["run_id"] == last_run):
    print(f"  {r.get('symbol'):8} {r.get('decision'):6} price={r.get('price')}  {r.get('reason')}")

missing = WANTED - seen
extra = seen - WANTED
if missing:
    print(f"MANCANO: {sorted(missing)}")
if extra:
    print(f"SIMBOLI NON PREVISTI: {sorted(extra)}")
sys.exit(1 if missing or extra else 0)
