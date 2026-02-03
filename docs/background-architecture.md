## Architecture-Aware View of Photonic Quantum Computing

This document explains the abstraction layers used in photonic quantum architectures
and clarifies where software frameworks such as PennyLane operate.

### Logical vs Physical Layers

- Photonic hardware is continuous-variable in nature
- Logical qubits (e.g. GKP) expose discrete behavior
- Users interact with logical circuits, not CV wavefunctions

### Why CV Gates Are Not User-Level Operations

- CV gates are implementation details
- Logical gates define the computational model
- Abstraction enables hardware-agnostic software