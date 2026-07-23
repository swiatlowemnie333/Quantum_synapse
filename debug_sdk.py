import inspect
from openquantum_sdk.clients import SchedulerClient

# Sprawdz jak dziala SchedulerClient
print("=== SchedulerClient.__init__ ===")
sig = inspect.signature(SchedulerClient.__init__)
for name, param in sig.parameters.items():
    print(f"  {name}: {param.default if param.default is not param.empty else 'REQUIRED'}")

print("\n=== SchedulerClient atrybuty ===")
sc = SchedulerClient()
print(f"  management: {sc.management}")
print(f"  auth: {getattr(sc, '_auth', 'N/A')}")
print(f"  base_url: {getattr(sc, '_base_url', 'N/A')}")

# Sprawdz env vars ktore widzi
import os
print("\n=== Env vars ===")
for k, v in os.environ.items():
    if 'quantum' in k.lower() or 'client' in k.lower() or 'secret' in k.lower():
        print(f"  {k}: {v[:30]}...")
