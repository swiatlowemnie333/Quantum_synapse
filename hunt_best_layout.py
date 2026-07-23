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

# Ten sam obwód co dał 87.5%
qc = QuantumCircuit(n, n)
qc.h(mid - 1); qc.h(mid)
for i in range(mid - 1, 0, -1): qc.cz(i, i - 1)
for i in range(mid, n - 1):     qc.cz(i, i + 1)
qc.z(0); qc.z(n - 1)
for i in range(0, mid - 1):     qc.cz(i, i + 1)
for i in range(n - 1, mid, -1): qc.cz(i, i - 1)
qc.measure(range(n), range(n))

props = backend.properties()

best_seed = None
best_score = 999
best_layout = None
best_depth = 999

print("=" * 70)
print("ZAZUL WORLD STS | HUNT BEST LAYOUT | 50 seedów")
print("=" * 70)

for seed in range(50):
    try:
        qc_t = transpile(qc, backend, optimization_level=3, seed_transpiler=seed, layout_method='sabre')
        layout = qc_t.layout
        if not layout or not layout.initial_layout:
            continue
        
        used = [int(layout.initial_layout[i]) for i in range(n)]
        readouts = []
        t1s = []
        for q in used:
            qubit_props = props.qubits[q]
            readout = next((p.value for p in qubit_props if p.name == 'readout_error'), 0.01)
            t1 = next((p.value for p in qubit_props if p.name == 'T1'), 100)
            readouts.append(readout)
            t1s.append(t1)
        
        avg_r = sum(readouts) / len(readouts)
        max_r = max(readouts)
        min_t1 = min(t1s)
        depth = qc_t.depth()
        # Score: karujemy za wysoki readout i niski T1
        score = avg_r * 10 + max_r * 5 + (100/min_t1 if min_t1 > 0 else 999)
        
        if score < best_score:
            best_score = score
            best_seed = seed
            best_layout = used
            best_depth = depth
            print(f"  🎯 NEW BEST seed={seed}: avg_readout={avg_r:.4f}, max={max_r:.4f}, min_T1={min_t1:.0f}μs, depth={depth}, score={score:.2f}")
    except Exception as e:
        continue

print(f"\n{'='*70}")
print(f"🏆 NAJLEPSZY SEED: {best_seed}")
print(f"   Layout: {best_layout}")
print(f"   Głębokość: {best_depth}")
print(f"   Score: {best_score:.2f}")
print(f"{'='*70}")

# Puszczamy z najlepszym layoutem
qc_best = transpile(qc, backend, optimization_level=3, seed_transpiler=best_seed, layout_method='sabre')
print(f"\nTranspilacja z seed={best_seed}...")
print(f"Głębokość: {qc_best.depth()}")

sampler = SamplerV2(backend)
job = sampler.run([(qc_best, None, 8192)])
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
    print("ZAZUL WORLD STS | HUNT BEST LAYOUT | WYNIK")
    print("=" * 60)
    print(f"Echo |0...0>: {echo}/{total} = {pct:.1f}%")
    print(f"Poprzedni rekord: 87.5%")
    print(f"Zmiana: {pct - 87.5:+.1f}%")
    
    if pct > 87.5:
        print(f"\n🔥 POBITY REKORD! Zapisuję...")
        with open('rekord_layout.txt', 'w') as f:
            f.write(f"seed={best_seed}\nlayout={best_layout}\nwynik={pct:.1f}%\n")
    
    top = sorted(counts.items(), key=lambda x: -x[1])[:5]
    print("\nTop 5:")
    for state, count in top:
        print(f"  {state}: {count} ({count/total*100:.1f}%)")
    print("=" * 60)
