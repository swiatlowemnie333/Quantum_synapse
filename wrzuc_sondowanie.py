import os
from openquantum_sdk.clients import SchedulerClient, JobSubmissionConfig

client_id = os.getenv('OPENQUANTUM_CLIENT_ID')
secret = os.getenv('OPENQUANTUM_CLIENT_SECRET')

print(f"Client ID: {client_id[:20]}...")

scheduler = SchedulerClient()

# Sondowanie 54q na IQM Emerald - PUBLIC (darmowe $50)
config = JobSubmissionConfig(
    backend_class_id="iqm:emerald",
    job_subcategory_id="public",  # <-- DODANE
    name="Zazul Kalibracja 54q",
    shots=8192,
)

job = scheduler.submit_job(config, file_path="sonda_54_IQM_kalibracja.qasm")
print(f"\nJob wyslany!")
print(f"Job ID: {job.id}")
print(f"Status: {job.status}")

import time
print("\nCzekam na wynik...")
while job.status not in ['COMPLETED', 'FAILED', 'ERROR']:
    time.sleep(15)
    job = scheduler.get_job(job.id)
    print(f"  Status: {job.status}")

if job.status == 'COMPLETED':
    result = scheduler.download_job_output(job)
    print(f"\n=== WYNIKI KALIBRACJI ===")
    print(result)
    with open('wyniki_kalibracji_54q.json', 'w') as f:
        f.write(str(result))
    print("Zapisano: wyniki_kalibracji_54q.json")
else:
    print(f"Job status: {job.status}")
    if hasattr(job, 'error'):
        print(f"Error: {job.error}")
