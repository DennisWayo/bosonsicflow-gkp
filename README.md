## BosonicFlow–GKP

This repository contains a **series** of educational PennyLane demos focused on GKP-based quantum error correction in photonic systems.
BosonicFlow provides the conceptual scaffolding used to organize the discussion. The demos themselves focus on GKP-encoded logical qubits, photonic noise, and how quantum error correction appears at the software abstraction layer.


### Where this work sits in the photonic stack

Photonic quantum computing spans multiple layers, from continuous-variable physics to high-level quantum algorithms. This project intentionally operates between hardware physics and algorithms, at the logical-qubit abstraction layer.
The demos in this repository live at the logical qubit layer. They do not simulate optical modes or CV wavefunctions, but instead study how GKP error correction manifests as effective logical noise suppression from the perspective of quantum software.

```
Physical photonic hardware
  └── Continuous-variable states
      (squeezing, phase space, homodyne detection)
        └── GKP encoding and correction
            (bosonic, non-Gaussian processes)
              └── Logical qubit with effective noise   ← this repo
                  └── Quantum algorithms
```

### What BosonicFlow is
- A conceptual framework, not a simulator 
- Focused on logical qubits, logical operations, and logical noise models 
- Architecture-aware, with a photonic-first interpretation 
- Designed to support education, documentation, and onboarding 
- Structured as a progressive demo series (S01, S02, …)


### What BosonicFlow is not
- Not a new quantum software framework 
- Not a continuous-variable (CV) gate tutorial 
- Not a replacement for PennyLane or Strawberry Fields 
- Not a fault-tolerance benchmark or hardware performance study 
- Not a physical simulation of GKP state preparation or decoding

### Motivation

Photonic quantum computing is often introduced through continuous-variable gates, optical primitives, and phase-space descriptions. While these tools are essential at the hardware level, practical photonic architectures ultimately deliver logical qubits, for example, GKP-encoded qubits, on which algorithms are executed using discrete logical operations.

BosonicFlow–GKP aims to clarify this abstraction boundary and help users reason correctly about:
- where software abstractions live, 
- how logical qubits emerge from photonic hardware, 
- how quantum error correction fits naturally into this picture, 
- and why error correction appears at the software level as noise suppression, not circuit complexity.