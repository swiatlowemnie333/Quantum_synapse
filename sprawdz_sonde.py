import os
from qiskit_ibm_runtime import QiskitRuntimeService
import time

service = QiskitRuntimeService(
    channel='ibm_quantum_platform',
    token=os.getenv('IBM_QUANTUM_API_KEY')
)

job_id = "d8r9jl6ab0ds73drdnig"

print(f"=== Sprawdzam sondę {job_id} ===")

job = service.job(job_id)
print(f"Status: {job.status()}")

while job.status() not in ['DONE', 'ERROR']:
    time.sleep(15)
    job = service.job(job_id)
    print(f"Status: {job.status()}")

if job.status() == 'ERROR':
    print("FAILED!")
    exit(1)

result = job.result()
pub = result[0]
counts = pub.data.meas.get_counts()
total = sum(counts.values())

print(f"\n=== WYNIKI SONDOVANIA 32q ===")
print(f"Total shots: {total}")
print(f"Unique states: {len(counts)}")

top = sorted(counts.items(), key=lambda x: -x[1])[:5]
print("\nTop 5:")
for state, count in top:
    print(f"  {state}: {count} ({count/total*100:.1f}%)")

print("\n=== GRUPOWANIE AUTO ===")
print("qubit | P(|0>) | kolor    | klasa      | numer | rz_boost")
print("-" * 60)

import json
cechy = {}
for q in range(32):
    p0 = sum(c for s, c in counts.items() if s[31-q] == '0') / total
    if p0 >= 0.99:
        kolor, klasa, rz = "ZIELONY", "MOCNY", 0.0
    elif p0 >= 0.97:
        kolor, klasa, rz = "ZOLTY", "SREDNI", 0.005
    else:
        kolor, klasa, rz = "CZERWONY", "SLABY", 0.015
    
    cechy[q] = {
        "numer": q,
        "kolor": kolor,
        "klasa": klasa,
        "p0": round(p0, 4),
        "rz_boost": rz
    }
    bar = '█' * int(p0 * 10) + '░' * (10 - int(p0 * 10))
    print(f"  q{q:2d}  | {p0:.2f}   | {kolor:8s} | {klasa:10s} | {q:5d} | {rz:.3f}")

with open('cechy_32q.json', 'w') as f:
    json.dump(cechy, f, indent=2)

print("\n=== STATYSTYKI ===")
for k in ["ZIELONY", "ZOLTY", "CZERWONY"]:
    ile = len([q for q, c in cechy.items() if c["kolor"] == k])
    print(f"  {k}: {ile} qubitów")

print("\n✅ Zapisano: cechy_32q.json")
print("\nTeraz wklej: python3 2_echo_synestezja.py")
