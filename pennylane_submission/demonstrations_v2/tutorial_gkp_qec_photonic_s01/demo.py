r"""GKP-Based Quantum Error Correction in Photonic Systems
======================================================
"""

######################################################################
# Introduction
# ------------
# 
# Let’s start with the big picture. Photonic hardware is continuous-variable, but most quantum
# algorithms are written in terms of discrete qubits. A GKP-encoded logical qubit is the bridge
# between those worlds: it hides the oscillator details and exposes a clean two-level abstraction to
# software.
# 
# That abstraction makes programming easier, but it doesn’t make noise disappear. As soon as we encode
# information, errors creep in. So we need error correction to keep the logical information stable.
# 
# There are many codes out there—repetition, Shor, Steane, surface codes, and bosonic codes. For
# photonic systems, bosonic codes are a natural fit. This family includes GKP, cat codes, binomial
# codes, and Fock-state encodings.
# 
# Among these, the Gottesman–Kitaev–Preskill (GKP) code plays a central role. GKP encoding stores
# logical qubits in grid-like structures in phase space, allowing small displacement errors—common in
# photonic systems—to be detected and corrected.
# 
# In this demo we stay at the software layer. We’ll follow a simple flow: logical state → error
# syndrome → correction. We won’t simulate optics; we’ll focus on the logical effect.
# 

######################################################################
# Logical Qubit Model in PennyLane
# --------------------------------
# 
# From a software point of view, a GKP logical qubit can be treated as an effective two-level system
# with a density matrix :math:`\rho`. The messy continuous-variable details live underneath, and their
# net effect shows up as an effective logical noise channel:
# 
# .. math::
# 
# 
#    \rho \;\longrightarrow\; \mathcal{E}(\rho).
# 
# Here :math:`\mathcal{E}` is a completely positive, trace-preserving (CPTP) map that represents
# residual logical errors after correction. This is the architecture-level view used in the original
# GKP proposal and later fault-tolerant extensions [1,2].
# 
# In practice, many different logical noise models are possible. PennyLane [5] provides a range of
# quantum channels for this purpose, including ``qml.PhaseDamping``, ``qml.BitFlip``,
# ``qml.PhaseFlip``, ``qml.AmplitudeDamping``, and ``qml.GeneralizedAmplitudeDamping``. Each
# corresponds to a different way logical information can degrade once the system is viewed as an
# effective qubit.
# 
# In this demo, we focus on the depolarizing channel, implemented in PennyLane as
# ``qml.DepolarizingChannel``. At the mathematical level, it acts as
# 
# .. math::
# 
# 
#    \mathcal{E}_{\text{dep}}(\rho)
#    \;=\;
#    (1 - p)\,\rho
#    \;+
#    \;\frac{p}{3}
#    \left(
#    X \rho X
#    +
#    Y \rho Y
#    +
#    Z \rho Z
#    \right),
# 
# where :math:`p \in [0,1]` is the effective logical noise strength and :math:`X`, :math:`Y`,
# :math:`Z` are the Pauli operators. You can read this as: with total probability :math:`p`, a random
# Pauli error is applied; otherwise the state is left alone.
# 
# The appeal of this model is clarity, not physical realism. In a real photonic system, residual
# logical noise after GKP correction arises from finite squeezing, photon loss, measurement
# imprecision, and imperfect decoding [1,4]. Modeling all of that explicitly would obscure the main
# point here.
# 
# Instead, the depolarizing channel gives us a clean, hardware-agnostic way to represent the net
# outcome of imperfect GKP error correction: a single parameter :math:`p` that tells us how much
# logical noise remains once the physical correction procedures have done their work.
# 

######################################################################
# Requirements
# ------------
# 
# This demo uses PennyLane to illustrate logical noise and error correction at the software level.
# Plots are generated with Matplotlib.
# 
# If PennyLane is not already installed, it can be installed with:
# 
# .. code:: bash
# 
#    pip install pennylane matplotlib
# 

