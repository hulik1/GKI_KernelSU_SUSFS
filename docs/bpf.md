# BTF / eBPF / FUSE-BPF

This kernel includes support for BTF (BPF Type Format), eBPF (extended Berkeley Packet Filter), and FUSE-BPF.

## BTF (`CONFIG_BTF`)

BTF provides type information for BPF programs, enabling better introspection and debugging of BPF-based features. BTF is also used by various kernel tooling and debugging facilities.

## eBPF (`CONFIG_BPF_EVENTS`)

eBPF allows sandboxed programs to run in the kernel without changing kernel source code or loading modules. `CONFIG_BPF_EVENTS` enables BPF programs to attach to kernel events for tracing, monitoring, and other purposes.

## FUSE-BPF (`CONFIG_FUSE_BPF`)

FUSE-BPF enables BPF programs to interact with FUSE (Filesystem in Userspace) filesystems. This is useful for BPF-based debugging and tooling that involves FUSE-mounted filesystems.

## Build Integration

These options are enabled via kernel configuration and are included when the `use_bpf` feature flag is set in the build workflow.

## Related

- [index.md](../index.md) — full feature index
