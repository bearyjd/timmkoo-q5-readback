# Timmkoo Q5 firmware handoff

## Goal

Replace the stock Q5 firmware. First get a recoverable copy of the installed firmware using native Linux. Then establish a working custom-ROM baseline and assess an unofficial LineageOS 14.1 port using Lithium 7 as a reference. The Q5 may become a Wi-Fi home automation remote.

## Current state

- Device is a Timmkoo Q5 with stock build `Q5-WV3.20` and Linux `3.4.67` dated September 2, 2022. A preloader handshake confirmed MediaTek `MT6582`, hardware subcode `0x8A00`. No flash writes or firmware backup occurred.
- The replacement data cable works. Last observed USB state was `0e8d:2000` on Linux port `3-6` at 480 Mb/s. A reboot-scoped udev rule at `/run/udev/rules.d/78-q5-readback.rules` grants the current user access to that VID/PID. Recheck the connection and permissions after a host reboot.
- The `win11-kindle` VM is shut off. The temporary EHCI configuration and MediaTek driver were removed, the staged guest files were recycled, and the original USB controller and CD-ROM configuration were verified. There is no physical Windows PC available.

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
- The native client parsed Timmkoo's download agent and reached `Syncing with MediaTek Preloader...` on both the existing connection and a fresh powered-off connection. On the fresh attempt, Linux enumerated `0e8d:2000` on port `3-6` at 480 Mb/s. The probe timed out after 90 seconds (exit 124) with a zero-byte output. See `firmware/q5-probe.tSY2b6/readback.log`.
- A subsequent libusb capture on a fresh powered-off connection recorded 12 successful request/reply pairs. Each request sent `0xA0` and each reply returned `0xA0`, matching the SP Flash Tool log. The native client expects `0x5F` at this step. The capture stopped after 24 transfers with a zero-byte output. See `firmware/q5-usb-fresh.fne0dM/fresh-connection.log`.
- The handshake-only serial probe opened `/dev/ttyACM0` on a fresh powered-off connection at 115200 baud. All three initial requests timed out without a reply or `READY` banner. The probe stopped before sending a download agent or accessing storage. See `firmware/q5-serial-probe.HWIThk/run.2piMuI/serial.log`.

## Current best theory

The earlier scatter-free SP Flash Tool run used the serial backend on `/dev/ttyACM0` at 115200 baud. It recognized the `READY` preloader banner, completed the handshake, and read the chip ID twice before failing platform selection. See `GLB_20261122-142127_0.log` under the `14-21-27` run. Adding the stock scatter populated the platform as `MT6582_S00` but selected a different connection backend that stalled at the first handshake byte. The standalone serial probe confirmed port access but did not reproduce the handshake. Compare SP Flash Tool's serial initialization and timing with the minimal probe before changing the readback client.

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
