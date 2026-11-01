import os
from openquantum_sdk.auth import ClientCredentials, ClientCredentialsAuth
from openquantum_sdk.clients import SchedulerClient

auth = ClientCredentialsAuth(
    creds=ClientCredentials(
        client_id=os.getenv("OPENQUANTUM_CLIENT_ID"),
        client_secret=os.getenv("OPENQUANTUM_CLIENT_SECRET")
    )
)
scheduler = SchedulerClient(auth=auth)

job_id = "ba45d39c-6a8b-4c04-845a-0259d7913aca"

print("=== SZCZEGÓŁY JOBA ===")
job = scheduler.get_job(job_id)

# Wszystkie atrybuty
print("Dostępne atrybuty:")
for attr in sorted(dir(job)):
    if not attr.startswith('_'):
        try:
            val = getattr(job, attr)
            if not callable(val):
                print(f"  {attr}: {val}")
        except:
            pass

# Spróbuj pobrać output nawet jak failed
print("\n=== PRÓBA POBRANIA OUTPUT ===")
try:
    output = scheduler.download_job_output(job)
    print(f"Output: {output}")
except Exception as e:
    print(f"Nie można pobrać: {e}")

scheduler.close()
