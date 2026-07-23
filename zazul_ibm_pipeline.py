import os
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService

# Połączenie
service = QiskitRuntimeService(
    channel='ibm_quantum_platform',
    token=os.getenv('IBM_QUANTUM_API_KEY')
)

# Wybierz backend
try:
    backend = service.backend('ibm_heron')
except:
    backend = service.backend('ibm_marrakesh')

print(f"Backend: {backend.name}")

# ============================================================
# JOB 1: SONDOVANIE 32q (fala od środka, odbicie, powrót)
# ============================================================

n = 32
mid = n // 2

qc_sonda = QuantumCircuit(n, n)

# Start: dwie linie równoległe w środku
qc_sonda.h(mid - 1)
qc_sonda.h(mid)

# LEWA fala: od środka do brzegu
for i in range(mid - 1, 0, -1):
    qc_sonda.cz(i, i - 1)

# PRAWA fala: od środka do brzegu
for i in range(mid, n - 1):
    qc_sonda.cz(i, i + 1)

# Odbicie na brzegach
qc_sonda.z(0)
qc_sonda.z(n - 1)

# Powrót LEWA: od brzegu do środka
for i in range(0, mid - 1):
    qc_sonda.cz(i, i + 1)

# Powrót PRAWA: od brzegu do środka
for i in range(n - 1, mid, -1):
    qc_sonda.cz(i, i - 1)

# Zamknięcie
qc_sonda.h(mid - 1)
qc_sonda.h(mid)

# Pomiar
for i in range(n):
    qc_sonda.measure(i, i)

qc_sonda_t = transpile(qc_sonda, backend, optimization_level=3)

print(f"\n=== JOB 1: SONDOVANIE 32q ===")
print(f"Głębokość: {qc_sonda_t.depth()}")

job1 = backend.run(qc_sonda_t, shots=8192)
print(f"Job ID: {job1.job_id()}")
print("Czekam na wynik...")

# Czekaj na wynik
import time
while job1.status() not in ['DONE', 'ERROR']:
    time.sleep(10)
    print(f"  Status: {job1.status()}")

if job1.status() == 'ERROR':
    print("SONDA FAILED!")
    exit(1)

result1 = job1.result()
counts1 = result1.get_counts()
total1 = sum(counts1.values())

print(f"\n=== WYNIKI SONDOVANIA ===")
print(f"Total shots: {total1}")
print(f"Unique states: {len(counts1)}")

# Top 5
top = sorted(counts1.items(), key=lambda x: -x[1])[:5]
print("Top 5:")
for state, count in top:
    print(f"  {state}: {count} ({count/total1*100:.1f}%)")

# Marginal P(|0>) per qubit
print("\nMarginal P(|0>) per qubit:")
cechy = {}
for q in range(n):
    p0 = sum(c for s, c in counts1.items() if s[n-1-q] == '0') / total1
    bar = '█' * int(p0 * 10) + '░' * (10 - int(p0 * 10))
    if p0 >= 0.99:
        kolor, rz = 'ZIELONY', 0.0
    elif p0 >= 0.97:
        kolor, rz = 'ZOLTY', 0.005
    else:
        kolor, rz = 'CZERWONY', 0.015
    cechy[q] = rz
    print(f"  q{q:2d}: {p0:.2f} {bar} {kolor}")

# ============================================================
# JOB 2: ECHO Z SYNESTEZJĄ (RZ boosty na słabych)
# ============================================================

qc_echo = QuantumCircuit(n, n)

# Inicjalizacja + boost na słabych
for i in range(n):
    qc_echo.h(i)
    if cechy[i] > 0:
        qc_echo.rz(cechy[i], i)

# LEWA fala z synestezją
for i in range(mid - 1, 0, -1):
    qc_echo.cz(i, i - 1)
    if cechy[i - 1] > 0:
        qc_echo.rz(cechy[i - 1], i - 1)

# PRAWA fala z synestezją
for i in range(mid, n - 1):
    qc_echo.cz(i, i + 1)
    if cechy[i + 1] > 0:
        qc_echo.rz(cechy[i + 1], i + 1)

# Odbicie + boost na brzegowych
qc_echo.z(0)
qc_echo.z(n - 1)
if cechy[0] > 0:
    qc_echo.rz(cechy[0], 0)
if cechy[n - 1] > 0:
    qc_echo.rz(cechy[n - 1], n - 1)

# Powrót LEWA z synestezją
for i in range(0, mid - 1):
    qc_echo.cz(i, i + 1)
    if cechy[i] > 0:
        qc_echo.rz(cechy[i], i)

# Powrót PRAWA z synestezją
for i in range(n - 1, mid, -1):
    qc_echo.cz(i, i - 1)
    if cechy[i] > 0:
        qc_echo.rz(cechy[i], i)

# Zamknięcie
qc_echo.h(mid - 1)
qc_echo.h(mid)

# Pomiar
for i in range(n):
    qc_echo.measure(i, i)

qc_echo_t = transpile(qc_echo, backend, optimization_level=3)

print(f"\n=== JOB 2: ECHO Z SYNESTEZJĄ ===")
print(f"Głębokość: {qc_echo_t.depth()}")
print(f"Bramki RZ: {qc_echo_t.count_ops().get('rz', 0)}")

job2 = backend.run(qc_echo_t, shots=8192)
print(f"Job ID: {job2.job_id()}")
print("Czekam na wynik...")

while job2.status() not in ['DONE', 'ERROR']:
    time.sleep(10)
    print(f"  Status: {job2.status()}")

if job2.status() == 'ERROR':
    print("ECHO FAILED!")
    exit(1)

result2 = job2.result()
counts2 = result2.get_counts()
total2 = sum(counts2.values())
zero2 = counts2.get('0' * n, 0)

print(f"\n=== WYNIKI ECHO ===")
print(f"Echo |0...0>: {zero2}/{total2} = {zero2/total2*100:.1f}%")

# Porównanie
print(f"\n=== PORÓWNANIE ===")
print(f"Bez synestezji: 74.0% (poprzedni wynik)")
print(f"Z synestezją:  {zero2/total2*100:.1f}%")
if zero2/total2 > 0.74:
    print(f"🎉 POPRAWA o +{zero2/total2*100 - 74:.1f}%!")
else:
    print(f"❌ Spadek o {74 - zero2/total2*100:.1f}%")

print(f"\nTop 5 echo:")
top2 = sorted(counts2.items(), key=lambda x: -x[1])[:5]
for state, count in top2:
    print(f"  {state}: {count} ({count/total2*100:.1f}%)")

print(f"\nMarginal P(|0>) per qubit (echo):")
for q in range(n):
    p0 = sum(c for s, c in counts2.items() if s[n-1-q] == '0') / total2
    bar = '█' * int(p0 * 10) + '░' * (10 - int(p0 * 10))
    print(f"  q{q:2d}: {p0:.2f} {bar}")

print(f"\n=== KONIEC ===")
print(f"Zużyte minuty: ~{2 + 2} min (szacunek)")