######################################################################
# Case 1: Logical coherence under effective noise
# -----------------------------------------------
# 
#    *Thinking question: “What does logical noise do if we don’t correct it well enough?”*
# 
# Before thinking about error correction, it’s useful to see how logical information degrades in the
# presence of noise.
# 
# From a software perspective, one of the simplest indicators of whether a logical qubit is behaving
# well is its coherence. For a qubit prepared in a superposition state, coherence tells us how
# reliably quantum information can be processed and interfered.
# 
# In this example, we prepare a logical qubit in a superposition using a Hadamard gate and then apply
# an effective logical noise channel. We monitor the expectation value ``⟨X⟩``, which serves as a
# proxy for logical coherence. As the strength of the effective noise increases, we expect this
# coherence to decrease.
# 
# The goal here is not to model the physical noise acting on a photonic system, but to observe how
# residual imperfections, after encoding and (imperfect) error correction, appear at the logical level
# seen by quantum software.
# 

import numpy as np
import matplotlib.pyplot as plt
import pennylane as qml

# Use a mixed-state simulator to model logical noise
dev = qml.device("default.mixed", wires=1)


def apply_plot_style():
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.alpha": 0.25,
            "grid.linestyle": "--",
            "axes.labelsize": 12,
            "axes.titlesize": 13,
            "axes.titlepad": 10,
            "legend.frameon": False,
            "legend.fontsize": 11,
            "lines.linewidth": 2.4,
            "lines.markersize": 5,
        }
    )


apply_plot_style()
colors = {
    "raw": "#1b9e77",
    "corrected": "#d95f02",
}


@qml.qnode(dev)
def logical_gkp_coherence(noise_strength):
    '''Logical qubit prepared in a superposition and subjected to effective logical noise.'''
    qml.Hadamard(wires=0)  # logical Clifford operation
    qml.DepolarizingChannel(noise_strength, wires=0)  # effective logical noise
    return qml.expval(qml.PauliX(0))  # logical coherence


print("Logical GKP qubit circuit (effective model):")
print(qml.draw(logical_gkp_coherence)(0.1))


# --- Sweep effective logical noise strength ---
ps = np.linspace(0.0, 0.30, 61)
coherences = np.array([logical_gkp_coherence(p) for p in ps])

# --- Plot logical coherence decay ---
fig, ax = plt.subplots(figsize=(6.5, 4))
ax.plot(ps, coherences, color=colors["raw"], marker="o", markevery=6, label="Logical coherence")
ax.set_xlabel("Effective logical noise strength p")
ax.set_ylabel(r"Logical coherence $\langle X \rangle$")
ax.set_title("Case 1: Coherence decay under effective noise")
ax.set_xlim(ps.min(), ps.max())
ax.set_ylim(0.5, 1.02)
ax.legend()
fig.tight_layout()
plt.show()


######################################################################
#    *What are we seeing here in case 1 above?*
# 
# Let’s walk through the results in plain language.
# 
# We prepare a logical qubit in a superposition using a Hadamard gate. In a noiseless world, this
# state is perfectly coherent. Measuring ``⟨X⟩`` gives ``1.0``, which tells us the superposition is
# intact.
# 
# Now we dial up effective logical noise using the depolarizing channel. This noise is not meant to
# describe the detailed physics of photons; it just captures the net effect of imperfections after
# encoding and imperfect correction.
# 
# As the noise strength ``p`` increases, the trend is clear:
# 
# - When ``p = 0.00``, ``⟨X⟩ = 1.000`` -> the logical qubit is perfectly coherent.
# - As ``p`` increases, ``⟨X⟩`` gradually decreases.
# - By ``p = 0.30``, ``⟨X⟩`` is about ``0.60``.
# 
# This is the simplest picture of logical noise: the circuit is still trivial, but the coherence
# steadily fades.
# 
#    *How do we correct this?*
# 
# In Case 2, we model how GKP correction reduces the effective logical noise.
# 

######################################################################
# Case 2: What changes when error correction does its job?
# --------------------------------------------------------
# 
# In Case 1, we deliberately looked at what happens when effective logical noise is left unchecked.
# The takeaway was simple: as logical noise increases, coherence steadily decays, and the quantum
# state becomes less useful for computation.
# 
# Now let’s flip the question:
# 
#    *What if error correction successfully suppresses logical noise?*
# 
# At the software level, this does not mean that noise disappears completely. Instead, it means that
# the effective logical noise strength is reduced. The circuit stays the same; the noise parameter
# changes.
# 

