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



## Experiment Log (IBM Quantum job IDs — verifiable on quantum.cloud.ibm.com)

| Date | Job ID | Experiment | Key result |
|---|---|---|---|
| 2026-07-23 | d9gr51khonhs73ac42mg | 156q live characterization (T1/T2* delay sweep) | median T1 159µs, T2* 13µs |
| 2026-07-23 | d9gqsld0k0jc738h8230 | 156q trait measurement (energy/phase/honesty) | clan map, q82 flagged |
| 2026-07-23 | d9gr86ggk0ls73f22a2g | Bell state + echo, golden pair q0–q1 | GHZ 98.2%, echo 96.9% |
| 2026-07-23 | d9gs3gshonhs73ac5ikg | Density wave 16q | 98.7% per-position |
| 2026-07-23 | d9gs7jt0k0jc738ha6fg | Density wave 32q (tuned line) | 97.9% |
| 2026-07-23 | d9gs8a4honhs73ac5ov0 | Density wave 64q | 97.9% |
| 2026-07-23 | d9gsac0gk0ls73f23tj0 | Density wave 83q | 97.5% |
| 2026-07-23 | d9gsccjsbqfc73ep69e0 | Density wave 86q (with bridges) | 97.4% |
| 2026-07-23 | d9gsd7shonhs73ac5vsg | Full-chip 156q density wave | 97.0%, 136/156 ≥95% |
| 2026-07-23 | d9grv4ogk0ls73f23dk0 | Hole transport, 13q line | 8 coherent jumps tracked |
| 2026-07-23 | d9gs1oshonhs73ac5flg | Two-hole dynamics + hole echo | predictions confirmed |
| 2026-07-23 | d9gsk7khonhs73ac69tg | GHZ-64 theta sweep | 12.4% baseline |
| 2026-07-23 | d9gt4rogk0ls73f25gog | GHZ-64 min-radius + DD + theta calibration | **27.3%** |
| 2026-07-23 | d9gsmv50k0jc738hasug | Hybrid density-wave entangled state 64q | 7.3%, branches confirmed |
| 2026-07-23 | d9grhbggk0ls73f22pig | GHZ-32 wave | 32.7% populations |
