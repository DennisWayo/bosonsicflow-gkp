import csv
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pennylane as qml
from PySide6 import QtCore, QtGui, QtWidgets

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


APP_NAME = "bosonicflow-gkp"
NOTEBOOK_BASE_URL = "https://github.com/DennisWayo/bosonicflow-gkp/blob/main/demos"
NOTEBOOK_NOTES = [
    ("S01", "Logical noise fundamentals", "gkp_qec_demo_01.ipynb"),
    ("S02", "Error correction as noise suppression", "gkp_qec_demo_02.ipynb"),
    ("S03", "Logical noise model exploration", "gkp_qec_demo_03.ipynb"),
    ("S04", "Multi-qubit logical systems", "gkp_qec_demo_04.ipynb"),
    ("S05", "Interactive logical noise playground", "gkp_qec_demo_05.ipynb"),
]


def notebook_link(filename):
    local_path = Path(__file__).resolve().parent.parent / "demos" / filename
    if local_path.exists():
        return local_path.as_uri()
    return f"{NOTEBOOK_BASE_URL}/{filename}"


def apply_axes_style(ax):
    ax.grid(True, alpha=0.25, linestyle="--")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


class PlotCanvas(FigureCanvas):
    def __init__(self, width=5.5, height=4.0, dpi=120):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)

    def clear(self):
        self.ax.clear()
        apply_axes_style(self.ax)

    def render(self):
        self.fig.tight_layout(pad=1.0)
        super().draw()


class BaseTab(QtWidgets.QWidget):
    def __init__(self, title, description):
        super().__init__()
        self.title = title
        self.description = description
        self.data = {}

        title_label = QtWidgets.QLabel(f"<h2>{title}</h2>")
        desc_label = QtWidgets.QLabel(description)
        desc_label.setWordWrap(True)

        self.controls_box = QtWidgets.QGroupBox("Controls")
        self.controls_layout = QtWidgets.QFormLayout()
        self.controls_box.setLayout(self.controls_layout)

        self.export_data_btn = QtWidgets.QPushButton("Export data (CSV)")
        self.export_plot_btn = QtWidgets.QPushButton("Export plots")

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(self.export_data_btn)
        btn_row.addWidget(self.export_plot_btn)
        self.controls_layout.addRow(btn_row)

        self.plot_container = QtWidgets.QWidget()
        self.plot_layout = QtWidgets.QGridLayout()
        self.plot_container.setLayout(self.plot_layout)

        splitter = QtWidgets.QSplitter()
        splitter.setOrientation(QtCore.Qt.Horizontal)
        splitter.addWidget(self.controls_box)
        splitter.addWidget(self.plot_container)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(splitter)
        self.setLayout(layout)


class IntroTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        notebook_rows = []
        for section, title, filename in NOTEBOOK_NOTES:
            href = notebook_link(filename)
            notebook_rows.append(
                f"<li><b>{section}</b> - {title}: "
                f'<a href="{href}">{filename}</a></li>'
            )

        intro_text = QtWidgets.QTextBrowser()
        intro_text.setOpenExternalLinks(True)
        intro_text.setHtml(
            "<h2>Welcome to BosonicFlow-GKP</h2>"
            "<p>"
            "BosonicFlow is a learning flow for logical quantum error correction in photonic "
            "systems, centered on GKP-encoded logical qubits and effective noise."
            "</p>"
            "<p>"
            "Start here, then move to <b>S01</b> through <b>S05</b> tabs to explore and play "
            "with the interactive simulations."
            "</p>"
            "<h3>Explanatory Notebook Notes</h3>"
            "<p>Open the notebook notes for deeper explanations behind each section:</p>"
            f"<ul>{''.join(notebook_rows)}</ul>"
        )

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(intro_text)
        self.setLayout(layout)


