from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

# Szumy jak na IBM Marrakesh
noise = NoiseModel()
noise.add_all_qubit_quantum_error(depolarizing_error(0.001, 1), ['h','rz','x','z'])
noise.add_all_qubit_quantum_error(depolarizing_error(0.005, 2), ['cz','cx'])
backend = AerSimulator(method='density_matrix', noise_model=noise)

def sondowanie(n, shots=4096):
    """Faza 1: Qubity same się wycechowują. Każdy qubit dostaje 'kolor' na podstawie P(|0>)."""
    q = QuantumCircuit(n, n)
    for i in range(n):
        q.h(i)
        q.measure(i, i)
    r = backend.run(q, shots=shots).result().get_counts()
    total = sum(r.values())
    
    cechy = {}
    for i in range(n):
        p0 = sum(c for s,c in r.items() if s[n-1-i] == '0') / total
        if p0 > 0.98:
            cechy[i] = 'ZIELONY'  # mocny
        elif p0 > 0.95:
            cechy[i] = 'ZOLTY'    # średni
        elif p0 > 0.90:
            cechy[i] = 'POMARANCZOWY'  # słabszy
        else:
            cechy[i] = 'CZERWONY'  # słaby, wymaga korekty
    
    print(f'\n=== SONDA {n}q ===')
    for i in range(n):
        p0 = sum(c for s,c in r.items() if s[n-1-i] == '0') / total
        print(f'  q{i:2d}: P(|0>)={p0:.3f} -> {cechy[i]}')
    
    return cechy

def echo_synergia_synestezja(n, cechy, shots=4096):
    """Faza 2: Fale równoległe + synestezja zależna od 'koloru' qubita."""
    q = QuantumCircuit(n, n)
    mid = n // 2
    
    # Inicjalizacja - każdy qubit z 'energią' zależną od koloru
    for i in range(n):
        q.h(i)
        if cechy[i] == 'CZERWONY':
            q.rz(0.02, i)  # boost energii
        elif cechy[i] == 'POMARANCZOWY':
            q.rz(0.01, i)
    
    # LEWA fala - synestezja (cross-coupling z cechami)
    for i in range(mid-1, 0, -1):
        q.cz(i, i-1)
        if cechy[i-1] == 'CZERWONY':
            q.rz(0.03, i-1)
        elif cechy[i-1] == 'POMARANCZOWY':
            q.rz(0.015, i-1)
        elif cechy[i-1] == 'ZOLTY':
            q.rz(0.005, i-1)
    
    # PRAWA fala
    for i in range(mid, n-1):
        q.cz(i, i+1)
        if cechy[i+1] == 'CZERWONY':
            q.rz(0.03, i+1)
        elif cechy[i+1] == 'POMARANCZOWY':
            q.rz(0.015, i+1)
        elif cechy[i+1] == 'ZOLTY':
            q.rz(0.005, i+1)
    
    # Odbicie - "lustro" na brzegach z boostem
    q.z(0)
    q.z(n-1)
    if cechy[0] == 'CZERWONY':
        q.rz(0.02, 0)
    if cechy[n-1] == 'CZERWONY':
        q.rz(0.02, n-1)
    
    # Powrót - synestezja z drugiej strony
    for i in range(0, mid-1):
        q.cz(i, i+1)
        if cechy[i] == 'CZERWONY':
            q.rz(0.03, i)
        elif cechy[i] == 'POMARANCZOWY':
            q.rz(0.015, i)
        elif cechy[i] == 'ZOLTY':
            q.rz(0.005, i)
    
    for i in range(n-1, mid, -1):
        q.cz(i, i-1)
        if cechy[i] == 'CZERWONY':
            q.rz(0.03, i)
        elif cechy[i] == 'POMARANCZOWY':
            q.rz(0.015, i)
        elif cechy[i] == 'ZOLTY':
            q.rz(0.005, i)
    
    # Zamknięcie - "harmonizacja"
    q.h(mid-1)
    q.h(mid)
    
    # Pomiar
    for i in range(n):
        q.measure(i, i)
    
    r = backend.run(q, shots=shots).result().get_counts()
    total = sum(r.values())
    zero = r.get('0'*n, 0)
    fidelity = zero/total*100
    
    print(f'\n=== ECHO SYNERGIA {n}q ===')
    print(f'Fidelity: {fidelity:.1f}%')
    print(f'Top 3:')
    for s,c in sorted(r.items(), key=lambda x:-x[1])[:3]:
        print(f'  {s}: {c} ({c/total*100:.1f}%)')
    
    return fidelity

# TESTUJEMY
for n in [16, 32, 64]:
    print(f'\n{"="*50}')
    print(f'N = {n} QUBITS')
    print(f'{"="*50}')
    cechy = sondowanie(n)
    fid = echo_synergia_synestezja(n, cechy)
    print(f'\n>>> WYNIK: {n}q = {fid:.1f}% <<<')
