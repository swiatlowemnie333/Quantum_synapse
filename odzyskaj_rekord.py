import os
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
import time

service = QiskitRuntimeService(
    channel='ibm_quantum_platform',
    token=os.getenv('IBM_QUANTUM_API_KEY')
)
backend = service.backend('ibm_marrakesh')

# Pobierz REKORDOWY job i jego layout
rekord_job_id = "d8r9jl6ab0ds73drdnig"
print(f"=== Odzyskuję layout z rekordu {rekord_job_id} ===")

rekord_job = service.job(rekord_job_id)

# Spróbujmy wyciągnąć obwód z joba
try:
    # Qiskit Runtime v2 - circuits() zwraca transpilowane obwody
    circuits = rekord_job.circuits()
    if circuits and len(circuits) > 0:
        qc_rekord = circuits[0]
        print(f"Obwód z joba: {qc_rekord.num_qubits} qubitów, głębokość {qc_rekord.depth()}")
        
        # Wyciągnij layout
        if hasattr(qc_rekord, 'layout') and qc_rekord.layout:
            layout = qc_rekord.layout
            mapping = layout.initial_layout.get_virtual_bits()
            print(f"\n=== REKORDOWE MAPOWANIE ===")
            for i in range(32):
                phys = mapping.get(qc_rekord.qubits[i], '?')
                print(f"  q{i:2d} -> {phys}")
        else:
            print("Brak layoutu w obwodzie z joba")
            qc_rekord = None
    else:
        print("Brak obwodów w jobie")
        qc_rekord = None
except Exception as e:
    print(f"Nie udało się pobrać obwodu: {e}")
    qc_rekord = None

# Jeśli nie da się pobrać, zgadujemy z poprzedniego wyniku
# Z poprzedniego czystego joba widało:
# q0->19, q1->15, q2->14, q3->13, q4->12, q5->11, q6->10, q7->9, q8->8, q9->7, q10->6, q11->5, q12->4, q13->3, q14->2, q15->1
# q16->74, q17->73, q18->72, q19->71, q20->70, q21->69, q22->78, q23->89, q24->90, q25->91, q26->98, q27->111, q28->110, q29->109, q30->118, q31->129

# Ale to był zły layout (21.5%). 
# Rekord 87.5% miał GŁĘBOKOŚĆ 2, czyli qubity były ułożone w DWIE FIZYCZNE LINIE.
# Sprawdźmy jakie linie są na Marrakesh i wymuśmy najlepszą.

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

# Szukamy 2 fizycznych linii po 16 qubitów każda na Marrakesh
from collections import defaultdict
cm = backend.configuration().coupling_map
neighbors = defaultdict(list)
for a, b in cm:
    neighbors[a].append(b)

# Znajdź linie (ścieżki) długości 16+
def find_lines():
    lines = []
    visited_global = set()
    
    for start in range(backend.num_qubits):
        if start in visited_global:
            continue
        # BFS line
        line = [start]
        visited = {start}
        current = start
        while True:
            next_nodes = [n for n in neighbors[current] if n not in visited]
            if not next_nodes:
                break
            # Wybierz ten z najmniejszym readout error
            props = backend.properties()
            best = min(next_nodes, key=lambda q: next((p.value for p in props.qubits[q] if p.name == 'readout_error'), 0.02)
            line.append(best)
            visited.add(best)
            current = best
        
        if len(line) >= 16:
            lines.append(line)
            for q in line:
                visited_global.add(q)
        if len(lines) >= 4:
            break
    
    return lines

print("\nSzukam fizycznych linii 16-qubitowych...")
lines = find_lines()
print(f"Znaleziono {len(lines)} linii:")

for i, line in enumerate(lines[:4]):
    readouts = []
    for q in line:
        props = backend.properties().qubits[q]
        r = next((p.value for p in props if p.name == 'readout_error'), 0.02)
        readouts.append(r)
    print(f"  Linia {i+1}: {line[:16]}... (readout avg: {sum(readouts)/len(readouts):.4f})")

# Wybierz 2 najlepsze linie po 16 qubitów
best_lines = []
for line in lines:
    if len(line) >= 16:
        readouts = []
        for q in line[:16]:
            props = backend.properties().qubits[q]
            r = next((p.value for p in props if p.name == 'readout_error'), 0.02)
            readouts.append(r)
        avg_r = sum(readouts) / len(readouts)
        best_lines.append((avg_r, line[:16]))

best_lines.sort()
if len(best_lines) >= 2:
    line1 = best_lines[0][1]
    line2 = best_lines[1][1]
    print(f"\n=== WYBRANE 2 LINIE ===")
    print(f"Linia 1 (lewa):  {line1}")
    print(f"Linia 2 (prawa): {line2}")
    
    # Wymuś layout: q0-q15 na linia1, q16-q31 na linia2
    initial_layout = {}
    for i, q in enumerate(line1):
        initial_layout[i] = q
    for i, q in enumerate(line2):
        initial_layout[16 + i] = q
    
    print(f"\nLayout: {initial_layout}")
    
    qc_t = transpile(qc, backend, 
        initial_layout=initial_layout,
        optimization_level=3
    )
    print(f"Głębokość po transpilacji: {qc_t.depth()}")
    
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
        print("ZAZUL WORLD STS | REKORD 2 LINIE FIZYCZNE")
        print("=" * 60)
        print(f"Echo |0...0>: {echo}/{total} = {pct:.1f}%")
        print(f"Poprzedni rekord: 87.5%")
        print(f"Zmiana: {pct - 87.5:+.1f}%")
        
        if pct > 87.5:
            print(f"\n🔥🔥🔥 REKORD POBITY! 🔥🔥🔥")
        
        top = sorted(counts.items(), key=lambda x: -x[1])[:5]
        print("\nTop 5:")
        for state, count in top:
            print(f"  {state}: {count} ({count/total*100:.1f}%)")
        print("=" * 60)
else:
    print("Nie znaleziono wystarczająco linii!")
