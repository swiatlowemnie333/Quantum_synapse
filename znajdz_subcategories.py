from openquantum_sdk.auth import ClientCredentials, ClientCredentialsAuth
from openquantum_sdk.clients import SchedulerClient

auth = ClientCredentialsAuth(
    creds=ClientCredentials(
        client_id="s_a6106557ee774c9c9365d47088e2edcf",
        client_secret="7204151edeff758d9d7e118e68adafe6bbbe2395ff242336d9177b57b978aefb"
    )
)
scheduler = SchedulerClient(auth=auth)
org_id = "fa4c0d3f-d89b-469c-a41f-7bc315867b4c"

print("=== Szukam subcategories ===")

# Wszystkie metody management
for m in sorted(dir(scheduler.management)):
    if not m.startswith('_'):
        print(f"  {m}")

# Proba z listowaniem jobs
print("\n=== Proba listowania jobs ===")
try:
    resp = scheduler.management._request("GET", "/v1/jobs")
    print(f"Jobs: {resp}")
except Exception as e:
    print(f"Blad: {str(e)[:80]}")

# Proba z organizacja
print("\n=== Proba /v1/organizations/{org_id}/jobs ===")
try:
    resp = scheduler.management._request("GET", f"/v1/organizations/{org_id}/jobs")
    print(f"Org jobs: {resp}")
except Exception as e:
    print(f"Blad: {str(e)[:80]}")

# Proba z compute
print("\n=== Proba /v1/compute ===")
try:
    resp = scheduler.management._request("GET", "/v1/compute")
    print(f"Compute: {resp}")
except Exception as e:
    print(f"Blad: {str(e)[:80]}")

# Moze subcategories sa pod /v1/billing?
print("\n=== Proba /v1/billing ===")
try:
    resp = scheduler.management._request("GET", "/v1/billing")
    print(f"Billing: {resp}")
except Exception as e:
    print(f"Blad: {str(e)[:80]}")

# Moze to jest po prostu ID organizacji jako subcategory?
print("\n=== Proba z org_id jako subcategory (z myslnikiem) ===")
try:
    from openquantum_sdk.clients import JobSubmissionConfig
    job = scheduler.submit_job(
        JobSubmissionConfig(
            backend_class_id="ionq:forte-ent",
            job_subcategory_id=org_id,
            organization_id=org_id,
            name="Zazul Test",
            shots=100,
        ),
        file_path="sonda_36_IONQ.qasm"
    )
    print(f"✅ DZIALA! Job ID: {job.id}")
except Exception as e:
    print(f"❌ {str(e)[:80]}")
