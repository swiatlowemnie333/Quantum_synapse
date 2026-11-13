# -*- coding: utf-8 -*-
"""
Mierzy PRAWDZIWE fidelity GHZ metoda oscylacji parzystosci (MQC) na IBM.
F = (populacja + koherencja) / 2.

Uruchom u siebie (PowerShell):   python fidelity_mqc_ibm.py

- Uzywa zapisanego konta IBM (QiskitRuntimeService). Token zostaje u Ciebie.
- Domyslnie liczy tylko GHZ-6 (tanio, walidacja metody). Zeby dodac 16 i 20,
  zmien linie SIZES = [6] na SIZES = [6, 16, 20].
- Zuzywa czas QPU z darmowego planu - zacznij od [6].
"""
import os, csv, numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

# ---------- USTAWIENIA ----------
BACKEND = "ibm_marrakesh"      # albo "ibm_fez"
SIZES   = [6, 16, 20]      # komplet do wniosku
SHOTS   = 4096
# --------------------------------

kw = {"channel": "ibm_quantum_platform"}
if os.getenv("IBM_QUANTUM_API_KEY"):
    kw["token"] = os.getenv("IBM_QUANTUM_API_KEY")
service = QiskitRuntimeService(**kw)
backend = service.backend(BACKEND)
print(f"Backend: {backend.name}")

def ghz(n):
    qc = QuantumCircuit(n)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    return qc

def build_circuits(n):
    circs, kinds, phis = [], [], []
    # 1) pomiar populacji w bazie Z
    c = ghz(n); c.measure_all()
    circs = [c]; kinds = ["pop"]; phis = [None]
    # 2) skan parzystosci: R(pi/2, phi) na kazdym kubicie, potem pomiar Z
    M = 4 * n            # liczba punktow fazy (> 2N, rozdziela czestotliwosc N)
    for k in range(M):
        phi = 2 * np.pi * k / M
        c = ghz(n)
        for q in range(n):
            c.r(np.pi / 2, phi, q)
        c.measure_all()
        circs.append(c); kinds.append("parity"); phis.append(phi)
    return circs, kinds, phis

rows = []
for n in SIZES:
    circs, kinds, phis = build_circuits(n)
    isa = transpile(circs, backend, optimization_level=3)
    print(f"GHZ-{n}: {len(circs)} obwodow, transpilacja OK, wysylam...")
    sampler = SamplerV2(mode=backend)
    job = sampler.run([(c,) for c in isa], shots=SHOTS)
    print(f"  job_id = {job.job_id()}  (czekam na wynik, moze stac w kolejce)")
    res = job.result()

    # populacja
    def parity_and_pop(pr):
        reg = list(pr.data.values())[0]
        bits = reg.to_bool_array().astype(np.int64)   # (shots, n)
        s = bits.sum(1)
        par = float(((-1.0) ** s).mean())
        p0 = float((s == 0).mean()); p1 = float((s == bits.shape[1]).mean())
        return par, p0 + p1

    P = None; sig = []
    for pr, kind, phi in zip(res, kinds, phis):
        par, pop = parity_and_pop(pr)
        if kind == "pop":
            P = pop
        else:
            sig.append((phi, par))
    # koherencja = amplituda skladowej cos(N*phi)
    phi_arr = np.array([p for p, _ in sig])
    s_arr   = np.array([v for _, v in sig])
    C = 2.0 / len(s_arr) * abs(np.sum(s_arr * np.exp(-1j * n * phi_arr)))
    F = (P + C) / 2.0
    print(f"GHZ-{n}:  populacja P={P:.4f}  koherencja C={C:.4f}  ->  FIDELITY F={F:.4f}  ({F*100:.1f}%)")
    print(f"         swiadek splatania: {'TAK, F>0.5 (prawdziwe GHZ)' if F > 0.5 else 'NIE (F<=0.5)'}")
    rows.append(dict(N=n, backend=backend.name, job_id=job.job_id(),
                     populacja=round(P, 4), koherencja=round(C, 4),
                     fidelity=round(F, 4), swiadek_ok=(F > 0.5)))

with open("fidelity_mqc_wyniki.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["N","backend","job_id","populacja","koherencja","fidelity","swiadek_ok"])
    w.writeheader(); w.writerows(rows)
print("\nZapisano: fidelity_mqc_wyniki.csv  -> napisz 'gotowe', sciagne i wpisze do wniosku.")
