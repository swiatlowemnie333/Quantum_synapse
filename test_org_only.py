from openquantum_sdk.auth import ClientCredentials, ClientCredentialsAuth
from openquantum_sdk.clients import SchedulerClient, JobSubmissionConfig

auth = ClientCredentialsAuth(
    creds=ClientCredentials(
        client_id="s_a6106557ee774c9c9365d47088e2edcf",
        client_secret="7204151edeff758d9d7e118e68adafe6bbbe2395ff242336d9177b57b978aefb"
    )
)
scheduler = SchedulerClient(auth=auth)
org_id = "fa4c0d3f-d89b-469c-a41f-7bc315867b4c"

print("=== Test z organization_id ZAMIAST job_subcategory_id ===")

# Dokumentacja pokazuje bez job_subcategory_id - moze organization_id wystarczy?
try:
    job = scheduler.submit_job(
        JobSubmissionConfig(
            backend_class_id="ionq:forte-ent",
            organization_id=org_id,
            name="Zazul Kalibracja 36q",
            shots=8192,
        ),
        file_path="sonda_36_IONQ.qasm"
    )
    print(f"✅ DZIALA! Job ID: {job.id}")
    print(f"Status: {job.status}")
except Exception as e:
    print(f"❌ Blad: {str(e)[:100]}")

# Albo moze trzeba podac oba?
print("\n=== Test z oboma ===")
try:
    job = scheduler.submit_job(
        JobSubmissionConfig(
            backend_class_id="ionq:forte-ent",
            job_subcategory_id="",
            organization_id=org_id,
            name="Zazul Test2",
            shots=100,
        ),
        file_path="sonda_36_IONQ.qasm"
    )
    print(f"✅ DZIALA! Job ID: {job.id}")
except Exception as e:
    print(f"❌ Blad: {str(e)[:100]}")
