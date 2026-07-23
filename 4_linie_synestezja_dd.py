import os
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2, SamplerOptions
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

# 4 linie po 8 qubitów
lines = [
    list(range(0, 8)),      # 0,1,2,3,4,5,6,7
    list(range(8, 16)),     # 8,9,10,11,12,13,14,15
    list(range(16, 24)),    # 16,17,18,19,20,21,22,23
    list(range(24, 32))     # 24,25,26,27,28,29,30,31
]

centers = [(3,4), (11,12), (19,20), (27,28)]

qc = QuantumCircuit(32, 32)

print(f"\n=== 4 LINIE + SYNESTEZJA + DD 32q ===")

# START: H na środkowych qubitach każdej linii
for c1, c2 in centers:
    qc.h(c1)
    qc.h(c2)

# FALE w każdej linii (lewo i prawo od środka)
for line in lines:
    mid = len(line) // 2
    for i in range(mid - 1, 0, -1):
        qc.cz(line[i], line[i-1])
    for i in range(mid, len(line) - 1):
        qc.cz(line[i], line[i+1])

# SYNESTEZJA: Krzyżowe CZ między liniami (synchronizacja fal)
qc.cz(4, 11)   # linia 1 <-> linia 2
qc.cz(12, 19)  # linia 2 <-> linia 3
qc.cz(20, 27)  # linia 3 <-> linia 4

# Odbicie na brzegach każdej linii
for line in lines:
    qc.z(line[0])
    qc.z(line[-1])

# Powrót LEWA w każdej linii
for line in lines:
    mid = len(line) // 2
    for i in range(0, mid - 1):
        qc.cz(line[i], line[i+1])

# Powrót PRAWA w każdej linii
for line in lines:
    mid = len(line) // 2
    for i in range(len(line) - 1, mid, -1):
        qc.cz(line[i], line[i-1])

# SYNESTEZJA: Krzyżowe CZ na końcu (zamknięcie synchronizacji)
qc.cz(4, 11)
qc.cz(12, 19)
qc.cz(20, 27)

# Zamknięcie
for c1, c2 in centers:
    qc.h(c1)
    qc.h(c2)

# Pomiar
for i in range(32):
    qc.measure(i, i)

# Transpilacja
qc_t = transpile(qc, backend, optimization_level=3)

print(f"Głębokość: {qc_t.depth()}")
print(f"CZ: {qc_t.count_ops().get('cz', 0)}")

# DD + Synestezja
options = SamplerOptions()
options.dynamical_decoupling.enable = True
options.dynamical_decoupling.sequence_type = "XpXm"

sampler = SamplerV2(mode=backend, options=options)
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
zero = counts.get('0' * 32, 0)

print(f"\n{'=' * 60}")
print(f"4 LINIE + SYNESTEZJA + DD 32q")
print(f"{'=' * 60}")
print(f"Echo |0...0>: {zero}/{total} = {zero/total*100:.1f}%")

print(f"\nPorównanie:")
print(f"  2 linie (czysta): 87.5%")
print(f"  2 linie + DD:     87.2%")
print(f"  4 linie + synestezja + DD: {zero/total*100:.1f}%")

if zero/total > 0.875:
    print(f"\n🎉 4 LINIE Z SYNESTEZJĄ DZIAŁAJĄ! +{zero/total*100 - 87.5:.1f}%!")
else:
    print(f"\n❌ Spadek. 2 linie 87.5% to nadal najlepszy wynik.")

print(f"\nTop 5:")
for st, cnt in sorted(counts.items(), key=lambda x: -x[1])[:5]:
    print(f"  {st}: {cnt} ({cnt/total*100:.1f}%)")

print(f"\n{'=' * 60}")
print(f"REKORDY ZAZUL WORLD STS:")
print(f"  6q:   95.0%")
print(f"  16q:  94.2%")
print(f"  32q:  87.5% (2 linie, czysta)")
print(f"  32q:  87.2% (2 linie + DD)")
print(f"  32q:  {zero/total*100:.1f}% (4 linie + synestezja + DD)")
print(f"{'=' * 60}")
