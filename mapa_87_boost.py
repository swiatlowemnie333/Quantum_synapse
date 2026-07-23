import os, json
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService(
    channel='ibm_quantum_platform',
    token=os.getenv('IBM_QUANTUM_API_KEY')
)
backend = service.backend('ibm_marrakesh')

job_id = "d8r9jl6ab0ds73drdnig"
print(f"=== Pobieram rekord 87.5% | {job_id} ===")

job = service.job(job_id)
result = job.result()
counts = result[0].data.c.get_counts()
total = sum(counts.values())

n = 32

print("\n" + "=" * 75)
print("ZAZUL WORLD STS | MAPA 87.5% | Dokręcenie fazowe")
print("=" * 75)
print(f"Echo |0...0>: {counts.get('0'*n, 0)}/{total} = {counts.get('0'*n, 0)/total*100:.1f}%")
print()

print("qubit | P(|0>) | brak   | boost_rz | kolor      | wykres")
print("-" * 75)

boosty = {}
for i in range(n):
    pos = i
    count_0 = sum(c for bits, c in counts.items() if bits[pos] == '0')
    p0 = count_0 / total
    brak = 1.0 - p0
    
    # Mikro-boost: proporcjonalny do braku, ale MAŁY (x0.3 rad)
    # Na 16q działało ~0.001-0.003, na 32q max 0.005
    boost = round(brak * 0.3, 5) if brak > 0.001 else 0.0
    boosty[i] = boost
    
    if p0 >= 0.995:
        kolor = "ZIELONY"
    elif p0 >= 0.99:
        kolor = "ZOLTY  "
    else:
        kolor = "CZERWONY"
    
    bar = '█' * int(p0 * 10) + '░' * (10 - int(p0 * 10))
    print(f"q{i:2d}   | {p0:.4f} | {brak:.4f} | {boost:+.5f}  | {kolor} | {bar}")

with open('boosty_mikro.json', 'w') as f:
    json.dump(boosty, f, indent=2)

zolte = [k for k,v in boosty.items() if v > 0]
print(f"\n{'='*75}")
print(f"Qubity do mikro-boosta: {zolte}")
print(f"Wartości: {[boosty[k] for k in zolte]}")
print(f"✅ Zapisano: boosty_mikro.json")
print(f"{'='*75}")
print("\n⚠️  Poprzednio: boosty ~0.05 rad -> 0%")
print("    Teraz: boosty ~0.001-0.003 rad -> powinno dać 90%+")
