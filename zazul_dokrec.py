from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit import QuantumCircuit, transpile
import math

SHOTS = 4096
TEAM = [0, 1]
ROUNDS = 3

service = QiskitRuntimeService()
backend = service.backend("ibm_marrakesh")
sampler = Sampler(mode=backend)

def echo_circuit(phi0, phi1):
    qc = QuantumCircuit(2)
    qc.h(0); qc.cx(0, 1); qc.barrier(); qc.cx(0, 1)
    qc.rz(phi0, 0); qc.rz(phi1, 1)
    qc.h(0)
    qc.measure_all()
    return qc

def run_batch(configs, tag):
    pubs = [transpile(echo_circuit(p0, p1), backend=backend, initial_layout=TEAM, optimization_level=1) for p0, p1 in configs]
    job = sampler.run(pubs, shots=SHOTS)
    print(f"[{tag}] Job ID: {job.job_id()}")
    res = job.result()
    out = []
    for (p0, p1), pub in zip(configs, res):
        counts = pub.data.meas.get_counts()
        p00 = counts.get("00", 0) / SHOTS
        out.append((p00, p0, p1))
    return sorted(out, reverse=True)

best_p00, best0, best1 = run_batch([(0.0, 0.0)], "baseline")[0]
print(f"Baseline: {100*best_p00:.2f}%")

span = math.pi
for r in range(1, ROUNDS + 1):
    step = span / 4
    # faza 1: pojedyncze podkrecanie
    grid = [best0 + k*step for k in (-2, -1, 1, 2)]
    single0 = run_batch([(p, best1) for p in grid], f"runda{r} q0")
    grid = [best1 + k*step for k in (-2, -1, 1, 2)]
    single1 = run_batch([(best0, p) for p in grid], f"runda{r} q1")
    cand = single0 + single1
    # faza 2: miksy top-3 x top-3
    t0 = sorted({c[1] for c in single0[:3]} | {best0})
    t1 = sorted({c[2] for c in single1[:3]} | {best1})
    mixes = run_batch([(p0, p1) for p0 in t0 for p1 in t1], f"runda{r} miksy")
    cand += mixes
    top = cand[0]
    print(f"Runda {r}: najlepszy {100*top[0]:.2f}% (phi0={top[1]:.3f}, phi1={top[2]:.3f})")
    if top[0] <= best_p00 + 1e-4:
        print("Wynik przestal rosnac -> stop (jak spada, wracamy do najlepszego)")
        break
    best_p00, best0, best1 = top
    span /= 3  # cieńsza siatka wokół zwycięzcy

print(f"\n=== FINAL: {100*best_p00:.2f}% (phi0={best0:.4f}, phi1={best1:.4f}) ===")
print(f"Poprawa vs baseline: {100*(best_p00):.2f}% (bylo 96.9% surowe)")
