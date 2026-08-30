# Installation

> [!CAUTION]
> Flashing a kernel can brick your device and will void your warranty. Make a full backup (boot partition at minimum) before proceeding. You are responsible for your device.

> [!NOTE]
> This method is more convenient when upgrading KernelSU and can be done without a computer.

## Prerequisites

- Device with unlocked bootloader running a supported GKI kernel (see KMI below)
- Root access already granted to the flashing app (for upgrades) or a working method to flash initially (fastboot / custom recovery)
- Battery >50%

## Choosing the correct AnyKernel3 ZIP

Each release artifact is named by **KMI (Kernel Module Interface)** and **Security Patch Level (SPL)**.

- **KMI** — e.g. `android12-5.10`, `android13-5.10`, `android13-5.15`, `android14-5.15`, `android14-6.1`, `android15-6.6`, `android16-6.12`. Must match your device's current kernel version. Check with `uname -r` or in Settings → About phone → Kernel version.
- **SPL** — monthly security patch string in the filename. Pick the build closest to your current SPL; newer SPL is generally backwards compatible but read the release notes for breaking changes.

If you don't know which file to download, carefully read the description of KMI and Security patch level in the release notes before downloading.

## Install with Kernel Flasher (recommended)

This requires the flashing app to have root permissions. On first install from stock (no root yet), flash via recovery or fastboot instead, then use this method for subsequent upgrades.

### Steps

1. **Download the AnyKernel3 ZIP** for your KMI/SPL from the latest [Releases](https://github.com/WildKernels/GKI_KernelSU_SUSFS/releases) page.
2. **Open the Kernel Flasher app**, grant necessary root permissions when prompted.
3. **Select the AnyKernel3 ZIP** you downloaded and flash. Do not interrupt the process.
4. **Reboot** when prompted and verify KernelSU manager shows the expected version.

### Supported flashing apps

- [Kernel Flasher](https://github.com/fatalcoder524/KernelFlasher) — recommended, actively maintained
- [PixelFlasher](https://github.com/badabing2005/PixelFlasher) — alternative with advanced options

Both require root to flash a kernel from within Android. For initial installation without root, use fastboot (`fastboot flash boot`) or a custom recovery that can flash AnyKernel3 ZIPs.

## After flashing

- Install / update the matching KernelSU manager APK (see release assets `manager-apk-*`).
- If using SUSFS, install the SUSFS module via the manager.
- Verify with `su` or manager app that root is working.

## Troubleshooting

- **Bootloop** — restore your boot backup via fastboot/recovery.
- **Wrong KMI** — re-flash with the correct KMI variant; KMI mismatch is the most common failure.
- **Manager shows old version** — ensure you flashed the intended variant and rebooted fully.

---

Related: [Kernel Features Documentation](index.md) · [Releases](https://github.com/WildKernels/GKI_KernelSU_SUSFS/releases) · [Kernel Flasher](https://github.com/fatalcoder524/KernelFlasher)
