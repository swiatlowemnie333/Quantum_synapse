from qiskit import QuantumCircuit
from qiskit.qasm3 import dumps

# Sonda 36q IonQ
qc = QuantumCircuit(36, 36)
for i in range(36):
    qc.h(i)
    qc.measure(i, i)
with open('sonda_36_IONQ.qasm', 'w') as f:
    f.write(dumps(qc))
print("[OK] sonda_36_IONQ.qasm")

# Sonda 54q IQM
qc = QuantumCircuit(54, 54)
for i in range(54):
    qc.h(i)
    qc.measure(i, i)
with open('sonda_54_IQM_kalibracja.qasm', 'w') as f:
    f.write(dumps(qc))
print("[OK] sonda_54_IQM_kalibracja.qasm")

# Echo 36q IonQ (globalne pierdolniecie)
qc = QuantumCircuit(36, 36)
mid = 18
for i in range(36):
    qc.h(i)
for i in range(36):
    if i != mid:
        qc.cz(mid, i)
qc.z(0)
qc.z(35)
for i in range(36):
    if i != mid:
        qc.cz(mid, i)
for i in range(36):
    qc.h(i)
for i in range(36):
    qc.measure(i, i)
with open('echo_36_IONQ.qasm', 'w') as f:
    f.write(dumps(qc))
print("[OK] echo_36_IONQ.qasm")
print("\nPliki gotowe!")
