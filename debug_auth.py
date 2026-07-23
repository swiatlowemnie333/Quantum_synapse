from openquantum_sdk.clients import SchedulerClient, ManagementClient
import os

client_id = os.getenv('OPENQUANTUM_CLIENT_ID')
secret = os.getenv('OPENQUANTUM_CLIENT_SECRET')

print("=== Proba autentykacji ===")

# Sprawdz czy ManagementClient ma metode auth
mc = ManagementClient()
print(f"ManagementClient methods: {[m for m in dir(mc) if not m.startswith('_') and 'auth' in m.lower()]}")

# Proba z token=None
try:
    sc = SchedulerClient(token=None)
    print("SchedulerClient z token=None OK")
    orgs = sc.management.list_user_organizations(limit=1)
    print(f"Orgs: {orgs}")
except Exception as e:
    print(f"Blad z token=None: {e}")

# Proba z auth=None
try:
    sc = SchedulerClient(auth=None)
    print("SchedulerClient z auth=None OK")
    orgs = sc.management.list_user_organizations(limit=1)
    print(f"Orgs: {orgs}")
except Exception as e:
    print(f"Blad z auth=None: {e}")

# Sprawdz czy jest jakis AuthClient
try:
    from openquantum_sdk.clients import AuthClient
    print(f"AuthClient OK")
    ac = AuthClient()
    print(f"AuthClient methods: {[m for m in dir(ac) if not m.startswith('_')]}")
except Exception as e:
    print(f"AuthClient blad: {e}")

# Sprawdz czy jest OAuth2
try:
    import requests
    url = "https://scheduler.openquantum.com/v1/auth/token"
    resp = requests.post(url, json={"client_id": client_id, "client_secret": secret})
    print(f"Token resp: {resp.status_code}")
    print(f"Token body: {resp.text[:200]}")
except Exception as e:
    print(f"Token blad: {e}")
