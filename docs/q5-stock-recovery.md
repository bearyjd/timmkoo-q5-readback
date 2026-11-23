# Timmkoo Q5 stock recovery plan

## Objective

Restore normal stock boot on the Timmkoo Q5 previously running `Q5-WV3.20`, if a reproducible manufacturer-supported connection and a compatible stock image can be established. The current evidence is in [HANDOFF.md](../HANDOFF.md#current-best-theory) and [diagnostic excerpts](diagnostic-excerpts.md). The authorized WV3.25 attempt stopped during the first handshake, before any image transfer.

## Acceptance criteria

- Reproduce the different SP Flash Tool backend decisions offline and identify the input or configuration that selects each path.
- Confirm the proposed connection mode on real hardware with a read-only identification or readback run. Record the backend, chip ID or first failing stage, tool exit, and log path.
- Before any write, verify the exact selected image files and partition list again. Use the already authorized stock WV3.25 boot and system scope only if the diagnostics establish a viable connection. A different image or wider write needs a separate decision.
- Verify any completed flash from the tool's terminal result, then confirm the player reaches the stock menu and can boot again. Record any remaining uncertainty.

## Execution

1. **Map and reproduce backend selection.** Compare the historical scatter-free and stock-scatter readback configurations, keeping the binary and image inputs fixed. Trace connection creation and the relevant library dispatch in an isolated process with no device nodes. Compare against the earlier hardware logs.
2. **Check documented configuration.** Look for a supported configuration that preserves the working serial connection while providing valid platform information. Check the vendor schema and Updater CE source before running a candidate. Keep the original scatter and vendor executables intact.
3. **Verify on the device.** Run a bounded, read-only test requiring one powered-off reconnect. If the candidate never reaches the stage it is meant to test, inspect the first divergence before repeating the test.
4. **Restore and verify boot.** If the previous gates pass, use Download Only with the verified partition selection, monitor every stage, and confirm stock boot with the user. If the viable route requires a different package, host, or broader write, identify that dependency with supporting evidence.

## Risks and mitigations

- The generic USB preloader descriptor and MT6582 chip ID do not identify the board or partition layout. Keep the preloader and partition table outside the current write scope.
- A stalled operation can look like an active write. When stopping a failed test, verify its stage first. Allow a transfer that has started to finish.
- Device experiments depend on a physical reconnect. Keep offline experiments independent of the device so progress can continue while it is unavailable.
- Retain full tool logs locally. Publish only reviewed excerpts if separately requested.

## Progress

- **Backend selection reproduced.** Device-isolated GDB runs stopped before USB discovery. The offline scatter-free run retained selector `0`. The historical chip-ID run separately reported use of v2. Loading the stock scatter called `DL_LoadScatter`, set `2`, then selected `1`. Static inspection confirmed that the decision uses the library's built-in chip table. The stock scatter also selected `1` with `BromUART`. See `firmware/q5-backend-trace.54e8wV/*-connect.log`, `firmware/q5-backend-trace.54e8wV/selector-disassembly.txt`, and [HANDOFF.md](../HANDOFF.md#current-best-theory).
- **First power-setting test.** Updater CE uses `without-battery="true"` in its console XML. That file passed the bundled schema, but the hardware run stopped during the first handshake. Subsequent offline comparison showed that this SP Flash Tool binary ignored the attribute. See `firmware/q5-usb-powered.dv28AF/console.log`. [Updater CE console configuration](https://github.com/y1-community/updater-ce-neo/blob/main/src/sp_console_config.py)
- **Corrected power-setting test completed.** GDB confirmed that `power="WithoutBattery"` reaches the mode-selection branch. The probe retained the same scatter, download agent, range, and USB port. On a fresh powered-off reconnect the tool opened `/dev/ttyACM0`, entered `BRom_StartCmd`, and timed out (exit 124) without creating a readback file. See `firmware/q5-usb-power-verified.FENd1d/console.log` and `*-preflight.log`.
- **Hardware acceptance remains open.** The corrected setting did not resolve the handshake. The next distinct environment is the manufacturer-supported Windows path on a physical host, with a vendor-confirmed recovery package and driver. A fresh physical reconnect through the Windows VM with the current cable and VCOM driver reached COM6 but yielded no bulk reply to 381 successful opening writes. The Windows control sequence differs from the Linux client's, but it did not produce a working handshake in the VM. A successful flash and stock boot remain unverified.
