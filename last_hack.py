from openquantum_sdk.auth import ClientCredentials, ClientCredentialsAuth
from openquantum_sdk.clients import SchedulerClient, JobSubmissionConfig

auth = ClientCredentialsAuth(
    creds=ClientCredentials(
        client_id="s_a6106557ee774c9c9365d47088e2edcf",
        client_secret="7204151edeff758d9d7e118e68adafe6bbbe2395ff242336d9177b57b978aefb"
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
