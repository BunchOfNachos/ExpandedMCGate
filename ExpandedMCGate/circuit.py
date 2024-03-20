from __future__ import annotations
import typing
from typing import Sequence
from qiskit.circuit import QuantumCircuit
from qiskit.circuit.bit import Bit
from qiskit.circuit.parameterexpression import ParameterValueType
from qiskit.circuit.register import Register
from qiskit.circuit.quantumregister import QuantumRegister, Qubit, AncillaRegister, AncillaQubit
from qiskit.circuit.instructionset import InstructionSet

from typing import (
    Union,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Sequence,
    Callable,
    Mapping,
    Iterable,
    Any,
    DefaultDict,
    Literal,
    overload,
)

QubitSpecifier = Union[
    Qubit,
    QuantumRegister,
    int,
    slice,
    Sequence[Union[Qubit, int]],
]


class ExtendedQuantumCircuit(QuantumCircuit):


    def __init__(self, *regs: Register | int | Sequence[Bit], name: str | None = None, global_phase: ParameterValueType = 0, metadata: dict | None = None):
        super().__init__(*regs, name=name, global_phase=global_phase, metadata=metadata)

        # check for only one mainreg in circuit
        #for register in circuit.qregs:
        #    dagcircuit.add_qreg(register)


    def mcx(
        self,
        control_qubits: Sequence[QubitSpecifier],
        target_qubit: QubitSpecifier,
        ancilla_qubits: QubitSpecifier | Sequence[QubitSpecifier] | None = None,
        mode: str = "noancilla",
    ) -> InstructionSet:
        """Apply :class:`~qiskit.circuit.library.MCXGate`.

        The multi-cX gate can be implemented using different techniques, which use different numbers
        of ancilla qubits and have varying circuit depth. These modes are:

        - ``'noancilla'``: Requires 0 ancilla qubits.
        - ``'recursion'``: Requires 1 ancilla qubit if more than 4 controls are used, otherwise 0.
        - ``'v-chain'``: Requires 2 less ancillas than the number of control qubits.
        - ``'v-chain-dirty'``: Same as for the clean ancillas (but the circuit will be longer).


        For the full matrix form of this gate, see the underlying gate documentation.

        Args:
            control_qubits: The qubits used as the controls.
            target_qubit: The qubit(s) targeted by the gate.
            ancilla_qubits: The qubits used as the ancillae, if the mode requires them.
            mode: The choice of mode, explained further above.

        Returns:
            A handle to the instructions created.

        Raises:
            ValueError: if the given mode is not known, or if too few ancilla qubits are passed.
            AttributeError: if no ancilla qubits are passed, but some are needed.
        """
        from qiskit.circuit.library.standard_gates.x import MCXGrayCode, MCXRecursive, MCXVChain

        print("It has been modified")

        num_ctrl_qubits = len(control_qubits)

        available_implementations = {
            "noancilla": MCXGrayCode(num_ctrl_qubits),
            "recursion": MCXRecursive(num_ctrl_qubits),
            "v-chain": MCXVChain(num_ctrl_qubits, False),
            "v-chain-dirty": MCXVChain(num_ctrl_qubits, dirty_ancillas=True),
            # outdated, previous names
            "advanced": MCXRecursive(num_ctrl_qubits),
            "basic": MCXVChain(num_ctrl_qubits, dirty_ancillas=False),
            "basic-dirty-ancilla": MCXVChain(num_ctrl_qubits, dirty_ancillas=True),
        }


        # check ancilla input
        if ancilla_qubits:
            _ = self.qbit_argument_conversion(ancilla_qubits)

        try:
            gate = available_implementations[mode]
        except KeyError as ex:
            all_modes = list(available_implementations.keys())
            raise ValueError(
                f"Unsupported mode ({mode}) selected, choose one of {all_modes}"
            ) from ex

        if hasattr(gate, "num_ancilla_qubits") and gate.num_ancilla_qubits > 0:
            required = gate.num_ancilla_qubits
            if ancilla_qubits is None:
                raise AttributeError(f"No ancillas provided, but {required} are needed!")

            # convert ancilla qubits to a list if they were passed as int or qubit
            if not hasattr(ancilla_qubits, "__len__"):
                ancilla_qubits = [ancilla_qubits]

            if len(ancilla_qubits) < required:
                actually = len(ancilla_qubits)
                raise ValueError(f"At least {required} ancillas required, but {actually} given.")
            # size down if too many ancillas were provided
            ancilla_qubits = ancilla_qubits[:required]
        else:
            ancilla_qubits = []

        return self.append(gate, control_qubits[:] + [target_qubit] + ancilla_qubits[:], [])
