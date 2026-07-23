import os
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import Layout
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

# Szukamy 2 ROZŁĄCZNYCH fizycznych linii po 16 qubitów
from collections import defaultdict
cm = backend.configuration().coupling_map
neighbors = defaultdict(list)
for a, b in cm:
    neighbors[a].append(b)

props = backend.properties()

def find_all_lines():
    """Znajdź wszystkie linie >= 16 qubitów"""
    all_lines = []
    for start in range(backend.num_qubits):
        for first_step in neighbors[start]:
            line = [start, first_step]
            visited = {start, first_step}
            current = first_step
            while True:
                next_nodes = [n for n in neighbors[current] if n not in visited]
                if not next_nodes:
                    break
                # Wybierz ten z najniższym readout
                best = min(next_nodes, key=lambda q: next((p.value for p in props.qubits[q] if p.name == 'readout_error'), 0.02))
                line.append(best)
                visited.add(best)
                current = best
            if len(line) >= 16:
                all_lines.append(line)
    return all_lines

print("Szukam wszystkich linii 16-qubitowych...")
all_lines = find_all_lines()
print(f"Znaleziono {len(all_lines)} linii")

# Znajdź 2 ROZŁĄCZNE linie z najniższym readout
best_pair = None
best_score = 999

for i, line1 in enumerate(all_lines):
    for j, line2 in enumerate(all_lines):
        if i >= j:
            continue
        # Sprawdź czy rozłączne
        if set(line1[:16]) & set(line2[:16]):
            continue  # mają wspólne qubity
        
        # Średni readout
        r1 = sum(next((p.value for p in props.qubits[q] if p.name == 'readout_error'), 0.02) for q in line1[:16]) / 16
        r2 = sum(next((p.value for p in props.qubits[q] if p.name == 'readout_error'), 0.02) for q in line2[:16]) / 16
        score = r1 + r2
        
        if score < best_score:
            best_score = score
            best_pair = (line1[:16], line2[:16])

if not best_pair:
    print("Nie znaleziono 2 rozłącznych linii!")
    exit(1)

line1, line2 = best_pair
print(f"\n=== 2 ROZŁĄCZNE LINIE ===")
print(f"Linia 1 (lewa):  {line1}")
print(f"Linia 2 (prawa): {line2}")

# Wymuś layout jako lista intów
initial_layout = line1 + line2
print(f"\nLayout: {initial_layout}")

qc_t = transpile(qc, backend, 
    initial_layout=initial_layout,
    optimization_level=3
)
print(f"Głębokość po transpilacji: {qc_t.depth()}")

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
    print("ZAZUL WORLD STS | 2 FIZYCZNE LINIE")
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
