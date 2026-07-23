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

print("=== Testy subcategory ===")

# Test 1: org_id jako subcategory
print("\n1. Org ID jako subcategory:")
try:
    job = scheduler.submit_job(
        JobSubmissionConfig(
            backend_class_id="ionq:forte-ent",
            job_subcategory_id=org_id,
            name="Zazul Test org-as-sub",
            shots=100,
        ),
        file_path="sonda_36_IONQ.qasm"
    )
    print(f"✅ DZIALA! Job ID: {job.id}")
except Exception as e:
    print(f"❌ {str(e)[:80]}")

# Test 2: Bez subcategory, tylko org_id
print("\n2. Bez subcategory, z org_id:")
try:
    # Uzywamy inspect zeby sprawdzic czy mozna pominac subcategory
    import inspect
    sig = inspect.signature(JobSubmissionConfig.__init__)
    print(f"   Parametry: {list(sig.parameters.keys())}")
    
    # Proba z org_id i pustym subcategory
    job = scheduler.submit_job(
        JobSubmissionConfig(
            backend_class_id="ionq:forte-ent",
            job_subcategory_id="default",
            organization_id=org_id,
            name="Zazul Test default-org",
            shots=100,
        ),
        file_path="sonda_36_IONQ.qasm"
    )
    print(f"✅ DZIALA! Job ID: {job.id}")
except Exception as e:
    print(f"❌ {str(e)[:80]}")

# Test 3: Sprawdz szczegoly organizacji
print("\n3. Szczegoly org:")
try:
    resp = scheduler.management._request("GET", f"/v1/organizations/{org_id}")
    print(f"   Org: {resp}")
except Exception as e:
    print(f"❌ {str(e)[:80]}")

# Test 4: Moze subcategory to jest 'spark' albo 'credits'?
print("\n4. Test 'spark':")
try:
    job = scheduler.submit_job(
        JobSubmissionConfig(
            backend_class_id="ionq:forte-ent",
            job_subcategory_id="spark",
            name="Zazul Test spark",
            shots=100,
        ),
        file_path="sonda_36_IONQ.qasm"
    )
    print(f"✅ DZIALA! Job ID: {job.id}")
except Exception as e:
    print(f"❌ {str(e)[:80]}")
