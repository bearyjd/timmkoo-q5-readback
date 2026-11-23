# Q5 readback diagnostic excerpts

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
