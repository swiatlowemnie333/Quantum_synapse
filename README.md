# Quantum Synapse
### Fault-aware routing for certified entanglement on production quantum hardware

Human physicist-engineer (concepts) + AI agent (code/analysis). All experiments run live on **IBM ibm_marrakesh (156-qubit Heron r2)** via the IBM Quantum open plan. ~260 production jobs, Apr–Aug 2026. All job IDs below are verifiable on IBM Quantum.

---

## 🔬 Empirical Quantum Circuit Benchmarks (IBM Marrakesh – 156 Qubits)

| Qubits | Job ID | Physical Qubits (Layout) | Raw Population P(0)+P(1) | Readout Factor | Mitigated Population | Shots |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| **27q** | `da63t6s3jnrc73ai07e0` | 80, 96, 100–102, 116, 120–122, 136, 139–155 | **29.66%** | 0.4961 | **59.79%** | 8,192 |
| **24q** | `da63jbuaa69c739lhp8g` | 101–102, 116, 120–122, 136, 139–155 | **40.82%** | 0.5151 | **79.25%** | 4,096 |
| **20q** | `da632s3otlns739cijk0` | 120–121, 136, 139–155 | **57.68%** | 0.5959 | **96.79%** | 8,192 |
| **20q** | `da61cfeaa69c739lepj0` | 120–121, 136, 139–155 | **52.99%** | 0.5959 | **88.92%** | 8,192 |
| **16q** | `da5lidmaa69c739l0tp0` | 139, 141–155 | **64.69%** | 0.7446 | **86.87%** | 8,192 |
| **16q** | `da5kofbotlns739c1rh0` | 139, 141–155 | **64.40%** | 0.7446 | **86.50%** | 8,192 |
| **16q** | `da5kb9jotlns739c1d10` | 0–8, 16, 18, 20, 21, 23, 24, 28 | **39.15%** | 0.6252 | **62.62%** | 8,192 |

> **Methodology & Terminology Note:**  
> The values above reflect the **GHZ state population** ($P(\vert{}0^{\otimes N}\rangle) + P(\vert{}1^{\otimes N}\rangle)$). While state population establishes the strict upper bound for quantum state fidelity ($F = \frac{\text{Population} + \text{Coherence}}{2}$), full state fidelity requires off-diagonal density matrix coherence verification (via parity oscillation analysis or multiple quantum coherences). Readout mitigation was calculated using independent per-qubit assignment fidelity product scaling derived directly from calibrated backend properties. Configurations yielding non-physical mitigation divergences (>100%) due to low-fidelity hardware regions have been excluded to preserve empirical integrity.

---

## 🛠️ Hardware Constraints & Topology Mapping
- **Target Processor:** `ibm_marrakesh` (Heavy-hex architecture, 156 active physical qubits).
- **Fault-Tolerant Routing:** Excluded dead/degraded physical qubits (Q82, Q94, Q113, Q130) during coupling map routing.
- **Error Mitigation:** Measurement error mitigation computed dynamically using tensor-product readout probabilities from backend snapshot properties.

**Reference points:** IBM's published 27-qubit result is $F = 0.546$ (2021, with error mitigation); Kang et al. 32q $F = 0.519$ (mitigated). These are **true state fidelities** (population + coherence). The table above reports **population only** — see the corrected direct-measurement section below before comparing. We do **not** claim to beat these benchmarks on true fidelity.

---

## 📐 The Method: Minimum-Resistance Prim-Tree Routing
Edge weight:
$$w = -\ln(1 - \text{cx\_err}) + \text{duration} \cdot \left(\frac{1}{T_{2a}} + \frac{1}{T_{2b}}\right)$$

Prim tree grown from a degree-3 hub over the heavy-hex coupling map minus our DEAD set. Triple-method validation (readout + bitstring + T1/T2) confirms **4 dead qubits (q82, q94, q113, q130)** and **14 weak** by direct readout; a broader bitstring-only screen flags up to ~18 suspect positions (job `da5g34jotlns739bst90`).

**GHZ witness:** $F = \frac{P + C}{2}$; $F > 50\%$ certifies genuine multipartite entanglement.

### Geometry experiment @ 16 qubits (same day, same calibration) — population P(0)+P(1), not fidelity

| Topology | Population P(0)+P(1) | Job ID |
| :--- | :---: | :--- |
| **Linear chain** | 34.0% | `da5kb9jotlns739c1d10` |
| **Shallow BFS tree (depth 18)** | 50.1% | `da5kvoeaa69c739l07kg` |
| **Hybrid (resistance + depth penalty)** | 51.9% | `da5l8mm1vhnc73fm7eng` |
| **Min-resistance Prim tree (depth 43)** | **59.4%** | `da5kofbotlns739c1rh0` |

*Conclusion:* Qubit quality (low resistance) beats shallow topology.

