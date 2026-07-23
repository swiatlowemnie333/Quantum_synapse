from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit import QuantumCircuit, transpile
from collections import deque, defaultdict
import math, functools

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
    slope = num/den if den else 0
    return -1/slope if slope < 0 else float('inf')

t1, t2 = {}, {}
for q in range(N):
    ep = [frac(res[2*i], q, '1') for i in range(6)]
    t1[q] = fit_t(DELAYS_US, [p/max(ep[0],1e-3) for p in ep])
    fp = [max(0.0, 2*(frac(res[2*i+1], q, '0')-0.5)) for i in range(6)]
    t2[q] = fit_t(DELAYS_US, [max(p/max(fp[0],1e-3),1e-3) for p in fp])

def score(q):
    return min(t1[q], 250) + 3 * min(t2[q], 100)

# zachlanny wzrost SPOJNEJ druzyny od najlepszego kubitu
pool = [q for q in range(N) if q not in BLACKLIST]
seed = max(pool, key=score)
team = [seed]
while len(team) < TARGET:
    cand = {}
    for q in team:
        for v in adj[q]:
            if v not in team and v not in BLACKLIST:
                cand[v] = max(cand.get(v, 0), score(v))
    if not cand: break
    team.append(max(cand, key=cand.get))
print(f"Druzyna spojna ({len(team)}), start od q{seed}:")
print(team)
print(f"Srednie T1={sum(t1[q] for q in team)/len(team):.0f}us T2={sum(t2[q] for q in team)/len(team):.0f}us")

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
print(f"Centrum: q{center}, warstw: {len(layers)}, kubity objete fala: {len(depth)}")

def wave(qc, reverse=False):
    for layer in (layers[::-1] if reverse else layers):
        for p, c in layer: qc.cx(loc[p], loc[c])

def make_echo(nx=1):
    qc = QuantumCircuit(K)
    qc.h(loc[center])
    for _ in range(nx): wave(qc)
    qc.barrier()
    for _ in range(nx): wave(qc, reverse=True)
    qc.h(loc[center]); qc.measure_all()
    return qc

ghz = QuantumCircuit(K); ghz.h(loc[center]); wave(ghz); ghz.measure_all()
cal0 = QuantumCircuit(K); cal0.measure_all()
cal1 = QuantumCircuit(K); cal1.x(range(K)); cal1.measure_all()

circuits = [ghz, make_echo(1), make_echo(3), cal0, cal1]
pubs = [transpile(c, backend=backend, initial_layout=team, optimization_level=1) for c in circuits]
print(f"Glebokosc: GHZ={pubs[0].depth()} Echo1x={pubs[1].depth()} Echo3x={pubs[2].depth()}")

sampler = Sampler(mode=backend)
job = sampler.run(pubs, shots=SHOTS)
print("Job ID:", job.job_id())
r = job.result()

cg = r[0].data.meas.get_counts()
e1 = r[1].data.meas.get_counts()
e3 = r[2].data.meas.get_counts()
c0 = r[3].data.meas.get_counts()
c1 = r[4].data.meas.get_counts()

zeros_g = cg.get("0"*K, 0); ones_g = cg.get("1"*K, 0)
raw1 = e1.get("0"*K, 0)/SHOTS; raw3 = e3.get("0"*K, 0)/SHOTS
leak1 = 1 - raw1 - e1.get("1"*K, 0)/SHOTS

hon = []
for i in range(K):
    h0 = sum(v for k, v in c0.items() if k[::-1][i] == '0')/SHOTS
    h1 = sum(v for k, v in c1.items() if k[::-1][i] == '1')/SHOTS
    hon.append((h0+h1)/2)
corr = functools.reduce(lambda a, b: a*b, hon, 1.0)

print(f"\n=== GHZ {K}q: {100*zeros_g/SHOTS:.1f}% + {100*ones_g/SHOTS:.1f}% = {100*(zeros_g+ones_g)/SHOTS:.1f}% ===")
print(f"\n=== ECHO {K}q ===")
print(f"surowe 1x: {100*raw1:.1f}%  | 3x: {100*raw3:.1f}%")
zne = min(raw1 + (raw1 - raw3)/2, 1.0)
print(f"ZNE: {100*zne:.1f}%  | korekta odczytu: {min(100*raw1/max(corr,1e-9),100):.1f}% (prod {100*corr:.1f}%)")
print(f"selekcia: bez przecieku {100*(1-leak1):.1f}%")

rates = sorted((100*sum(v for k, v in e1.items() if k[::-1][i]=='0')/SHOTS, team[i]) for i in range(K))
print("\nNajslabsze 8:", [(q, f"{p:.0f}%") for p, q in rates[:8]])
print("Najlepsze 5:", [(q, f"{p:.0f}%") for p, q in rates[-5:]])
