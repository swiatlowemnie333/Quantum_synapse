import os
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService

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

qc = QuantumCircuit(n, n)

# Dwie linie równoległe w środku
qc.h(mid - 1)
qc.h(mid)

# LEWA fala: od środka do brzegu
for i in range(mid - 1, 0, -1):
    qc.cz(i, i - 1)

# PRAWA fala: od środka do brzegu
for i in range(mid, n - 1):
    qc.cz(i, i + 1)

# Odbicie na brzegach
qc.z(0)
qc.z(n - 1)

# Powrót LEWA: od brzegu do środka
for i in range(0, mid - 1):
    qc.cz(i, i + 1)

# Powrót PRAWA: od brzegu do środka
for i in range(n - 1, mid, -1):
    qc.cz(i, i - 1)

# Zamknięcie
qc.h(mid - 1)
qc.h(mid)

# Pomiar
for i in range(n):
    qc.measure(i, i)

qc_t = transpile(qc, backend, optimization_level=3)

print(f"\n=== SONDA 32q ===")
print(f"Głębokość: {qc_t.depth()}")
print(f"CZ bramek: {qc_t.count_ops().get('cz', 0)}")

job = backend.run(qc_t, shots=8192)
print(f"\nJob ID: {job.job_id()}")
print("Czekam na wynik...")

import time
while job.status() not in ['DONE', 'ERROR']:
    time.sleep(10)
    print(f"  Status: {job.status()}")

if job.status() == 'ERROR':
    print("FAILED!")
    exit(1)

result = job.result()
counts = result.get_counts()
total = sum(counts.values())

print(f"\n=== MAPA KUBITÓW 32q ===")
print(f"Total shots: {total}")
print(f"Unique states: {len(counts)}")

top = sorted(counts.items(), key=lambda x: -x[1])[:5]
print("\nTop 5:")
for state, count in top:
    print(f"  {state}: {count} ({count/total*100:.1f}%)")

print("\nMarginal P(|0>) per qubit:")
with open('mapa_32q.txt', 'w') as f:
    for q in range(n):
        p0 = sum(c for s, c in counts.items() if s[n-1-q] == '0') / total
        bar = '█' * int(p0 * 10) + '░' * (10 - int(p0 * 10))
        if p0 >= 0.99:
            kolor = "ZIELONY"
        elif p0 >= 0.97:
            kolor = "ZOLTY"
        else:
            kolor = "CZERWONY"
        print(f"  q{q:2d}: {p0:.2f} {bar} {kolor}")
        f.write(f"q{q}: {p0:.4f} -> {kolor}\n")

print("\n✅ Zapisano: mapa_32q.txt")
print("\nPowiedz mi które qubity są słabe — przygotuję echo z synestezją!")
