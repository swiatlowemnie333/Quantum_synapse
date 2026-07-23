from qiskit_ibm_runtime import QiskitRuntimeService
from collections import deque, defaultdict
import math

JOB_ID = "d9gqsld0k0jc738h8230"
SHOTS = 4096

service = QiskitRuntimeService()
job = service.job(JOB_ID)
print("Status:", job.status())
res = job.result()

backend = service.backend("ibm_marrakesh")
cmap = backend.configuration().coupling_map
props = backend.properties()

adj = defaultdict(set)
for a, b in cmap:
    adj[a].add(b); adj[b].add(a)
N = len(adj)

def frac(pub, q, bit):
    counts = pub.data.meas.get_counts()
    return sum(v for k, v in counts.items() if k[::-1][q] == bit) / SHOTS

m, freq = {}, {}
for q in range(N):
    h0 = frac(res[0], q, '0'); h1 = frac(res[1], q, '1')
    e = frac(res[2], q, '1') / max(h1, 1e-9)
    p = max(0.0, 2 * (frac(res[3], q, '0') - 0.5))
    m[q] = (e, p, (h0 + h1) / 2)
    try: freq[q] = props.frequency(q) / 1e9
    except Exception: freq[q] = 0.0

names = ["energia", "faza", "uczciwosc"]
cols = [[m[q][i] for q in range(N)] for i in range(3)]

def pearson(x, y):
    n = len(x); mx = sum(x)/n; my = sum(y)/n
    cov = sum((a-mx)*(b-my) for a, b in zip(x, y))/n
    sx = math.sqrt(sum((a-mx)**2 for a in x)/n); sy = math.sqrt(sum((b-my)**2 for b in y)/n)
    return cov/(sx*sy) if sx*sy > 0 else 0.0

print("\n=== KORELACJE miedzy cechami ===")
for i in range(3):
    for j in range(i+1, 3):
        r = pearson(cols[i], cols[j])
        print(f"  {names[i]} x {names[j]}: r = {r:.3f}")

print("\n=== KORELACJA z czestotliwoscia (sygnatura TLS) ===")
fv = [freq[q] for q in range(N)]
for i in range(3):
    print(f"  czestotliwosc x {names[i]}: r = {pearson(fv, cols[i]):.3f}")

print("\n=== KORELACJA PRZESTRZENNA (sasiedzi vs losowe) ===")
import random
random.seed(7)
neigh = []
for a, b in cmap:
    for i in range(3):
        neigh.append((cols[i][a], cols[i][b]))
far = []
for _ in range(400):
    a, b = random.sample(range(N), 2)
    if b not in adj[a]:
        i = random.randrange(3)
        far.append((cols[i][a], cols[i][b]))
print(f"  sasiedzi: r = {pearson([p[0] for p in neigh], [p[1] for p in neigh]):.3f}")
print(f"  dalekie:  r = {pearson([p[0] for p in far], [p[1] for p in far]):.3f}")

def tier(v, vals):
    s = sorted(vals); t1, t2 = s[len(s)//3], s[2*len(s)//3]
    return 0 if v < t1 else (1 if v < t2 else 2)

colors = {q: tuple(tier(m[q][i], cols[i]) for i in range(3)) for q in range(N)}
groups = defaultdict(list)
for q, c in colors.items(): groups[c].append(q)

print("\n=== KLANY (energia,faza,uczciwosc) ===")
for c, qs in sorted(groups.items(), key=lambda x: (-sum(x[0]), -len(x[1]))):
    print(f"  {c}: {len(qs)} kubitow")

def islands(qs):
    qs, seen, out = set(qs), set(), []
    for q in qs:
        if q in seen: continue
        comp, dq = [], deque([q]); seen.add(q)
        while dq:
            u = dq.popleft(); comp.append(u)
            for v in adj[u]:
                if v in qs and v not in seen: seen.add(v); dq.append(v)
        out.append(sorted(comp))
    return sorted(out, key=len, reverse=True)

print("\n=== WYSPY najlepszych klanow ===")
shown = 0
for c, qs in sorted(groups.items(), key=lambda x: -sum(x[0])):
    isl = islands(qs)
    if isl and len(isl[0]) >= 8 and shown < 4:
        print(f"Klan {c}: rozmiary wysp {[len(i) for i in isl][:6]}, najwieksza: {isl[0][:24]}")
        shown += 1

print("\n=== TOP 10 (energia) ===")
for q in sorted(m, key=lambda q: -m[q][0])[:10]:
    e, p, h = m[q]
    print(f"  q{q}: E{100*e:.0f}% F{100*p:.0f}% U{100*h:.0f}% f={freq[q]:.2f}GHz")

print("\n=== WYRZUTNIE (lamia reguly: faza duza, energia mala lub odwrotnie) ===")
score = {q: abs(cols[1][q] - cols[0][q]) for q in range(N)}
for q in sorted(score, key=lambda q: -score[q])[:5]:
    e, p, h = m[q]
    print(f"  q{q}: E{100*e:.0f}% F{100*p:.0f}% U{100*h:.0f}%")
