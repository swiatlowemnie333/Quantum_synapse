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

print("=== KREDYTY ===")
try:
    credits = scheduler.management.get_credit_balance(organization_id=org_id)
    print(f"Credits: {credits}")
except Exception as e:
    print(f"Blad kredyty: {e}")

print("\n=== PUSZCZAM KALIBRACJE ===")

# Sprawdzamy rozne job_subcategory_id
subcategories_to_test = ["public", "private", "standard", "default", "free", ""]

for sub in subcategories_to_test:
    try:
        print(f"\nProba z subcategory='{sub}'...")
        job = scheduler.submit_job(
            JobSubmissionConfig(
                backend_class_id="ionq:forte-ent",
                job_subcategory_id=sub,
                name=f"Zazul Test {sub}",
                shots=100,
            ),
            file_path="sonda_36_IONQ.qasm"
        )
        print(f"✅ DZIALA! Job ID: {job.id}")
        break
    except Exception as e:
        print(f"❌ Blad: {str(e)[:80]}")

# Jak nie zadziala zadna, sprobujmy bez subcategory ale z organization_id
print("\n=== Proba z organization_id ===")
try:
    job = scheduler.submit_job(
        JobSubmissionConfig(
            backend_class_id="ionq:forte-ent",
            job_subcategory_id="public",
            organization_id=org_id,
            name="Zazul Test org",
            shots=100,
        ),
        file_path="sonda_36_IONQ.qasm"
    )
    print(f"✅ DZIALA z org_id! Job ID: {job.id}")
except Exception as e:
    print(f"❌ Blad: {str(e)[:80]}")
