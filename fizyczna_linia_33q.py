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

# PRAWDZIWA fizyczna linia 33-qubitowa na Marrakesh
# Od wspólnego końca (140) do przeciwnego (0)
linia = [0, 1, 2, 3, 16, 23, 22, 21, 36, 41, 42, 43, 56, 63, 62, 61, 76, 81, 82, 83, 96, 103, 102, 101, 116, 121, 122, 123, 136, 143, 142, 141, 140]

n = len(linia)
mid = n // 2  # 16

qc = QuantumCircuit(n, n)

print(f"\n=== FIZYCZNA LINIA 33q MARRAKESH ===")
print(f"Fala od wspólnego końca (140) do przeciwnego (0)")
print(f"Qubity: {linia}")

# START: H na środkowych qubitach fizycznej linii
qc.h(mid - 1)
qc.h(mid)

# LEWA fala: od środka do wspólnego końca (140)
for i in range(mid - 1, 0, -1):
    qc.cz(i, i - 1)

# PRAWA fala: od środka do przeciwnego końca (0)
for i in range(mid, n - 1):
    qc.cz(i, i + 1)

# Odbicie na brzegach
qc.z(0)
qc.z(n - 1)

# Powrót LEWA
for i in range(0, mid - 1):
    qc.cz(i, i + 1)

# Powrót PRAWA
for i in range(n - 1, mid, -1):
    qc.cz(i, i - 1)

# Zamknięcie
qc.h(mid - 1)
qc.h(mid)

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
print(f"FIZYCZNA LINIA 33q MARRAKESH")
print(f"{'=' * 60}")
print(f"Echo |0...0>: {zero}/{total} = {zero/total*100:.1f}%")

print(f"\nPorównanie:")
print(f"  Logiczna 32q (transpilator mapuje): 87.5%")
print(f"  Fizyczna 33q (własna mapa):         {zero/total*100:.1f}%")

if zero/total > 0.875:
    print(f"\n🎉 FIZYCZNA LINIA LEPIEJ! +{zero/total*100 - 87.5:.1f}%!")
else:
    print(f"\n❌ Spadek. Logiczna 32q 87.5% to nadal najlepszy.")

print(f"\nTop 5:")
for st, cnt in sorted(counts.items(), key=lambda x: -x[1])[:5]:
    print(f"  {st}: {cnt} ({cnt/total*100:.1f}%)")
