# KernelSU / KernelSU-Next / ReSukiSU

KernelSU is a root solution for Android GKI devices that operates in kernel mode and grants root permission to userspace applications directly from kernel space.

This repository builds kernels that integrate KernelSU, KernelSU-Next, and ReSukiSU depending on the selected `root_flavor` at build time.

## Source Locations

| Implementation | Upstream Repository | Branch Used |
|----------------|---------------------|-------------|
| KernelSU-Next (manager) | [KernelSU-Next/KernelSU-Next](https://github.com/KernelSU-Next/KernelSU-Next) | `dev` |
| KernelSU-Next (kernel with SUSFS) | [pershoot/KernelSU-Next](https://github.com/pershoot/KernelSU-Next) | `dev-susfs` (when SUSFS enabled) |
| KernelSU (classic) | [tiann/KernelSU](https://github.com/tiann/KernelSU) | `main` |
| ReSukiSU | [ReSukiSU/ReSukiSU](https://github.com/ReSukiSU/ReSukiSU) | `main` |

## Manager

Each root implementation ships its own KernelSU Manager APK. The manager must match the kernel version for full compatibility.

- **KernelSU-Next manager:** built from the official `KernelSU-Next/KernelSU-Next` repo at `dev`-tip.
- **KernelSU manager:** built from `tiann/KernelSU`.
- **ReSukiSU manager:** built from `ReSukiSU/ReSukiSU`.

## Version Compatibility

Ensure the manager version and the kernel version match. For example, if the kernel reports version `30100`, use manager version `30100`.

## SUSFS Integration

When `use_susfs` is enabled, KernelSU-Next kernels are sourced from the `pershoot/KernelSU-Next` fork on the `dev-susfs` branch. Classic KernelSU and ReSukiSU get SUSFS patches applied during the build workflow.

For more on the root-hiding side of SUSFS, see [susfs.md](susfs.md).

## Related

- [susfs.md](susfs.md) — root hiding add-on
- [nomount.md](nomount.md) — NoMount metamodule
- [index.md](../index.md) — full feature index
