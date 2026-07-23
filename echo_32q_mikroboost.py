import os, json
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
import time

service = QiskitRuntimeService(
    channel='ibm_quantum_platform',
    token=os.getenv('IBM_QUANTUM_API_KEY')
)
backend = service.backend('ibm_marrakesh')

# Wczytaj boosty z mapy 87.5%
with open('boosty_mikro.json', 'r') as f:
    boosty = json.load(f)

n = 32
mid = n // 2

# TEN SAM obwód co dał 87.5% (dwie linie, fala od środka)
qc = QuantumCircuit(n, n)

# START: H na środkowych qubitach (dwie linie równoległe)
qc.h(mid - 1)
qc.h(mid)

# FALA WYCHODZĄCA: od środka do brzegów
# Lewa: q15 -> q14 -> ... -> q0
for i in range(mid - 1, 0, -1):
    qc.cz(i, i - 1)
# Prawa: q16 -> q17 -> ... -> q31
for i in range(mid, n - 1):
    qc.cz(i, i + 1)

# ODBICIE na brzegach
qc.z(0)
qc.z(n - 1)

# FALA WRACAJĄCA: od brzegów do środka
# Lewa: q0 -> q1 -> ... -> q15
for i in range(0, mid - 1):
    qc.cz(i, i + 1)
# Prawa: q31 -> q30 -> ... -> q16
for i in range(n - 1, mid, -1):
    qc.cz(i, i - 1)

# MIKRO-BOOSTY RZ: dopiero po fali, przed pomiarem
# Dokręcamy fazę słabym qubitom żeby wskoczyły na 1.0
print("=== Mikro-boosty RZ (po fali, przed pomiarem) ===")
boost_count = 0
for i in range(n):
    rz_val = boosty.get(str(i), 0.0)
    if rz_val > 0:
        qc.rz(rz_val, i)
        print(f"  q{i:2d}: RZ({rz_val:+.5f})")
        boost_count += 1
print(f"Liczba boostów: {boost_count}")

qc.measure(range(n), range(n))

# Transpilacja
print("\nTranspilacja...")
qc_t = transpile(qc, backend, optimization_level=3)
print(f"Głębokość: {qc_t.depth()}")

# Job na IBM
sampler = SamplerV2(backend)
job = sampler.run([(qc_t, None, 8192)])
print(f"Job ID: {job.job_id()}")

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
    print("ZAZUL WORLD STS | ECHO 32q + MIKRO-BOOST")
    print("=" * 60)
    print(f"Echo |0...0>: {echo}/{total} = {pct:.1f}%")
    print(f"Poprzedni rekord: 87.5%")
    print(f"Zmiana: {pct - 87.5:+.1f}%")
    
    if pct > 87.5:
        print(f"\n🔥🔥🔥 REKORD POBITY! 🔥🔥🔥")
        with open('rekord_mikroboost.txt', 'w') as f:
            f.write(f"wynik={pct:.1f}%\njob={job.job_id()}\n")
    
    top = sorted(counts.items(), key=lambda x: -x[1])[:5]
    print("\nTop 5:")
    for state, count in top:
        print(f"  {state}: {count} ({count/total*100:.1f}%)")
    print("=" * 60)
