from __future__ import annotations

from qiskit import circuit
from qiskit.circuit import QuantumRegister
from qiskit.circuit.library import MCMT
from qiskit.quantum_info import Operator

class Barenco(MCMT):
    """Multi-controlled circuit scheme that follows the ideas presented in [1].

    Example of a circuit with 3 control Qubits and the fourth being the target:
    
      ──■────■──────────■────────────────────■────────────────────■───────
        │  ┌─┴─┐      ┌─┴─┐                  │                    │       
      ──┼──┤ X ├──■───┤ X ├──■────■──────────┼─────────■──────────┼───────
        │  └───┘  │   └───┘  │  ┌─┴─┐      ┌─┴─┐     ┌─┴─┐      ┌─┴─┐     
      ──┼─────────┼──────────┼──┤ X ├──■───┤ X ├──■──┤ X ├──■───┤ X ├──■──
      ┌─┴─┐     ┌─┴──┐     ┌─┴─┐└───┘┌─┴──┐└───┘┌─┴─┐└───┘┌─┴──┐└───┘┌─┴─┐
      ┤ V ├─────┤ V† ├─────┤ V ├─────┤ V† ├─────┤ V ├─────┤ V† ├─────┤ V ├
      └───┘     └────┘     └───┘     └────┘     └───┘     └────┘     └───┘ 

    References:
        [1] Barenco et al., 1995. https://arxiv.org/pdf/quant-ph/9503016.pdf
    """
    
    def _build(self):
        """Define the MCMT gate."""
        control_qubits = self.qubits[:-self.num_ctrl_qubits-1:-1] # Most significant Qubits, and on reverse order
        target_qubits = self.qubits[: self.num_target_qubits] # Least significant Qubits

        if len(control_qubits) == 2:
            self._2ctrl_version(control_qubits, target_qubits)
        else:
            self._general_version(control_qubits, target_qubits)

    def _2ctrl_version(
            self,
            control_qubits: QuantumRegister | list[circuit.Qubit],
            target_qubits: QuantumRegister | list[circuit.Qubit],
    ) -> None:
        """Predefined version when only using 2 control Qubits.

        Uses the principles presented in Lemma 6.1 of [1].

        Args:
            control_qubits (QuantumRegister | list[circuit.Qubit]): List of Qubits that are controlling the gate
            target_qubits (QuantumRegister | list[circuit.Qubit]): List of Qubits that are targeted by the gate
        """
        for qubit in target_qubits:
            self.append(self._get_V_instruction(), [control_qubits[1], qubit])
        self.cx(control_qubits[0], control_qubits[1])
        for qubit in target_qubits:
            self.append(self._get_V_instruction(inverse=True), [control_qubits[1], qubit])
        self.cx(control_qubits[0], control_qubits[1])
        for qubit in target_qubits:
            self.append(self._get_V_instruction(), [control_qubits[0], qubit])
    
    def _general_version(
            self,
            control_qubits: QuantumRegister | list[circuit.Qubit],
            target_qubits: QuantumRegister | list[circuit.Qubit],
    ) -> None:
        """The general technique for the simulation of multi-controlled unitary gates in n-bit networks. Uses 0 ancillas.
        
        Uses the principles presented in chapter 7 and Lemma 7.1 of [1].

        The construction of the circuit takes 2^n - 1 controlled V gates and 2^(n-1) - 2 CNOTs, n being the number of control qubits.

        The strategy revolves around performing operations with the V gate on the target Qubits using all the possible 
        combinations of the control Qubits. The control Qubits operate through CNOTs over each other to create the different
        combinations for the V gates. Using the V gate or V† (inversed) is decided by the parity of the Qubits that are going
        to influence the operation.

        x1, x2, and x3 being the control Qubits:

        V iff x1 = 1 (100)
        V† iff x1 ⊕ x2 = 1 (110)
        V iff x2 = 1 (010)
        V† iff x2 ⊕ x3 = 1 (011)
        V iff x1 ⊕ x2 ⊕ x3 = 1 (111)
        V† iff x1 ⊕ x3 = 1 (101)
        V iff x3 = 1 (001)

        The order in which we use the setup the different combinations of the control Qubits determines how many CNOTs we
        have to use. 
        To minimize the number of CNOT gates, the combinations follow a Gray Code sequence (https://en.wikipedia.org/wiki/Gray_code).

        Example of a circuit with 3 control Qubits and the fourth being the target:


        ──■────■──────────■────────────────────■────────────────────■───────
          │  ┌─┴─┐      ┌─┴─┐                  │                    │       
        ──┼──┤ X ├──■───┤ X ├──■────■──────────┼─────────■──────────┼───────
          │  └───┘  │   └───┘  │  ┌─┴─┐      ┌─┴─┐     ┌─┴─┐      ┌─┴─┐     
        ──┼─────────┼──────────┼──┤ X ├──■───┤ X ├──■──┤ X ├──■───┤ X ├──■──
        ┌─┴─┐     ┌─┴──┐     ┌─┴─┐└───┘┌─┴──┐└───┘┌─┴─┐└───┘┌─┴──┐└───┘┌─┴─┐
        ┤ V ├─────┤ V† ├─────┤ V ├─────┤ V† ├─────┤ V ├─────┤ V† ├─────┤ V ├
        └───┘     └────┘     └───┘     └────┘     └───┘     └────┘     └───┘ 

        Args:
            control_qubits (QuantumRegister | list[circuit.Qubit]): List of Qubits that are controlling the gate
            target_qubits (QuantumRegister | list[circuit.Qubit]): List of Qubits that are targeted by the gate
        """
        previous = int(0)

        # The expected amount of controlled V gates
        for i in range(2**len(control_qubits)):
            if i == 0:
                continue
            gray_code = i ^ i >> 1  # Getting the next code from the Gray Code sequence
            idx = int(gray_code).bit_length() - 1 # Which Qubit is the control for the next V gate
            diff = int(gray_code^previous).bit_length() - 1 # Which Qubit is the control for the next CNOT gate
            previous = gray_code
            parity = int(gray_code).bit_count() % 2 == 0 # Checking if the number of 1's in the binary code is even or not

            if idx == diff and i != 1:
                self.cx(control_qubits[idx - 1], control_qubits[idx])
            elif i != 1:
                self.cx(control_qubits[diff], control_qubits[idx])
            
            for target in target_qubits:
                if parity:
                    self.append(self._get_V_instruction(inverse=True), [control_qubits[idx], target])
                else:
                    self.append(self._get_V_instruction(), [control_qubits[idx], target])


    def _get_V_operator(
            self,
            inverse: bool = False
        ) -> Operator:
        """Construct the matrix and operator for the V gate from the original gate matrix.

        V is defined as V^4 = U, U being the original gate that we want to control. 

        Args:
            inverse (bool, optional): Whether or not to return the conjugate transpose of V. Defaults to False.

        Returns:
            Operator: Returns operator for the V gate
        """
        V_matrix = self.gate.control(1).power(1/4).to_matrix()
        V_operator = Operator(V_matrix)
        return V_operator.conjugate().transpose() if inverse else V_operator
    
    def _get_V_instruction(
            self,
            inverse: bool = False
        ) -> Operator:
        """Construct the matrix and instruction for the V gate from the original gate matrix.

        V is defined as V^4 = U, U being the original gate that we want to control. 

        Args:
            inverse (bool, optional): Whether or not to return the inverse of V. Defaults to False.

        Returns:
            Operator: Returns instruction for the V gate
        """
        V_matrix = self.gate.power(1/4).to_matrix()
        V_instruction = Operator(V_matrix).to_instruction().control(1)
        if inverse:
            V_instruction = V_instruction.inverse()
            # Telling python to interpret this as raw string instead of Unicode to avoid a syntax warning.
            V_instruction.base_gate.label = r"$V^{\dagger}$"
        else:
            V_instruction.base_gate.label = "$V$"
        return V_instruction