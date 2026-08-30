<div align="center">

# Wild Kernels for Android

[![KernelSU](https://img.shields.io/badge/KernelSU-Supported-green)](https://kernelsu.org/)
[![SUSFS](https://img.shields.io/badge/SUSFS-Integrated-orange)](https://gitlab.com/simonpunk/susfs4ksu)

</div>

## Your warranty is no longer valid!

I am **not responsible** for bricked devices, damaged hardware, or any issues that arise from using this kernel.

**Please** do thorough research and fully understand the features included in this kernel before flashing it!

By flashing this kernel, **YOU** are choosing to make these modifications. If something goes wrong, **do not blame me**!

---

### Proceed at your own risk!

---

## Available Devices

| Device | Repository |
|--------|------------|
| **Generic** | [GKI_KernelSU_SUSFS](https://github.com/WildKernels/GKI_KernelSU_SUSFS) |
| **Pixel** | [Sultan_KernelSU_SUSFS](https://github.com/WildKernels/Sultan_KernelSU_SUSFS) |
| **Samsung** | [Samsung_KernelSU_SUSFS](https://github.com/WildKernels/Samsung_KernelSU_SUSFS) |
| **OnePlus** | [OnePlus_KernelSU_SUSFS](https://github.com/WildKernels/OnePlus_KernelSU_SUSFS) |

---

## Features

- [KernelSU-Next](docs/kernelsu-next.md) / [KernelSU (Classic)](docs/kernelsu-classic.md) / [ReSukiSU](docs/resukisu.md) — root implementations
- [SUSFS](docs/susfs.md) — root hiding
- [NoMount](docs/nomount.md) — mount metamodule (root hiding)
- [Baseband Guard](docs/bbg.md) — partition protection
- [Networking](docs/networking.md) — WireGuard, BBR, IPSet, CIFS
- [NTSync](docs/ntsync.md) — NT sync primitives
- [TMPFS](docs/tmpfs.md) — xattr / POSIX ACLs
- [BPF](docs/bpf.md) — BTF / eBPF / FUSE-BPF
- [Ptrace Leak Fix](docs/ptrace.md) — internal to root hiding
- [Unicode Fix](docs/unicode.md) — internal to root hiding (experimental)
- [Performance](docs/performance.md)
- [DroidSpaces](docs/droidspaces.md) — container runtime

Full documentation: [docs/index.md](docs/index.md)

---

## Installation

See **[Installation Guide](docs/installation.md)** — [Kernel Flasher](docs/kernelflasher.md) · [Patch boot.img with magiskboot](docs/magiskboot.md).

---

## Credits

- **KernelSU**: Developed by [tiann](https://github.com/tiann/KernelSU)
- **KernelSU-Next**: Developed by [rifsxd](https://github.com/KernelSU-Next/KernelSU-Next)
- **KernelSU-Next SUSFS Fork**: Developed by [pershoot](https://github.com/pershoot/KernelSU-Next) (`dev-susfs` branch used for SUSFS builds)
- **ReSukiSU**: Developed by [ReSukiSU](https://github.com/ReSukiSU/ReSukiSU)
- **Magic-KSU**: Developed by [5ec1cff](https://github.com/5ec1cff/KernelSU)
- **SUSFS**: Developed by [simonpunk](https://gitlab.com/simonpunk/susfs4ksu)
- **SUSFS Module**: Developed by [sidex15](https://github.com/sidex15)
- **NoMount**: Developed by [maxsteeel](https://github.com/maxsteeel/nomount)
- **DroidSpaces-OSS**: Developed by [ravindu644](https://github.com/ravindu644/Droidspaces-OSS)
- **Baseband-guard (BBG)**: Developed by [vc-teahouse](https://github.com/vc-teahouse/Baseband-guard)
- **Kernel Patches**: Maintained by [WildKernels/kernel_patches](https://github.com/WildKernels/kernel_patches)
- **AnyKernel3**: Maintained by [WildKernels/AnyKernel3](https://github.com/WildKernels/AnyKernel3) (fork of [osm0sis/AnyKernel3](https://github.com/osm0sis/AnyKernel3))
- **Sultan Kernels (Pixel)**: Developed by [kerneltoast](https://github.com/kerneltoast)
- **Device Boot Fix**: [Boot fix commit](https://github.com/Anything-at-25-00/android_kernel_common_android12-5.10/commit/2476d262b597fe8af82cfb7aaf96676f51c6b4ed) for fixing some devices not booting

Special thanks to the open-source community for their contributions!

---

## Support

If you encounter any issues or need help, feel free to:
- Open an issue in this repository
- Reach out to me directly

---

## Disclaimer

Flashing this kernel will void your warranty, and there is always a risk of bricking your device. Please make sure to:
- Back up your data
- Understand the risks before proceeding

**Proceed at your own risk!**

---

<div align="center">

## Connect With Us

[![Telegram](https://img.shields.io/badge/Telegram-TheWildJames-blue?logo=telegram)](https://t.me/TheWildJames)
[![Telegram Group](https://img.shields.io/badge/Telegram-WildKernelsTG-blue?logo=telegram)](https://t.me/WildKernelsTG)

</div>

---

## Special Thanks

**These amazing people help make this project possible!**

| Contributor | Contribution |
|-------------|-------------|
| [simonpunk](https://gitlab.com/simonpunk/susfs4ksu.git) | Created SUSFS! |
| [sidex15](https://github.com/sidex15) | Created module! |
| [backslashxx](https://github.com/backslashxx) | Helped with patches! |
| [Teemo](https://github.com/liqideqq) | Helped with patches! |
| [幕落](https://github.com/MuLuo688) | Donation! |
| [vc-teahouse](https://github.com/vc-teahouse) | Created Baseband-guard (BBG)! |

*If you have contributed and are not listed here, please remind me!* 

---

## Donations

Any and all donations are appreciated!

- PayPal: [bauhd@outlook.com](mailto:bauhd@outlook.com)
- Card: <https://buy.stripe.com/5kQ28sdi08Nr0Xc2fU5os00>
- LTC: MVaN1ToSuks2cdK9mB3M8EHCfzQSyEMf6h
- BTC: 3BBXAMS4ZuCZwfbTXxWGczxHF4isymeyxG
- ETH: 0x2b9C846c84d58717e784458406235C09a834274e
- Patreon: <https://patreon.com/WildKernels>
