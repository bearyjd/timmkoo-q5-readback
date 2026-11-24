# Timmkoo Q5 firmware handoff

## Claude Code continuation

**Goal.** Ship a native Linux CLI for one confirmed Q5 board and stock package. It should identify the device, back up its firmware, preview exact write ranges, flash the approved partitions, and verify the result by readback. The user has specialist models for reconstructing the vendor protocol. Stock recovery can proceed through a proven vendor route while the Linux tool is developed.

**Workspace.** Branch `docs/q5-windows-readback` is two commits ahead of its upstream. The roadmap and diagnostic checklist edits are in the working tree, and the protocol brief is untracked. Preserve these drafts when continuing. No device operation occurred during the roadmap session.

| File | Use |
| --- | --- |
| [docs/roadmap.md](docs/roadmap.md) | Milestones, PR dependencies, approvals, and specialist assignments. Milestone 4 covers native flash implementation, hardware qualification, and release. |
| [docs/q5-protocol-analysis.md](docs/q5-protocol-analysis.md) | PR 2.4 assignment and local evidence paths for the identification specialist. |
| [docs/diagnostic-excerpts.md](docs/diagnostic-excerpts.md) | Stage checklist, including platform selection between chip ID and download-agent initialization. |
| [docs/q5-stock-recovery.md](docs/q5-stock-recovery.md) | Board, map, backup, and rollback requirements for the existing stock recovery scope. |
| `firmware/protocol-analysis-software/INVENTORY.md` | Local-only pinned software, including Updater CE 2.5.6.5 source and portable builds. All 15 entries passed `sha256sum -c firmware/protocol-analysis-software/SHA256SUMS` on this workstation. |

**First unresolved stage.** The historical scatter-free Linux vendor run read MT6582 and failed platform selection. The later scatter-free run stalled earlier. The native Linux client captured an opening-byte echo and rejected it, while the fresh Windows VM COM6 trace recorded 381 completed opening writes with zero incoming bulk payload. Backend selection, connection state, and receive timing remain competing explanations. The device history and exact artifact paths are below.

**Resolved 2026-11-23.** The unit boots stock `Q5-WV3.20` (see the live session below), so the stored "would not boot" state was a soft boot-loop rather than a brick, and the preloader handshake is reachable by retrying `0xA0` until `0x5F`. The remaining gap is a verified firmware backup. ADB/root is unavailable, so preloader -> download agent -> readback is the only route.

**Next steps.**

1. Run `git status --short --branch` from this workspace and reconcile the baseline under PR 1.1. Use the protocol brief to assemble a small local evidence packet for PR 2.4 from the historical successful run, contrasting captures, and pinned source.
2. Use the user's chosen specialist model to produce a stage matrix, ranked hypotheses, and one bounded identification-only test card. Arrange independent review of source and trace references before PR 2.3. Confirm the model and evidence scope with the user before any hosted transfer.
3. Advance package compatibility research (PR 2.1) and the device-free Linux build (PR 3.1) in parallel. Before opening a hardware window, confirm capture access, the device and operation in scope, and stop conditions.
4. For a firmware backup, use the preloader -> download agent -> readback path (PR 3.4) now that the handshake is reachable. Keep it read-only until an independent duplicate read with matching hashes is complete.

**Approval boundary.** The existing device write approval covers vendor Download Only with WV3.25 `BOOTIMG` and `ANDROID`, subject to the recovery gates. Native writes require a demonstrated independent fallback and separate exact-device and exact-plan approval. Keep raw captures, dumps, and vendor bundles local unless the user approves sharing.

## Goal

Obtain a recoverable copy of the installed firmware through a verified readback path and restore normal stock boot if needed. Develop native Linux readback in parallel. Once backup and rollback are verified, establish a custom ROM baseline and assess an unofficial LineageOS 14.1 port using Lithium 7 as a reference. The Q5 may become a Wi-Fi home automation remote.

## Current state

- The Timmkoo Q5 runs stock build `Q5-WV3.20`, model `Q5`, Linux `3.4.67 build@dsj #1` dated September 2, 2022. On 2026-11-23 the unit booted a working Android baseline (battery 87%, Wi-Fi up), confirming the build and that the device is not bricked. One earlier preloader run identified MediaTek `MT6582`, hardware subcode `0x8A00`. The owner's earlier "would not boot" symptom matches a soft boot-loop between the preloader and the bootloader described below. No flash writes or firmware backup have occurred.
- The replacement data cable works. Last observed USB state was `0e8d:2000` on Linux port `3-6` at 480 Mb/s. The reboot-scoped udev rule at `/run/udev/rules.d/78-q5-readback.rules` no longer exists after later host reboots, so non-root tools hit `errno 13` again; see the live session below for the current access route.
- An earlier `win11-kindle` VM test removed its temporary EHCI configuration and test driver. The later COM6 test installed a Microsoft Update Catalog MediaTek VCOM driver and left it installed. The final COM6 run released USB passthrough and restored the original CD-ROM. Access to a physical Windows PC has yet to be confirmed.

