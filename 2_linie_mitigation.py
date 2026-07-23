import os
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2, SamplerOptions

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

qc_t = transpile(qc, backend, optimization_level=3)

print(f"\n=== 2 LINIE + MEASURE MITIGATION 32q ===")
print(f"Głębokość: {qc_t.depth()}")

# Mitigation w Qiskit 2.x
options = SamplerOptions()
options.resilience = {"measure_mitigation": True}

sampler = SamplerV2(mode=backend, options=options)
job = sampler.run([(qc_t, None, 8192)])
print(f"Job ID: {job.job_id()}")

import time
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
print(f"2 LINIE + MEASURE MITIGATION 32q")
print(f"{'=' * 60}")
print(f"Echo |0...0>: {zero}/{total} = {zero/total*100:.1f}%")
print(f"\nBez mitigation: 87.5%")
print(f"Z mitigation:   {zero/total*100:.1f}%")

if zero/total > 0.875:
    print(f"\n🎉 MITIGATION DZIAŁA! +{zero/total*100 - 87.5:.1f}%!")
else:
    print(f"\n❌ Spadek. 87.5% bez mitigation to był rekord.")

print(f"\nTop 5:")
for st, cnt in sorted(counts.items(), key=lambda x: -x[1])[:5]:
    print(f"  {st}: {cnt} ({cnt/total*100:.1f}%)")
