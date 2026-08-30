# Performance Tuning

This kernel includes performance-related tuning and options, including NTSync.

## Features

| Feature | Description |
|---------|-------------|
| NTSync | High-performance synchronization primitives compatible with Windows NT kernel API. Internal to performance category. |
| Performance Tuning | Kernel configuration and tuning options and optimizations aimed at improving system responsiveness and throughput. |

## Build Integration

Performance-related features are enabled via the `use_perf` feature flag in the build workflow. This flag is disabled by default. NTSync is controlled separately via `use_ntsync` (enabled by default) but documented under performance.

## Related

- [ntsync.md](ntsync.md) — NTSync details
- [index.md](index.md) — full feature index
