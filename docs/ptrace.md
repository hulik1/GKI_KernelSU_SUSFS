# Ptrace Leak Fix

Fixes ptrace info leak on kernels older than 5.16. Internal to root hiding.

## Source

- **Source:** Upstream kernel community - [patch](https://github.com/WildKernels/kernel_patches/blob/main/gki_ptrace.patch) (`kernel_patches/gki_ptrace.patch`)

## Purpose

On kernels older than 5.16, a ptrace-related information leak may be present. This fix patches the kernel to close that leak, improving security for systems using ptrace.

It is documented as internal to root hiding (SUSFS/KernelSU) - not a standalone top-level feature.

## Build Integration

The ptrace leak fix is applied as a patch during the build workflow when `use_ptrace` is enabled. It is enabled by default.

## Related

- [susfs.md](susfs.md) - root hiding
- [index.md](index.md) - full feature index
