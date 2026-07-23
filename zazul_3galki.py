from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit import QuantumCircuit, transpile

SHOTS = 8192
TEAM = [0, 1]

service = QiskitRuntimeService()
backend = service.backend("ibm_marrakesh")
sampler = Sampler(mode=backend)

def echo(nx=1):
    # h, cx^nx, barrier, cx^nx, h -> echo z nx-krotnym halasem CNOT
    qc = QuantumCircuit(2)
    qc.h(0)
    for _ in range(nx): qc.cx(0, 1)
    qc.barrier()
    for _ in range(nx): qc.cx(0, 1)
    qc.h(0)
    qc.measure_all()
    return qc

def ghz(nx=1):
    qc = QuantumCircuit(2)
    qc.h(0)
    for _ in range(nx): qc.cx(0, 1)
    qc.measure_all()
    return qc

cal0 = QuantumCircuit(2); cal0.measure_all()
cal1 = QuantumCircuit(2); cal1.x([0, 1]); cal1.measure_all()

pubs = [transpile(c, backend=backend, initial_layout=TEAM, optimization_level=1)
        for c in (cal0, cal1, echo(1), echo(3), ghz(1))]
job = sampler.run(pubs, shots=SHOTS)
print("Job ID:", job.job_id())
res = job.result()

def counts(i): return res[i].data.meas.get_counts()
def frac(c, s): return c.get(s, 0) / SHOTS

c0, c1 = counts(0), counts(1)
p00 = {q: sum(v for k, v in c0.items() if k[::-1][q] == '0') / SHOTS for q in range(2)}
p11 = {q: sum(v for k, v in c1.items() if k[::-1][q] == '1') / SHOTS for q in range(2)}
print(f"Odczyt: q0 ({p00[0]:.3f}/{p11[0]:.3f}), q1 ({p00[1]:.3f}/{p11[1]:.3f})")

def correct(p):
    return min(p / max(p00[0] * p00[1], 1e-9), 1.0)

e1, e3 = counts(2), counts(3)
raw1, raw3 = frac(e1, '00'), frac(e3, '00')
leak1 = frac(e1, '01') + frac(e1, '10')

print(f"\n=== GALKA 1: korekta odczytu ===")
print(f"echo 1x surowe: {100*raw1:.2f}% -> skorygowane: {100*correct(raw1):.2f}%")

print(f"\n=== GALKA 2: ZNE ===")
zne = min(raw1 + (raw1 - raw3) / 2, 1.0)
print(f"1x: {100*raw1:.2f}%  3x: {100*raw3:.2f}%  -> ZNE: {100*zne:.2f}%")

print(f"\n=== GALKA 3: selekcia ===")
print(f"przeciek 1x: {100*leak1:.2f}%  |  strzal bez przecieku: {100*(1-leak1):.2f}%")

print(f"\n=== WSZYSTKIE NARAZ ===")
print(f"ZNE + korekta: {100*correct(zne):.2f}%")

g = counts(4)
gp = frac(g, '00') + frac(g, '11')
print(f"\nGHZ 1x: {100*gp:.2f}% -> po korekcie: {100*correct(gp):.2f}%")
