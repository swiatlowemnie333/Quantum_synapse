import os
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
import time

service = QiskitRuntimeService(
    channel='ibm_quantum_platform',
    token=os.getenv('IBM_QUANTUM_API_KEY')
)

try:
    backend = service.backend('ibm_heron')
except:
    backend = service.backend('ibm_marrakesh')

print(f"Backend: {backend.name}")

# DWIE OSOBNE fizyczne linie na Marrakesh (bez wspólnych qubitów!)
# Linia 1: od 0 do 61 (16 qubitów)
# Linia 2: od 13 do 77 (16 qubitów)
linia1 = [0, 1, 2, 3, 16, 23, 22, 21, 36, 41, 42, 43, 56, 63, 62, 61]
linia2 = [13, 12, 11, 18, 31, 30, 29, 38, 49, 48, 47, 57, 67, 66, 65, 77]

n = 32  # 16 + 16

qc = QuantumCircuit(n, n)

print(f"\n=== 2 FIZYCZNE LINIE 16+16q MARRAKESH ===")
print(f"Linia 1: {linia1}")
print(f"Linia 2: {linia2}")

mid1 = len(linia1) // 2  # 8
mid2 = len(linia2) // 2  # 8

# START: H na środkowych qubitach każdej linii
qc.h(mid1 - 1)   # q7 (linia1[7] = 21)
qc.h(mid1)       # q8 (linia1[8] = 36)
qc.h(mid1 + mid2 - 1)  # q15 (linia2[7] = 47)
qc.h(mid1 + mid2)      # q16 (linia2[8] = 57)

# LEWA fala linia 1: od środka do brzegu (q0)
for i in range(mid1 - 1, 0, -1):
    qc.cz(i, i - 1)

# PRAWA fala linia 1: od środka do brzegu (q15)
for i in range(mid1, len(linia1) - 1):
    qc.cz(i, i + 1)

# LEWA fala linia 2: od środka do brzegu (q16)
for i in range(mid1 + mid2 - 1, mid1, -1):
    qc.cz(i, i - 1)

# PRAWA fala linia 2: od środka do brzegu (q31)
for i in range(mid1 + mid2, n - 1):
    qc.cz(i, i + 1)

# Odbicie na brzegach każdej linii
qc.z(0)
qc.z(len(linia1) - 1)
qc.z(len(linia1))
qc.z(n - 1)

# Powrót LEWA linia 1
for i in range(0, mid1 - 1):
    qc.cz(i, i + 1)

# Powrót PRAWA linia 1
for i in range(len(linia1) - 1, mid1, -1):
    qc.cz(i, i - 1)

# Powrót LEWA linia 2
for i in range(mid1, mid1 + mid2 - 1):
    qc.cz(i, i + 1)

# Powrót PRAWA linia 2
for i in range(n - 1, mid1 + mid2, -1):
    qc.cz(i, i - 1)

# Zamknięcie
qc.h(mid1 - 1)
qc.h(mid1)
qc.h(mid1 + mid2 - 1)
qc.h(mid1 + mid2)

# Pomiar
for i in range(n):
    qc.measure(i, i)

qc_t = transpile(qc, backend, optimization_level=3)

print(f"Głębokość: {qc_t.depth()}")
print(f"CZ: {qc_t.count_ops().get('cz', 0)}")

sampler = SamplerV2(mode=backend)
job = sampler.run([(qc_t, None, 8192)])
print(f"\nJob ID: {job.job_id()}")

print("Czekam na wynik...")
while job.status() not in ['DONE', 'ERROR']:
    time.sleep(10)
    print(f"  Status: {job.status()}")

if job.status() == 'ERROR':
    print("FAILED!")
    exit(1)

result = job.result()
counts = result[0].data.c.get_counts()
total = sum(counts.values())
zero = counts.get('0' * n, 0)

print(f"\n{'=' * 60}")
print(f"2 FIZYCZNE LINIE 16+16q MARRAKESH")
print(f"{'=' * 60}")
print(f"Echo |0...0>: {zero}/{total} = {zero/total*100:.1f}%")

print(f"\nPorównanie:")
print(f"  1 fizyczna linia 33q: 86.1%")
print(f"  2 logiczne linie 32q: 87.5%")
print(f"  2 fizyczne linie 32q: {zero/total*100:.1f}%")

if zero/total > 0.875:
    print(f"\n🎉 FIZYCZNE 2 LINIE REKORD! +{zero/total*100 - 87.5:.1f}%!")
elif zero/total > 0.86:
    print(f"\n✅ Dobry wynik, blisko rekordu.")
else:
    print(f"\n❌ Spadek. 2 logiczne linie 87.5% to nadal najlepszy.")

print(f"\nTop 5:")
for st, cnt in sorted(counts.items(), key=lambda x: -x[1])[:5]:
    print(f"  {st}: {cnt} ({cnt/total*100:.1f}%)")
