import os
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
import time

service = QiskitRuntimeService(
    channel='ibm_quantum_platform',
    token=os.getenv('IBM_QUANTUM_API_KEY')
)
backend = service.backend('ibm_marrakesh')

n = 32
mid = n // 2

# DOKŁADNIE TEN SAM obwód co dał 87.5%
qc = QuantumCircuit(n, n)

# START: dwie linie równoległe w środku
qc.h(mid - 1)
qc.h(mid)

# LEWA fala: od środka (q15) do brzegu (q0)
for i in range(mid - 1, 0, -1):
    qc.cz(i, i - 1)

# PRAWA fala: od środka (q16) do brzegu (q31)
for i in range(mid, n - 1):
    qc.cz(i, i + 1)

# ODBICIE na brzegach
qc.z(0)
qc.z(n - 1)

# LEWA fala wracająca: od brzegu (q0) do środka (q15)
for i in range(0, mid - 1):
    qc.cz(i, i + 1)

# PRAWA fala wracająca: od brzegu (q31) do środka (q16)
for i in range(n - 1, mid, -1):
    qc.cz(i, i - 1)

qc.measure(range(n), range(n))

# Transpilacja
print("Transpilacja...")
qc_t = transpile(qc, backend, optimization_level=3)
print(f"Głębokość: {qc_t.depth()}")

# Mapowanie (poprawione)
layout = qc_t.layout
if layout and layout.initial_layout:
    print("\n=== Mapowanie logiczne -> fizyczne ===")
    mapping = layout.initial_layout.get_virtual_bits()
    for i in range(n):
        phys = mapping.get(qc.qubits[i], '?')
        print(f"  q{i:2d} -> {phys}")

# Job
sampler = SamplerV2(backend)
job = sampler.run([(qc_t, None, 8192)])
print(f"\nJob ID: {job.job_id()}")

print("Czekam na wynik...")
while job.status() not in ['DONE', 'ERROR']:
    time.sleep(15)
    job = service.job(job.job_id())
    print(f"Status: {job.status()}")

if job.status() == 'ERROR':
    print("❌ FAILED!")
else:
    result = job.result()
    counts = result[0].data.c.get_counts()
    total = sum(counts.values())
    echo = counts.get('0'*n, 0)
    pct = echo / total * 100
    
    print("\n" + "=" * 60)
    print("ZAZUL WORLD STS | ECHO 32q CZYSTY")
    print("=" * 60)
    print(f"Echo |0...0>: {echo}/{total} = {pct:.1f}%")
    print(f"Rekord: 87.5%")
    print(f"Różnica: {pct - 87.5:+.1f}%")
    
    top = sorted(counts.items(), key=lambda x: -x[1])[:5]
    print("\nTop 5:")
    for state, count in top:
        print(f"  {state}: {count} ({count/total*100:.1f}%)")
    print("=" * 60)
