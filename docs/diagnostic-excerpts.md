# Q5 readback diagnostic excerpts

## Run checklist

Record the run ID, host and OS, cable and port, boot state, and whether the connection was fresh. Include tool version and hash, driver and backend, scatter and power settings, permissions, timeout, exit status, and evidence path. For readback runs, record the range, byte count, and SHA-256 if data was saved.

Track the last confirmed stage and the first failed, unavailable, or unobserved stage. Use the order **USB enumeration → port or interface open → first protocol reply → handshake → chip ID → download-agent start → verified read**. Record stages the chosen read-only test does not request as outside its scope. An echoed byte counts as a reply and must still pass the expected handshake checks.

Use up to two fresh powered-off reconnects per configuration, with a bounded timeout for each read-only run. Compare one variable at a time where possible. When the second attempt still fails, record the first failing stage and change a specific variable or stop. Record unavailable hosts, drivers, or capture permissions explicitly. Leave the write gate closed until storage readback and compatibility evidence pass.

| Saved run | Last confirmed stage | First failure or limit | Local evidence |
| --- | --- | --- | --- |
| Linux SP Flash Tool without scatter | Chip ID `0x6582` | Platform selection failed after identification, before download-agent start | SP Flash Tool log for the `14-21-27` run |
| Windows VM automatic scan | USB enumeration | COM5 failed to open | `firmware/q5-windows-usb.ruRuxD/` |
| Windows VM COM6, fresh reconnect | Port open and opening writes completed | First protocol reply absent in the capture | `firmware/q5-windows-fresh.mQJnFH/summary.txt` |
| Native libusb, fresh reconnect | First protocol reply | Opening byte echoed instead of the expected handshake response | `firmware/q5-usb-fresh.fne0dM/fresh-connection.log` |
| Linux SP Flash Tool, limited restore attempt | Port open | Stalled at the opening handshake before download-agent start | `firmware/q5-limited-restore.GtnLd2/restore.log` |

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
