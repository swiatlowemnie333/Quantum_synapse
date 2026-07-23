import os
from openquantum_sdk.auth import ClientCredentials, ClientCredentialsAuth
from openquantum_sdk.clients import SchedulerClient

print("=== Proba z ClientCredentialsAuth ===")

auth = ClientCredentialsAuth(
    creds=ClientCredentials(
        client_id="s_a6106557ee774c9c9365d47088e2edcf",
        client_secret="7204151edeff758d9d7e118e68adafe6bbbe2395ff242336d9177b57b978aefb"
    )
)

scheduler = SchedulerClient(auth=auth)

try:
    orgs = scheduler.management.list_user_organizations(limit=1)
    print(f"✅ DZIALA! Orgs: {orgs}")

    # PUSZCZAMY JOB OD RAZU
    from openquantum_sdk.clients import JobSubmissionConfig
    config = JobSubmissionConfig(
        backend_class_id="ionq:forte-1",
python3 test_sdk_key.py}")tatus}")fig, file_path="echo_36_IONQ.qasm
=== Proba z ClientCredentialsAuth ===
✅ DZIALA! Orgs: PaginatedOrganizations(organizations=[OrganizationRead(id='fa4c0d3f-d89b-469c-a41f-7bc315867b4c', name='Michał Zazuniuk')], pagination=PaginationInfo(next_cursor=None))
❌ Blad: JobSubmissionConfig.__init__() missing 1 required positional argument: 'job_subcategory_id'
zazul@vmi2593380:~/open_quantum_tests$
zazul@vmi2593380:~/open_quantum_tests$
zazul@vmi2593380:~/open_quantum_tests$
zazul@vmi2593380:~/open_quantum_tests$ cd ~/open_quantum_tests

cat > test_token_qr.py << 'PYEOF'
# Quantum Rings uzywa token, nie client_id/secret
from quantum_rings import QuantumRings

# Proba z tokenem jako API key
try:
    qr = QuantumRings(token="7204151edeff758d9d7e118e68adafe6bbbe2395ff242336d9177b57b978aefb")
    print("QuantumRings z tokenem OK")
    backends = qr.backends()
    print(f"Backends: {backends}")
except Exception as e:
    print(f"QuantumRings blad: {e}")
