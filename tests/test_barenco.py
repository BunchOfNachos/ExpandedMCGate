import unittest
import itertools
from qiskit.circuit import library
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.providers.basic_provider import BasicSimulator
from ..ExpandedMCGate.ExtendedMCMT import Barenco

def all_subsets(set):
    # Auxiliary code to get all subsets of a set
    list = []
    for l in range(len(set) + 1):
        for subset in itertools.combinations(set, l):
            list.append(subset)
    return list

class Test_2ctrl_version(unittest.TestCase):
    """
    Test the _2ctrl_version method from barenco.py
    """

    def setUp(self) -> None:
        # Circuits built with our own library
        self._2control_1target = Barenco(library.XGate(), 2, 1)
        self._2control_2target = Barenco(library.XGate(), 2, 2)

        # Circuits built with Qiskit in-buily methods
        self._qiskit_2control_1target = library.MCMT(library.XGate(), 2, 1)
        self._qiskit_2control_2target = library.MCMT(library.XGate(), 2, 2)

        # Simulator
        self.backend = BasicSimulator()
    
    def test_all_ctrl_are_1(self):
        """
        Test that the target Qubit is flipped when all control Qubits are |1⟩.
        """
        # Preparing the circuit
        qreg = QuantumRegister(3)
        creg = ClassicalRegister(3)

        circ = QuantumCircuit(qreg, creg)

        # Put in state |1⟩ all of the control Qubits
        circ.x([1,2])
        # Add our multi-controlled gate targeting the Qubit 0, and measure it
        circ.append(self._2control_1target, qreg)
        circ.measure(qreg[0], creg[0])

        # Transpile circuit to our backend
        transpiled_circ = transpile(circ, self.backend)

        # Run circuit and get the results
        result = self.backend.run(transpiled_circ, shots=128).result()

        # Check that we only have one result and that it is '0x1'
        self.assertEqual(len(result.data()['counts']), 1)
        self.assertEqual(list(result.data()['counts'].keys())[0], '0x1')
    
    def test_not_all_ctrl_are_1(self):
        """
        Test that the target Qubit is not flipped when not all control Qubits are |1⟩.
        """
        # Preparing the circuit
        qreg = QuantumRegister(3)
        creg = ClassicalRegister(3)

        # All the subsets of the control Qubits except the last subset because it includes all control Qubits
        for subset in all_subsets(qreg[1:])[:-1]:
            circ = QuantumCircuit(qreg, creg)

            # Put in state |1⟩ the control Qubits of the subset
            if len(subset) != 0:
                circ.x(subset)
            # Add our multi-controlled gate targeting the Qubit 0, and measure it
            circ.append(self._2control_1target, qreg)
            circ.measure(qreg[0], creg[0])

            # Transpile circuit to our backend
            transpiled_circ = transpile(circ, self.backend)

            # Run circuit and get the results
            result = self.backend.run(transpiled_circ, shots=128).result()

            # Check that we only have one result and that it is '0x0'
            self.assertEqual(len(result.data()['counts']), 1)
            self.assertEqual(list(result.data()['counts'].keys())[0], '0x0')
    
    def test_multi_targets_are_equals(self):
        """
        Test that with multiple target Qubits all of them are flipped or not flipped equally.
        """
        # Preparing the circuit
        qreg = QuantumRegister(4)
        creg = ClassicalRegister(4)

        # All the subsets of the control Qubits
        for subset in all_subsets(qreg[2:]):
            circ = QuantumCircuit(qreg, creg)

            # Put in state |1⟩ the control Qubits of the subset
            if len(subset) != 0:
                circ.x(subset)
            # Add our multi-controlled gate targeting the Qubits 0 and 1, and measure them
            circ.append(self._2control_2target, qreg)
            circ.measure(qreg[0:2], creg[0:2])

            # Transpile circuit to our backend
            transpiled_circ = transpile(circ, self.backend)

            # Run circuit and get the results
            result = self.backend.run(transpiled_circ, shots=128).result()

            # Check that we only have one result and that it is '0x0' or '0x3'
            self.assertEqual(len(result.data()['counts']), 1)
            self.assertIn(list(result.data()['counts'].keys())[0], ['0x0', '0x3'])


