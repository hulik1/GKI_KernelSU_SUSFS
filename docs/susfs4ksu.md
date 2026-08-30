# susfs4ksu

susfs4ksu is a KernelSU add-on that provides root-hiding mechanisms using kernel patches and a userspace module.

## Source

- **Source:** [simonpunk/susfs4ksu](https://gitlab.com/simonpunk/susfs4ksu)
- **Module (userspace add-on):** [sidex15/susfs4ksu-module](https://github.com/sidex15/susfs4ksu-module)

## Capabilities

SUSFS provides multiple root-hiding and spoofing capabilities:

| Capability | Description |
|------------|-------------|
| `SUS_PATH` | Hide suspicious paths from various system calls. Effective on zygote-spawned user app processes with `uid >= 10000`. |
| `SUS_MOUNT` | Assign fake mount IDs to mounts and hide sus mounts from `/proc/self/[mounts|mountinfo|mountstat]` for non-su processes. |
| `SUS_KSTAT` | Spoof kernel statistics for user-defined files/directories. Effective on zygote-spawned user app processes with `uid >= 10000`. |
| `SPOOF_UNAME` | Spoof the string returned by the `uname` syscall to a user-defined string. Effective on all processes. |
| `ENABLE_LOG` | Log SUSFS events to the kernel log. Disable to completely suppress SUSFS logging. |
| `HIDE_KSU_SUSFS_SYMBOLS` | Automatically hide KSU and SUSFS symbols from `/proc/kallsyms`. Effective on all processes. |
| `SPOOF_CMDLINE_OR_BOOTCONFIG` | Spoof `/proc/bootconfig` (GKI) or `/proc/cmdline` (non-GKI) output with a user-defined file. Effective on all processes. |
| `OPEN_REDIRECT` | Redirect a target path to be opened with another user-defined path. Both paths must exist before they can be added. Requires SELinux permissions for both paths. Effective only on processes with a pre-defined UID scheme. |
| `SUS_MAP` | Hide mmapped real files from `/proc/<pid>/[maps|smaps|smaps_rollup|map_files|mem|pagemap]`. No anonymous-memory support; does not hide inline/PLT hooks caused by the injected library itself. May not evade strong injection detection. Effective only on zygote-spawned unmounted user app processes with `uid >= 10000`. |
| `AVC_SPOOF` | Spoof procfs AVC denial logs. Enabled at runtime via the sidex15 module - not a build-time Kconfig option. |

## Build Integration

In this repository, SUSFS kernel patches are applied per Android/kernel version variant. The pinned SUSFS commits per variant are defined in the build workflow (`.github/workflows/main.yml`).

SUSFS is always built at the latest branch tip when the root flavor is KernelSU-Next; for KernelSU and ReSukiSU, it uses the audited pinned commits.

## Related

- [index.md](../index.md) - full feature index
