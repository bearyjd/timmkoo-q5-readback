# Q5 Protocol Analysis Brief

This brief supports [roadmap PR 2.4](roadmap.md#milestone-2--establish-a-connection-and-confirm-the-stock-package). Reconstruct the supported identification exchange from existing evidence and select one read-only experiment that can explain the first divergence. The deliverable is a reviewable analysis that can guide PR 2.3 while the device is unavailable.

## Evidence packet

Start with the smallest set of inputs that spans the successful and stalled runs. Record each artifact's source, tool version or Git revision, SHA-256 where available, and what part of the session it covers. Use reviewed excerpts when sending the packet to a hosted model. Keep local capture files and vendor packages on the workstation or Alto.

On the original workstation, see `firmware/protocol-analysis-software/INVENTORY.md` for the pinned software paths and checksum manifest. Use the historical versions for reproducing past runs and the newer Updater CE release for comparative inspection.

| Evidence | Where to find it | Question it can answer |
| --- | --- | --- |
| Successful historical identification | `14-21-27/GLB_20261122-142127_0.log` and neighboring logs in `firmware/sp-logs/` | Which tool and backend reported `READY`, completed identification, and then rejected the platform? |
| Scatter and backend comparison | `firmware/q5-backend-trace.54e8wV/` and the `14-23-32` Linux tool logs | Which selector changes were observed offline, and which outcomes were observed on hardware? |
| Fresh native libusb connection | `firmware/q5-usb-fresh.fne0dM/fresh-connection.log` and native client checkout at `dd4f3640be4a271ee72bd43005986307ad46050f` | What response did each side report, and where did the native client reject it? |
| Windows VM COM6, fresh and existing connections | `firmware/q5-windows-fresh.mQJnFH/summary.txt` and `firmware/q5-windows-usb.ruRuxD/handshake-comparison.txt` | Were transfers pending, which completed, and were any incoming bytes captured? |
| Later scatter-free serial run and standalone probe | `firmware/q5-vendor-fresh.nvVIWe/` and `scripts/q5-serial-probe.py` | Did the scatter-free path reproduce its earlier result? Where did each later serial run stop? |
| Vendor and community configuration references | Local package inventory, [Timmkoo guide](https://support.timmkoo.com/download/flashing_tutorial/Flashing_tutorial-Q5_ENG.pdf), and [historical Updater CE console configuration](https://github.com/y1-community/updater-ce-neo/blob/4e431330d69bbe05617c52313f86bfb5b0f37d75/src/sp_console_config.py) | Which tool and settings are documented, and which were actually observed in this tool build? |

Use the [handoff](../HANDOFF.md) to locate full paths and distinguish run chronology. For each log or capture, note whether it started before device enumeration and where collection stopped. If a signal was outside the capture window, mark it **unobserved**.

## Specialist model assignment

> Work offline from the supplied evidence and the pinned native client source. Identify the earliest observable divergence between the successful historical chip-ID run and each stalled run. Report facts with artifact references, label inferences, and list unknowns. Describe the supported protocol as stages and observations from this device. Compare backend selection, connection state, serial setup, and receive timing as competing explanations. Propose one bounded, identification-only experiment through an existing supported transport. Give the control, single variable, expected results for competing explanations, capture requirements, and stop conditions. Return the result as a stage matrix, a ranked hypothesis table, and one test card.

### Pass 1 — Trace and align

- Use the [diagnostic checklist](diagnostic-excerpts.md#run-checklist) stages. Split first reply from completed handshake and chip ID from later platform selection. Establish a separate timeline for each run before comparing times across tools.
- For each stage, record the source line or captured event, timestamp relative to the run's own time origin, host or guest vantage point, interface or port, outcome, and confidence. When available, match submissions to completions by transfer ID and record actual length and status.
- Classify a pending or cancelled receive, a completed receive with no payload, a received echo, and a recognized reply as distinct outcomes. The Windows capture counts opening writes within its capture window. The Linux echo and the Windows absence of input are separate observed behaviors.
- Use a source-backed transition table with states, observed events, timeouts, and exit reasons. Mark the latest stage each run demonstrably reached. Stop the reconstruction at the supported identification boundary and log later stages only as status.
- For ambiguous vendor settings, compare the shipped schema, Updater CE's wrapper configuration, and the saved device-isolated backend traces. If a setting remains ambiguous, repeat the configuration check offline with device access disabled. Record the exact input and the tool's observed selection. Treat a schema-accepted setting as a candidate until that tool build shows it took effect.

### Pass 2 — Rank explanations

For each explanation, give supporting evidence, contradictory evidence, confounders, and one observable result that would change the ranking. Start with these questions:

| Candidate | Evidence to reconcile | What could discriminate |
| --- | --- | --- |
| Backend or tool configuration | The successful historical run reported v2. The offline trace showed that loading the stock scatter selects v1. A later scatter-free run still stalled. | Repeatable stage differences under a supported configuration change with transport and connection conditions held fixed. |
| Connection state or receive timing | Windows had a read pending at the opening writes and still received no payload. Native libusb recorded echoes in a different run. | A matched pair with documented receive timing and the same observed connection state. |
| Serial setup, host, or VM behavior | The guest and native paths made different control requests. Earlier and later Linux serial runs had different outcomes despite similar port-open timing. | The earliest confirmed divergence in a matched capture, with host changes recorded as observational when other variables change. |

Avoid assigning a root cause from one successful historical run. Rank a hypothesis as unresolved when the evidence cannot distinguish it from a competing explanation.

### Pass 3 — Submit one experiment card

Include the following fields in the PR:

1. **Question and alternatives** — State which two explanations the test can separate and what each predicts at a named diagnostic stage.
2. **Control and variant** — List tool revision and hash, backend, scatter and power configuration, cable, USB port, and reconnect state. Identify the one changed variable. If a matched pair is unavailable, report the comparison as observational.
3. **Preflight** — Verify target and capture access, agree on timing for a powered-off reconnect, and confirm that the test stops at identification. Use synthetic fixtures to exercise expected outcomes before device time.
4. **Run limits** — Use an explicit per-run timeout and the checklist's cap of two fresh reconnects per configuration. Stop on unexpected device identity, missing capture, disconnect, timeout, or successful identification. Record the last confirmed stage and first failure.
5. **Decision** — Define what would advance the transport PR, what would lower a hypothesis's priority, and what result would leave the test inconclusive. Require fresh confirmation before treating a one-off success as a reliable route.

## Review and handoff

- A second reviewer checks the stage matrix against original artifacts and the model's source references against the pinned checkout. Resolve contradictory claims or carry them forward as open questions.
- Accept PR 2.4 when it records the first supported divergence for each run, distinguishes observations from inference, and presents either one actionable test card or the exact missing evidence needed to choose one. Publish synthetic fixtures or approved excerpts.
- In PR 2.3, record the hardware result against the card's predictions. Two cold connections that identify the same chip earn a readback attempt under Milestone 3. If identification repeats but storage access fails, record the new blocker and keep the restore gate closed.
- In PRs 3.2 and 3.3, verify storage reads, the exact board and partition layout, backup coverage, and rollback readiness before using the approved stock restore path. In PR 3.4, extend the stage matrix through native DA initialization, storage discovery, and repeatable readback. Give that reviewed evidence and the verified stock baseline to the write analyst for PR 4.1. [Stock recovery gates](q5-stock-recovery.md#backup-and-rollback-gate) · [Native flashing milestone](roadmap.md#milestone-4--ship-the-native-linux-flashing-tool)
