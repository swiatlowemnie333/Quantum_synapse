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

# Obwód identyczny jak rekordowy
qc = QuantumCircuit(n, n)
qc.h(mid - 1)
qc.h(mid)
for i in range(mid - 1, 0, -1): qc.cz(i, i - 1)
for i in range(mid, n - 1):     qc.cz(i, i + 1)
qc.z(0)
qc.z(n - 1)
for i in range(0, mid - 1):     qc.cz(i, i + 1)
for i in range(n - 1, mid, -1): qc.cz(i, i - 1)
qc.measure(range(n), range(n))

props = backend.properties()

print("=" * 70)
print("ZAZUL WORLD STS | HUNT BEST SEED | 50 prób offline")
print("=" * 70)

best_seed = None
best_score = 999
best_depth = 999
best_layout = None

for seed in range(50):
    try:
        qc_t = transpile(qc, backend, optimization_level=3, seed_transpiler=seed)
        depth = qc_t.depth()
        
        if depth > 5:  # Za dużo SWAPów, odrzucamy
            continue
        
        # Wyciągnij użyte fizyczne qubity
        layout = qc_t.layout
        if not layout or not layout.initial_layout:
            continue
        
        mapping = layout.initial_layout.get_virtual_bits()
        used = []
        for i in range(n):
            phys = mapping.get(qc.qubits[i], None)
            if phys is None:
                break
            used.append(int(phys))
        
        if len(used) != n:
            continue
        
        # Oblicz readout error i T1
        readouts = []
        t1s = []
        for q in used:
            qubit_props = props.qubits[q]
            r = next((p.value for p in qubit_props if p.name == 'readout_error'), 0.02)
            t1 = next((p.value for p in qubit_props if p.name == 'T1'), 100)
            readouts.append(r)
            t1s.append(t1)
        
        avg_r = sum(readouts) / n
        max_r = max(readouts)
        min_t1 = min(t1s)
        
        # Score: niższy = lepszy. Kara za wysoki readout i niski T1
        score = avg_r * 100 + max_r * 50 + (100 / min_t1 if min_t1 > 0 else 999)
        
        if score < best_score:
            best_score = score
            best_seed = seed
            best_depth = depth
            best_layout = used
            print(f"  🎯 NEW BEST seed={seed}: depth={depth}, avg_readout={avg_r:.4f}, max={max_r:.4f}, min_T1={min_t1:.0f}μs, score={score:.2f}")
            print(f"      Layout: {used}")
        
    except Exception as e:
        continue

if not best_seed:
    print("Nie znaleziono dobrego seeda!")
    exit(1)

print(f"\n{'='*70}")
print(f"🏆 NAJLEPSZY SEED: {best_seed}")
print(f"   Layout: {best_layout}")
print(f"   Głębokość: {best_depth}")
print(f"   Score: {best_score:.2f}")
print(f"{'='*70}")

# Puszczamy z najlepszym seedem
qc_best = transpile(qc, backend, optimization_level=3, seed_transpiler=best_seed)
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
    print("ZAZUL WORLD STS | HUNT BEST SEED | WYNIK")
    print("=" * 60)
    print(f"Echo |0...0>: {echo}/{total} = {pct:.1f}%")
    print(f"Rekord: 87.5%")
    print(f"Zmiana: {pct - 87.5:+.1f}%")
    
    if pct > 87.5:
        print(f"\n🔥🔥🔥 REKORD POBITY! 🔥🔥🔥")
        with open('rekord_hunt.txt', 'w') as f:
            f.write(f"seed={best_seed}\nlayout={best_layout}\nwynik={pct:.1f}%\njob={job.job_id()}\n")
    
    top = sorted(counts.items(), key=lambda x: -x[1])[:5]
    print("\nTop 5:")
    for state, count in top:
        print(f"  {state}: {count} ({count/total*100:.1f}%)")
    print("=" * 60)
