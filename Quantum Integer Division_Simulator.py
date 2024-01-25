# Required Python packages:
# pip install matplotlib
# pip install qiskit
# pip install qiskit-aer

import random
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, AncillaRegister
from qiskit import Aer, execute



# Classical Sanity Check ==================================================================================================================
n = 3 # Size of qubit operation. Eg: n-qubit addition

a_int = random.randint(1, 2**(n-1)) # Generate random integer
b_int = random.randint(1, 2**(n-1))
quotient_int = a_int // b_int
remainder_int = a_int % b_int

a_bin = bin(a_int)[2:].zfill(n) # Convert integer to binary
b_bin = bin(b_int)[2:].zfill(n)
quotient_bin = bin(quotient_int)[2:].zfill(n)
remainder_bin = bin(remainder_int)[2:].zfill(n+1)

print("Expected: \n{}({}) / {}({}) = Q {}({}) R {}({})" .format(a_bin, a_int, b_bin, b_int, quotient_bin, quotient_int, remainder_bin, remainder_int))



# Adder Building Block - Cuccaro Adder (4-qubit addition, 10 total qubits) ================================================================
def add(division,c_in,b3,a3,b2,a2,b1,a1,b0,a0,anc0):
    division.cx(a3,b3)
    division.cx(a3,c_in)
    division.ccx(c_in,b3,a3)
    division.cx(a2,b2)
    division.cx(a2,a3)
    division.ccx(a3,b2,a2)
    division.cx(a1,b1)
    division.cx(a1,a2)
    division.ccx(a2,b1,a1)
    division.cx(a0,b0)
    division.cx(a0,a1)
    division.ccx(a1,b0,a0)

    division.cx(a0,anc0)

    division.ccx(a1,b0,a0)
    division.cx(a0,a1)
    division.cx(a1,b0)
    division.ccx(a2,b1,a1)
    division.cx(a1,a2)
    division.cx(a2,b1)
    division.ccx(a3,b2,a2)
    division.cx(a2,a3)
    division.cx(a3,b2)
    division.ccx(c_in,b3,a3)
    division.cx(a3,c_in)
    division.cx(c_in,b3)

# Subtractor Module (4-qubit subtraction, 10 total qubits) ================================================================================
def sub(division,c_in,a0,a1,a2,a3,b0,b1,b2,b3,anc0):
    division.x(c_in)
    division.x(b0)
    division.x(b1)
    division.x(b2)
    division.x(b3)
    add(division,c_in,a3,b3,a2,b2,a1,b1,a0,b0,anc0)
    division.x(b3)
    division.x(b2)
    division.x(b1)
    division.x(b0)

# Add-Sub Module (4-qubit addition/subtraction, 11 total qubits) ==========================================================================
# If ctrl = 0, add. If ctrl = 1, subtract.
def addsub(division,ctrl,c_in,a0,a1,a2,a3,b0,b1,b2,b3,anc0):
    division.cx(ctrl,c_in)
    division.cx(ctrl,b0)
    division.cx(ctrl,b1)
    division.cx(ctrl,b2)
    division.cx(ctrl,b3)
    add(division,c_in,a3,b3,a2,b2,a1,b1,a0,b0,anc0)
    division.cx(ctrl,b3)
    division.cx(ctrl,b2)
    division.cx(ctrl,b1)
    division.cx(ctrl,b0)

# Cond-Add Module (4-qubit conditionaladdition, 9 total qubits) ===========================================================================
# If ctrl = 0, values pass through unchanged. If ctrl = 1, add.
def cond(division,ctrl,a0,a1,a2,a3,b0,b1,b2,b3):
    division.cx(b2,a2)
    division.cx(b1,a1)
    division.cx(b0,a0)
    division.cx(b1,b0)
    division.cx(b2,b1)
    division.ccx(a3,b3,b2)
    division.ccx(a2,b2,b1)
    division.ccx(a1,b1,b0)
    division.ccx(ctrl,b0,a0)
    division.ccx(a1,b1,b0)
    division.ccx(ctrl,b1,a1)
    division.ccx(a2,b2,b1)
    division.ccx(ctrl,b2,a2)
    division.ccx(a3,b3,b2)
    division.ccx(ctrl,b3,a3)
    division.cx(b2,b1)
    division.cx(b1,b0)
    division.cx(b0,a0)
    division.cx(b1,a1)
    division.cx(b2,a2)

# Quantum Non-Restoring Main Circuit ======================================================================================================
division = QuantumCircuit(20,7)
initial_state = "111" + a_bin[2] + a_bin[1] + a_bin[0] + "000" + b_bin[2] + b_bin[1] + b_bin[0] + "0" + "0000000"
print("\nInitial Qubit States = ",initial_state)
division.initialize(initial_state)

# Quotient Generation - Iteration 1
sub(division,6,11,12,13,14,7,8,9,10,5)
division.cx(11,17)
# Quotient Generation - Iteration 2
division.x(11)
addsub(division,11,4,12,13,14,15,7,8,9,10,3)
division.cx(12,18)
# Quotient Generation - Iteration 3
division.x(12)
addsub(division,12,2,13,14,15,16,7,8,9,10,1)
division.cx(13,19)
# Remainder Restoration
division.cx(13,0)
cond(division,0,13,14,15,16,7,8,9,10)



# Simulation ==============================================================================================================================
print("Beginning simulation")
measure_list = [16,15,14,13,19,18,17] # Qubits to be measured
division.measure(measure_list, range(len(measure_list)))
simulator = Aer.get_backend('qasm_simulator')
result = execute(division, simulator, shots=3, memory=True).result()
memory = result.get_memory(division) # Type: List of Strings

for i in range(3): memory[i] = "Q " + memory[i][:3] + " R " + memory[i][3:]
print("Result:\n{}" .format(memory))