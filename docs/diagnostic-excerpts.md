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
