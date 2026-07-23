from openquantum_sdk.auth import ClientCredentials, ClientCredentialsAuth
from openquantum_sdk.clients import SchedulerClient
import time

auth = ClientCredentialsAuth(
    creds=ClientCredentials(
        client_id="s_a6106557ee774c9c9365d47088e2edcf",
        client_secret="7204151edeff758d9d7e118e68adafe6bbbe2395ff242336d9177b57b978aefb"
    )
)
scheduler = SchedulerClient(auth=auth)

job_id = "ba45d39c-6a8b-4c04-845a-0259d7913aca"

print(f"=== AUTO-CZEKANIE NA {job_id} ===")
print("Sprawdzam co 30 sekund...")

while True:
    job = scheduler.get_job(job_id)
    print(f"Status: {job.status}")
    
    if job.status == 'COMPLETED':
        result = scheduler.download_job_output(job)
        print(f"\n🎉 JOB SKONCZONY!")
        
        import json
        with open('wynik_108q.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("Zapisano: wynik_108q.json")
        
        # MAPA KUBITOW
        if isinstance(result, dict) and 'counts' in result:
            counts = result['counts']
            total = sum(counts.values())
            
            print(f"\n=== MAPA KUBITOW 108q ===")
            print(f"Total shots: {total}")
            print(f"Unique states: {len(counts)}")
            
            # Top 5 wynikow
            top = sorted(counts.items(), key=lambda x: -x[1])[:5]
            print("\nTop 5:")
            for state, count in top:
                print(f"  {state}: {count} ({count/total*100:.1f}%)")
            
            # Marginal P(|0>) per qubit
            print("\nMarginal P(|0>) per qubit:")
            for q in range(108):
                p0 = sum(c for s, c in counts.items() if s[107-q] == '0') / total
                bar = '█' * int(p0 * 10) + '░' * (10 - int(p0 * 10))
                kolor = 'ZIELONY' if p0 >= 0.99 else 'ZOLTY' if p0 >= 0.97 else 'CZERWONY'
                print(f"  q{q:3d}: {p0:.2f} {bar} {kolor}")
            
            # Zapisz do pliku tekstowego
            with open('mapa_108q.txt', 'w') as f:
                f.write("=== MAPA KUBITOW 108q ===\n")
                f.write(f"Total shots: {total}\n")
                f.write(f"Unique states: {len(counts)}\n\n")
                for q in range(108):
                    p0 = sum(c for s, c in counts.items() if s[107-q] == '0') / total
                    kolor = 'ZIELONY' if p0 >= 0.99 else 'ZOLTY' if p0 >= 0.97 else 'CZERWONY'
                    f.write(f"q{q:3d}: {p0:.3f} -> {kolor}\n")
            print("\nZapisano: mapa_108q.txt")
        
        break
        
    elif job.status in ['FAILED', 'ERROR']:
        print(f"❌ FAILED: {job.error}")
        break
    
    time.sleep(30)

scheduler.close()
print("\n=== KONIEC ===")
