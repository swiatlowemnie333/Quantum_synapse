from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit import QuantumCircuit, transpile
from collections import deque, defaultdict
import math

OLD_JOB = "d9gr51khonhs73ac42mg"
SHOTS = 4096
DELAYS_US = [0, 5, 10, 20, 35, 50]
TARGET = 32
BLACKLIST = {82, 26, 72, 76}

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

sub = {q: [v for v in adj[q] if v in team] for q in team}
center = max(sub, key=lambda q: len(sub[q]))
depth = {center: 0}; parent = {}
dq = deque([center])
while dq:
    u = dq.popleft()
    for v in sub[u]:
        if v not in depth: depth[v] = depth[u]+1; parent[v] = u; dq.append(v)
leaf = max(depth, key=lambda q: depth[q])
path = []
u = leaf
while u != center: path.append(u); u = parent[u]
path.append(center)
K = len(path)
print(f"Linia: {K} kubitow")

def holes_circuit(start_holes, jumps, back=False):
    qc = QuantumCircuit(K)
    for i in range(K):
        if i not in start_holes: qc.x(i)
    seq = list(range(jumps))
    for j in seq:
        qc.swap(j, j+1)
    if back:
        for j in reversed(seq):
            qc.swap(j, j+1)
    qc.measure_all()
    return qc

J = 4
circs = [
    ("1 dziura tam+powrot", holes_circuit([0], J, back=True)),
    ("2 dziury, 4 skoki", holes_circuit([0, K-1], 0)),  # baseline 2 dziur bez ruchu
    ("2 dziury po skokach", holes_circuit([0, 2], J)),
]
pubs = [transpile(c, backend=backend, initial_layout=path, optimization_level=1) for _, c in circs]
sampler = Sampler(mode=backend)
job = sampler.run(pubs, shots=SHOTS)
print("Job ID:", job.job_id())
r = job.result()

def hole_positions(k):
    return tuple(i for i, b in enumerate(k[::-1]) if b == '0')

for (name, _), pub in zip(circs, r):
    counts = pub.data.meas.get_counts()
    from collections import Counter
    pos_counter = Counter()
    for k, v in counts.items():
        pos_counter[hole_positions(k)] += v
    top = pos_counter.most_common(5)
    print(f"\n=== {name} ===")
    for pos, v in top:
        print(f"  dziury na {pos}: {100*v/SHOTS:.1f}%")
