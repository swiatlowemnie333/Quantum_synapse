from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit import QuantumCircuit, transpile
from collections import deque, defaultdict
import math

OLD_JOB = "d9gr51khonhs73ac42mg"
SHOTS = 4096
DELAYS_US = [0, 5, 10, 20, 35, 50]
BLACKLIST = {82, 26, 72, 76, 113, 130}
TARGET = 64
PI = math.pi

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
pool = [q for q in range(N) if q not in BLACKLIST]
team = [max(pool, key=score)]
while len(team) < TARGET:
    cand = {}
    for q in team:
        for v in adj[q]:
            if v not in team and v not in BLACKLIST:
                cand[v] = max(cand.get(v, 0), score(v))
    if not cand: break
    team.append(max(cand, key=cand.get))

K = len(team)
loc = {q: i for i, q in enumerate(team)}
sub = {q: [v for v in adj[q] if v in team] for q in team}

def build_tree(root):
    depth = {root: 0}; parent = {}
    dq = deque([root])
    while dq:
        u = dq.popleft()
        for v in sub[u]:
            if v not in depth: depth[v] = depth[u]+1; parent[v] = u; dq.append(v)
    return depth, parent

best_root, best_rad = None, 999
for q in team:
    d, _ = build_tree(q)
    if len(d) == K and max(d.values()) < best_rad:
        best_rad = max(d.values()); best_root = q
depth, parent = build_tree(best_root)
layers = [[(parent[v], v) for v in depth if depth[v] == d] for d in range(1, best_rad+1)]

def ghz(theta):
    qc = QuantumCircuit(K)
    qc.ry(theta, loc[best_root])
    active = {best_root}
    for layer in layers:
        for p, c in layer: qc.cx(loc[p], loc[c])
        for q in active:
            qc.x(loc[q]); qc.x(loc[q])
        for p, c in layer: active.add(c)
    qc.measure_all()
    return qc

thetas = [PI/2 * f for f in (0.45, 0.525, 0.675, 0.75)]
pubs = [transpile(ghz(t), backend=backend, initial_layout=team, optimization_level=1) for t in thetas]
sampler = Sampler(mode=backend)
job = sampler.run(pubs, shots=SHOTS)
print("Job ID:", job.job_id())
r = job.result()
best = (0, 0)
for t, pub in zip(thetas, r):
    counts = pub.data.meas.get_counts()
    s = (counts.get("0"*K, 0) + counts.get("1"*K, 0)) / SHOTS
    if s > best[0]: best = (s, t)
    print(f"theta={t:.3f}: {100*s:.2f}%")
print(f"\nSzczyt: {100*best[0]:.2f}% @ theta={best[1]:.3f} (rekord dnia: 27.29%)")
