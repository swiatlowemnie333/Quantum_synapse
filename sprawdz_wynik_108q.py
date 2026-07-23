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

print(f"=== Sprawdzam job {job_id} ===")

job = scheduler.get_job(job_id)
print(f"Status: {job.status}")

if job.status == 'COMPLETED':
    result = scheduler.download_job_output(job)
    print(f"\n=== WYNIKI 108q ===")
    print(result)
    
    import json
    with open('wynik_108q.json', 'w') as f:
        json.dump(result, f, indent=2)
    print("\n✅ Zapisano: wynik_108q.json")
    
    # Generuj mape ciepla
    if isinstance(result, dict) and 'counts' in result:
        print("\n=== MAPA KUBITOW 108q ===")
        counts = result['counts']
        total = sum(counts.values())
        
        for q in range(108):
            p0 = sum(c for s, c in counts.items() if s[107-q] == '0') / total
            bar = '█' * int(p0 * 10) + '░' * (10 - int(p0 * 10))
            kolor = 'ZIELONY' if p0 >= 0.99 else 'ZOLTY' if p0 >= 0.97 else 'CZERWONY'
            print(f"  q{q:3d}: {p0:.2f} {bar} {kolor}")
            
elif job.status in ['FAILED', 'ERROR']:
    print(f"❌ FAILED: {job.error}")
else:
    print(f"⏳ Job w trakcie... status: {job.status}")
    print("Sprawdz ponownie za 10-15 minut.")

scheduler.close()
