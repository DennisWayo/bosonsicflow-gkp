## BosonicFlow–GKP

This repository contains an educational PennyLane demo on GKP-based quantum error correction in photonic systems. 
BosonicFlow provides the conceptual scaffolding used to organize the discussion, but the focus of the demo is on GKP qubits, photonic noise, and logical error correction.

### What BosonicFlow Is

- A conceptual framework, not a simulator
- Focused on logical qubits, logical operations, and logical error models
- Architecture-aware and photonics-specific in interpretation
- Designed to support education, documentation, and onboarding

### What BosonicFlow Is Not

- Not a new quantum software framework
- Not a CV gate tutorial
- Not a replacement for Strawberry Fields or PennyLane
- Not a fault-tolerance implementation or benchmark suite

### Motivation

Photonic quantum computing is often introduced through continuous-variable (CV) gates and optical primitives.  
However, practical photonic architectures operate on logical qubits, such as GKP-encoded qubits, using discrete logical operations.

BosonicFlow aims to clarify this abstraction boundary and help users reason correctly about:
- where software abstractions live,
- how logical qubits emerge from photonic hardware,
- and how quantum error correction fits naturally into this picture.


### Architectural Perspective

BosonicFlow adopts the following conceptual stack:
**Conceptual abstraction stack used in BosonicFlow:**

```text
Algorithm / Circuit (discrete)
↓
Logical Qubits (GKP encoding)
↓
Logical Error Models
↓
Photonic Physical Substrate
```
