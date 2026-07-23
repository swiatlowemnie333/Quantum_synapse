import os, json
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService(
    channel='ibm_quantum_platform',
    token=os.getenv('IBM_QUANTUM_API_KEY')
)
backend = service.backend('ibm_marrakesh')

n = 32
mid = n // 2

# Oryginalny obwód co dał 87.5%
qc = QuantumCircuit(n, n)
qc.h(mid - 1); qc.h(mid)
for i in range(mid - 1, 0, -1): qc.cz(i, i - 1)
for i in range(mid, n - 1):     qc.cz(i, i + 1)
qc.z(0); qc.z(n - 1)
for i in range(0, mid - 1):     qc.cz(i, i + 1)
for i in range(n - 1, mid, -1): qc.cz(i, i - 1)
qc.measure(range(n), range(n))

# Transpilacja żeby zobaczyć jak IBM to zmapował
qc_t = transpile(qc, backend, optimization_level=3)
layout = qc_t.layout

print("=" * 70)
print("ZAZUL WORLD STS | ANALIZA 87.5% | 32q IBM Marrakesh")
print("=" * 70)

# Mapowanie logiczne -> fizyczne
mapa = {}
print("\n=== MAPOWANIE LOGICZNE -> FIZYCZNE ===")
for i in range(n):
    phys = int(layout.initial_layout[i]) if layout and layout.initial_layout else i
    mapa[i] = phys
    print(f"  qubit logiczny {i:2d}  ->  fizyczny {phys:3d}")

# Pobierz wynik joba 87.5%
job_id = "d8r9jl6ab0ds73drdnig"
print(f"\n=== POBIERAM WYNIK JOB: {job_id} ===")
job = service.job(job_id)
result = job.result()
counts = result[0].data.c.get_counts()
total = sum(counts.values())

# Analiza bitowa — które bity najczęściej się flipują
print(f"\n=== ANALIZA BITOWA (P|0>) ===")
print("logiczny | fizyczny | P|0>  | flipów | wykres       | ocena")
print("-" * 70)
p0_list = []
for i in range(n):
    pos = i  # q0 = lewy znak w bitstringu
    count_0 = sum(c for bits, c in counts.items() if bits[pos] == '0')
    p0 = count_0 / total
    p0_list.append(p0)
    flips = total - count_0
    bar = '█' * int(p0 * 10) + '░' * (10 - int(p0 * 10))
    ocena = "ZIELONY" if p0 >= 0.995 else "ZOLTY" if p0 >= 0.99 else "CZERWONY"
    print(f"q{i:2d}      | {mapa[i]:3d}      | {p0:.3f} | {flips:4d}   | {bar} | {ocena}")

# Właściwości fizyczne użytych qubitów
print(f"\n=== WŁAŚCIWOŚCI FIZYCZNE (T1, T2, readout_error) ===")
print("logiczny | fizyczny | T1(μs) | T2(μs) | readout_err | boost_rz")
print("-" * 70)
props = backend.properties()
boosty = {}
for i in range(n):
    phys = mapa[i]
    qubit_props = props.qubits[phys]
    t1 = next((p.value for p in qubit_props if p.name == 'T1'), 0)
    t2 = next((p.value for p in qubit_props if p.name == 'T2'), 0)
    readout = next((p.value for p in qubit_props if p.name == 'readout_error'), 0.01)
    
    # Boost: tylko jeśli readout > 0.004 i P0 < 0.995
    if readout > 0.004 and p0_list[i] < 0.995:
        boost = round(readout * 0.3, 5)
        boosty[i] = boost
    else:
        boosty[i] = 0.0
    
    print(f"q{i:2d}      | {phys:3d}      | {t1:6.1f} | {t2:6.1f} | {readout:.5f}     | {boosty[i]:.5f}")

with open('boosty_32q.json', 'w') as f:
    json.dump(boosty, f, indent=2)

print(f"\n{'='*70}")
print(f"REKORD ZAZUL: 87.5% (job {job_id})")
print(f"Średni błąd odczytu użytych qubitów: {sum(next((p.value for p in props.qubits[mapa[i]] if p.name=='readout_error'),0.01) for i in range(n))/n:.4f}")
print(f"Qubity do boosta: {[k for k,v in boosty.items() if v > 0]}")
print(f"✅ Boosty zapisane do boosty_32q.json")
print(f"{'='*70}")
