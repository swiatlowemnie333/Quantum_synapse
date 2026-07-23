# Quantum Rings uzywa token, nie client_id/secret
from quantum_rings import QuantumRings

# Proba z tokenem jako API key
try:
    qr = QuantumRings(token="7204151edeff758d9d7e118e68adafe6bbbe2395ff242336d9177b57b978aefb")
    print("QuantumRings z tokenem OK")
    backends = qr.backends()
    print(f"Backends: {backends}")
except Exception as e:
    print(f"QuantumRings blad: {e}")
