# Ptrace Leak Fix

Applicable to kernels older than 5.16, this fix addresses a ptrace-related information leak.

## Purpose

On kernels older than 5.16, a ptrace-related information leak may be present. This fix patches the kernel to close that leak, improving security for systems using ptrace.

## Build Integration

The ptrace leak fix is applied as a patch during the build workflow when `use_ptrace` is enabled. It is enabled by default.

## Related

- [index.md](../index.md) — full feature index
