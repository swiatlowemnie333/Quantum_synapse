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

with open("sonda_108_RIGETTI.qasm", "rb") as f:
    qasm_bytes = f.read()

print("=== SONDA 108q RIGETTI (8192 shots) ===")
config = JobSubmissionConfig(
    organization_id=org_id,
    backend_class_id="rigetti:cepheus-1-108q",
    name="Zazul Sonda 108q",
    job_subcategory_id="phys:hds",
    shots=8192,
    execution_plan="auto",
    queue_priority="auto",
    auto_approve_quote=True,
    verbose=True,
)

job = scheduler.submit_job(config, file_content=qasm_bytes)
print(f"Job ID: {job.id}")
print(f"Status: {job.status}")

print("\nCzekam...")
while job.status not in ['COMPLETED', 'FAILED', 'ERROR']:
    time.sleep(30)
    job = scheduler.get_job(job.id)
    print(f"Status: {job.status}")

if job.status == 'COMPLETED':
    result = scheduler.download_job_output(job)
    print(f"\n=== WYNIKI 108q ===")
    print(result)
    import json
    with open('sonda_rigetti_108q.json', 'w') as f:
        json.dump(result, f, indent=2)
    print("Zapisano!")
else:
    print(f"FAILED: {job.error}")

scheduler.close()