# Effective logical noise ranges
p_raw = np.linspace(0.0, 0.30, 61)  # before correction
alpha = 0.25  # correction efficiency factor
p_corrected = alpha * p_raw  # after correction

# Compute coherences
coh_raw = np.array([logical_gkp_coherence(p) for p in p_raw])
coh_corrected = np.array([logical_gkp_coherence(p) for p in p_corrected])

# Plot
fig, ax = plt.subplots(figsize=(6.5, 4))
ax.plot(p_raw, coh_raw, "o-", color=colors["raw"], markevery=6, label="Before correction")
ax.plot(p_raw, coh_corrected, "s--", color=colors["corrected"], markevery=6, label="After correction")
ax.fill_between(p_raw, coh_corrected, coh_raw, color=colors["corrected"], alpha=0.12)
ax.text(0.02, 0.52, rf"$\alpha = {alpha:.2f}$", transform=ax.transAxes, color=colors["corrected"])

ax.set_xlabel("Effective logical noise strength p")
ax.set_ylabel(r"Logical coherence $\langle X \rangle$")
ax.set_title("Case 2: Coherence improvement after GKP correction")
ax.set_xlim(p_raw.min(), p_raw.max())
ax.set_ylim(0.5, 1.02)
ax.legend()
fig.tight_layout()
plt.show()


######################################################################
# In Case 2, we model the effect of GKP error correction by reducing the effective logical noise
# strength according to
# 
# .. math::
# 
# 
#    p_{\text{corrected}} = \alpha \, p_{\text{raw}} .
# 
# Here, ``p_raw`` represents the effective logical noise seen by a qubit before error correction,
# while ``p_corrected`` represents the noise that remains after correction. The parameter
# :math:`\alpha \in (0,1)` captures how effective the error-correction process is at suppressing
# logical errors.
# 
# Intuitively, :math:`\alpha` acts as a correction efficiency factor. Values of :math:`\alpha` closer
# to one correspond to weaker correction, where a large fraction of the logical noise survives.
# Smaller values of :math:`\alpha` correspond to stronger correction, where logical errors are more
# effectively suppressed.
# 
# It is important to emphasize that :math:`\alpha` is not derived from hardware physics in this demo.
# In a real photonic system, its value would depend on concrete physical factors such as squeezing
# levels, photon loss rates, measurement precision, and decoding strategies. Here, we deliberately
# treat :math:`\alpha` as a tunable knob that lets us explore how improved error correction would
# appear at the software level, without committing to a specific hardware implementation.
# 
#    *How should we interpret the result in Case 2?*
# 
# The key thing to notice in the figure above is that the logical circuit itself never changes.
# 
# In both cases, ``before and after correction``, we prepare the same logical qubit, apply the same
# Hadamard gate, and measure the same observable ``⟨X⟩``. There are no additional logical gates, no
# explicit correction steps, and no extra measurements introduced at the circuit level. From the
# software’s point of view, everything looks identical.
# 
# What does change is the effective logical noise associated with the qubit. Before correction,
# increasing logical noise leads to a steady decay of coherence. After correction, the same sweep of
# conditions corresponds to a reduced effective logical noise, and the coherence remains significantly
# higher across the entire range.
# 
# **The separation between the two curves is therefore the software-level signature of GKP error
# correction.**
# 
#    *What is actually happening under the hood?*
# 
# GKP error correction operates on the physical photonic degrees of freedom—continuous variables such
# as small displacements in phase space, well below the level of this circuit. Those physical
# processes never appear explicitly in the logical program. They can, however, introduce substantial
# overhead at the hardware and control layers (syndrome extraction, decoding, feedforward, and time).
# 
# Instead, their net effect is captured by a reduction in the logical noise experienced by the qubit.
# In this demo, that reduction is modeled by scaling the effective logical noise parameter through
# :math:`\alpha`. Smaller values of :math:`\alpha` correspond to more effective correction, while
# larger values indicate that more logical noise remains.
# 
# While the numerical value of :math:`\alpha` is hardware-dependent in practice, the qualitative
# outcome is universal: successful GKP correction suppresses logical errors before the qubit is
# exposed to the program.
# 
#    *Why this matters for quantum software*
# 
# From the perspective of an algorithm designer, error correction is not something you manually
# invoke. It is something that improves the quality of the logical qubits you are given.
# 
# This is why high-level frameworks like PennyLane can treat logical qubits uniformly, regardless of
# whether they come from superconducting devices, trapped ions, or photonic GKP encodings. The
# software interacts with the same abstraction; only the effective noise differs.
# 
#    *Lessons drawn from Case 2*
# 
# Effective error correction shows up at the software level as noise suppression, not circuit
# complexity. GKP encoding allows photonic hardware to deliver logical qubits that behave closer to
# ideal qubits, while keeping the continuous-variable physics hidden beneath the abstraction layer.
# 

