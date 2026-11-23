import os
from pathlib import Path
import select
import termios
import time
import tty


def find_device():
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        for entry in Path("/sys/class/tty").glob("ttyACM*"):
            usb_interface = (entry / "device").resolve()
            for parent in usb_interface.parents:
                try:
                    vendor = (parent / "idVendor").read_text().strip()
                    product = (parent / "idProduct").read_text().strip()
                except FileNotFoundError:
                    continue
                if (vendor, product) == ("0e8d", "2000"):
                    path = Path("/dev") / entry.name
                    if path.exists() and os.access(path, os.R_OK | os.W_OK):
                        return path
                break
        time.sleep(0.02)
    raise SystemExit("Timed out waiting for an accessible Q5 serial port")


def read_exact(port, size):
    data = bytearray()
    deadline = time.monotonic() + 0.5
    while len(data) < size:
        remaining = deadline - time.monotonic()
        if remaining <= 0 or not select.select([port], [], [], remaining)[0]:
            break
        chunk = os.read(port, size - len(data))
        if not chunk:
            break
        data.extend(chunk)
    return bytes(data)


print("Waiting for the Q5 serial port")
device = find_device()
print(f"Opening {device}")
port = os.open(device, os.O_RDWR | os.O_NOCTTY)
try:
    tty.setraw(port, when=termios.TCSANOW)
    attributes = termios.tcgetattr(port)
    attributes[4] = termios.B115200
    attributes[5] = termios.B115200
    termios.tcsetattr(port, termios.TCSANOW, attributes)

    for attempt in range(3):
        for request in bytes.fromhex("a0 0a 50 05"):
            os.write(port, bytes([request]))
            reply = read_exact(port, 1)
            if request == 0xA0 and reply == b"R":
                reply += read_exact(port, 4)
            print(f"TX {request:02x} RX {reply.hex(' ') or '(timeout)'}")
            if reply != bytes([request ^ 0xFF]):
                break
        else:
            print("Standard handshake completed. No further commands sent.")
            break
    else:
        raise SystemExit("Standard handshake did not complete")
finally:
    os.close(port)