class Test_general_version(unittest.TestCase):
    """
    Test the _general_version method from barenco.py
    """

    def setUp(self) -> None:
        # Circuits built with our own library
        self._3control_1target = Barenco(library.XGate(), 3, 1)
        self._3control_2target = Barenco(library.XGate(), 3, 2)

        # Circuits built with Qiskit in-buily methods
        self._qiskit_3control_1target = library.MCMT(library.XGate(), 3, 1)
        self._qiskit_3control_2target = library.MCMT(library.XGate(), 3, 2)

        # Simulator
        self.backend = BasicSimulator()
    
    def test_all_ctrl_are_1(self):
        """
        Test that the target Qubit is flipped when all control Qubits are |1⟩.
        """
        # Preparing the circuit
        qreg = QuantumRegister(4)
        creg = ClassicalRegister(4)

        circ = QuantumCircuit(qreg, creg)

        # Put in state |1⟩ all the control Qubits
        circ.x([1,2,3])
        # Add our multi-controlled gate targeting the Qubit 0, and measure it
        circ.append(self._3control_1target, qreg)
        circ.measure(qreg[0], creg[0])

        # Transpile circuit to our backend
        transpiled_circ = transpile(circ, self.backend)

        # Run circuit and get the results
        result = self.backend.run(transpiled_circ, shots=128).result()

        # Check that we only have one result and that it is '0x1'
        self.assertEqual(len(result.data()['counts']), 1)
        self.assertEqual(list(result.data()['counts'].keys())[0], '0x1')
    
    def test_not_all_ctrl_are_1(self):
        """
        Test that the target Qubit is not flipped when not all control Qubits are |1⟩.
        """
        # Preparing the circuit
        qreg = QuantumRegister(4)
        creg = ClassicalRegister(4)

        # All the subsets of the control Qubits except the last subset because it includes all control Qubits
        for subset in all_subsets(qreg[1:])[:-1]:
            circ = QuantumCircuit(qreg, creg)

            # Put in state |1⟩ the control Qubits of the subset
            if len(subset) != 0:
                circ.x(subset)
            # Add our multi-controlled gate targeting the Qubit 0, and measure it
            circ.append(self._3control_1target, qreg)
            circ.measure(qreg[0], creg[0])

            # Transpile circuit to our backend
            transpiled_circ = transpile(circ, self.backend)

            # Run circuit and get the results
            result = self.backend.run(transpiled_circ, shots=128).result()

            # Check that we only have one result and that it is '0x0'
            self.assertEqual(len(result.data()['counts']), 1)
            self.assertEqual(list(result.data()['counts'].keys())[0], '0x0')

    def test_multi_targets_are_equals(self):
        """
        Test that with multiple target Qubits all of them are flipped or not flipped equally.
        """
        # Preparing the circuit
        qreg = QuantumRegister(5)
        creg = ClassicalRegister(5)

        # All the subsets of the control Qubits
        for subset in all_subsets(qreg[2:]):
            circ = QuantumCircuit(qreg, creg)

            # Put in state |1⟩ the control Qubits of the subset
            if len(subset) != 0:
                circ.x(subset)
            # Add our multi-controlled gate targeting the Qubits 0 and 1, and measure them
            circ.append(self._3control_2target, qreg)
            circ.measure(qreg[0:2], creg[0:2])

            # Transpile circuit to our backend
            transpiled_circ = transpile(circ, self.backend)

            # Run circuit and get the results
            result = self.backend.run(transpiled_circ, shots=128).result()

            # Check that we only have one result and that it is '0x0' or '0x3'
            self.assertEqual(len(result.data()['counts']), 1)
            self.assertIn(list(result.data()['counts'].keys())[0], ['0x0', '0x3'])


if __name__ == '__main__':
    unittest.main()