######################################################################
# Summary: What we did — and what we didn’t
# -----------------------------------------
# 
#    *What we did*
# 
# We treated a GKP-encoded photonic qubit as a logical two-level system with an effective noise
# channel. Using PennyLane’s ``DepolarizingChannel`` on ``default.mixed``, we saw that:
# 
# - logical coherence decays as effective logical noise increases (Case 1).
# - improved error correction appears as a reduction in that effective noise, leading to higher
#   coherence without changing the circuit (Case 2).
# 
#    *What we didn’t do*
# 
# We did not simulate the physical implementation of GKP error correction. In particular, this demo
# does not include:
# 
# - non-Gaussian continuous-variable simulations of GKP states.
# - explicit syndrome extraction or displacement correction.
# - feedforward operations or decoding circuits.
# - hardware-specific noise models such as photon loss or finite squeezing.
# 
# The correction efficiency parameter :math:`\alpha` is treated as a tunable abstraction, not derived
# from first-principles hardware physics.
# 

######################################################################
# Conclusion
# ----------
# 
# If you’re writing quantum software, GKP error correction shows up as better logical qubits, not as
# extra gates in your program. That’s the key takeaway of this demo.
# 
# We kept the circuit fixed and watched how logical noise affects coherence. Then we modeled
# correction as a reduction in that noise. The result is a clear software-level picture of GKP error
# correction: the logical circuit stays the same, while the effective noise gets smaller.
# 

######################################################################
# AI-use disclosure
# -----------------
# 
# ChatGPT model support was used only for language editing and writing clarity checks.
# 
# Experimental design, implementation, tuning, verification, and all technical conclusions are the
# author’s own work and responsibility.
# 
# All notebook content was reviewed by the author before submission.
# 
# Any opinions, findings, conclusions, or recommendations expressed in this demo are those of the
# author(s) and do not necessarily reflect the views of PennyLane.
# 

######################################################################
# Further reading
# ---------------
# 
# For readers who would like to explore these ideas in more depth, the following references provide
# useful background on GKP encoding, bosonic error correction, and photonic quantum computing:
# 
# - [1] **D. Gottesman, A. Kitaev, and J. Preskill**, *Encoding a qubit in an oscillator*,
#   arXiv:quant-ph/0008040 (2000). https://arxiv.org/abs/quant-ph/0008040
# 
# - [2] **N. C. Menicucci**, *Fault-tolerant measurement-based quantum computing with
#   continuous-variable cluster states*, *Physical Review Letters* **112**, 120504 (2014).
#   https://doi.org/10.1103/PhysRevLett.112.120504
# 
# - [3] **M. Mirrahimi et al.**, *Dynamically protected cat-qubits: a new paradigm for universal
#   quantum computation*, *New Journal of Physics* **16**, 045014 (2014).
#   https://doi.org/10.1088/1367-2630/16/4/045014
# 
# - [4] **M. Banić et al.**, *Exact simulation of realistic Gottesman–Kitaev–Preskill cluster states*,
#   *Physical Review A* **112**, 052425 (2025). https://doi.org/10.1103/PhysRevA.112.052425
# 
# - [5] **V. Bergholm et al.**, *PennyLane: Automatic differentiation of hybrid quantum–classical
#   computations*, arXiv:1811.04968 (2018). https://arxiv.org/abs/1811.04968
# 
