import os
from openquantum_sdk.clients import SchedulerClient

client_id = os.getenv('OPENQUANTUM_CLIENT_ID')
secret = os.getenv('OPENQUANTUM_CLIENT_SECRET')

print(f"Client ID: {client_id}")
print(f"Secret: {secret[:20]}...")

# Proba bezposredniego przekazania kluczy
try:
    scheduler = SchedulerClient(client_id=client_id, client_secret=secret)
    print("SchedulerClient OK")
    orgs = scheduler.management.list_user_organizations(limit=1)
    print(f"Orgs: {orgs}")
except Exception as e:
    print(f"Blad: {e}")
    print("\nProba 2 - tylko client_id...")
    try:
        scheduler = SchedulerClient(client_id=client_id)
        orgs = scheduler.management.list_user_organizations(limit=1)
        print(f"Orgs: {orgs}")
    except Exception as e2:
        print(f"Blad 2: {e2}")
