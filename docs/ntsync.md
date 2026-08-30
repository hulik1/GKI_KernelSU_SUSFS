# NTSync

NTSync provides high-performance, low-latency synchronization primitives compatible with the Windows NT kernel API.

It is included in builds from this repository when the corresponding feature flag is enabled.

## Purpose

NTSync brings Windows-compatible synchronization primitives (such as those used by NT kernel objects) to the Android kernel, which can be useful for compatibility with software expecting Windows-style synchronization behavior.

## Build Integration

NTSync is enabled via the `use_ntsync` feature flag in the build workflow. It is enabled by default.

## Related

- [index.md](../index.md) — full feature index
