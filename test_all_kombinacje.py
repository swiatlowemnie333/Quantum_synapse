import os
from openquantum_sdk.clients import SchedulerClient

# Twoje 4 klucze
klucze = {
    'client_id_1': 's_a6106557ee774c9c9365d47088e2edcf',
    'client_secret_1': '7204151edeff758d9d7e118e68adafe6bbbe2395ff242336d9177b57b978aefb',
    'identyfikator': 's_ff347ee786534d6f99cae8d5831c879f',
    'api_openquantum': '7daf11130733507c44e65910c60b39ce50f4fbd066fe9d271ff4ba4ced2038b5',
}

# Wszystkie mozliwe pary
pary = [
    ('client_id_1', 'client_secret_1'),
    ('identyfikator', 'api_openquantum'),
    ('client_id_1', 'api_openquantum'),
    ('identyfikator', 'client_secret_1'),
]

print("=== TESTUJE WSZYSTKIE KOMBINACJE ===\\n")

for i, (id_key, secret_key) in enumerate(pary, 1):
    client_id = klucze[id_key]
    secret = klucze[secret_key]
    
    print(f"Proba {i}: {id_key} + {secret_key}")
    print(f"  ID: {client_id[:25]}...")
    print(f"  Secret: {secret[:25]}...")
    
    os.environ['OPENQUANTUM_CLIENT_ID'] = client_id
    os.environ['OPENQUANTUM_CLIENT_SECRET'] = secret
    
    try:
        scheduler = SchedulerClient()
        orgs = scheduler.management.list_user_organizations(limit=1)
        print(f"  ✅ DZIALA! Orgs: {orgs}")
        print(f"\\n🎉 WYGRANA KOMBINACJA: {id_key} + {secret_key}")
        break
    except Exception as e:
        print(f"  ❌ Blad: {str(e)[:80]}")
        print()

else:
    print("❌ ZADNA KOMBINACJA NIE DZIALA!")
    print("Trzeba wygenerowac NOWE klucze na dashboardzie.")