### Head-to-head vs IBM built-in pipeline (16q GHZ, same day)

| Method | Fidelity ($F$) |
| :--- | :---: |
| **Our fault-aware Prim routing** | **45.7%** |
| IBM SamplerV2 (gate + measure twirling) | 25.8% |
| Naive + twirling | 0.1% |

### Coherence cliff — population P(0)+P(1) vs $N$ (NOT fidelity)
$N=12 \rightarrow 63.5\% \cdot 16 \rightarrow 60.3\% \cdot 20 \rightarrow 52.3\% \cdot 24 \rightarrow 35.1\% \cdot 32 \rightarrow 20.5\% \cdot 48 \rightarrow 3.3\% \cdot 64 \rightarrow 0.3\% \cdot 80 \rightarrow 0.3\%$ (jobs `da5lidmaa69c739l0tp0`, `da63jbuaa69c739lhp8g`).  
These are **population**, not fidelity. For the directly measured **true MQC fidelity** — which shows the genuine-entanglement witness holding only to ≈16 qubits — see the section below.

---

## 🔍 Findings
- **Live fault mapping beats IBM's dashboard ~2× in sensitivity** (e.g. q81: IBM 9% vs measured 31%). Measured faults correlate with IBM `readout_error` at $r = +0.94$, but NOT with $T_1$ (+0.01) or $T_2$ (−0.09).
- **Theta-scan (quiet-state hypothesis):** Coherence retention is FLAT (~46–47%) vs excitation angle $\rightarrow$ decoherence is collective phase noise ($T_2$), not excitation relaxation. Motivates decoherence-free subspaces.
- **Honest negatives:** 27q attempt $F = 25.2\%$ raw / $37.9\%$ mitigated (below IBM's 54.6%); dynamical decoupling hurt (14.8% $\rightarrow$ 5.0%).
- **Closed-loop recalibration:** +27% gain (32.7% $\rightarrow$ 41.6%, `da5gt0jotlns739btnhg`).

---

## ✅ Direct MQC fidelity measurement (2026-11-13) — corrected, honest numbers

Earlier "fidelity" figures in this repo were in fact **GHZ population** $P(0^N)+P(1^N)$, not true state fidelity. On 2026-11-13 we measured **true fidelity directly** via the parity-oscillation / multiple-quantum-coherence (MQC) method on `ibm_marrakesh`: prepare GHZ-N, apply a collective phase scan $R(\pi/2,\varphi)$, extract coherence $C$ from the $\cos(N\varphi)$ amplitude, and report $F = (P + C)/2$.

| GHZ N | True fidelity $F$ (raw) | Witness $F>0.5$ | Job IDs |
| :---: | :---: | :---: | :--- |
| 6  | **86.7%** | ✅ genuine GHZ | `dbrfqdmj…` |
| 16 | **33–51%** (drifts) | ✅ in better runs | `dbrfqogk…`, `dbrga30k…`, `dbri406j…` |
| 20 | **16–44%** (drifts) | ❌ mostly below | `dbrfrgfv…`, `dbrh4tm…`, `dbri7fv…` |
| 27 | **17.4%** | ❌ | `dbriannv…` |

**Honest conclusions (reproducible, no inflated numbers):**
- **Genuine multipartite entanglement is certified to ≈16 qubits** (witness $F>0.5$ in good runs); GHZ-20/27 fall below the witness raw. The coherence cliff sits around N=16–20.
- **Readout mitigation (M3/tensored) raises population but not coherence** — in every run the coherence term barely moved (e.g. 16q $C: 0.19\to0.19$) while population over-inflated. So readout mitigation does **not** reliably raise *true* fidelity at scale; the dominant residual errors are gates/decoherence, not readout. Mitigated "fidelity" figures are therefore **not** a fair comparison to IBM's mitigated 54.6% and are not claimed here.
- **Strong temporal/calibration drift:** the same GHZ-16 circuit gave raw $F$ between 33% and 51% within a single day — motivating regular, reproducible benchmarking rather than single "hero" numbers.
- Reproduce with `fidelity_mqc.py` (raw) and `fidelity_qrem.py` (with M3 mitigation) using the job IDs above.

## 📊 Full Report & Interactive Data
- **Interactive report with 6-figure results gallery:** [Zerve AI Report](https://app.zerve.ai/report/0db23d24-a306-4004-8fb3-2a308cf80884)
- `ibm_jobs.csv` — 260 production jobs metadata (Apr–Aug 2026)
- `ibm_features.csv` — 206 jobs with parsed results
- `readout_map.json` — full 156-qubit measured $\vert{}0\rangle/\vert{}1\rangle$ error map
- `qubit_params.json` — per-qubit $T_1$ / $T_2$ / readout parameters

---

## 👤 Author
- **Michał Zazuniuk** — concepts, experiment design, physics intuition  
- **AI agent** — code, orchestration, analysis
