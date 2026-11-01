import os
# Quantum Rings uzywa token, nie client_id/secret
from quantum_rings import QuantumRings

# Proba z tokenem jako API key
try:
    qr = QuantumRings(token=os.getenv("OPENQUANTUM_CLIENT_SECRET"))
    print("QuantumRings z tokenem OK")
    backends = qr.backends()
    print(f"Backends: {backends}")
except Exception as e:
    print(f"QuantumRings blad: {e}")
