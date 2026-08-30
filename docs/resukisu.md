# ReSukiSU

ReSukiSU is a root solution for Android GKI devices that operates in kernel mode and grants root permission to userspace applications from kernel space. It is a fork/variant of KernelSU maintained by the ReSukiSU project.

## Source

- **Source:** [ReSukiSU/ReSukiSU](https://github.com/ReSukiSU/ReSukiSU) (`main` branch)
- **Pinned commit:** `03b60f260cce36f23efbd26c9c334edfdc9ce7eb`

Pinned in `main.yml` as `PIN_RESUKISU` and resolved via `pick` so builds are always verified against an exact commit.

## How This Repo Uses It

- Built when `root_flavor` is **`ReSukiSU`** or **`All`**.
- SUSFS patches are applied during the build workflow (when `use_susfs` is enabled), and ReSukiSU also has its own per-flavor SUSFS pins.
- Resolved at the pinned commit in verified mode; at latest `main` tip in latest mode.

## Manager

The ReSukiSU manager APK is built from `ReSukiSU/ReSukiSU`. The manager version should match the kernel version (e.g., kernel version `30100` → manager version `30100`).

## Related

- [kernelsu.md](kernelsu.md) - KernelSU
- [kernelsu-next.md](kernelsu-next.md) - KernelSU-Next
- [susfs.md](susfs.md) - root hiding add-on
- [index.md](../index.md) - full feature index
