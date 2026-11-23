# Timmkoo Q5 Readback

This project investigates how to back up the stock firmware on a Timmkoo Q5 running `Q5-WV3.20` using Linux. The device reported a MediaTek MT6582. Firmware readback remains unverified.

- [Handoff](HANDOFF.md) records the experiments and the next diagnostic step. Paths under `firmware/` refer to locally acquired tools and artifacts.
- [Recovery plan](docs/q5-stock-recovery.md) tracks the checks required before another restore attempt.
- [Diagnostic excerpts](docs/diagnostic-excerpts.md) record the chip-ID result, connection traces, and readback outcomes.
- [Serial probe](scripts/q5-serial-probe.py) uses Python 3 and the Linux CDC ACM serial driver. It stops at the preloader handshake without accessing storage.

To reproduce the serial test, power off and disconnect the Q5, run `python3 -u scripts/q5-serial-probe.py`, then reconnect once the probe reports that it is waiting. Your account needs access to the Q5's serial device.
