# Q5 readback diagnostic excerpts

## Run checklist

Record the run ID, host and OS, cable and port, boot state, and whether the connection was fresh. Include tool version and hash, driver and backend, scatter and power settings, permissions, timeout, exit status, and evidence path. For readback runs, record the range, byte count, and SHA-256 if data was saved.

Track the last confirmed stage and the first failed, unavailable, or unobserved stage. Use the order **USB enumeration → port or interface open → first protocol reply → handshake → chip ID → platform selection → download-agent upload and initialization → storage discovery → first read → verified read**. Platform selection can be specific to the host tool. Record stages the chosen read-only test does not request as outside its scope. An echoed byte counts as a reply and must still pass the expected handshake checks.

Use up to two fresh powered-off reconnects per configuration, with a bounded timeout for each read-only run. Compare one variable at a time where possible. When the second attempt still fails, record the first failing stage and change a specific variable or stop. Record unavailable hosts, drivers, or capture permissions explicitly. Leave the write gate closed until storage readback and compatibility evidence pass.

| Saved run | Last confirmed stage | First failure or limit | Local evidence |
| --- | --- | --- | --- |
| Linux SP Flash Tool without scatter | Chip ID `0x6582` | Platform selection failed after identification, before download-agent start | SP Flash Tool log for the `14-21-27` run |
| Windows VM automatic scan | USB enumeration | COM5 failed to open | `firmware/q5-windows-usb.ruRuxD/` |
| Windows VM COM6, fresh reconnect | Port open and opening writes completed | First protocol reply absent in the capture | `firmware/q5-windows-fresh.mQJnFH/summary.txt` |
| Native libusb, fresh reconnect | First protocol reply | Opening byte echoed instead of the expected handshake response | `firmware/q5-usb-fresh.fne0dM/fresh-connection.log` |
| Linux SP Flash Tool, limited restore attempt | Port open | Stalled at the opening handshake before download-agent start | `firmware/q5-limited-restore.GtnLd2/restore.log` |
| Live serial probe, 2026-11-23 | Handshake `0x5F` | Not continued to chip ID; the unit booted Android | Station-only `q5catch/probe*.py` |
| Live session, 2026-11-23 (boot) | Android booted, `Q5-WV3.20` baseline | ADB `offline` and USB debugging not enableable | On-device About screen |
| Live preloader, echo sub-state | Port open (echo) | Opening byte returned verbatim (`a0` -> `a0`); no handshake | Station-only `q5catch/probe*.py` |
| BROM entry attempt, Vol+/Vol-/Power | Boot splash then preloader | No `0e8d:0003` seen; bus monitor logged only `0e8d:2000` | Host `journalctl -k` during the attempt |
| mtkclient serial, 2026-11-23 | Port open (echo sub-state) | Handshake never completed; no GPT or read produced | Station-only `q5catch/mtk-serial*.log` |

## SP Flash Tool on Linux

The scatter-free serial run recognized the preloader and read the chip ID. The stock-scatter run selected a legacy backend and stalled at the handshake.

```text
chip id: hw_code[0x6582] hw_sub_code[0x8A00] hw_version[0xCA01] sw_version[0x1]
Not Support platform: , type:
SEND(0xA0)->RECV(0xA0), fail_retry(1).
```

## Native libusb client

The fresh connection returned this pair 12 times.

```text
01 OUT endpoint=0x01 requested=1 status=0 actual=1 a0
02 IN  endpoint=0x81 requested=512 status=0 actual=1 a0
```

## Standalone Linux serial probe

```text
Waiting for the Q5 serial port
Opening /dev/ttyACM0
TX a0 RX (timeout)
TX a0 RX (timeout)
TX a0 RX (timeout)
Standard handshake did not complete
```

## Live preloader handshake (2026-11-23)

Left alone, the preloader floods `READY` on `/dev/ttyACM0` and resets after a few seconds (about a 14 s cycle on port `3-6`). A single `0xA0` is lost in that stream; retrying `0xA0` in a tight loop elicits `0x5F`, matching the historical SP Flash Tool sequence. DTR/RTS state does not change the result. The unit then booted Android `Q5-WV3.20`. Across power cycles the preloader also presented two other behaviours: **echo** (the opening byte returned verbatim, `a0` -> `a0`) and **silent** (no output). Only the READY-flood state accepts the handshake, and after repeated power cycles the device settled in the echo state. Holding Vol+/Vol-/Power did not reach BROM; a bus monitor observed only `0e8d:2000`.

```text
RX 52 45 41 44 59 52 45 41 44 59 ...   ("READY" repeated)
TX a0 (retried) -> RX ... 5f
```

## Offline SP Flash Tool backend selection

The device-isolated debugger stopped at the connection entry point. Selector
`0` is the unset value. The historical adapter log records that the
scatter-free hardware run used library version 2.

| Configuration | Observed assignments | Selector at connect |
| --- | --- | --- |
| Scatter-free USB | None | 0 |
| Stock scatter with USB | 2, then 1 | 1 |
| Stock scatter with UART | 2, then 1 | 1 |

## Stock restore and corrected readback

The Download Only configuration enabled `BOOTIMG` and `ANDROID` only.
After a reconnect, a debugger found SP Flash Tool waiting in
`BRom_AutoBoot::BRom_StartCmd`. The attempt stopped there with no image transfer.

The subsequent `power="WithoutBattery"` readback opened `/dev/ttyACM0`
and stalled at the same opening handshake. The 110-second outer timeout
returned exit 124 and no readback file.
