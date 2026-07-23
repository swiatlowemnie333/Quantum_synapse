from openquantum_sdk.auth import ClientCredentials, ClientCredentialsAuth
from openquantum_sdk.clients import SchedulerClient

auth = ClientCredentialsAuth(
    creds=ClientCredentials(
        client_id="s_a6106557ee774c9c9365d47088e2edcf",
        client_secret="7204151edeff758d9d7e118e68adafe6bbbe2395ff242336d9177b57b978aefb"
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
