# NTSync

High-performance synchronization primitives compatible with Windows NT kernel API. Internal to performance category.

## Source

- **Internal**

## Purpose

NTSync brings Windows-compatible synchronization primitives (such as those used by NT kernel objects) to the Android kernel, which can be useful for compatibility with software expecting Windows-style synchronization behavior.

It is documented as internal to the performance category.

## Build Integration

NTSync is enabled via the `use_ntsync` feature flag in the build workflow. It is enabled by default.

## Related

- [performance.md](performance.md) — performance category
- [index.md](index.md) — full feature index
