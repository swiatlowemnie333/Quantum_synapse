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
center = max(sub, key=lambda q: len(sub[q]))
depth = {center: 0}; parent = {}
dq = deque([center])
while dq:
    u = dq.popleft()
    for v in sub[u]:
        if v not in depth: depth[v] = depth[u]+1; parent[v] = u; dq.append(v)
layers = [[(parent[v], v) for v in depth if depth[v] == d] for d in range(1, max(depth.values())+1)]
print(f"Druzyna {K}, centrum q{center}, warstw {len(layers)}")

# wzorzec wg PARZYSTOSCI GLEBOKOSCI w drzewie fali
patbits = {q: depth[q] % 2 for q in team}
pattern = "".join(str(patbits[team[K-1-j]]) for j in range(K))
antipat = "".join(str(1 - patbits[team[K-1-j]]) for j in range(K))

def circ(theta, use_pattern=True):
    qc = QuantumCircuit(K)
    if use_pattern:
        for q in team:
            if patbits[q] == 1: qc.x(loc[q])
    qc.ry(theta, loc[center])
    for layer in layers:
        for p, c in layer: qc.cx(loc[p], loc[c])
    qc.measure_all()
    return qc

thetas = [PI/2 * f for f in (0.6, 0.8, 1.0, 1.2)]
pubs = [transpile(circ(t, True), backend=backend, initial_layout=team, optimization_level=1) for t in thetas]
pubs.append(transpile(circ(PI/2, False), backend=backend, initial_layout=team, optimization_level=1))

sampler = Sampler(mode=backend)
job = sampler.run(pubs, shots=SHOTS)
print("Job ID:", job.job_id())
r = job.result()

for t, pub in zip(thetas, r[:-1]):
    counts = pub.data.meas.get_counts()
    s = (counts.get(pattern, 0) + counts.get(antipat, 0)) / SHOTS
    print(f"theta={t:.3f}: wzorzec+anty = {100*s:.2f}%")
counts = r[-1].data.meas.get_counts()
s = (counts.get("0"*K, 0) + counts.get("1"*K, 0)) / SHOTS
print(f"baseline zwykle GHZ: {100*s:.2f}%")
