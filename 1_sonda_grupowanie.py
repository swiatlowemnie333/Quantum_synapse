import os
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
import time
import json

service = QiskitRuntimeService(
    channel='ibm_quantum_platform',
    token=os.getenv('IBM_QUANTUM_API_KEY')
)

try:
    backend = service.backend('ibm_heron')
except:
    backend = service.backend('ibm_marrakesh')

print(f"Backend: {backend.name}")

n = 32
mid = n // 2

# Fala równoległa od środka
qc = QuantumCircuit(n, n)
qc.h(mid - 1)
qc.h(mid)

for i in range(mid - 1, 0, -1):
    qc.cz(i, i - 1)
for i in range(mid, n - 1):
    qc.cz(i, i + 1)

qc.z(0)
qc.z(n - 1)

for i in range(0, mid - 1):
    qc.cz(i, i + 1)
for i in range(n - 1, mid, -1):
    qc.cz(i, i - 1)

qc.h(mid - 1)
qc.h(mid)

for i in range(n):
    qc.measure(i, i)

# TRANSPILACJA pod backend
print("Transpilacja...")
qc_t = transpile(qc, backend, optimization_level=3)

print(f"\n=== SONDA 32q ===")
print(f"Głębokość: {qc_t.depth()}")
print(f"CZ: {qc_t.count_ops().get('cz', 0)}")

sampler = SamplerV2(mode=backend)
job = sampler.run([(qc_t, None, 8192)])
print(f"Job ID: {job.job_id()}")

while job.status() not in ['DONE', 'ERROR']:
    time.sleep(10)
    print(f"  Status: {job.status()}")

if job.status() == 'ERROR':
    print("FAILED!")
    exit(1)

result = job.result()
counts = result[0].data.meas.get_counts()
total = sum(counts.values())

print(f"\n=== GRUPOWANIE AUTO ===")
print("qubit | P(|0>) | kolor    | klasa      | numer | rz_boost")
print("-" * 60)

cechy = {}
for q in range(n):
    p0 = sum(c for s, c in counts.items() if s[n-1-q] == '0') / total
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
print("\nTeraz wklej drugi skrypt (2_echo_synestezja.py) żeby puścić echo z boostami!")
