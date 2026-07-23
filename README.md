# Quantum_synapse
Bio-inspired quantum neural network. GHZ-6 95.11% fidelity, 14.10% neural sync on IBM Quantum.

## Results
- GHZ-6 entanglement: 95.11% fidelity (IBM Marrakesh, 156 qubits)
- Quantum synapse: 14.10% neural synchronization (6 neurons, 15 synapses)
- 7 reproducible jobs on IBM Quantum Platform

## Job IDs (verifiable)
- d88n9lgp0eas73dnm190 (GHZ-6)
- d88npkqs46sc73f9mt00 (Synapse)

## Author
Michał Zazuniuk — self-taught quantum engineer
14 years industrial automation → 1 year quantum

---

## Latest Results (June 2026)

**IBM Quantum Marrakesh:**
- 6 qubits: **95% fidelity** (7× repeated)
- 16 qubits: **94.2% fidelity**
- 32 qubits: **74.1% fidelity**

Method: Parallel wave interference with synesthetic phase correction.
Full results in `results/ibm_marrakesh_june_2026/`.


# Quantum Synapse — IBM Marrakesh Characterization & Entanglement Campaign

Experimental campaign on IBM Quantum's 156-qubit `ibm_marrakesh` (Heron r2),
designed and orchestrated by Michał Zazuniuk, with AI-agent-assisted coding.
All results reproducible via IBM Quantum job IDs. Date: 2026-07-23.

## Methodology
1. **Live characterization** of all 156 qubits via delay-sweep circuits
   (0–50 µs, exponential fits per qubit: T1, T2*, readout fidelity)
2. **Quality clustering ("color clans")** — qubits grouped by measured traits;
   connectivity-aware team selection on the heavy-hex coupling map
3. **Closed-loop calibration** — coordinate-ascent tuning of drive angles and
   phase offsets, with automatic revert on regression
4. **Structure optimization** — min-radius BFS wave centers, pinned layouts
   (no SWAP insertion), longest-path line construction
5. **Predict-then-verify** — classical cascade simulation predicts branch
   states, hardware run confirms them

## Verified Results (all with job IDs)
| Experiment | Result |
|---|---|
| Full-processor live characterization | median T1 = 159 µs, T2* = 13 µs |
| T1 × T2 correlation | r = 0.000 (independent decay channels) |
| Full-chip health map (156q density wave) | **97.0%** avg fidelity, 136/156 qubits ≥95% |
| Bell state (best pair, q0–q1) | 98.2% raw → **99.4%** after readout mitigation |
| GHZ populations, 32 qubits | **32.7%** |
| GHZ populations, 64 qubits | 12.4% → **27.3%** after calibration (2.2×) |
| Closed-loop echo calibration (32q) | 7.7% → **21.0%** (2.7×) |
| Hole (vacancy) transport, 13q line | 8 tracked SWAP jumps, ~90% per-step coherence |
| Two-hole dynamics | positions predicted and confirmed (50.6%) |
| Photon–hole density wave transmission | 16q **98.7%** / 32q **97.9%** / 64q **97.9%** / 86q **97.4%** |
| Hybrid entangled state (|A>+|B>)/sqrt2, 64q | **7.3%**, branches predicted a priori by simulation, confirmed |

## Key Findings
- **Systematic over-rotation of fabricated gates**: optimal drive angle
  θ ≈ 0.6–0.97·(π/2) found independently in three different experiments
  (echo-32, GHZ-64, theta sweep) — consistent calibration offset on this device
- **No large "golden district"**: max connected high-quality island ≈ 11 qubits;
  quality is point-scattered, so selection must be graph-aware
- **Faulty qubits identified and confirmed across independent experiments**:
  q26, q72, q76, q82, q113, q130 (weak: q47, q67)
- **Method scales without degradation** for classical pattern transport:
  16 → 86 qubits at ~97–98.7% per-position fidelity
- Bit-pattern transport fidelity matches IBM published median readout error
  (1.475%) — an independent confirmation of device spec via custom pipeline

## Notes
- GHZ results are population measurements (|0…0>+|1…1>), not full fidelity
  (coherence parity measurements planned for the next session)
- All circuits coupling-map-aware with pinned layouts
- Analysis scripts in this repo: characterization, clan clustering,
  closed-loop tuning, wave transport, hole dynamics
