from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit import QuantumCircuit, transpile
from collections import deque

BACKEND_NAME = "ibm_marrakesh"
SHOTS = 8192

service = QiskitRuntimeService()
backend = service.backend(BACKEND_NAME)
cmap = backend.configuration().coupling_map

adj = {}
for a, b in cmap:
    adj.setdefault(a, set()).add(b)
    adj.setdefault(b, set()).add(a)

center = max(adj, key=lambda q: len(adj[q]))
N = len(adj)
print(f"Backend: {BACKEND_NAME}, kubitow: {N}, centrum: q{center} (stopien {len(adj[center])})")

depth = {center: 0}
parent = {}
dq = deque([center])
while dq:
    u = dq.popleft()
    for v in adj[u]:
        if v not in depth:
            depth[v] = depth[u] + 1
            parent[v] = u
            dq.append(v)

max_d = max(depth.values())
layers = []
for d in range(1, max_d + 1):
    layers.append([(parent[v], v) for v in depth if depth[v] == d])
print(f"Promien drzewa: {max_d} warstw")

def wave(qc, reverse=False):
    seq = layers[::-1] if reverse else layers
    for layer in seq:
        for p, c in layer:
            qc.cx(p, c)

ghz = QuantumCircuit(N)
ghz.h(center)
wave(ghz)
ghz.measure_all()

echo = QuantumCircuit(N)
echo.h(center)
wave(echo)
echo.barrier()
wave(echo, reverse=True)
echo.h(center)
echo.measure_all()

ghz_t = transpile(ghz, backend=backend, optimization_level=1)
echo_t = transpile(echo, backend=backend, optimization_level=1)
print(f"GHZ glebokosc po transpilacji: {ghz_t.depth()}, Echo: {echo_t.depth()}")

sampler = Sampler(mode=backend)
job = sampler.run([ghz_t, echo_t], shots=SHOTS)
print("Job ID:", job.job_id())
res = job.result()

for name, pub in zip(["GHZ", "ECHO"], res):
    counts = pub.data.meas.get_counts()
    zeros = counts.get("0" * N, 0)
    print(f"\n=== {name} ===")
    print(f"|0...0>: {zeros}/{SHOTS} = {100*zeros/SHOTS:.1f}%")
    if name == "GHZ":
        ones = counts.get("1" * N, 0)
        print(f"|1...1>: {ones}/{SHOTS} = {100*ones/SHOTS:.1f}%")
        print(f"Suma populacji GHZ: {100*(zeros+ones)/SHOTS:.1f}%")
    else:
        print("Per-kubit powrot do |0> (najgorsze 10):")
        rates = []
        for q in range(N):
            ok = sum(v for k, v in counts.items() if k[::-1][q] == "0")
            rates.append((100 * ok / SHOTS, q))
        rates.sort()
        for pct, q in rates[:10]:
            print(f"  q{q}: {pct:.1f}%")
    print("Top 5:", sorted(counts.items(), key=lambda x: -x[1])[:5])
