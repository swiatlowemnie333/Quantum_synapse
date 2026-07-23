from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit import QuantumCircuit, transpile
from collections import deque, defaultdict
import math, random

OLD_JOB = "d9gr51khonhs73ac42mg"
SHOTS = 4096
DELAYS_US = [0, 5, 10, 20, 35, 50]
BLACKLIST = {82, 26, 72, 76}
random.seed(42)

service = QiskitRuntimeService()
backend = service.backend("ibm_marrakesh")
cmap = backend.configuration().coupling_map
adj = defaultdict(set)
for a, b in cmap:
    adj[a].add(b); adj[b].add(a)
N = len(adj)

res = service.job(OLD_JOB).result()
def frac(pub, q, bit):
    counts = pub.data.meas.get_counts()
    return sum(v for k, v in counts.items() if k[::-1][q] == bit) / 2048

def fit_t(times, probs):
    pts = [(t, math.log(max(p, 1e-3))) for t, p in zip(times, probs)]
    n = len(pts); mx = sum(t for t,_ in pts)/n; my = sum(l for _,l in pts)/n
    num = sum((t-mx)*(l-my) for t,l in pts); den = sum((t-mx)**2 for t,_ in pts)
    s = num/den if den else 0
    return -1/s if s < 0 else float('inf')

t1, t2 = {}, {}
for q in range(N):
    ep = [frac(res[2*i], q, '1') for i in range(6)]
    t1[q] = fit_t(DELAYS_US, [p/max(ep[0],1e-3) for p in ep])
    fp = [max(0.0, 2*(frac(res[2*i+1], q, '0')-0.5)) for i in range(6)]
    t2[q] = fit_t(DELAYS_US, [max(p/max(fp[0],1e-3),1e-3) for p in fp])

def score(q): return min(t1[q], 250) + 3*min(t2[q], 100)

# dluga sciezka: losowe greedy walki z preferencja jakosci, caly procesor
best = []
nodes = [q for q in range(N) if q not in BLACKLIST]
for _ in range(300):
    start = random.choice(nodes)
    path, seen = [start], {start}
    u = start
    while True:
        nxt = [v for v in adj[u] if v not in seen and v not in BLACKLIST]
        if not nxt: break
        nxt.sort(key=score, reverse=True)
        # 70% bierze najlepszy, 30% losuje z top-3 -> eksploracja
        if random.random() < 0.7 or len(nxt) == 1:
            u = nxt[0]
        else:
            u = random.choice(nxt[:3])
        path.append(u); seen.add(u)
    if len(path) > len(best): best = path

path = best[:32]
K = len(path)
print(f"Najdluzsza linia: {K} kubitow")
print(path)
print(f"Srednie T1={sum(t1[q] for q in path)/K:.0f} T2={sum(t2[q] for q in path)/K:.0f}")

bits = [i % 2 for i in range(K)]
qc = QuantumCircuit(K)
for i, b in enumerate(bits):
    if b: qc.x(i)
qc.swap(0, 1); qc.swap(1, 2)
qc.measure_all()

pub = transpile(qc, backend=backend, initial_layout=path, optimization_level=1)
sampler = Sampler(mode=backend)
job = sampler.run([pub], shots=SHOTS)
print("Job ID:", job.job_id())
counts = job.result()[0].data.meas.get_counts()

per_pos = []
for i in range(K - 2):
    sent = bits[i]
    got1 = sum(v for k, v in counts.items() if k[::-1][i+2] == '1') / SHOTS
    fid = got1 if sent == 1 else 1 - got1
    per_pos.append((fid, i, path[i+2]))
avg = sum(p[0] for p in per_pos) / len(per_pos)
per_pos.sort()
print(f"\n=== FALA 1010 na {K} kubitach: {100*avg:.2f}% ===")
print("Najslabsze 5:", [(f"p{i} q{q}", f"{100*f:.0f}%") for f, i, q in per_pos[:5]])
print("Najlepsze 5:", [(f"p{i} q{q}", f"{100*f:.0f}%") for f, i, q in per_pos[-5:]])
