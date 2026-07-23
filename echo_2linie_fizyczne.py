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

# TEN SAM obwód co 87.5%
qc = QuantumCircuit(n, n)
qc.h(mid - 1)
qc.h(mid)

# Lewa fala wychodząca: q15 -> q14 -> ... -> q0
for i in range(mid - 1, 0, -1):
    qc.cz(i, i - 1)

# Prawa fala wychodząca: q16 -> q17 -> ... -> q31
for i in range(mid, n - 1):
    qc.cz(i, i + 1)

# Odbicie na brzegach
qc.z(0)
qc.z(n - 1)

# Lewa fala wracająca: q0 -> q1 -> ... -> q15
for i in range(0, mid - 1):
    qc.cz(i, i + 1)

# Prawa fala wracająca: q31 -> q30 -> ... -> q16
for i in range(n - 1, mid, -1):
    qc.cz(i, i - 1)

qc.measure(range(n), range(n))

# DWIE FIZYCZNE LINIE na Marrakesh (z poprzedniej analizy)
# Lewa: 0-1-2-3-16-23-22-21-36-41-42-43-56-63-62-61
# Prawa: 76-81-82-83-96-103-102-101-116-121-122-123-136-143-142-141
linia_lewa = [0, 1, 2, 3, 16, 23, 22, 21, 36, 41, 42, 43, 56, 63, 62, 61]
linia_prawa = [76, 81, 82, 83, 96, 103, 102, 101, 116, 121, 122, 123, 136, 143, 142, 141]

initial_layout = linia_lewa + linia_prawa

print("=" * 70)
print("ZAZUL WORLD STS | 2 FIZYCZNE LINIE RÓWNOLEGŁE")
print("=" * 70)
print(f"Linia lewa (q0-q15):  {linia_lewa}")
print(f"Linia prawa (q16-q31): {linia_prawa}")

# Transpilacja z wymuszonym layoutem
qc_t = transpile(qc, backend, 
    initial_layout=initial_layout,
    optimization_level=3
)

print(f"\nGłębokość: {qc_t.depth()}")

# Sprawdź mapowanie
if qc_t.layout and qc_t.layout.initial_layout:
    print("\n=== Mapowanie ===")
    mapping = qc_t.layout.initial_layout.get_virtual_bits()
    for i in range(32):
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
    print("ZAZUL WORLD STS | 2 FIZYCZNE LINIE | WYNIK")
    print("=" * 60)
    print(f"Echo |0...0>: {echo}/{total} = {pct:.1f}%")
    print(f"Rekord: 87.5%")
    print(f"Zmiana: {pct - 87.5:+.1f}%")
    
    if pct > 87.5:
        print(f"\n🔥🔥🔥 REKORD POBITY! 🔥🔥🔥")
    
    top = sorted(counts.items(), key=lambda x: -x[1])[:5]
    print("\nTop 5:")
    for state, count in top:
        print(f"  {state}: {count} ({count/total*100:.1f}%)")
    print("=" * 60)
