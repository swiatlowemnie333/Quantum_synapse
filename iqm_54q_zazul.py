from qiskit import QuantumCircuit

print("=" * 60)
print("ZAZUL WORLD STS | IQM EMERALD 54q | SYNERGIA + SYNESTEZJA")
print("=" * 60)

# ============================================================
# FAZA 1: SONDOVANIE (kalibracja)
# ============================================================
qc_sonda = QuantumCircuit(54, 54)
for i in range(54):
    qc_sonda.h(i)
    qc_sonda.measure(i, i)

with open('sonda_54_IQM_kalibracja.qasm', 'w') as f:
    f.write(qc_sonda.qasm())

print("[OK] sonda_54_IQM_kalibracja.qasm")
print("     Wrzuc na Open Quantum -> IQM Emerald -> shots: 8192")

# ============================================================
# FAZA 2: ECHO Z SYNESTEZJA (auto-grupowanie)
# ============================================================
# Zakladamy wyniki kalibracji - ZAMIN na prawdziwe z Open Quantum
# Grupy: ZIELONY, ZOLTY, POMARANCZOWY, CZERWONY
# Kazdy qubit dostaje: kolor + numer + cecha (opoznienie)

def generuj_echo_iqm_54q(wyniki_kalibracji):
    """
    wyniki_kalibracji: dict {qubit_index: P(|0>)}
    Zwraca: QuantumCircuit z synestezja
    """
    n = 54
    mid = n // 2  # 27
    
    # GRUPOWANIE AUTOMATYCZNE
    grupy = {}
    for i, p0 in wyniki_kalibracji.items():
        if p0 >= 0.99:
            grupy[i] = {'kolor': 'ZIELONY', 'rz': 0.0, 'opoznienie': 0}
        elif p0 >= 0.97:
            grupy[i] = {'kolor': 'ZOLTY', 'rz': 0.005, 'opoznienie': 1}
        elif p0 >= 0.95:
            grupy[i] = {'kolor': 'POMARANCZOWY', 'rz': 0.015, 'opoznienie': 2}
        else:
            grupy[i] = {'kolor': 'CZERWONY', 'rz': 0.03, 'opoznienie': 3}
    
    print(f"\n=== GRUPOWANIE AUTOMATYCZNE 54q ===")
    for kolor in ['ZIELONY', 'ZOLTY', 'POMARANCZOWY', 'CZERWONY']:
        ile = len([q for q, g in grupy.items() if g['kolor'] == kolor])
        print(f"  {kolor}: {ile} qubitow")
    
    # ECHO Z SYNESTEZJA
    qc = QuantumCircuit(n, n)
    
    # START: Dwie linie rownolegle w srodku (q26 i q27)
    qc.h(mid - 1)
    qc.h(mid)
    
    # Boost startowych jesli slabe
    for i in [mid - 1, mid]:
        if i in grupy and grupy[i]['rz'] > 0:
            qc.rz(grupy[i]['rz'], i)
    
    # LEWA FALA: od srodka (q26) do brzegu (q0)
    # Synestezja: kazdy qubit dostaje korekte zalezną od swojej grupy
    for i in range(mid - 1, 0, -1):
        qc.cz(i, i - 1)
        # Korekta na sasiadzie (i-1) - jego energia/sila
        if (i - 1) in grupy and grupy[i - 1]['rz'] > 0:
            qc.rz(grupy[i - 1]['rz'], i - 1)
    
    # PRAWA FALA: od srodka (q27) do brzegu (q53)
    for i in range(mid, n - 1):
        qc.cz(i, i + 1)
        if (i + 1) in grupy and grupy[i + 1]['rz'] > 0:
            qc.rz(grupy[i + 1]['rz'], i + 1)
    
    # ODBICIE: Z na brzegach + extra boost dla slabych brzegowych
    qc.z(0)
    qc.z(n - 1)
    if 0 in grupy and grupy[0]['rz'] > 0:
        qc.rz(grupy[0]['rz'], 0)
    if (n - 1) in grupy and grupy[n - 1]['rz'] > 0:
        qc.rz(grupy[n - 1]['rz'], n - 1)
    
    # POWROT LEWA: od brzegu do srodka
    for i in range(0, mid - 1):
        qc.cz(i, i + 1)
        if i in grupy and grupy[i]['rz'] > 0:
            qc.rz(grupy[i]['rz'], i)
    
    # POWROT PRAWA: od brzegu do srodka
    for i in range(n - 1, mid, -1):
        qc.cz(i, i - 1)
        if i in grupy and grupy[i]['rz'] > 0:
            qc.rz(grupy[i]['rz'], i)
    
    # ZAMKNIECIE: Powrot do stanu startowego
    qc.h(mid - 1)
    qc.h(mid)
    
    # POMIAR
    for i in range(n):
        qc.measure(i, i)
    
    return qc, grupy

# ============================================================
# PRZYKLADOWE DANE (ZAMIN na prawdziwe z Open Quantum)
# ============================================================
przykladowe_wyniki = {i: 0.99 for i in range(54)}
# Brzegowe slabsze
przykladowe_wyniki[0] = 0.96
przykladowe_wyniki[53] = 0.95
przykladowe_wyniki[1] = 0.98
przykladowe_wyniki[52] = 0.97
# Srodkowe mocne
for i in range(20, 34):
    przykladowe_wyniki[i] = 1.00

qc_echo, grupy = generuj_echo_iqm_54q(przykladowe_wyniki)

with open('echo_54_IQM_synestezja.qasm', 'w') as f:
    f.write(qc_echo.qasm())

print(f"\n[OK] echo_54_IQM_synestezja.qasm")
print(f"     Glebokosc: {qc_echo.depth()}")
print(f"     Bramki CZ: {qc_echo.count_ops().get('cz', 0)}")
print(f"     Bramki RZ: {qc_echo.count_ops().get('rz', 0)}")

print("\n" + "=" * 60)
print("INSTRUKCJA:")
print("  1. Wrzuc sonda_54_IQM_kalibracja.qasm na IQM Emerald")
print("  2. Pobierz wyniki (marginal P(|0>) per qubit)")
print("  3. Zamien 'przykladowe_wyniki' w tym skrypcie na prawdziwe")
print("  4. Uruchom ponownie -> wygeneruje echo z synestezja")
print("  5. Wrzuc echo_54_IQM_synestezja.qasm na IQM Emerald")
print("=" * 60)
