from openquantum_sdk.auth import ClientCredentials, ClientCredentialsAuth
from openquantum_sdk.clients import SchedulerClient

auth = ClientCredentialsAuth(
    creds=ClientCredentials(
        client_id="s_a6106557ee774c9c9365d47088e2edcf",
        client_secret="7204151edeff758d9d7e118e68adafe6bbbe2395ff242336d9177b57b978aefb"
    )
)
scheduler = SchedulerClient(auth=auth)

print("=== Sprawdzam dostepne subcategories ===")

# Proba przez management API
try:
    # List job subcategories
    resp = scheduler.management._request("GET", "/v1/job-subcategories")
    print(f"Subcategories: {resp}")
except Exception as e:
    print(f"Blad subcategories: {e}")

# Proba przez backend info
try:
    resp = scheduler.management._request("GET", "/v1/backends")
    print(f"\nBackends: {resp}")
except Exception as e:
    print(f"Blad backends: {e}")

# Proba user info
try:
    resp = scheduler.management._request("GET", "/v1/users/me")
    print(f"\nUser: {resp}")
except Exception as e:
    print(f"Blad user: {e}")

# Proba organization details
try:
    orgs = scheduler.management.list_user_organizations(limit=1)
    org_id = orgs.organizations[0].id
    print(f"\nOrg ID: {org_id}")
    
    resp = scheduler.management._request("GET", f"/v1/organizations/{org_id}")
    print(f"Org details: {resp}")
except Exception as e:
    print(f"Blad org: {e}")

# Proba job subcategories dla organizacji
try:
    resp = scheduler.management._request("GET", f"/v1/organizations/{org_id}/job-subcategories")
    print(f"\nOrg subcategories: {resp}")
except Exception as e:
    print(f"Blad org subcategories: {e}")
