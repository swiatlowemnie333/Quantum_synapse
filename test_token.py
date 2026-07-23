import os
from openquantum_sdk.clients import SchedulerClient

# Proba z tokenem zamiast client_id/secret
token = os.getenv('OPENQUANTUM_CLIENT_SECRET')  # moze secret to token?

try:
    scheduler = SchedulerClient(token=token)
    print("SchedulerClient z token=SECRET OK")
    orgs = scheduler.management.list_user_organizations(limit=1)
    print(f"Orgs: {orgs}")
except Exception as e:
    print(f"Blad z token: {e}")

# Proba z oboma
try:
    scheduler = SchedulerClient(
        token=os.getenv('OPENQUANTUM_CLIENT_SECRET'),
        auth=None
    )
    print("SchedulerClient z token OK")
    orgs = scheduler.management.list_user_organizations(limit=1)
    print(f"Orgs: {orgs}")
except Exception as e:
    print(f"Blad 2: {e}")
