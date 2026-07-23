from openquantum_sdk.auth import ClientCredentials, ClientCredentialsAuth
from openquantum_sdk.clients import SchedulerClient

auth = ClientCredentialsAuth(
    creds=ClientCredentials(
        client_id="s_a6106557ee774c9c9365d47088e2edcf",
        client_secret="7204151edeff758d9d7e118e68adafe6bbbe2395ff242336d9177b57b978aefb"
    )
)
scheduler = SchedulerClient(auth=auth)

print("=== Backend Classes ===")
backends = scheduler.management.list_backend_classes()
print(backends)

print("\n=== Credit Balance ===")
credits = scheduler.management.get_credit_balance()
print(credits)

print("\n=== Providers ===")
providers = scheduler.management.list_providers()
print(providers)

print("\n=== Org ID ===")
print("fa4c0d3f-d89b-469c-a41f-7bc315867b4c")
