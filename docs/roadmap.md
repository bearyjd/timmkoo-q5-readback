# Timmkoo Q5 Development Roadmap

The Q5 last ran WV3.20. One historical run identified an MT6582. A fresh Linux run captured repeated `0xA0` echoes, and the Windows COM6 capture recorded 381 completed opening writes with zero bulk input. No run has produced a firmware backup or completed a write. The immediate goal is a repeatable connection and verified readback. See [HANDOFF.md](../HANDOFF.md) for the evidence.

## Milestone 1 — Make diagnostics reproducible

1. **Record the baseline and run checklist.** Reconcile the driver and VM history, record the last reported boot state, and classify the saved runs using the [diagnostic stages](diagnostic-excerpts.md#run-checklist).
2. **Turn the serial probe into a bounded diagnostic CLI.** Add explicit device selection, timeouts, and a structured run summary. Test unrelated devices, permission failures, timeouts, and disconnects offline. Keep the command limited to identification. [Linux CDC ACM documentation](https://docs.kernel.org/usb/acm.html)
3. **Add a capture summarizer and offline CI.** Use synthetic fixtures to verify USB submission/completion pairing, pending reads, payload counts, and first failing stage. Keep raw captures and vendor packages local. Publish real excerpts with separate approval. [Linux usbmon documentation](https://docs.kernel.org/usb/usbmon.html)

**Exit criterion.** CI passes without hardware and fixtures produce their expected stage classifications.

## Milestone 2 — Establish a connection and confirm the stock package

1. **Build the stock compatibility record.** Inventory WV3.25 and the local WV3.27 reference with hashes, scatter regions, and image differences. Seek the exact WV3.20 package or written confirmation of the compatible board, layout, package, and driver from Timmkoo. The published guide identifies WV3.25 with SP Flash Tool v5.1904 and illustrates a full format. Use it to establish provenance and driver requirements. [Timmkoo flashing guide](https://support.timmkoo.com/download/flashing_tutorial/Flashing_tutorial-Q5_ENG.pdf)
2. **Run a physical Windows read-only comparison.** Use the known-good cable on bare metal. Record the driver package, version, and source, including whether Timmkoo confirmed it. Mark this comparison unavailable if the host or driver is missing. Compare community tooling offline by reviewing its SP Flash Tool configuration. [Updater CE console configuration](https://github.com/y1-community/updater-ce-neo/blob/main/src/sp_console_config.py)
3. **Test the Linux transports on matched reconnects.** Verify USB monitor access before comparing captures. Start with the existing kernel serial path. If the evidence warrants it, compare the pinned userspace client with a bounded asynchronous receive test that stops after identification. Hold tool, backend, scatter, power setting, and connection state fixed where possible. Label any comparison with multiple differences as observational. Pursue a kernel driver only if the results identify a specific limitation in both available transports. [libusb I/O documentation](https://libusb.sourceforge.io/api-1.0/libusb_io.html) · [Client upstream](https://github.com/saleemrashid/mediatek_flash_tool)

**Exit criterion.** A supported route identifies the same chip on two independent cold connections. Record package eligibility for read-only testing at this stage. Confirm the actual layout before any write. If available routes exhaust their retry limits without identification, record the furthest stage and pursue vendor service or a known-good same-revision comparison unit. If identification succeeds but readback stalls, keep the restore gate closed and investigate the first failing stage.

## Milestone 3 — Verify backup and restore stock

1. **Package and validate a read-only Linux build in parallel.** Pin the upstream client revision, document Meson and libusb dependencies, and add a device-free build and CLI check. Separate the public readback command from the upstream tool's write interface. On hardware, use the same readback acceptance checks as the stock path when Linux reaches storage access.
2. **Verify small reads and build the recovery backup.** Use any supported path that passes the connection gate. Require two successful independent 1 MiB reads of the same stable range with exact size, matching SHA-256 hashes, and plausible metadata. Confirm the hardware partition map and verify backup coverage against the [stock recovery plan](q5-stock-recovery.md).
3. **Run the approved stock restore and record acceptance.** Confirm board and layout compatibility, operation scope, backup coverage, and rollback preflight. The current scope covers WV3.25 `BOOTIMG` and `ANDROID` only. A different package, partition scope, or write procedure needs a separate decision. If the device boots before the attempt, record the stock baseline and reassess the need for a write.

**Exit criterion.** A supported path produces a verified backup, and the device reaches a working stock menu on two cold boots. If a restore was needed, record tool success. If stock already boots, record the decision to omit the restore. Test touch, Wi-Fi, charging, and sleep/wake to establish the hardware baseline. Report native Linux readback and any demonstrated rollback separately.

## Milestone 4 — Establish a custom ROM baseline

1. **Compare boot and partition requirements offline.** Compare the confirmed stock image, T-ROM, and Lithium boot and recovery metadata. Record compatibility prerequisites, required inputs, and redistribution terms. The published Lithium install report describes a working T-ROM boot as a prerequisite. [Lithium 7 beta](https://github.com/NoahDomingues/Lithium/releases/tag/v7.1.06.13.25) · [Port contributor's install report](https://jtechforums.org/t/lithium-os-boot-loop-and-manufactory-os-on-timmkoo/9056/2) · [AOSP boot-image documentation](https://source.android.com/docs/core/architecture/bootloader/boot-image-header)
2. **Validate one compatible community baseline.** After stock recovery passes, list every partition the image would touch. Verify original backups for all of them and demonstrate a stock rollback path covering that scope on confirmed hardware before authorizing the ROM test. Record cold boot, display, touch, Wi-Fi, charging, and sleep/wake.
3. **Decide whether to build a LineageOS 14.1 port.** Identify missing kernel sources, device configuration, and proprietary inputs. Publish a reproducible build and staged bring-up plan if those inputs are available. Otherwise record the blockers and keep the validated baseline.

**Exit criterion.** One custom baseline boots repeatably, stock rollback has been demonstrated, and further port work has a documented feasibility decision.

## Milestone 5 — Prototype the Wi-Fi remote

Proceed if the home automation use case remains a goal. Begin on the first stable OS with the required networking and UI support.

1. **Prototype the smallest interaction.** Define a single action, a local test service, and visible success and error states. Run the UI against the test service without the Q5.
2. **Connect and test on the device.** Check authentication, offline behavior, Wi-Fi reconnect, and sleep/wake. Track regressions against the stock and custom-ROM baselines.
3. **Document a repeatable setup.** Provide installation, configuration, and recovery steps. Validate end to end with a representative action after a cold boot.

**Exit criterion.** The Q5 runs the action reliably after a cold boot, a sleep cycle, and a Wi-Fi interruption.

## PR order

Start with **1.1 → 1.2 → 1.3**. Run stock-package research and access to a Windows host in parallel. Offline build and ROM inventory work can advance while hardware access is pending. The Linux build and hardware validation in 3.1 run independently of stock backup and restore in 3.2 and 3.3. Each PR should carry test evidence and list any hardware gate it leaves open. Keep hardware results tied to the tested version, configuration, and artifact hashes.
