from openquantum_sdk.auth import ClientCredentials, ClientCredentialsAuth
from openquantum_sdk.clients import SchedulerClient, JobSubmissionConfig
import time

auth = ClientCredentialsAuth(
    creds=ClientCredentials(
        client_id="s_a6106557ee774c9c9365d47088e2edcf",
        client_secret="7204151edeff758d9d7e118e68adafe6bbbe2395ff242336d9177b57b978aefb"
    )
)
scheduler = SchedulerClient(auth=auth)
org_id = "fa4c0d3f-d89b-469c-a41f-7bc315867b4c"

with open("sonda_32_qasm2.qasm", "rb") as f:
    qasm = f.read()

print("=== KALIBRACJA 32q IQM EMERALD ===")
config = JobSubmissionConfig(
    organization_id=org_id,
    backend_class_id="iqm:emerald",
    name="Zazul Kalibracja 32q",
    job_subcategory_id="phys:hds",
    shots=8192,
    execution_plan="auto",
    queue_priority="auto",
    auto_approve_quote=True,
    verbose=True,
)

job = scheduler.submit_job(config, file_content=qasm)
print(f"Job ID: {job.id}")
print(f"Status: {job.status}")

print("\nCzekam na wynik...")
while job.status not in ['COMPLETED', 'FAILED', 'ERROR']:
    time.sleep(30)
    job = scheduler.get_job(job.id)
    print(f"Status: {job.status}")

if job.status == 'COMPLETED':
    result = scheduler.download_job_output(job)
    print(f"\n=== WYNIKI 32q ===")
    print(result)
    
    import json
    with open('kalibracja_32q.json', 'w') as f:
        json.dump(result, f, indent=2)
    print("Zapisano: kalibracja_32q.json")
    
    # Mapa ciepła
    if isinstance(result, dict) and 'counts' in result:
        counts = result['counts']
        total = sum(counts.values())
        print(f"\nTotal shots: {total}")
        print(f"Unique states: {len(counts)}")
        
        top = sorted(counts.items(), key=lambda x: -x[1])[:5]
        print("\nTop 5:")
        for state, count in top:
            print(f"  {state}: {count} ({count/total*100:.1f}%)")
        
        print("\nMarginal P(|0>) per qubit:")
        for q in range(32):
            p0 = sum(c for s, c in counts.items() if s[31-q] == '0') / total
            bar = '█' * int(p0 * 10) + '░' * (10 - int(p0 * 10))
            kolor = 'ZIELONY' if p0 >= 0.99 else 'ZOLTY' if p0 >= 0.97 else 'CZERWONY'
            print(f"  q{q:2d}: {p0:.2f} {bar} {kolor}")
else:
    print(f"FAILED: {job.error}")

scheduler.close()
