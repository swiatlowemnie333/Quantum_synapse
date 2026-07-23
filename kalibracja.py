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

print("=== KALIBRACJA IONQ 36q ===")
job1 = scheduler.submit_job(
    JobSubmissionConfig(
        backend_class_id="ionq:forte-1",
        job_subcategory_id="public",
        name="Zazul Kalibracja 36q",
        shots=8192,
    ),
    file_path="sonda_36_IONQ.qasm"
)
print(f"IonQ Job ID: {job1.id}")

print("\n=== KALIBRACJA IQM 54q ===")
job2 = scheduler.submit_job(
    JobSubmissionConfig(
        backend_class_id="iqm:emerald",
        job_subcategory_id="public",
        name="Zazul Kalibracja 54q",
        shots=8192,
    ),
    file_path="sonda_54_IQM_kalibracja.qasm"
)
print(f"IQM Job ID: {job2.id}")

print("\nCzekam na wyniki...")
while True:
    time.sleep(20)
    j1 = scheduler.get_job(job1.id)
    j2 = scheduler.get_job(job2.id)
    print(f"IonQ: {j1.status} | IQM: {j2.status}")
    if j1.status == 'COMPLETED' and j2.status == 'COMPLETED':
        r1 = scheduler.download_job_output(job1)
        r2 = scheduler.download_job_output(job2)
        print(f"\n=== IONQ WYNIKI ===\n{r1}")
        print(f"\n=== IQM WYNIKI ===\n{r2}")
        break
    if 'FAIL' in j1.status or 'FAIL' in j2.status:
        print("JOB FAILED!")
        break
