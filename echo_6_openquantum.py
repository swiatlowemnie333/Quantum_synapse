from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, transpile
from openquantum import get_backend

# Open Quantum backend
backend = get_backend("rigetti")  # lub "ionq", "iqm", "aqt"
print(f"Backend: {backend.name}")
print(f"Qubits: {backend.num_qubits}")

qreg = QuantumRegister(6, 'q')
creg = ClassicalRegister(6, 'm')
circuit = QuantumCircuit(qreg, creg)

# Synergy initialization
for i in range(6):
    circuit.h(qreg[i])

# Synesthetic coupling
for i in range(5):
    circuit.cz(qreg[i], qreg[i+1])
    circuit.rz(0.01, qreg[i])

# Reflection
circuit.z(qreg[0])
circuit.z(qreg[5])

# Return
for i in range(4, -1, -1):
    circuit.cz(qreg[i], qreg[i+1])
    circuit.rz(0.01, qreg[i])

# Measure
for i in range(6):
    circuit.measure(qreg[i], creg[i])

transpiled = transpile(circuit, backend, optimization_level=3)
job = backend.run(transpiled, shots=8192)
print(f"Job ID: {job.job_id()}")
print(f"Status: {job.status()}")
