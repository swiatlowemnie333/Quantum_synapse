# -*- coding: utf-8 -*-
"""
Pobiera WSZYSTKIE joby z IBM Quantum i liczy metryke populacji GHZ:
P(same 0) + P(same 1) na aktywnych kubitach -- to samo co podsumuj_joby.py.
Wynik: dwa pliki CSV w tym samym folderze + wydruk najlepszych wynikow wg
rozmiaru GHZ (6,12,16,20,...), z numerami jobow.

Uruchom u siebie (PowerShell):   python policz_ghz_wszystkie.py

Klucz: uzywa zapisanego konta (QiskitRuntimeService.save_account). Jesli
konta nie ma, ustaw zmienna IBM_QUANTUM_API_KEY. NIE wklejaj klucza do czatu.
"""
import os, csv
import numpy as np
from collections import defaultdict
from qiskit_ibm_runtime import QiskitRuntimeService

kw = {"channel": "ibm_quantum_platform"}
if os.getenv("IBM_QUANTUM_API_KEY"):
    kw["token"] = os.getenv("IBM_QUANTUM_API_KEY")

service = QiskitRuntimeService(**kw)
LIMIT = 400
jobs = service.jobs(limit=LIMIT, descending=False)
print(f"Znaleziono jobow: {len(jobs)}  (limit {LIMIT})")

rows = []
for n, j in enumerate(jobs, 1):
    jid = j.job_id()
    try:
        backend = j.backend().name if j.backend() else ""
    except Exception:
        backend = ""
    status = str(j.status())
    if status not in ("DONE", "JobStatus.DONE"):
        print(f"[{n}/{len(jobs)}] {jid} {status} - pomijam")
        continue
    try:
        res = j.result()
    except Exception as e:
        print(f"[{n}/{len(jobs)}] {jid} BLAD wyniku: {str(e)[:70]}")
        continue
    liczba_ok = 0
    for pi, pr in enumerate(res):
        try:
            regs = list(pr.data.values())
            if not regs:                     # pusty wynik - pomijamy
                continue
            reg = regs[0]                    # BitArray
            bits = reg.to_bool_array().astype(np.int64)  # (shots, num_bits)
            if bits.size == 0:
                continue
            shots = bits.shape[0]
            active = np.where(bits.max(0) == 1)[0]
            na = len(active)
            if na:
                s = bits[:, active].sum(1)
                p0 = float((s == 0).mean()); p1 = float((s == na).mean())
            else:
                p0, p1 = 1.0, 0.0
            rows.append(dict(job_id=jid, pub=pi, backend=backend, created=str(getattr(j, "creation_date", "")),
                             shots=shots, n_active=na,
                             P0=round(p0, 4), P1=round(p1, 4), P0_plus_P1=round(p0 + p1, 4)))
            liczba_ok += 1
        except Exception as e:
            print(f"    pub {pi}: pomijam ({str(e)[:50]})")
    print(f"[{n}/{len(jobs)}] {jid} {backend} OK  obwodow={liczba_ok}")

# pelna tabela
with open("joby_pelne.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["job_id","pub","backend","created","shots","n_active","P0","P1","P0_plus_P1"])
    w.writeheader(); w.writerows(rows)

# najlepszy wg rozmiaru
if not rows:
    print("Brak danych - zadnego joba nie udalo sie policzyc."); raise SystemExit
best = {}
for r in rows:
    k = r["n_active"]
    if k not in best or r["P0_plus_P1"] > best[k]["P0_plus_P1"]:
        best[k] = r
with open("joby_najlepsze_wg_rozmiaru.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["n_active","P0_plus_P1","P0","P1","shots","job_id","pub","backend"])
    w.writeheader()
    for k in sorted(best):
        b = best[k]; w.writerow({x: b[x] for x in ["n_active","P0_plus_P1","P0","P1","shots","job_id","pub","backend"]})

print("\n=== NAJLEPSZY P0+P1 WG LICZBY KUBITOW ===")
print(f"{'kubity':>7}{'P0+P1':>9}   job_id (pub)")
for k in sorted(best):
    b = best[k]
    print(f"{k:>7}{b['P0_plus_P1']*100:>8.1f}%   {b['job_id']} (pub {b['pub']})")
print("\nZapisano: joby_pelne.csv  oraz  joby_najlepsze_wg_rozmiaru.csv")
print("Wrzuc oba pliki do czatu, a ja policze z nich pelne fidelity i poprawie wniosek.")
