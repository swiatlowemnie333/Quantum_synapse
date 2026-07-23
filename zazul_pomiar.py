from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit import QuantumCircuit, transpile
from collections import deque, defaultdict

BACKEND_NAME = "ibm_marrakesh"
SHOTS = 4096
DELAY_NS = 50000

service = QiskitRuntimeService()
backend = service.backend(BACKEND_NAME)
cmap = backend.configuration().coupling_map

adj = defaultdict(set)
for a, b in cmap:
    adj[a].add(b)
    adj[b].add(a)
N = len(adj)
layout = list(range(N))

cA = QuantumCircuit(N); cA.measure_all()                          # spoczynek
cB = QuantumCircuit(N); cB.x(range(N)); cB.measure_all()          # energia od razu
cC = QuantumCircuit(N); cC.x(range(N)); cC.delay(DELAY_NS, range(N), unit='ns'); cC.measure_all()   # energia po czasie
cD = QuantumCircuit(N); cD.h(range(N)); cD.delay(DELAY_NS, range(N), unit='ns'); cD.h(range(N)); cD.measure_all()  # faza

cs = [transpile(c, backend=backend, initial_layout=layout, optimization_level=1) for c in (cA, cB, cC, cD)]
sampler = Sampler(mode=backend)
job = sampler.run(cs, shots=SHOTS)
print("Job ID:", job.job_id())
res = job.result()

def frac(pub, q, bit):
    counts = pub.data.meas.get_counts()
    return sum(v for k, v in counts.items() if k[::-1][q] == bit) / SHOTS

# cechy na zywo
m = {}
for q in range(N):
    honest0 = frac(res[0], q, '0')              # uczciwosc przy 0
    honest1 = frac(res[1], q, '1')              # uczciwosc przy 1
    energy  = frac(res[2], q, '1') / max(honest1, 1e-9)   # przezywalnosc energii
    phase   = max(0.0, 2 * (frac(res[3], q, '0') - 0.5))  # przezywalnosc fazy
    m[q] = (energy, phase, (honest0 + honest1) / 2)

def tier(v, vals):
    s = sorted(vals)
    t1, t2 = s[len(s)//3], s[2*len(s)//3]
    return 0 if v < t1 else (1 if v < t2 else 2)

allv = [[m[q][i] for q in range(N)] for i in range(3)]
colors = {q: tuple(tier(m[q][i], allv[i]) for i in range(3)) for q in range(N)}

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
    big = [i for i in isl if len(i) >= 8]
    if big and shown < 4:
        print(f"Klan {c}: wyspy {[len(i) for i in isl][:6]}, najwieksza: {isl[0][:24]}")
        shown += 1

print("\n=== Najszybsze kubity (energia) TOP 10 ===")
for q in sorted(m, key=lambda q: -m[q][0])[:10]:
    e, p, h = m[q]
    print(f"  q{q}: energia {100*e:.0f}% faza {100*p:.0f}% uczciwosc {100*h:.0f}%")

print("\n=== Uszkodzone (najgorsza uczciwosc) ===")
for q in sorted(m, key=lambda q: m[q][2])[:5]:
    print(f"  q{q}: {m[q]}")
