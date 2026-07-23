from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, transpile
from openquantum import get_backend

backend = get_backend("rigetti")  # 79 qubitów
print(f"Backend: {backend.name} | Qubits: {backend.num_qubits}")

qreg = QuantumRegister(32, 'q')
creg = ClassicalRegister(32, 'm')
circuit = QuantumCircuit(qreg, creg)

# Center
circuit.h(qreg[15])
circuit.h(qreg[16])

# Left wave
for i in range(15, 0, -1):
    circuit.cz(qreg[i], qreg[i-1])

# Right wave
for i in range(16, 31):
    circuit.cz(qreg[i], qreg[i+1])

# Reflection
circuit.z(qreg[0])
circuit.z(qreg[31])

# Return
for i in range(0, 15):
    circuit.cz(qreg[i], qreg[i+1])

for i in range(31, 16, -1):
    circuit.cz(qreg[i], qreg[i-1])

# Close
circuit.h(qreg[15])
circuit.h(qreg[16])

# Measure
for i in range(32):
    circuit.measure(qreg[i], creg[i])

transpiled = transpile(circuit, backend, optimization_level=3)
job = backend.run(transpiled, shots=8192)
print(f"Job ID: {job.job_id()}")
print(f"Status: {job.status()}")