## Live session 2026-11-23

A live USB session on the tower host (Fedora, kernel 7.3.4; device on xHCI port `3-6`) confirmed the following.

- **Baseline confirmed.** The unit booted stock Android `Q5-WV3.20`, model `Q5`, kernel `3.4.67 build@dsj #1 Fri Sep 2 12:15:04 CST 2022`, battery 87%, Wi-Fi up. This matches the original handoff record, so the device is unbricked and on original stock.
- **Boot behaviour.** On power-up the device cycles between two USB identities: the preloader `0e8d:2000` (`MT65xx Preloader`; enumerated ~2-3 s, absent ~11 s, roughly a 14 s period) and the MediaTek bootloader/LK stage `0bb4:0c02` (`MT65xx Android Phone`, MTP plus an ADB interface, serial `0123456789ABCDEF`, where `adb` reports `offline`). It settles in the bootloader stage and eventually boots Android once conditions are right. The stored "would not boot" symptom is this loop, most consistent with a low battery.
- **Preloader sub-states.** Across power cycles the preloader presented three distinct CDC-ACM behaviours: **READY-flood** (streams the ASCII banner `READY`; retrying `0xA0` in a tight loop elicits `0x5F`, matching the historical sequence `a0` -> `READY`, `a0` -> `5F`), **echo** (returns the host's bytes verbatim, `a0` -> `a0`), and **silent** (no output). Only the READY-flood state accepts the handshake, and DTR/RTS state does not change the result. After repeated power cycles the device settled in the echo state, where no host tool could complete the handshake. This is the gate the historical and later runs stalled on.
- **BROM not reachable.** Holding Vol+, Vol-, and Power does not enter BROM (`0e8d:0003`): the device shows its boot splash and falls back to the cycling preloader. A live bus monitor observed no ID other than `0e8d:2000` across the attempt. No button combination tried reached BROM.
- **mtkclient attempt.** `mtkclient` 2.1.4 (installed from source) was run in a privileged container. Its default bulk transport fails on the echo state. Its serial transport was made to open the port (deassert DTR/RTS, explicit `/dev/ttyACM0`, and a tolerant handshake that scans a short read window for the expected complement), but it still could not complete a handshake while the device was in the echo state, so no partition table or read was produced. No flash writes occurred.
- **ADB is blocked.** The bootloader's ADB interface is present but `adb` reports `offline`, and USB debugging cannot be enabled on the device, so there is no adb/root backup path.
- **Access constraints.** `/dev/ttyACM0` is `root:dialout` and the raw USB nodes are `root:root` `0660`; the `/run`-scoped `0e8d` udev rule used earlier is gone after a host reboot, so non-root tools hit `errno 13` again. The session obtained access through a privileged container (`docker run --privileged -v /dev:/dev`), which the host user may run because they are in the `docker` group.

## Files in play

| Path relative to the workspace | Purpose |
| --- | --- |
| `firmware/mediatek-readback` | Built native Linux client. Source is in `firmware/mediatek-readback-client/` at commit `dd4f3640be4a271ee72bd43005986307ad46050f`. The upstream author tested MT6580. Q5 compatibility is unverified. [Upstream source](https://github.com/saleemrashid/mediatek_flash_tool) |
| `firmware/Q5-English.rar` | Timmkoo's original Windows v5.1904.00 tool package. Also contains the newer stock `WV3.25` reference. [Manufacturer guide](https://support.timmkoo.com/download/flashing_tutorial/Flashing_tutorial-Q5_ENG.pdf) |
| `firmware/timmkoo-spft-windows/Q5-English/SP_Flash_Tool_exe_Windows_v5.1904/MTK_AllInOne_DA.bin` | Manufacturer-bundled download agent used by the native client. |
| `firmware/q5-stock-wvga.zip`, `firmware/stock-reference/` | Archived `WV3.27` stock reference. The scatter filename says MT6580, while its internal platform field says MT6582. An exact `WV3.20` recovery image was not found. |
| `firmware/readback-probe*.xml`, `firmware/sp-logs/` | SP Flash Tool probe configurations and Linux logs. The directory ending in `14-21-27` contains chip-ID evidence. The one ending in `14-23-32` records the repeated handshake failure. |
| `firmware/Lithium.Beta.v7.1.06.13.25.zip` | Lithium 7 beta package. The author's documented path starts with booting compatible T-ROM. The published Lithium boot ramdisk imports `init.cm.rc`, labeled “LineageOS extras.” [Release](https://github.com/NoahDomingues/Lithium/releases/tag/v7.1.06.13.25) · [Port developer's install procedure](https://jtechforums.org/t/lithium-os-boot-loop-and-manufactory-os-on-timmkoo/9056/2) |

## What has been tried

- Native Linux SP Flash Tool identified itself as `v5.2032.00` despite its directory name. The first USB access error was `errno 13` on `/dev/ttyACM0`, resolved by the temporary udev rule.
- The Linux probe without a scatter read chip ID `0x6582` and then stopped at `STATUS_SCATTER_HW_CHIP_ID_MISMATCH`. Its log said `Not Support platform:` with a blank platform. With the stock scatter loaded, the legacy handshake repeatedly logged `SEND(0xA0)->RECV(0xA0), fail_retry`.
- The verified Windows `v5.1904.00` tool showed the same repeated handshake failure on xHCI COM3, including after a fresh reconnect. It also failed on EHCI COM4 using the existing connection. No fresh reconnect was captured during the EHCI run.
- A subsequent Windows VM retry with the current data cable passed the already connected Q5 through to the guest. Windows detected `MT65xx Preloader` with a PnP error and exposed no MediaTek COM port. The read-only tool timed out scanning USB. The host-side Q5-only capture contained 11 control requests and their 11 completions, with no bulk transfers. See `firmware/q5-windows-usb.ruRuxD/windows-vm-test.pcap`. The matching MediaTek VCOM driver from Microsoft Update Catalog is staged on a guest ISO.
- After the Microsoft Catalog VCOM driver installed, SP Flash Tool's automatic scan selected COM5 and reported `S_COM_PORT_OPEN_FAIL(1013)`. Windows reported COM6 as openable. An explicit COM6 readback on the existing physical connection reached the handshake. The Q5-only sample contained 189 successful `0xA0` bulk writes and no incoming bulk payload. Windows issued CDC line-coding and control-line requests. The native Linux client, retested on the same physical connection after detaching the guest, sent one `0xA0` and timed out on its input transfer. It issued one class control request before bulk I/O. No firmware was read or written. See `firmware/q5-windows-usb.ruRuxD/handshake-comparison.txt`.
- A fresh physical reconnect using the same cable and installed Windows driver reproduced the COM6 handshake stall. In 10,000 captured USB records, Windows submitted 381 `0xA0` writes and all completed successfully, with zero incoming bulk payload bytes. The read-only run was stopped, the USB passthrough released, and the original VM CD restored. The MediaTek VCOM driver remains installed in the guest. See `firmware/q5-windows-fresh.mQJnFH/windows-fresh.pcap` and `summary.txt`.
- Matching submissions and completions in the saved USB traces showed that Windows had a bulk read pending at every captured opening write, on both the fresh and existing connection. The native libusb client queued its read after its opening write completed. Neither received input in these samples. Linux's stock `cdc_acm` driver queues reads as part of opening the serial port. A follow-up capture through that driver did not start because USB monitor access was unavailable.
- The native client parsed Timmkoo's download agent and reached `Syncing with MediaTek Preloader...` on both the existing connection and a fresh powered-off connection. On the fresh attempt, Linux enumerated `0e8d:2000` on port `3-6` at 480 Mb/s. The probe timed out after 90 seconds (exit 124) with a zero-byte output. See `firmware/q5-probe.tSY2b6/readback.log`.
- A subsequent libusb capture on a fresh powered-off connection recorded 12 successful request/reply pairs. Each request sent `0xA0` and each reply returned `0xA0`, matching the SP Flash Tool log. The native client expects `0x5F` at this step. The capture stopped after 24 transfers with a zero-byte output. See `firmware/q5-usb-fresh.fne0dM/fresh-connection.log`.
- The handshake-only serial probe opened `/dev/ttyACM0` on a fresh powered-off connection at 115200 baud. All three initial requests timed out without a reply or `READY` banner. The probe stopped before sending a download agent or accessing storage. See `firmware/q5-serial-probe.HWIThk/run.2piMuI/serial.log`.
- The bundled Linux SP Flash Tool now starts again. Its logger tried to create `/Users` on Linux and aborted. A temporary Bubblewrap mount supplied a writable `/Users`. On the existing Q5 connection, the scatter-free readback timed out scanning USB, both with automatic discovery and with port `3-6` specified. A targeted USB reset removed the serial interface without re-enumerating the device. A fresh reconnect with the tool scanning did enumerate the Q5 and open `/dev/ttyACM0`. The serial backend then retried the first handshake byte without a reply until the outer timeout. No dump was created. See `firmware/q5-vendor-fresh.nvVIWe/console.log` and the `GLB_20261122-203119_0.log` under its log directory.
- An instrumented repeat with the Q5 left powered off recorded successful serial setup at 115200 baud and a flush of both serial queues. SP Flash Tool took 102 ms to open the port, close to 111 ms in the earlier successful chip-ID run. It logged 2,588 first-byte sends and zero replies. No dump was created. See `firmware/q5-vendor-serial.OgOcZc/console.log` and `GLB_20261122-205024_0.log` under its log directory.
- On 2026-11-23 a live session on port `3-6` observed the preloader `0e8d:2000` cycling (about a 14 s period) and the bootloader `0bb4:0c02`. A serial probe that retried `0xA0` reached `0x5F`; a single `0xA0` was buried in the device's continuous `READY` output. Helper scripts were kept on the workstation (`q5catch/probe*.py`), not in the repository.
- The device later booted Android `Q5-WV3.20`. `adb` reported the bootloader interface as `offline`, `fastboot` and MTP did not respond, and USB debugging could not be enabled, so no adb/root backup path was available.

## Current best theory

The earlier scatter-free SP Flash Tool run used the v2 library on `/dev/ttyACM0` at 115200 baud. It recognized the `READY` preloader banner, completed the handshake, and read the chip ID twice before failing platform selection. See `GLB_20261122-142127_0.log` under the `14-21-27` run. The stock scatter sets platform `MT6582_S00` and selects the v1 library on the same serial device. A device-isolated GDB trace confirmed that `DL_LoadScatter` sets this selection before USB discovery, and the documented `BromUART` option leaves it at v1. See `firmware/q5-backend-trace.54e8wV/*-connect.log`.

The `without-battery="true"` readback timed out at the opening handshake. Offline GDB confirmed that this SP Flash Tool build accepts `power="WithoutBattery"` instead. The corrected read-only probe detected a fresh powered-off reconnect and opened `/dev/ttyACM0`. It then retried the opening handshake until the 110-second outer timeout (exit 124), with no readback file. See `firmware/q5-usb-power-verified.FENd1d/console.log` and the `22-01-11` run's `BROM_DLL_V5.log`.

The 2026-11-23 live session narrows the earlier ambiguity: in this power state the preloader emits a continuous `READY` banner and answers `0xA0` with `0x5F` only when the opening byte is retried, so a host that sends `0xA0` once and reads immediately can miss the reply. The device then boots stock, so the earlier "no reply" runs are consistent with missing the preloader window or losing the single opening byte rather than a device fault.

## Stock recovery candidate

The `MX2-WVGA_TM-WV3.25-20240606` image in Timmkoo's English Q5 package passed the RAR integrity check. Its scatter, MBR, and EBR1 are byte-identical to the archived WV3.27 equivalents. Both scatters declare `MT6582`, `eastaeon80_wet_kk`, and eMMC despite the `MT6580` filename. The preloader, LK, boot, and recovery images differ between versions. USB enumerates the unit as MediaTek `0e8d:2000` with no USB serial number or board identifier in its descriptors. The rear label just says Timmkoo Q5 Digital Player. The installed `Q5-WV3.20` board revision and partition layout remain unverified.

An authorized WV3.25 Download Only attempt enabled `BOOTIMG` and `ANDROID` exclusively. SP Flash Tool detected the powered-off Q5 reconnect at port `3-6` and opened `/dev/ttyACM0`. After repeated serial retries, the process was stopped while a debugger confirmed it was still waiting inside `BRom_StartCmd`. It never transferred the download agent or wrote either image. See `firmware/q5-limited-restore.GtnLd2/restore.log` and `BROM_DLL_V5.log` under the `21-38-54` run.

## Reproduce the Linux readback probe

1. Have the user power off and unplug the Q5. Confirm the old preloader has disappeared with `lsusb -d 0e8d:` before arming the client.
2. Run the following from the workspace root. Once the client says it is waiting, have the user plug in the powered-off Q5 with the known data cable.

   ```bash
   set -o pipefail
   umask 077
   q5_probe=$(mktemp -d firmware/q5-probe.XXXXXX)
   q5_da=firmware/timmkoo-spft-windows/Q5-English/SP_Flash_Tool_exe_Windows_v5.1904/MTK_AllInOne_DA.bin
   timeout 90s stdbuf -oL -eL firmware/mediatek-readback -d "$q5_da" \
     -a 0 -l 0x100000 -D "$q5_probe/emmc-user-first-mib.bin" 2>&1 | tee "$q5_probe/readback.log"
   ```

3. Require a reported successful read and exactly `1048576` bytes, then check the data and record its hash. This is a connectivity probe. Confirm the actual device partition layout and acquire and verify a recovery-grade backup before treating it as available.
4. After a usable baseline, compare Lithium's boot ramdisk and the Q5 vendor files with a LineageOS 14.1 MT6582 reference. Prioritize display, touch, Wi-Fi, and sleep/wake for the remote.
