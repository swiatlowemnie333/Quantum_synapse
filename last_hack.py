import os
from openquantum_sdk.auth import ClientCredentials, ClientCredentialsAuth
from openquantum_sdk.clients import SchedulerClient, JobSubmissionConfig

auth = ClientCredentialsAuth(
    creds=ClientCredentials(
        client_id=os.getenv("OPENQUANTUM_CLIENT_ID"),
        client_secret=os.getenv("OPENQUANTUM_CLIENT_SECRET")
    )
)
scheduler = SchedulerClient(auth=auth)

subcategories = ["open", "shared", "compute", "trial", "demo", "sandbox", "community", "basic", "premium", "payg", "on-demand", "spot", "dedicated"]

for sub in subcategories:
    try:
        job = scheduler.submit_job(
            JobSubmissionConfig(
                backend_class_id="ionq:forte-ent",
                job_subcategory_id=sub,
                name=f"Zazul {sub}",
                shots=100,
            ),
            file_path="sonda_36_IONQ.qasm"
        )
        print(f"✅ DZIALA! subcategory='{sub}' Job ID: {job.id}")
        break
    except Exception as e:
        print(f"❌ '{sub}': {str(e)[:40]}")
