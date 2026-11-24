# Timmkoo Q5 Development Roadmap

The goal is a native Linux CLI that identifies a supported Timmkoo Q5, backs up its firmware, previews an exact stock flash plan, writes the approved partitions, and verifies their contents. Reverse engineering the vendor flashing workflow is part of that work, from preloader identification through the download agent (DA), storage discovery, readback, and write verification. The first release targets one confirmed Q5 board and stock package.

The Q5 runs stock WV3.20 (`Q5-WV3.20`, model `Q5`); a 2026-11-23 live session booted the unit and confirmed the build, so the device is not bricked. One historical run identified an MT6582. A fresh Linux run captured repeated `0xA0` echoes, and the Windows COM6 capture recorded 381 completed opening writes with zero bulk input. On 2026-11-23 the preloader handshake was reached live: the preloader emits a continuous `READY` banner and answers `0xA0` with `0x5F` once the opening byte is retried. A repeatable identification, firmware backup, and completed write are still pending. [Firmware handoff](../HANDOFF.md)

## Milestone 1 — Make diagnostics reproducible

1. **Record the baseline and run checklist.** Reconcile the driver and VM history, record the last reported boot state, and classify the saved runs using the [diagnostic stages](diagnostic-excerpts.md#run-checklist).
2. **Turn the serial probe into a bounded diagnostic CLI.** Add explicit device selection, timeouts, and a structured run summary. Test unrelated devices, permission failures, timeouts, and disconnects offline. Keep the command limited to identification. [Linux CDC ACM documentation](https://docs.kernel.org/usb/acm.html)
3. **Add a capture summarizer and offline CI.** Use synthetic fixtures to verify USB submission/completion pairing, pending reads, payload counts, and first failing stage. Keep raw captures and vendor packages local. Publish real excerpts with separate approval. [Linux usbmon documentation](https://docs.kernel.org/usb/usbmon.html)

**Exit criterion.** CI passes without hardware and fixtures produce their expected stage classifications.

## Milestone 2 — Establish a connection and confirm the stock package

1. **Build the stock compatibility record.** Inventory WV3.25 and the local WV3.27 reference with hashes, scatter regions, and image differences. Seek the exact WV3.20 package or written confirmation of the compatible board, layout, package, and driver from Timmkoo. The published guide identifies WV3.25 with SP Flash Tool v5.1904 and illustrates a full format. Use it to establish provenance and driver requirements. [Timmkoo flashing guide](https://support.timmkoo.com/download/flashing_tutorial/Flashing_tutorial-Q5_ENG.pdf)
2. **Run a physical Windows read-only comparison.** Use the known-good cable on bare metal. Record the driver package, version, and source, including whether Timmkoo confirmed it. Mark this comparison unavailable if the host or driver is missing. Review the historical and current Updater CE configurations as separate sources and pin the revision for each observation. [Historical Updater CE configuration](https://github.com/y1-community/updater-ce-neo/blob/4e431330d69bbe05617c52313f86bfb5b0f37d75/src/sp_console_config.py) · [Updater CE 2.5.6.5](https://github.com/y1-community/updater-ce-neo/releases/tag/2.5.6.5)
3. **Test the Linux transports on matched reconnects.** Verify USB monitor access before comparing captures. Start with the existing kernel serial path. If the evidence warrants it, compare the pinned userspace client with a bounded asynchronous receive test that stops after identification. Hold tool, backend, scatter, power setting, and connection state fixed where possible. Label any comparison with multiple differences as observational. Pursue a kernel driver only if the results identify a specific limitation in both available transports. [libusb I/O documentation](https://libusb.sourceforge.io/api-1.0/libusb_io.html) · [Client upstream](https://github.com/saleemrashid/mediatek_flash_tool)
4. **Reconstruct the preloader identification exchange offline.** Give the specialist model the successful chip-ID log, contrasting captures, pinned native source, and device-isolated backend evidence. Require an evidence-linked stage comparison, a ranked hypothesis list, and one bounded read-only experiment. Start this PR in parallel with package research and use its reviewed result to scope the Linux hardware comparison in 2.3. [Protocol analysis brief](q5-protocol-analysis.md)

**Exit criterion.** A supported route identifies the same chip on two independent cold connections. Record which route passed and which inputs are eligible for read-only testing. A vendor-tool success advances stock recovery. Native identification must pass independently before native storage tests. If the bounded attempts stall, record the last confirmed stage and pursue vendor service or a known-good same-revision comparison unit.

## Milestone 3 — Verify backup and restore stock

1. **Package and validate a read-only Linux build offline.** Pin the upstream client revision, document Meson and libusb dependencies, and add a device-free build and CLI check. Expose identification and readback in the public command. The upstream client reports testing on MT6580 with an SP Flash Tool DA. Treat its code as a candidate implementation until Q5 evidence confirms compatibility. [Native client upstream](https://github.com/saleemrashid/mediatek_flash_tool)
2. **Verify small reads and build the recovery backup.** Use any supported path that passes the connection gate. Require two independent 1 MiB reads of the same stable range with exact size, matching SHA-256 hashes, and plausible metadata. Confirm the on-device partition map and back up the complete affected ranges. Verify the manifest and a second private copy. [Stock recovery plan](q5-stock-recovery.md#backup-and-rollback-gate)
3. **Run the approved stock restore and record acceptance.** Confirm board and layout compatibility, operation scope, backup coverage, and rollback preflight. The current scope is vendor Download Only with WV3.25 `BOOTIMG` and `ANDROID`. A different package, partition scope, or write procedure needs a separate decision. If the device boots before the attempt, record the stock baseline and reassess the need for a write.
4. **Reconstruct and validate native storage access.** After native identification, record vendor and native behavior at platform selection, DA upload and initialization, storage discovery, and first read. Build fixtures from confirmed behavior, then demonstrate the same small-read acceptance as 3.2 through the Linux CLI. Match a trusted comparator where available. Exercise native backup and verify exact byte counts and hashes on the approved ranges before treating it as a recovery input. [Protocol analysis brief](q5-protocol-analysis.md)

**Exit criterion.** A supported path produces a verified backup, and the device reaches a working stock menu on two cold boots. If a restore was needed, record tool success. If stock already boots, record the decision to omit the restore. Test touch, Wi-Fi, charging, and sleep/wake to establish the hardware baseline. The native readback acceptance in 3.4 also passes before the Linux write design is approved.

## Milestone 4 — Ship the native Linux flashing tool

1. **Reconstruct and review the write and verification protocol.** Compare vendor documentation, pinned client source, and approved reference traces. Specify supported DA stages, storage regions, address units, image handling, completion status, verification, and failure behavior. Mark any uncertain state and identify the evidence needed to resolve it. If a reference write capture is necessary, collect it during the existing approved stock restore if the scope matches. Otherwise require a separate approval and a confirmed matching test unit with a recovery path. Before approving implementation, record a demonstrated recovery route independent of the native writer for the same ranges on matching hardware. Use an existing demonstration with verified coverage or obtain separate owner approval for a recovery rehearsal.
2. **Build and test the flash plan offline.** Parse the confirmed package and on-device map input, then produce a reviewable plan with board identity, DA and image hashes, exact named regions and byte ranges, and verification coverage. Reject mismatches, overlaps, out-of-bounds ranges, and unsupported image types. Check whether images are raw or sparse. If sparse support is needed, specify how to verify written extents and handle skipped ranges. [AOSP sparse image format](https://android.googlesource.com/platform/system/core/+/refs/heads/main/libsparse/sparse_format.h)
3. **Implement the native write and verify path.** After design approval, validate the reviewed plan again against the connected device and current inputs before sending writes. Exercise the implementation against an offline test double, including short transfers, timeout, cancellation, disconnect, partial completion, and verification mismatch. Report confirmed and uncertain ranges and avoid automatic retries of writes with uncertain completion.
4. **Qualify repeatable Linux stock flashing on hardware.** Demonstrate two independent runs on the supported configuration. Prefer confirmed matching spare hardware when available. For each run, get owner approval for the exact device, package, plan digest, and target ranges, and confirm the previously demonstrated fallback covers those ranges. Verify affected ranges by independent readback and confirm two stock cold boots. Record touch, Wi-Fi, charging, and sleep/wake acceptance.
5. **Prepare the Linux release.** Produce reproducible build instructions or artifacts, a supported board and package matrix, and a runbook for identification, backup, plan review, flash, verification, and recovery. Record the tested DA hash and keep proprietary inputs user-supplied. Require a clean-host Linux check and a reviewed evidence bundle before publication.

**Exit criterion.** The release candidate has demonstrated native Linux identification and backup, two independently verified flash runs, and two working stock cold boots per run for the listed configuration. The evidence also covers a recovery path independent of the new writer. Broader board, image, format, or partition support requires its own evidence and approval.

## Milestone 5 — Establish a custom ROM baseline

1. **Compare boot and partition requirements offline.** Compare the confirmed stock image, T-ROM, and Lithium boot and recovery metadata. Record compatibility prerequisites, required inputs, and redistribution terms. The published Lithium install report describes a working T-ROM boot as a prerequisite. [Lithium 7 beta](https://github.com/NoahDomingues/Lithium/releases/tag/v7.1.06.13.25) · [Port contributor's install report](https://jtechforums.org/t/lithium-os-boot-loop-and-manufactory-os-on-timmkoo/9056/2) · [AOSP boot-image documentation](https://source.android.com/docs/core/architecture/bootloader/boot-image-header)
2. **Validate one compatible community baseline.** After stock recovery passes, list every partition the image would touch. Verify original backups for all of them and demonstrate a stock rollback path covering that scope on confirmed hardware before authorizing the ROM test. Record cold boot, display, touch, Wi-Fi, charging, and sleep/wake.
3. **Decide whether to build a LineageOS 14.1 port.** Identify missing kernel sources, device configuration, and proprietary inputs. Publish a reproducible build and staged bring-up plan if those inputs are available. Otherwise record the blockers and keep the validated baseline.

**Exit criterion.** One custom baseline boots repeatably, stock rollback has been demonstrated, and further port work has a documented feasibility decision.

## Milestone 6 — Prototype the Wi-Fi remote

Proceed if the home automation use case remains a goal. Begin on the first stable OS with the required networking and UI support.

1. **Prototype the smallest interaction.** Define a single action, a local test service, and visible success and error states. Run the UI against the test service without the Q5.
2. **Connect and test on the device.** Check authentication, offline behavior, Wi-Fi reconnect, and sleep/wake. Track regressions against the stock and custom-ROM baselines.
3. **Document a repeatable setup.** Provide installation, configuration, and recovery steps. Validate end to end with a representative action after a cold boot.

**Exit criterion.** The Q5 runs the action reliably after a cold boot, a sleep cycle, and a Wi-Fi interruption.

## PR order and dependencies

PR IDs refer to the numbered items in each milestone. A dependency can supply evidence even when its hardware work is recorded in a separate PR.

| PRs | Can start after | Acceptance or handoff |
| --- | --- | --- |
| 1.1, 2.1, 3.1 | Now, in parallel | Baseline and checklist, stock-package compatibility record, and an offline Linux build |
| 1.2, 1.3, 2.4 | 1.1 | Bounded diagnostic CLI, offline capture fixtures, and a reviewed identification specification with one test card |
| 2.2 | 1.1 and access to a physical host and driver | Windows comparison, or an explicit record that the comparator is unavailable |
| 2.3 | 2.4 and diagnostic/capture preflight | Controlled Linux identification test, using 1.2 and 1.3 where applicable |
| 3.2 → 3.3 | Repeatable identification on a supported route | Verified backup and map, then stock acceptance or a scoped stock restore if needed. A restore also needs compatibility evidence from 2.1 |
| 3.4 | 3.1 and repeatable native identification from 2.3 | Native DA/storage evidence and independently verified Linux readback |
| 4.1 and 4.2 | Draft 4.1 from existing evidence. Start 4.2 with 2.1 and a representative map fixture | Final write design uses 3.3 and 3.4 results. Final plan validation uses the actual map from 3.2 |
| 4.3 → 4.4 → 4.5 | Approved 4.1 and 4.2, verified native backup, and a demonstrated independent fallback covering the planned scope | Offline-tested writer, approved hardware qualification, then release review |
| 5.1 → 5.2 → 5.3 | Start 5.1 offline once inputs are available. Hardware work follows 3.3 and a demonstrated rollback for every affected partition | Custom baseline and port decision. Depend on 4.4 if the native writer is the chosen recovery path |
| 6.1 → 6.2 → 6.3 | Start 6.1 offline when the use case is confirmed. Device tests need a stable stock or custom OS | End-to-end remote with repeatable setup |

## Approval gates

| Decision | Required evidence and owner |
| --- | --- |
| Use a hosted specialist model | The owner approves the packet and destination before transfer. Use pinned public source, synthetic fixtures, and reviewed excerpts. Keep raw captures, vendor bundles, and device dumps local by default. |
| Start a device experiment | The owner confirms the unit, reconnect window, and allowed operation. The reviewer checks the test card, transport settings, capture access, limits, and stop conditions. DA and storage tests require explicit scope beyond identification. |
| Attempt stock recovery | The owner confirms any change to the approved WV3.25 Download Only scope of `BOOTIMG` and `ANDROID`. Board and layout, verified backup, and rollback preflight must pass before using that scope. [Stock recovery gates](q5-stock-recovery.md#backup-and-rollback-gate) |
| Implement and enable native writes | The owner approves the reviewed compatibility specification, exact initial write scope, plan validation, and evidence that an independent recovery path covers it. Offline plan and test-double work can proceed before this gate. |
| Run a native device write | The owner approves the exact device and flash plan, including its digest, partition ranges, image and DA hashes, pre-write backup, and demonstrated recovery path. Applying the stock package through a new writer is a separate decision. |
| Publish or ship | A reviewer checks release claims against hardware evidence and checks distribution scope. The owner approves publishing release artifacts or real capture excerpts. |

## Specialist model assignments

- **Identification analyst for 2.4.** Reconcile the successful historical run with the stalled Linux and Windows runs. Produce a stage matrix with trace or source references, distinguish observations from inferences, and propose one bounded experiment. [Identification brief](q5-protocol-analysis.md)
- **Storage analyst for 3.4.** Extend the matrix through DA initialization, storage geometry, first read, and shutdown. Specify supported transitions and failure states. Supply synthetic fixtures and name the remaining hardware checks.
- **Write protocol analyst for 4.1.** Map the confirmed vendor write lifecycle from plan selection through completion and verification. Identify ambiguous behavior that would block implementation or require a separately approved reference test. Supply a compatibility specification and failure cases for the implementer.
- **Independent reviewer.** Check each analyst's claims against pinned sources and original evidence. Record which rows are confirmed on Q5 hardware, which are inferred, and which remain unknown. Reviewers hand off accepted behavior and fixtures to the implementer. Each implementation and qualification PR records its own tests, input hashes, hardware scope, and unresolved gates.
