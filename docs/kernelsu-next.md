# KernelSU-Next

KernelSU-Next is a root solution for Android GKI devices that operates in kernel mode and grants root permission to userspace applications from kernel space.

## Source

- **Official:** [KernelSU-Next/KernelSU-Next](https://github.com/KernelSU-Next/KernelSU-Next) (`dev` branch)
- **SUSFS-enabled fork:** [pershoot/KernelSU-Next](https://github.com/pershoot/KernelSU-Next) (`dev-susfs` branch, used when `use_susfs` is enabled)

## How This Repo Uses It

- Built when `root_flavor` is **`KernelSU-Next`** or **`All`**.
- With SUSFS enabled, kernel sources come from the `pershoot/KernelSU-Next` fork.
- Without SUSFS, kernel sources come from the official `KernelSU-Next/KernelSU-Next` `dev` branch.
- Always resolves at latest dev-tip (not pinned).

## Manager

The KernelSU-Next manager APK is built from the official `KernelSU-Next/KernelSU-Next` repo and must match the kernel version (e.g., kernel version `30100` → manager version `30100`).

## Related

- [kernelsu.md](kernelsu.md) - KernelSU
- [resukisu.md](resukisu.md) - ReSukiSU
- [susfs4ksu.md](susfs4ksu.md) - root hiding add-on
- [index.md](../index.md) - full feature index
