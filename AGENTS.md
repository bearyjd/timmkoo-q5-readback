# Repository Guidelines

## Project Structure

This workspace supports firmware recovery and development for the Timmkoo Q5. Start with `HANDOFF.md` for the device version, known results, and the current recovery procedure.

- `firmware/mediatek-readback-client/` contains the native MediaTek C client. Protocol and USB code live in `src/`, public headers in `include/`, and CLI parsing and file I/O in `flash_tool/`.
- `firmware/mediatek-readback` is the existing Linux executable. `firmware/stock-reference/` holds stock firmware images and partition metadata. `firmware/readback-probe*.xml` and `firmware/sp-logs/` hold probe configurations and logs.

## Build and Local Development

Install Meson, Ninja, a C compiler, argp (provided by glibc on Linux), and libusb 1.0.16 or newer with its static development library. Run these commands from the workspace root:

```sh
meson setup /tmp/q5-readback-build firmware/mediatek-readback-client
meson compile -C /tmp/q5-readback-build
/tmp/q5-readback-build/flash_tool/flash_tool --help
```

The commands configure an out-of-tree build, compile the CLI, and check that it starts without a connected device. Use `firmware/mediatek-readback --help` to check the existing binary.

## Coding Style

Use four spaces for C indentation, place opening braces on the same line, and use `snake_case` for functions and variables. Match existing prefixes such as `mtk_device_` for protocol and device functions. Meson enables warning level 3 and treats warnings as errors.

## Testing and Hardware Verification

The native client has no automated test suite or coverage target. Compile and run the CLI help check before testing on hardware. For readback changes, follow `HANDOFF.md` and record the device build, command, exit status, output size, and checksum. Verify a recovery-grade backup before attempting firmware writes.

## Commits and Pull Requests

The nested client checkout uses short, scoped subjects such as `LICENSE: Relicense from MS-RSL to MIT`. In pull requests, summarize the change, link a relevant issue if available, and report the build, CLI, or hardware checks performed. Include relevant log excerpts and keep raw device dumps out of the diff.
