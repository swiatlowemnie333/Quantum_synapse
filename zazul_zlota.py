from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit import QuantumCircuit, transpile
from collections import deque, defaultdict
import math

OLD_JOB = "d9gr51khonhs73ac42mg"
SHOTS = 8192
DELAYS_US = [0, 5, 10, 20, 35, 50]
T1_MIN, T2_MIN = 150, 40
BLACKLIST = {82}

service = QiskitRuntimeService()
backend = service.backend("ibm_marrakesh")
cmap = backend.configuration().coupling_map

adj = defaultdict(set)
for a, b in cmap:
    adj[a].add(b); adj[b].add(a)
N = len(adj)

# --- odczyt fitow z poprzedniego joba ---
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

# --- wybor zlotej druzyny: spojna, T1>=150, T2>=40, bez blacklist ---
ok = {q for q in range(N) if t1[q] >= T1_MIN and t2[q] >= T2_MIN and q not in BLACKLIST}
print(f"Kandydaci (T1>={T1_MIN}, T2>={T2_MIN}): {len(ok)} -> {sorted(ok)}")

# najwieksza spojna wyspa wsrod kandydatow
seen, best_island = set(), []
for q in ok:
    if q in seen: continue
    comp, dq = [], deque([q]); seen.add(q)
    while dq:
        u = dq.popleft(); comp.append(u)
        for v in adj[u]:
            if v in ok and v not in seen: seen.add(v); dq.append(v)
    if len(comp) > len(best_island): best_island = sorted(comp)
print(f"Zlota druzyna ({len(best_island)} kubitow): {best_island}")
for q in best_island:
    print(f"  q{q}: T1={t1[q]:.0f}us T2={t2[q]:.0f}us")

# --- fala GHZ + echo na druzynie ---
team = best_island
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

def wave(qc, reverse=False):
    for layer in (layers[::-1] if reverse else layers):
        for p, c in layer: qc.cx(loc[p], loc[c])

ghz = QuantumCircuit(K); ghz.h(loc[center]); wave(ghz); ghz.measure_all()
echo = QuantumCircuit(K); echo.h(loc[center]); wave(echo); echo.barrier(); wave(echo, reverse=True); echo.h(loc[center]); echo.measure_all()

ghz_t = transpile(ghz, backend=backend, initial_layout=team, optimization_level=1)
echo_t = transpile(echo, backend=backend, initial_layout=team, optimization_level=1)
print(f"Glebokosc: GHZ={ghz_t.depth()} Echo={echo_t.depth()}")

sampler = Sampler(mode=backend)
job = sampler.run([ghz_t, echo_t], shots=SHOTS)
print("Job ID:", job.job_id())
r = job.result()

for name, pub in zip(["GHZ", "ECHO"], r):
    counts = pub.data.meas.get_counts()
    zeros = counts.get("0"*K, 0)
    print(f"\n=== {name} na zlotej druzynie ===")
    print(f"|0...0>: {zeros}/{SHOTS} = {100*zeros/SHOTS:.1f}%")
    if name == "GHZ":
        ones = counts.get("1"*K, 0)
        print(f"|1...1>: {ones}/{SHOTS} = {100*ones/SHOTS:.1f}%")
        print(f"Suma populacji GHZ: {100*(zeros+ones)/SHOTS:.1f}%")
    else:
        rates = sorted((100*sum(v for k, v in counts.items() if k[::-1][i] == '0')/SHOTS, i) for i in range(K))
        print("Powrot per kubit (najslabsze 5):")
        for pct, i in rates[:5]:
            print(f"  q{team[i]}: {pct:.1f}%")
    print("Top 5:", sorted(counts.items(), key=lambda x: -x[1])[:5])
