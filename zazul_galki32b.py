from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit import QuantumCircuit, transpile
from collections import deque, defaultdict
import math, itertools

OLD_JOB = "d9gr51khonhs73ac42mg"
SHOTS = 4096
DELAYS_US = [0, 5, 10, 20, 35, 50]
TARGET = 32
BLACKLIST = {82, 26, 72, 76}
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

def wave(qc, reverse=False, phi=0.0):
    for layer in (layers[::-1] if reverse else layers):
        for p, c in layer:
            qc.cx(loc[p], loc[c])
            if phi: qc.rz(phi, loc[c])

def circ(tf, tb, phi):
    qc = QuantumCircuit(K)
    qc.ry(tf, loc[center])
    wave(qc, phi=phi)
    qc.barrier()
    wave(qc, reverse=True, phi=-phi)
    qc.ry(tb, loc[center])
    qc.measure_all()
    return qc

sampler = Sampler(mode=backend)
def batch(configs, tag):
    pubs = [transpile(circ(*c), backend=backend, initial_layout=team, optimization_level=1) for c in configs]
    job = sampler.run(pubs, shots=SHOTS)
    print(f"[{tag}] job {job.job_id()}")
    res = job.result()
    out = []
    for c, pub in zip(configs, res):
        p0 = pub.data.meas.get_counts().get("0"*K, 0) / SHOTS
        out.append((p0, c))
    out.sort(reverse=True)
    print(f"  best: {100*out[0][0]:.2f}% @ {tuple(round(x,3) for x in out[0][1])}")
    return out

best_score, bcfg = 0.1414, (0.971, -0.971, 0.0)
print(f"Start (z rundy 1): {100*best_score:.2f}%\n")

for rnd in (2, 3):
    span = 0.5 / rnd
    improved = False
    per = []
    for gi, name in enumerate(["theta_przod", "theta_tyl", "phi"]):
        grid = [bcfg[gi] + k*span/2 for k in (-2, -1, 1, 2)]
        configs = [bcfg[:gi] + (g,) + bcfg[gi+1:] for g in grid]
        r = batch(configs, f"r{rnd} {name}")
        vals = sorted({x[1][gi] for x in r[:2]} | {bcfg[gi]})
        per.append(vals)
        if r[0][0] > best_score + 1e-4:
            best_score, bcfg = r[0]
            improved = True
            print(f"  -> poprawa! {100*best_score:.2f}%")
        else:
            print(f"  -> cofam (zostaje {tuple(round(x,3) for x in bcfg)})")
    mixes = [c for c in itertools.product(*per) if c != bcfg][:14]
    r = batch(mixes, f"r{rnd} MIKSY")
    if r[0][0] > best_score + 1e-4:
        best_score, bcfg = r[0]
        improved = True
        print(f"  -> miksy poprawily! {100*best_score:.2f}%")
    if not improved:
        print("Szczyt osiagniety -> stop")
        break

print(f"\n=== FINAL 32q: {100*best_score:.2f}% @ {tuple(round(x,4) for x in bcfg)} ===")
print(f"(bylo: 7.7% fabrycznie -> teraz: {100*best_score:.2f}%)")
