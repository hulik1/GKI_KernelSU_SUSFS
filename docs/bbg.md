# Baseband Guard (BBG)

Baseband Guard is a lightweight Linux Security Module (LSM) for the Android kernel, designed to block unauthorized writes to critical partitions and device nodes at the system level.

## Source

- **Source:** [vc-teahouse/Baseband-guard](https://github.com/vc-teahouse/Baseband-guard)

## Purpose

BBG protects critical baseband-related partitions and device nodes from unauthorized modifications. It operates at the kernel security module level, intercepting write operations to protected resources.

## Build Integration

When `use_bbg` is enabled in the build workflow, BBG is included in the kernel build. It is enabled by default.

## Related

- [index.md](../index.md) - full feature index
