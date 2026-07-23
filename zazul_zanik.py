from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit import QuantumCircuit, transpile
from collections import defaultdict
import math

BACKEND_NAME = "ibm_marrakesh"
SHOTS = 2048
DELAYS_US = [0, 5, 10, 20, 35, 50]

service = QiskitRuntimeService()
backend = service.backend(BACKEND_NAME)
cmap = backend.configuration().coupling_map

adj = defaultdict(set)
for a, b in cmap:
    adj[a].add(b); adj[b].add(a)
N = len(adj)
layout = list(range(N))

pubs = []
for d in DELAYS_US:
    c1 = QuantumCircuit(N); c1.x(range(N))
    if d: c1.delay(int(d*1000), range(N), unit='ns')
    c1.measure_all(); pubs.append(c1)
    c2 = QuantumCircuit(N); c2.h(range(N))
    if d: c2.delay(int(d*1000), range(N), unit='ns')
    c2.h(range(N)); c2.measure_all(); pubs.append(c2)

cs = [transpile(c, backend=backend, initial_layout=layout, optimization_level=1) for c in pubs]
sampler = Sampler(mode=backend)
job = sampler.run(cs, shots=SHOTS)
print("Job ID:", job.job_id())
res = job.result()

def frac(pub, q, bit):
    counts = pub.data.meas.get_counts()
    return sum(v for k, v in counts.items() if k[::-1][q] == bit) / SHOTS

def fit_t(times, probs):
    # log-liniowe dopasowanie: p(t) = a * exp(-t/T)
    pts = [(t, math.log(max(p, 1e-3))) for t, p in zip(times, probs)]
    n = len(pts); mx = sum(t for t,_ in pts)/n; my = sum(l for _,l in pts)/n
    num = sum((t-mx)*(l-my) for t,l in pts); den = sum((t-mx)**2 for t,_ in pts)
    slope = num/den if den else 0
    return -1/slope if slope < 0 else float('inf')

print("\nkubit: T1[us] T2[us] (fit z 6 punktow)")
t1s, t2s = {}, {}
for q in range(N):
    e_probs = [frac(res[2*i], q, '1') for i in range(len(DELAYS_US))]
    e0 = max(e_probs[0], 1e-3)
    t1 = fit_t(DELAYS_US, [max(p, 1e-3)/e0 for p in e_probs])
    f_probs = [max(0.0, 2*(frac(res[2*i+1], q, '0')-0.5)) for i in range(len(DELAYS_US))]
    f0 = max(f_probs[0], 1e-3)
    t2 = fit_t(DELAYS_US, [max(p/f0, 1e-3) for p in f_probs])
    t1s[q] = t1; t2s[q] = t2

print("\n=== TOP 15 T1 ===")
for q in sorted(t1s, key=lambda q: -t1s[q])[:15]:
    print(f"  q{q}: T1={t1s[q]:.0f}us T2={t2s[q]:.0f}us")

print("\n=== TOP 15 T2 ===")
for q in sorted(t2s, key=lambda q: -t2s[q])[:15]:
    print(f"  q{q}: T1={t1s[q]:.0f}us T2={t2s[q]:.0f}us")

print("\n=== Najgorsze 10 ===")
for q in sorted(t1s, key=lambda q: t1s[q])[:10]:
    print(f"  q{q}: T1={t1s[q]:.0f}us T2={t2s[q]:.0f}us")

vals1 = sorted(t1s.values()); vals2 = sorted(t2s.values())
med1 = vals1[N//2]; med2 = vals2[N//2]
print(f"\nMediana: T1={med1:.0f}us T2={med2:.0f}us")

def pearson(x, y):
    n=len(x); mx=sum(x)/n; my=sum(y)/n
    cov=sum((a-mx)*(b-my) for a,b in zip(x,y))/n
    sx=math.sqrt(sum((a-mx)**2 for a in x)/n); sy=math.sqrt(sum((b-my)**2 for b in y)/n)
    return cov/(sx*sy) if sx*sy>0 else 0.0

print(f"\nKorelacja T1 x T2: r = {pearson(list(t1s.values()), list(t2s.values())):.3f}")

# granica fizyczna: T2 <= 2*T1
bad = [q for q in range(N) if t2s[q] > 2*t1s[q] + 5]
print(f"Kubity lamiaace granice T2<=2*T1 (podejrzane pomiary): {len(bad)} {bad[:10]}")
