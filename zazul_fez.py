from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit import QuantumCircuit, transpile
from collections import defaultdict
import random

BACKEND = "ibm_fez"
SHOTS = 4096
random.seed(47)

service = QiskitRuntimeService()
backend = service.backend(BACKEND)
cmap = backend.configuration().coupling_map
adj = defaultdict(set)
for a, b in cmap:
    adj[a].add(b); adj[b].add(a)
N = len(adj)
print(f"{BACKEND}: {N} kubitow")

sampler = Sampler(mode=backend)

def wave_pattern(K, shift=False, path=None):
    bits = [i % 2 for i in range(K)]
    qc = QuantumCircuit(N if not path else K)
    for i, b in enumerate(bits):
        if b: qc.x(i)
    if shift:
        qc.swap(0, 1); qc.swap(1, 2)
    qc.measure_all()
    layout = path if path else None
    return transpile(qc, backend=backend, initial_layout=layout, optimization_level=1), bits

def score_counts(counts, bits, shift=False):
    per = []
    rng = range(len(bits) - 2) if shift else range(len(bits))
    for i in rng:
        pos = i + 2 if shift else i
        got1 = sum(v for k, v in counts.items() if k[::-1][pos] == '1') / SHOTS
        per.append((got1 if bits[i] == 1 else 1 - got1, i))
    return per

def find_path(L):
    best = []
    nodes = list(adj.keys())
    tries = 0
    while len(best) < L and tries < 8000:
        tries += 1
        start = random.choice(nodes)
        path, seen = [start], {start}
        u = start
        while True:
            nxt = [v for v in adj[u] if v not in seen]
            if not nxt: break
            u = random.choice(nxt)
            path.append(u); seen.add(u)
        if len(path) > len(best): best = path
    return best[:L]

jobs = []
pub156, bits156 = wave_pattern(N)
jobs.append(("156 caly chip", pub156, bits156, False))

p64 = find_path(64)
print(f"Linia 64 znaleziona ({len(p64)})")
pub64, bits64 = wave_pattern(len(p64), shift=True, path=p64)
jobs.append(("64 linia+przesuniecie", pub64, bits64, True))

p96 = find_path(96)
print(f"Linia 96 znaleziona ({len(p96)})")
pub96, bits96 = wave_pattern(len(p96), shift=True, path=p96)
jobs.append(("96 linia+przesuniecie", pub96, bits96, True))

job = sampler.run([p for _, p, _, _ in jobs], shots=SHOTS)
print("Job ID:", job.job_id())
res = job.result()

for (name, _, bits, shift), pub in zip(jobs, res):
    counts = pub.data.meas.get_counts()
    per = score_counts(counts, bits, shift)
    avg = sum(f for f, _ in per) / len(per)
    per.sort()
    print(f"\n=== {name}: {100*avg:.2f}% ===")
    print("najslabsze 5:", [(f"p{i}", f"{100*f:.0f}%") for f, i in per[:5]])
