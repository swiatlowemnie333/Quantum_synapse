from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit import QuantumCircuit, transpile
from collections import deque, defaultdict
import math

OLD_JOB = "d9gr51khonhs73ac42mg"
SHOTS = 2048
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
center = max(sub, key=lambda q: len(sub[q]))
depth = {center: 0}; parent = {}
dq = deque([center])
while dq:
    u = dq.popleft()
    for v in sub[u]:
        if v not in depth: depth[v] = depth[u]+1; parent[v] = u; dq.append(v)
layers = [[(parent[v], v) for v in depth if depth[v] == d] for d in range(1, max(depth.values())+1)]
print(f"Druzyna {K}, centrum q{center}")

pattern = "".join(str(i % 2) for i in range(K))[::-1]
antipat = "".join(str((i+1) % 2) for i in range(K))[::-1]

def circ(theta, pe, po, use_pattern=True):
    qc = QuantumCircuit(K)
    if use_pattern:
        for i in range(K):
            if i % 2 == 1: qc.x(i)
    qc.ry(theta, loc[center])
    for li, layer in enumerate(layers):
        phi = pe if li % 2 == 0 else po
        for p, c in layer:
            qc.cx(loc[p], loc[c])
            if phi: qc.rz(phi, loc[c])
    qc.measure_all()
    return qc

configs = [("baseline_plain", PI/2, 0.0, 0.0, False), ("baseline_fala", PI/2, 0.0, 0.0, True)]
for t in (0.6, 0.8, 1.2, 1.4): configs.append((f"theta{t}", PI/2*t, 0, 0, True))
for pe in (-0.5, -0.25, 0.25, 0.5): configs.append((f"phiE{pe}", PI/2, pe, 0, True))
for po in (-0.5, -0.25, 0.25, 0.5): configs.append((f"phiO{po}", PI/2, 0, po, True))
configs.append(("miks+", PI/2*0.8, 0.25, 0.25, True))
configs.append(("miks-", PI/2*0.8, -0.25, -0.25, True))

pubs = [transpile(circ(t, pe, po, up), backend=backend, initial_layout=team, optimization_level=1) for _, t, pe, po, up in configs]
sampler = Sampler(mode=backend)
job = sampler.run(pubs, shots=SHOTS)
print("Job ID:", job.job_id())
r = job.result()

for (name, t, pe, po, up), pub in zip(configs, r):
    counts = pub.data.meas.get_counts()
    if up:
        s = (counts.get(pattern, 0) + counts.get(antipat, 0)) / SHOTS
        print(f"{name}: wzorzec+anty = {100*s:.2f}%")
    else:
        s = (counts.get("0"*K, 0) + counts.get("1"*K, 0)) / SHOTS
        print(f"{name}: |0..0>+|1..1> = {100*s:.2f}%")
