# Timmkoo Q5 Development Roadmap

The Q5 last ran WV3.20. One historical run identified an MT6582, but no run has produced a firmware backup or completed a write. The recent Windows VM run opened COM6 and delivered 381 opening writes without receiving a bulk reply. The immediate goal is a repeatable connection and verified readback. Stock recovery makes later ROM work reversible. See [HANDOFF.md](../HANDOFF.md) for the evidence.

## Milestone 1 — Make diagnostics reproducible

1. **Publish the baseline and run checklist.** Reconcile the current driver and VM state in the handoff. Record the known-good cable, fresh versus existing connection, permissions, tool version, first failing stage, and exit status. Distinguish historical chip identification, USB enumeration, protocol exchange, and storage access.
2. **Turn the serial probe into a bounded diagnostic CLI.** Add explicit device selection, timeouts, and a structured run summary. Test unrelated devices, permission failures, timeouts, and disconnects offline. Keep the command limited to identification. [Linux CDC ACM documentation](https://docs.kernel.org/usb/acm.html)
3. **Add a capture summarizer and offline CI.** Use synthetic fixtures to verify USB submission/completion pairing, pending reads, and payload counts. Publish reviewed summaries and keep raw captures and vendor packages local. Demonstrate that someone without a Q5 or firmware can run the tests. [Linux usbmon documentation](https://docs.kernel.org/usb/usbmon.html)

**Exit criterion.** CI passes without hardware, and two people can classify the same sample run at the same first failing stage.

## Milestone 2 — Establish a connection and confirm the stock package

1. **Build the stock compatibility record.** Inventory WV3.25 and the local WV3.27 reference with hashes, scatter regions, and image differences. Seek the exact WV3.20 package or written confirmation of the compatible board, layout, package, and driver from Timmkoo. The published guide identifies WV3.25 with SP Flash Tool v5.1904 and illustrates a full format. Use it to establish provenance and driver requirements. [Timmkoo flashing guide](https://support.timmkoo.com/download/flashing_tutorial/Flashing_tutorial-Q5_ENG.pdf)
2. **Run a physical Windows read-only comparison.** Use the known-good cable and confirmed VCOM driver on bare metal. Record port discovery, tool stage, and identification or first failure on two fresh reconnects. This PR depends on access to a physical Windows host. Compare any community tooling offline by reviewing its documented SP Flash Tool configuration. [Updater CE console configuration](https://github.com/y1-community/updater-ce-neo/blob/main/src/sp_console_config.py)
3. **Test the Linux transports on matched reconnects.** Capture the existing kernel serial path first. If the evidence warrants it, compare the pinned userspace client with a bounded asynchronous receive test that stops after identification. Log which transport reaches which stage. Pursue a kernel driver only if the results identify a specific limitation in both available transports. [libusb I/O documentation](https://libusb.sourceforge.io/api-1.0/libusb_io.html) · [Pinned client's upstream](https://github.com/saleemrashid/mediatek_flash_tool)

**Exit criterion.** A supported route identifies the same chip on two independent cold connections, and compatibility has a recorded decision supported by board and layout evidence. If neither route improves on the opening stall, record the blocker and prioritize vendor service or a known-good same-revision comparison unit before further identical retries.

## Milestone 3 — Verify native Linux backup and restore stock

1. **Package a reproducible read-only Linux build.** Pin the upstream client revision, document Meson and libusb dependencies, and add a device-free build and CLI check. Separate the public readback command from the upstream tool's write interface.
2. **Verify small reads and build the recovery backup.** Require two successful independent 1 MiB reads with exact size, matching SHA-256 hashes, and plausible metadata. Then confirm the hardware partition map and back up the regions needed for recovery. Record sizes, hashes, and a second copy. Record which regions were verified and which remain unavailable.
3. **Run the approved stock restore and record acceptance.** Use the confirmed path under [the stock recovery plan](q5-stock-recovery.md). Require a verified backup and rollback procedure before writing. The current scope covers WV3.25 `BOOTIMG` and `ANDROID` only. A different package, partition scope, or write procedure needs a separate decision.

**Exit criterion.** The native reader reproduces the small read, the recovery backup passes verification, and the stock restore records tool success, a working stock menu, and a second cold boot. Test touch, Wi-Fi, charging, and sleep/wake to establish the hardware baseline.

## Milestone 4 — Establish a custom ROM baseline

1. **Compare boot and partition requirements offline.** Compare the confirmed stock image, T-ROM, and Lithium boot and recovery metadata. Record compatibility prerequisites, required inputs, and redistribution terms. The published Lithium install report describes a working T-ROM boot as a prerequisite. [Lithium 7 beta](https://github.com/NoahDomingues/Lithium/releases/tag/v7.1.06.13.25) · [Port contributor's install report](https://jtechforums.org/t/lithium-os-boot-loop-and-manufactory-os-on-timmkoo/9056/2) · [AOSP boot-image documentation](https://source.android.com/docs/core/architecture/bootloader/boot-image-header)
2. **Validate one compatible community baseline.** After stock recovery passes, test the selected image on a confirmed board and document a stock rollback. Record cold boot, display, touch, Wi-Fi, charging, and sleep/wake.
3. **Decide whether to build a LineageOS 14.1 port.** Identify missing kernel sources, device configuration, and proprietary inputs. Publish a reproducible build and staged bring-up plan if those inputs are available. Otherwise record the blockers and keep the validated baseline.

**Exit criterion.** One custom baseline boots repeatably, stock rollback has been demonstrated, and further port work has a documented feasibility decision.

## Milestone 5 — Prototype the Wi-Fi remote

Proceed if the home automation use case remains a goal. Begin on the first stable OS with the required networking and UI support.

1. **Prototype the smallest interaction.** Define a single action, a local test service, and visible success and error states. Run the UI against the test service without the Q5.
2. **Connect and test on the device.** Check authentication, offline behavior, Wi-Fi reconnect, and sleep/wake. Track regressions against the stock and custom-ROM baselines.
3. **Document a repeatable setup.** Provide installation, configuration, and recovery steps. Validate end to end with a representative action after a cold boot.

**Exit criterion.** The Q5 runs the action reliably after a cold boot, a sleep cycle, and a Wi-Fi interruption.

## PR order

Start with **1.1 → 1.2 → 1.3**. Run stock-package research and access to a Windows host in parallel. Offline build and ROM inventory work can advance while hardware access is pending. Each PR should carry test evidence and list any hardware gate it leaves open. Keep hardware results tied to the tested version, configuration, and artifact hashes.