class S01Tab(BaseTab):
    def __init__(self):
        super().__init__(
            "S01: Logical noise fundamentals",
            "We start with a single logical qubit. The circuit is as simple as it gets: "
            "prepare |+>, apply logical noise, then measure <X>. We sweep the logical "
            "noise strength and watch coherence decay.",
        )

        self.p_max = QtWidgets.QDoubleSpinBox()
        self.p_max.setRange(0.05, 0.8)
        self.p_max.setSingleStep(0.05)
        self.p_max.setValue(0.30)
        self.p_max.setKeyboardTracking(False)

        self.points = QtWidgets.QSpinBox()
        self.points.setRange(21, 201)
        self.points.setSingleStep(10)
        self.points.setValue(61)
        self.points.setKeyboardTracking(False)

        self.controls_layout.insertRow(0, "Max p", self.p_max)
        self.controls_layout.insertRow(1, "Points", self.points)

        self.canvas = PlotCanvas(width=6.2, height=4.2)
        self.plot_layout.addWidget(self.canvas, 0, 0)

        self.dev = qml.device("default.mixed", wires=1)

        @qml.qnode(self.dev)
        def coherence(p):
            qml.Hadamard(wires=0)
            qml.DepolarizingChannel(p, wires=0)
            return qml.expval(qml.PauliX(0))

        self.coherence = coherence

        self.p_max.valueChanged.connect(self.update_plots)
        self.points.valueChanged.connect(self.update_plots)
        self.export_data_btn.clicked.connect(self.export_data)
        self.export_plot_btn.clicked.connect(self.export_plots)

        self.update_plots()

    def update_plots(self):
        p_max = self.p_max.value()
        points = self.points.value()
        ps = np.linspace(0.0, p_max, points)
        coherences = np.array([self.coherence(p) for p in ps])

        self.data = {
            "p": ps,
            "coherence": coherences,
        }

        self.canvas.clear()
        ax = self.canvas.ax
        ax.plot(ps, coherences, color="#1b9e77", marker="o", markevery=max(1, points // 10))
        ax.set_xlabel("Effective logical noise strength p")
        ax.set_ylabel(r"Logical coherence $\langle X \rangle$")
        ax.set_title("Coherence decay under logical noise")
        ax.set_xlim(ps.min(), ps.max())
        ax.set_ylim(0.5, 1.02)
        self.canvas.render()

    def export_data(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export data", "s01_data.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["p", "coherence"])
            for p, c in zip(self.data["p"], self.data["coherence"]):
                writer.writerow([p, c])

    def export_plots(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select export folder")
        if not directory:
            return
        self.canvas.fig.savefig(os.path.join(directory, "s01_coherence.png"), dpi=300)


class S02Tab(BaseTab):
    def __init__(self):
        super().__init__(
            "S02: Error correction as noise suppression",
            "We tie logical noise to a physical displacement scale. A toy mapping "
            "turns displacement noise into a logical error rate, and correction "
            "suppresses that rate. The circuit is unchanged, only the noise scale changes.",
        )

        self.sigma_max = QtWidgets.QDoubleSpinBox()
        self.sigma_max.setRange(0.1, 1.0)
        self.sigma_max.setSingleStep(0.05)
        self.sigma_max.setValue(0.6)
        self.sigma_max.setKeyboardTracking(False)

        self.sigma0 = QtWidgets.QDoubleSpinBox()
        self.sigma0.setRange(0.05, 1.0)
        self.sigma0.setSingleStep(0.05)
        self.sigma0.setValue(0.35)
        self.sigma0.setKeyboardTracking(False)

        self.alpha = QtWidgets.QDoubleSpinBox()
        self.alpha.setRange(0.0, 1.0)
        self.alpha.setSingleStep(0.05)
        self.alpha.setValue(0.25)
        self.alpha.setKeyboardTracking(False)

        self.points = QtWidgets.QSpinBox()
        self.points.setRange(21, 201)
        self.points.setSingleStep(10)
        self.points.setValue(61)
        self.points.setKeyboardTracking(False)

        self.controls_layout.insertRow(0, "Sigma max", self.sigma_max)
        self.controls_layout.insertRow(1, "Sigma0", self.sigma0)
        self.controls_layout.insertRow(2, "Alpha", self.alpha)
        self.controls_layout.insertRow(3, "Points", self.points)

        self.canvas_coh = PlotCanvas(width=5.4, height=3.8)
        self.canvas_p = PlotCanvas(width=5.4, height=3.8)
        self.plot_layout.addWidget(self.canvas_coh, 0, 0)
        self.plot_layout.addWidget(self.canvas_p, 0, 1)

        self.dev = qml.device("default.mixed", wires=1)

        @qml.qnode(self.dev)
        def coherence(p):
            qml.Hadamard(wires=0)
            qml.DepolarizingChannel(p, wires=0)
            return qml.expval(qml.PauliX(0))

        self.coherence = coherence

        self.sigma_max.valueChanged.connect(self.update_plots)
        self.sigma0.valueChanged.connect(self.update_plots)
        self.alpha.valueChanged.connect(self.update_plots)
        self.points.valueChanged.connect(self.update_plots)
        self.export_data_btn.clicked.connect(self.export_data)
        self.export_plot_btn.clicked.connect(self.export_plots)

        self.update_plots()

    def update_plots(self):
        sigma_max = self.sigma_max.value()
        sigma0 = self.sigma0.value()
        alpha = self.alpha.value()
        points = self.points.value()

        sigma = np.linspace(0.0, sigma_max, points)
        p_raw = 1.0 - np.exp(-(sigma / sigma0) ** 2)
        p_corrected = alpha * p_raw

        coh_raw = np.array([self.coherence(p) for p in p_raw])
        coh_corrected = np.array([self.coherence(p) for p in p_corrected])

        self.data = {
            "sigma": sigma,
            "p_raw": p_raw,
            "p_corrected": p_corrected,
            "coh_raw": coh_raw,
            "coh_corrected": coh_corrected,
        }

        self.canvas_coh.clear()
        ax = self.canvas_coh.ax
        ax.plot(sigma, coh_raw, "o-", color="#1b9e77", markevery=max(1, points // 10), label="Raw")
        ax.plot(
            sigma,
            coh_corrected,
            "s--",
            color="#d95f02",
            markevery=max(1, points // 10),
            label="Corrected",
        )
        ax.fill_between(sigma, coh_corrected, coh_raw, color="#d95f02", alpha=0.12)
        ax.set_xlabel(r"Displacement scale $\sigma$ (toy model)")
        ax.set_ylabel(r"Logical coherence $\langle X \rangle$")
        ax.set_title("Coherence vs displacement scale")
        ax.set_xlim(sigma.min(), sigma.max())
        ax.set_ylim(0.5, 1.02)
        ax.legend()

        self.canvas_p.clear()
        ax2 = self.canvas_p.ax
        ax2.plot(sigma, p_raw, color="#1b9e77", label=r"$p_{raw}$")
        ax2.plot(sigma, p_corrected, color="#d95f02", label=r"$p_{corrected}$")
        ax2.set_xlabel(r"Displacement scale $\sigma$")
        ax2.set_ylabel("Effective logical noise p")
        ax2.set_title("Toy mapping to logical noise")
        ax2.set_xlim(sigma.min(), sigma.max())
        ax2.set_ylim(0.0, 1.0)
        ax2.legend()

        self.canvas_coh.render()
        self.canvas_p.render()

    def export_data(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export data", "s02_data.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["sigma", "p_raw", "p_corrected", "coh_raw", "coh_corrected"])
            for row in zip(
                self.data["sigma"],
                self.data["p_raw"],
                self.data["p_corrected"],
                self.data["coh_raw"],
                self.data["coh_corrected"],
            ):
                writer.writerow(row)

    def export_plots(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select export folder")
        if not directory:
            return
        self.canvas_coh.fig.savefig(os.path.join(directory, "s02_coherence.png"), dpi=300)
        self.canvas_p.fig.savefig(os.path.join(directory, "s02_mapping.png"), dpi=300)


class S03Tab(BaseTab):
    def __init__(self):
        super().__init__(
            "S03: Logical noise model exploration",
            "We keep the logical circuit fixed and swap out the noise channel. "
            "Any differences you see come from the noise model itself, not the circuit.",
        )

        self.p_max = QtWidgets.QDoubleSpinBox()
        self.p_max.setRange(0.05, 0.8)
        self.p_max.setSingleStep(0.05)
        self.p_max.setValue(0.30)
        self.p_max.setKeyboardTracking(False)

        self.points = QtWidgets.QSpinBox()
        self.points.setRange(21, 201)
        self.points.setSingleStep(10)
        self.points.setValue(61)
        self.points.setKeyboardTracking(False)

        self.controls_layout.insertRow(0, "Max p", self.p_max)
        self.controls_layout.insertRow(1, "Points", self.points)

        self.canvas = PlotCanvas(width=6.6, height=4.2)
        self.plot_layout.addWidget(self.canvas, 0, 0)

        self.dev = qml.device("default.mixed", wires=1)

        @qml.qnode(self.dev)
        def coherence_with_channel(channel, p):
            qml.Hadamard(wires=0)
            if channel == "depolarizing":
                qml.DepolarizingChannel(p, wires=0)
            elif channel == "bit_flip":
                qml.BitFlip(p, wires=0)
            elif channel == "phase_flip":
                qml.PhaseFlip(p, wires=0)
            elif channel == "amplitude_damping":
                qml.AmplitudeDamping(p, wires=0)
            elif channel == "phase_damping":
                qml.PhaseDamping(p, wires=0)
            else:
                raise ValueError(f"Unknown channel: {channel}")
            return qml.expval(qml.PauliX(0))

        self.coherence_with_channel = coherence_with_channel

        self.channels = [
            ("Depolarizing", "depolarizing", "#1b9e77"),
            ("Bit flip", "bit_flip", "#8da0cb"),
            ("Phase flip", "phase_flip", "#fc8d62"),
            ("Amplitude damping", "amplitude_damping", "#66c2a5"),
            ("Phase damping", "phase_damping", "#e78ac3"),
        ]

        self.p_max.valueChanged.connect(self.update_plots)
        self.points.valueChanged.connect(self.update_plots)
        self.export_data_btn.clicked.connect(self.export_data)
        self.export_plot_btn.clicked.connect(self.export_plots)

        self.update_plots()

    def update_plots(self):
        p_max = self.p_max.value()
        points = self.points.value()
        ps = np.linspace(0.0, p_max, points)

        data = {"p": ps}
        self.canvas.clear()
        ax = self.canvas.ax

        for label, name, color in self.channels:
            coh = np.array([self.coherence_with_channel(name, p) for p in ps])
            data[name] = coh
            ax.plot(ps, coh, label=label, color=color)

        self.data = data

        ax.set_xlabel("Noise strength p")
        ax.set_ylabel(r"Logical coherence $\langle X \rangle$")
        ax.set_title("Comparing logical noise channels")
        ax.set_xlim(ps.min(), ps.max())
        ax.set_ylim(0.5, 1.02)
        ax.legend(ncol=2)
        self.canvas.render()

    def export_data(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export data", "s03_data.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        headers = ["p"] + [name for _, name, _ in self.channels]
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for i in range(len(self.data["p"])):
                row = [self.data["p"][i]] + [self.data[name][i] for _, name, _ in self.channels]
                writer.writerow(row)

    def export_plots(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select export folder")
        if not directory:
            return
        self.canvas.fig.savefig(os.path.join(directory, "s03_channels.png"), dpi=300)


class S04Tab(BaseTab):
    def __init__(self):
        super().__init__(
            "S04: Multi-qubit logical systems",
            "We move from single qubits to entanglement. We track Bell-state "
            "correlations and GHZ coherence under logical noise.",
        )

        self.p_max = QtWidgets.QDoubleSpinBox()
        self.p_max.setRange(0.05, 0.8)
        self.p_max.setSingleStep(0.05)
        self.p_max.setValue(0.30)
        self.p_max.setKeyboardTracking(False)

        self.points = QtWidgets.QSpinBox()
        self.points.setRange(21, 201)
        self.points.setSingleStep(10)
        self.points.setValue(61)
        self.points.setKeyboardTracking(False)

        self.controls_layout.insertRow(0, "Max p", self.p_max)
        self.controls_layout.insertRow(1, "Points", self.points)

        self.canvas_bell = PlotCanvas(width=5.4, height=3.8)
        self.canvas_ghz = PlotCanvas(width=5.4, height=3.8)
        self.plot_layout.addWidget(self.canvas_bell, 0, 0)
        self.plot_layout.addWidget(self.canvas_ghz, 0, 1)

        self.dev2 = qml.device("default.mixed", wires=2)
        self.dev3 = qml.device("default.mixed", wires=3)

        @qml.qnode(self.dev2)
        def bell_correlations(p):
            qml.Hadamard(wires=0)
            qml.CNOT(wires=[0, 1])
            qml.DepolarizingChannel(p, wires=0)
            qml.DepolarizingChannel(p, wires=1)
            xx = qml.expval(qml.PauliX(0) @ qml.PauliX(1))
            zz = qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))
            return xx, zz

        @qml.qnode(self.dev3)
        def ghz_correlations(p):
            qml.Hadamard(wires=0)
            qml.CNOT(wires=[0, 1])
            qml.CNOT(wires=[0, 2])
            for w in [0, 1, 2]:
                qml.DepolarizingChannel(p, wires=w)
            xxx = qml.expval(qml.PauliX(0) @ qml.PauliX(1) @ qml.PauliX(2))
            zz = qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))
            return xxx, zz

        self.bell_correlations = bell_correlations
        self.ghz_correlations = ghz_correlations

        self.p_max.valueChanged.connect(self.update_plots)
        self.points.valueChanged.connect(self.update_plots)
        self.export_data_btn.clicked.connect(self.export_data)
        self.export_plot_btn.clicked.connect(self.export_plots)

        self.update_plots()

    def update_plots(self):
        p_max = self.p_max.value()
        points = self.points.value()
        ps = np.linspace(0.0, p_max, points)

        bell_xx = []
        bell_zz = []
        ghz_xxx = []
        ghz_zz = []

        for p in ps:
            xx, zz = self.bell_correlations(p)
            bell_xx.append(xx)
            bell_zz.append(zz)

            xxx, zz2 = self.ghz_correlations(p)
            ghz_xxx.append(xxx)
            ghz_zz.append(zz2)

        self.data = {
            "p": ps,
            "bell_xx": np.array(bell_xx),
            "bell_zz": np.array(bell_zz),
            "ghz_xxx": np.array(ghz_xxx),
            "ghz_zz": np.array(ghz_zz),
        }

        self.canvas_bell.clear()
        ax = self.canvas_bell.ax
        ax.plot(ps, self.data["bell_xx"], label=r"$\langle X \otimes X \rangle$")
        ax.plot(ps, self.data["bell_zz"], label=r"$\langle Z \otimes Z \rangle$")
        ax.set_xlabel("Noise strength p")
        ax.set_ylabel("Correlation")
        ax.set_title("Bell-state correlations")
        ax.set_xlim(ps.min(), ps.max())
        ax.set_ylim(0.5, 1.02)
        ax.legend()

        self.canvas_ghz.clear()
        ax2 = self.canvas_ghz.ax
        ax2.plot(ps, self.data["ghz_xxx"], label=r"$\langle X \otimes X \otimes X \rangle$")
        ax2.plot(ps, self.data["ghz_zz"], label=r"$\langle Z_0 Z_1 \rangle$")
        ax2.set_xlabel("Noise strength p")
        ax2.set_ylabel("Correlation")
        ax2.set_title("GHZ-state coherence")
        ax2.set_xlim(ps.min(), ps.max())
        ax2.set_ylim(0.5, 1.02)
        ax2.legend()

        self.canvas_bell.render()
        self.canvas_ghz.render()

    def export_data(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export data", "s04_data.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["p", "bell_xx", "bell_zz", "ghz_xxx", "ghz_zz"])
            for row in zip(
                self.data["p"],
                self.data["bell_xx"],
                self.data["bell_zz"],
                self.data["ghz_xxx"],
                self.data["ghz_zz"],
            ):
                writer.writerow(row)

    def export_plots(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select export folder")
        if not directory:
            return
        self.canvas_bell.fig.savefig(os.path.join(directory, "s04_bell.png"), dpi=300)
        self.canvas_ghz.fig.savefig(os.path.join(directory, "s04_ghz.png"), dpi=300)


class S05Tab(BaseTab):
    def __init__(self):
        super().__init__(
            "S05: Interactive logical noise playground",
            "Pick a noise model, noise strength, correction factor, and qubit count. "
            "You can also switch between direct logical noise and a displacement mapping.",
        )

        self.noise_model = QtWidgets.QComboBox()
        self.noise_model.addItems(
            [
                "depolarizing",
                "bit_flip",
                "phase_flip",
                "amplitude_damping",
                "phase_damping",
            ]
        )

        self.n_qubits = QtWidgets.QComboBox()
        self.n_qubits.addItems(["1", "2", "3"])

        self.measurement = QtWidgets.QComboBox()
        self._update_measurement_options()

        self.mode = QtWidgets.QComboBox()
        self.mode.addItems(["Direct p", "Sigma mapping"])

        self.p_value = QtWidgets.QDoubleSpinBox()
        self.p_value.setRange(0.0, 0.5)
        self.p_value.setSingleStep(0.05)
        self.p_value.setValue(0.2)
        self.p_value.setKeyboardTracking(False)

        self.p_max = QtWidgets.QDoubleSpinBox()
        self.p_max.setRange(0.1, 0.8)
        self.p_max.setSingleStep(0.05)
        self.p_max.setValue(0.5)
        self.p_max.setKeyboardTracking(False)

        self.alpha = QtWidgets.QDoubleSpinBox()
        self.alpha.setRange(0.0, 1.0)
        self.alpha.setSingleStep(0.05)
        self.alpha.setValue(0.25)
        self.alpha.setKeyboardTracking(False)

        self.sigma0 = QtWidgets.QDoubleSpinBox()
        self.sigma0.setRange(0.05, 1.0)
        self.sigma0.setSingleStep(0.05)
        self.sigma0.setValue(0.35)
        self.sigma0.setKeyboardTracking(False)

        self.sigma_max = QtWidgets.QDoubleSpinBox()
        self.sigma_max.setRange(0.1, 1.0)
        self.sigma_max.setSingleStep(0.05)
        self.sigma_max.setValue(0.6)
        self.sigma_max.setKeyboardTracking(False)

        self.points = QtWidgets.QSpinBox()
        self.points.setRange(21, 201)
        self.points.setSingleStep(10)
        self.points.setValue(61)
        self.points.setKeyboardTracking(False)

        self.p_label = QtWidgets.QLabel("p value")
        self.max_label = QtWidgets.QLabel("Max p")

        self.controls_layout.insertRow(0, "Noise model", self.noise_model)
        self.controls_layout.insertRow(1, "Qubits", self.n_qubits)
        self.controls_layout.insertRow(2, "Measurement", self.measurement)
        self.controls_layout.insertRow(3, "Mode", self.mode)
        self.controls_layout.insertRow(4, self.p_label, self.p_value)
        self.controls_layout.insertRow(5, self.max_label, self.p_max)
        self.controls_layout.insertRow(6, "Alpha", self.alpha)
        self.controls_layout.insertRow(7, "Sigma0", self.sigma0)
        self.controls_layout.insertRow(8, "Sigma max", self.sigma_max)
        self.controls_layout.insertRow(9, "Points", self.points)

        self.canvas_bar = PlotCanvas(width=5.2, height=3.6)
        self.canvas_curve = PlotCanvas(width=5.6, height=3.8)
        self.plot_layout.addWidget(self.canvas_bar, 0, 0)
        self.plot_layout.addWidget(self.canvas_curve, 0, 1)

        self._circuit_cache = {}

        self.noise_model.currentIndexChanged.connect(self.update_plots)
        self.n_qubits.currentIndexChanged.connect(self._handle_qubits_change)
        self.measurement.currentIndexChanged.connect(self.update_plots)
        self.mode.currentIndexChanged.connect(self._handle_mode_change)
        self.p_value.valueChanged.connect(self.update_plots)
        self.p_max.valueChanged.connect(self.update_plots)
        self.alpha.valueChanged.connect(self.update_plots)
        self.sigma0.valueChanged.connect(self.update_plots)
        self.sigma_max.valueChanged.connect(self.update_plots)
        self.points.valueChanged.connect(self.update_plots)
        self.export_data_btn.clicked.connect(self.export_data)
        self.export_plot_btn.clicked.connect(self.export_plots)

        self._handle_mode_change()
        self.update_plots()

    def _update_measurement_options(self):
        self.measurement.clear()
        n = int(self.n_qubits.currentText())
        if n == 1:
            self.measurement.addItems(["X", "Z"])
        elif n == 2:
            self.measurement.addItems(["XX", "ZZ"])
        else:
            self.measurement.addItems(["XXX", "ZZ"])

    def _handle_qubits_change(self):
        self._update_measurement_options()
        self.update_plots()

    def _handle_mode_change(self):
        mode = self.mode.currentText()
        if mode == "Direct p":
            self.p_label.setText("p value")
            self.max_label.setText("Max p")
            self.p_value.setRange(0.0, 0.8)
            self.p_max.setRange(0.1, 0.8)
            self.sigma0.setEnabled(False)
            self.sigma_max.setEnabled(False)
        else:
            self.p_label.setText("Sigma value")
            self.max_label.setText("Sigma max")
            self.p_value.setRange(0.0, 1.0)
            self.p_max.setRange(0.1, 1.0)
            self.sigma0.setEnabled(True)
            self.sigma_max.setEnabled(True)
        self.update_plots()

    def _apply_noise(self, noise_model, p, wires):
        for w in wires:
            if noise_model == "depolarizing":
                qml.DepolarizingChannel(p, wires=w)
            elif noise_model == "bit_flip":
                qml.BitFlip(p, wires=w)
            elif noise_model == "phase_flip":
                qml.PhaseFlip(p, wires=w)
            elif noise_model == "amplitude_damping":
                qml.AmplitudeDamping(p, wires=w)
            elif noise_model == "phase_damping":
                qml.PhaseDamping(p, wires=w)
            else:
                raise ValueError(f"Unknown noise model: {noise_model}")

    def _measurement_op(self, n_qubits, measurement):
        if n_qubits == 1 and measurement == "X":
            return qml.PauliX(0)
        if n_qubits == 1 and measurement == "Z":
            return qml.PauliZ(0)
        if n_qubits == 2 and measurement == "XX":
            return qml.PauliX(0) @ qml.PauliX(1)
        if n_qubits == 2 and measurement == "ZZ":
            return qml.PauliZ(0) @ qml.PauliZ(1)
        if n_qubits == 3 and measurement == "XXX":
            return qml.PauliX(0) @ qml.PauliX(1) @ qml.PauliX(2)
        if n_qubits == 3 and measurement == "ZZ":
            return qml.PauliZ(0) @ qml.PauliZ(1)
        return qml.PauliX(0)

    def _get_circuit(self, n_qubits, noise_model, measurement):
        key = (n_qubits, noise_model, measurement)
        if key in self._circuit_cache:
            return self._circuit_cache[key]

        dev = qml.device("default.mixed", wires=n_qubits)
        meas_op = self._measurement_op(n_qubits, measurement)

        @qml.qnode(dev)
        def circuit(p):
            if n_qubits == 1:
                qml.Hadamard(wires=0)
            elif n_qubits == 2:
                qml.Hadamard(wires=0)
                qml.CNOT(wires=[0, 1])
            else:
                qml.Hadamard(wires=0)
                qml.CNOT(wires=[0, 1])
                qml.CNOT(wires=[0, 2])

            self._apply_noise(noise_model, p, range(n_qubits))
            return qml.expval(meas_op)

        self._circuit_cache[key] = circuit
        return circuit

    def _sigma_to_p(self, sigma, sigma0):
        return 1.0 - np.exp(-(sigma / sigma0) ** 2)

    def update_plots(self):
        noise_model = self.noise_model.currentText()
        n_qubits = int(self.n_qubits.currentText())
        measurement = self.measurement.currentText()
        mode = self.mode.currentText()
        alpha = self.alpha.value()
        points = self.points.value()

        circuit = self._get_circuit(n_qubits, noise_model, measurement)

        if mode == "Direct p":
            p_val = self.p_value.value()
            p_max = self.p_max.value()
            x_vals = np.linspace(0.0, p_max, points)
            p_raw_curve = x_vals
            p_raw_point = p_val
            xlabel = "Noise strength p"
        else:
            sigma_val = self.p_value.value()
            sigma_max = self.sigma_max.value()
            sigma0 = self.sigma0.value()
            x_vals = np.linspace(0.0, sigma_max, points)
            p_raw_curve = self._sigma_to_p(x_vals, sigma0)
            p_raw_point = self._sigma_to_p(sigma_val, sigma0)
            xlabel = r"Displacement scale $\sigma$"

        p_corrected_curve = alpha * p_raw_curve
        p_corrected_point = alpha * p_raw_point

        raw_curve = np.array([circuit(p) for p in p_raw_curve])
        corr_curve = np.array([circuit(p) for p in p_corrected_curve])
        raw_point = circuit(p_raw_point)
        corr_point = circuit(p_corrected_point)

        self.data = {
            "x": x_vals,
            "raw_curve": raw_curve,
            "corr_curve": corr_curve,
            "raw_point": raw_point,
            "corr_point": corr_point,
            "mode": mode,
            "xlabel": xlabel,
        }

        self.canvas_bar.clear()
        axb = self.canvas_bar.ax
        axb.bar(["Raw", "Corrected"], [raw_point, corr_point], color=["#1b9e77", "#d95f02"])
        axb.set_ylim(0.0, 1.02)
        axb.set_ylabel("Coherence")
        axb.set_title("Point comparison")
        axb.text(0, raw_point + 0.02, f"{raw_point:.2f}", ha="center")
        axb.text(1, corr_point + 0.02, f"{corr_point:.2f}", ha="center")

        self.canvas_curve.clear()
        axc = self.canvas_curve.ax
        axc.plot(x_vals, raw_curve, color="#1b9e77", label="Raw")
        axc.plot(x_vals, corr_curve, color="#d95f02", label="Corrected")
        axc.fill_between(x_vals, corr_curve, raw_curve, color="#d95f02", alpha=0.12)
        axc.set_xlabel(xlabel)
        axc.set_ylabel(r"Coherence $\langle O \rangle$")
        axc.set_title("Coherence vs noise scale")
        axc.set_xlim(x_vals.min(), x_vals.max())
        axc.set_ylim(0.0, 1.02)
        axc.legend()

        self.canvas_bar.render()
        self.canvas_curve.render()

    def export_data(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export data", "s05_data.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["x", "raw_curve", "corr_curve", "raw_point", "corr_point", "mode"])
            for i in range(len(self.data["x"])):
                writer.writerow(
                    [
                        self.data["x"][i],
                        self.data["raw_curve"][i],
                        self.data["corr_curve"][i],
                        self.data["raw_point"],
                        self.data["corr_point"],
                        self.data["mode"],
                    ]
                )

    def export_plots(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select export folder")
        if not directory:
            return
        self.canvas_bar.fig.savefig(os.path.join(directory, "s05_point.png"), dpi=300)
        self.canvas_curve.fig.savefig(os.path.join(directory, "s05_curve.png"), dpi=300)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BosonicFlow-GKP")
        self.setMinimumSize(1200, 720)

        tabs = QtWidgets.QTabWidget()
        tabs.addTab(IntroTab(), "Intro")
        tabs.addTab(S01Tab(), "S01")
        tabs.addTab(S02Tab(), "S02")
        tabs.addTab(S03Tab(), "S03")
        tabs.addTab(S04Tab(), "S04")
        tabs.addTab(S05Tab(), "S05")

        self.setCentralWidget(tabs)


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
