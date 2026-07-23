import os
from openquantum_sdk.clients import SchedulerClient, JobSubmissionConfig

# NOWE KLUCZE
os.environ['OPENQUANTUM_CLIENT_ID'] = 's_a6106557ee774c9c9365d47088e2edcf'
os.environ['OPENQUANTUM_CLIENT_SECRET'] = '7204151edeff758d9d7e118e68adafe6bbbe2395ff242336d9177b57b978aefb'

print("=== TEST NOWYCH KLUCZY ===")

try:
    scheduler = SchedulerClient()
    orgs = scheduler.management.list_user_organizations(limit=1)
    print(f"✅ DZIALA! Orgs: {orgs}")
    
    # PUSZCZAMY JOB OD RAZU
    print("\n=== PUSZCZAM SONDOVANIE 54q IQM ===")
    config = JobSubmissionConfig(
        backend_class_id="iqm:emerald",
        name="Zazul Sonda 54q",
        shots=8192,
    )
    job = scheduler.submit_job(config, file_path="sonda_54_IQM_kalibracja.qasm")
    print(f"Job ID: {job.id}")
    print(f"Status: {job.status}")
    
    # PUSZCZAMY ECHO 36q IONQ
    print("\n=== PUSZCZAM ECHO 36q IONQ ===")
    config2 = JobSubmissionConfig(
        backend_class_id="ionq:forte-1",
        name="Zazul Echo 36q",
        shots=8192,
    )
    job2 = scheduler.submit_job(config2, file_path="echo_36_IONQ.qasm")
    print(f"Job ID: {job2.id}")
    print(f"Status: {job2.status}")
    
    print("\nCzekaj na wyniki... sprawdz za 5-10 minut:")
    print(f"python3 -c \"from openquantum_sdk.clients import SchedulerClient; import os; os.environ['OPENQUANTUM_CLIENT_ID']='s_a6106557ee774c9c9365d47088e2edcf'; os.environ['OPENQUANTUM_CLIENT_SECRET']='7204151edeff758d9d7e118e68adafe6bbbe2395ff242336d9177b57b978aefb'; s=SchedulerClient(); j=s.get_job('{job.id}'); print(j.status()); r=s.download_job_output(j); print(r)\"")
    
except Exception as e:
    print(f"❌ Blad: {e}")
