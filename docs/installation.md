# Installation

> [!CAUTION]
> Flashing a kernel can brick your device and will void your warranty. Make a full backup (boot partition at minimum) before proceeding.

Choose the method that fits your situation:

| Method | When to use | Requires root | Guide |
|--------|-------------|---------------|-------|
| **Kernel Flasher** | Upgrading with root already available, no PC needed | Yes | [kernelflasher.md](kernelflasher.md) |
| **magiskboot** | When you want to flash a pre-patched `boot.img` directly (no pre-rooted setup required) | No | [magiskboot.md](magiskboot.md) |

## Choosing the correct AnyKernel3 ZIP

Each release artifact is named by **KMI** (Kernel Module Interface) and **Security Patch Level (SPL)**.

- **KMI** - e.g. `android12-5.10`, `android13-5.10`, `android13-5.15`, `android14-5.15`, `android14-6.1`, `android15-6.6`, `android16-6.12`. Must match your device's current kernel version. Check with `uname -r` or in **Settings → About phone → Kernel version**.
- **SPL** - monthly security patch string in the filename. Pick the build closest to your current SPL; newer SPL is generally backwards compatible but read the release notes for breaking changes.

If you don't know which file to download, carefully read the description of KMI and Security patch level in the release notes before downloading.

## After flashing (both methods)

- Install / update the matching KernelSU manager APK (`manager-apk-*`).
- If using SUSFS, install the SUSFS module.
- Verify root with `su` or manager app.

---

See also: [Kernel Features Documentation](features.md) · [Releases](https://github.com/WildKernels/GKI_KernelSU_SUSFS/releases)
