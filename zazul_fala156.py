from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit import QuantumCircuit, transpile

SHOTS = 4096

service = QiskitRuntimeService()
backend = service.backend("ibm_marrakesh")
N = backend.configuration().n_qubits
print(f"Procesor: {N} kubitow")

bits = [i % 2 for i in range(N)]
qc = QuantumCircuit(N)
for i, b in enumerate(bits):
    if b: qc.x(i)
qc.measure_all()

pub = transpile(qc, backend=backend, optimization_level=1)
sampler = Sampler(mode=backend)
job = sampler.run([pub], shots=SHOTS)
print("Job ID:", job.job_id())
counts = job.result()[0].data.meas.get_counts()

per = []
for i in range(N):
    sent = bits[i]
    got1 = sum(v for k, v in counts.items() if k[::-1][i] == '1') / SHOTS
    fid = got1 if sent == 1 else 1 - got1
    per.append((fid, i))

avg = sum(f for f, _ in per) / N
per.sort()
print(f"\n=== FALA 1010 na CALYCH {N} kubitach: {100*avg:.2f}% ===")
print("Najslabsze 10:", [(f"q{q}", f"{100*f:.0f}%") for f, q in per[:10]])
print("Najlepsze 5:", [(f"q{q}", f"{100*f:.0f}%") for f, q in per[-5:]])
above95 = sum(1 for f, _ in per if f >= 0.95)
above90 = sum(1 for f, _ in per if f >= 0.90)
print(f"\nKubity >=95%: {above95}/{N}  |  >=90%: {above90}/{N}")
