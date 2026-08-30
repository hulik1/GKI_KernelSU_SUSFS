# Installation

> [!CAUTION]
> Flashing a kernel can brick your device and will void your warranty. Make a full backup before proceeding.

Choose the method that fits your situation:

| Method | When to use | Guide |
|--------|-------------|-------|
| **Kernel Flasher** | Upgrading with root already available, no PC needed | [kernelflasher.md](kernelflasher.md) |
| **Patch boot.img manually** | Pixel / `lz4_legacy` or non-standard `boot.img` that won't boot directly | [magiskboot.md](magiskboot.md) |

## Choosing the correct AnyKernel3 ZIP

Each release artifact is named by **KMI** and **SPL**:

- **KMI** — `android12-5.10`, `android13-5.10`, `android13-5.15`, `android14-5.15`, `android14-6.1`, `android15-6.6`, `android16-6.12`. Must match `uname -r`.
- **SPL** — monthly security patch level. Pick the build closest to your current SPL.

If you don't know which file to download, read the KMI/SPL description in the release notes.

## After flashing (both methods)

- Install / update the matching KernelSU manager APK (`manager-apk-*`).
- If using SUSFS, install the SUSFS module.
- Verify root with `su` or manager app.

---

See also: [Kernel Features Documentation](index.md) · [Releases](https://github.com/WildKernels/GKI_KernelSU_SUSFS/releases)
