# -*- coding: utf-8 -*-
"""
GHZ fidelity SUROWE vs PO MITYGACJI (M3), POPRAWIONA koherencja.
Dla 16, 20, 27 kubitow. F = (populacja + koherencja)/2.
Koherencja po mitygacji liczona przez M3 .expval() (parzystosc <Z..Z>),
NIE przez sumowanie quasi-rozkladu -> teraz korekta koherencji dziala.

Uruchom:  python fidelity_qrem_v4.py
Wymaga mthree. Konto IBM zapisane. Zuzywa czas QPU.
"""
import os, csv, numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
try:
    import mthree
except ImportError:
    raise SystemExit("Brak mthree. Zainstaluj:  pip install mthree")

BACKEND = "ibm_marrakesh"
SIZES   = [16, 20, 27]
SHOTS   = 4096

kw = {"channel": "ibm_quantum_platform"}
if os.getenv("IBM_QUANTUM_API_KEY"):
    kw["token"] = os.getenv("IBM_QUANTUM_API_KEY")
service = QiskitRuntimeService(**kw)
backend = service.backend(BACKEND)
print(f"Backend: {backend.name}")

def ghz(n):
    qc = QuantumCircuit(n); qc.h(0)
    for i in range(n-1): qc.cx(i, i+1)
    return qc

def build(n):
    circs, kinds, phis = [], [], []
    c = ghz(n); c.measure_all(); circs.append(c); kinds.append("pop"); phis.append(None)
    for k in range(4*n):
        phi = 2*np.pi*k/(4*n)
        c = ghz(n)
        for q in range(n): c.r(np.pi/2, phi, q)
        c.measure_all(); circs.append(c); kinds.append("parity"); phis.append(phi)
    return circs, kinds, phis

def raw_pop_par(counts, n):
    tot = sum(counts.values()) or 1
    p = (counts.get("0"*n,0)+counts.get("1"*n,0))/tot
    par = sum(c*(-1.0)**(bs.count("1")) for bs,c in counts.items())/tot
    return p, par

rows = []
for n in SIZES:
    circs, kinds, phis = build(n)
    isa = transpile(circs, backend, optimization_level=3)
    qubits_used = isa[0].layout.final_index_layout()[:n]
    print(f"GHZ-{n}: {len(circs)} obwodow; kubity {qubits_used}; wysylam...")
    sampler = SamplerV2(mode=backend)
    job = sampler.run([(c,) for c in isa], shots=SHOTS)
    print(f"  job_id = {job.job_id()}")
    res = job.result()
    counts_list = [list(pr.data.values())[0].get_counts() for pr in res]

    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system(qubits_used, shots=SHOTS)

    # SUROWE
    P_r=None; sig_r=[]
    # PO MITYGACJI
    P_m=None; sig_m=[]
    for cc, kind, phi in zip(counts_list, kinds, phis):
        pr, par_r = raw_pop_par(cc, n)
        q = mit.apply_correction(cc, qubits_used)        # QuasiDistribution
        qd = dict(q)
        pm = qd.get("0"*n,0.0) + qd.get("1"*n,0.0)       # populacja zmitygowana
        par_m = q.expval()                                # koherencja/parzystosc zmitygowana (POPRAWKA)
        if kind=="pop":
            P_r, P_m = pr, pm
        else:
            sig_r.append((phi,par_r)); sig_m.append((phi,par_m))

    def coher(sig):
        phia=np.array([p for p,_ in sig]); sa=np.array([v for _,v in sig])
        return 2.0/len(sa)*abs(np.sum(sa*np.exp(-1j*n*phia)))
    Cr=coher(sig_r); Cm=coher(sig_m)
    Fr=(P_r+Cr)/2; Fm=(P_m+Cm)/2
    print(f"GHZ-{n} SUROWE:       P={P_r:.3f} C={Cr:.3f} F={Fr:.3f} ({Fr*100:.1f}%)")
    print(f"GHZ-{n} PO MITYGACJI:  P={P_m:.3f} C={Cm:.3f} F={Fm:.3f} ({Fm*100:.1f}%)  | IBM 27q=54.6%")
    rows.append(dict(N=n, job_id=job.job_id(),
                     F_surowe=round(Fr,4), F_mit=round(Fm,4),
                     P_sur=round(P_r,4), C_sur=round(Cr,4), P_mit=round(P_m,4), C_mit=round(Cm,4)))

with open("fidelity_qrem_v4_wyniki.csv","w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=["N","job_id","F_surowe","F_mit","P_sur","C_sur","P_mit","C_mit"])
    w.writeheader(); w.writerows(rows)
print("\nZapisano: fidelity_qrem_v4_wyniki.csv  -> napisz 'gotowe'.")
