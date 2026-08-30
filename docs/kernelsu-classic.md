# KernelSU (Classic)

Classic KernelSU is a root solution for Android GKI devices that operates in kernel mode and grants root permission to userspace applications from kernel space. It is the original implementation by `tiann`.

## Source

- **Upstream:** [tiann/KernelSU](https://github.com/tiann/KernelSU) (`main` branch)
- **Pinned commit:** `932014ab5b2c9b74a3d11e2ec4d17dd10fc9442e`

Pinned in `main.yml` as `PIN_KERNELSU` and resolved via `pick` so builds are always verified against an exact commit.

## How This Repo Uses It

- Built when `root_flavor` is **`KernelSU`** or **`All`**.
- SUSFS patches are applied during the build workflow (when `use_susfs` is enabled) rather than sourced from a SUSFS-enabled fork.
- Resolved at the pinned commit in verified mode; at latest `main` tip in latest mode.

## Manager

The KernelSU manager APK is built from `tiann/KernelSU`. The manager version should match the kernel version (e.g., kernel version `30100` → manager version `30100`).

## Related

- [kernelsu-next.md](kernelsu-next.md) — KernelSU-Next
- [resukisu.md](resukisu.md) — ReSukiSU
- [susfs.md](susfs.md) — root hiding add-on
- [index.md](../index.md) — full feature index
