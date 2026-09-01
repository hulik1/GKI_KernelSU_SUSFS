# Installation

> [!CAUTION]
> Wild Kernels is not responsible for bricked devices or damage. By flashing, you assume all risk. Back up your data and understand the risks before flashing.

## Choose your method

| Method | When to use | Requires root |
|--------|-------------|---------------|
| **Kernel Flasher** | Upgrading with root already available, no PC needed | Yes |
| **magiskboot** | Flash a pre-patched `boot.img` directly (no pre-rooted setup required) | No |

Expand the section you need below — all are collapsed by default.

## Prerequisites

- [ ] GKI 2.0 device with an unlocked bootloader
- [ ] Full backup (at minimal the `boot` partition or have a stock unmodified `boot.img`)
- [ ] Correct AnyKernel3 ZIP for your kernel version from [Releases](https://github.com/WildKernels/GKI_KernelSU_SUSFS/releases)

### Supported versions

Only GKI 2.0 is supported — check marks show builds provided by this project:

| Pre-GKI | GKI 1.0 | GKI 2.0 |
|---------|---------|---------|
| 3.10.x | 5.4.x | 5.10.x-android12 ✓ |
| 3.18.x | | 5.10.x-android13 ✓ |
| 4.4.x | | 5.15.x-android13 ✓ |
| 4.9.x | | 5.15.x-android14 ✓ |
| 4.14.x | | 6.1.x-android14 ✓ |
| 4.19.x | | 6.6.x-android15 ✓ |
| | | 6.12.x-android16 ✓ |

For Pre-GKI or GKI 1.0 kernels, contact [@TheWildJames](https://t.me/TheWildJames) to discuss possiblities.

> [!IMPORTANT]
> Match by the full kernel version (e.g., `6.1.x-androidXX`) — your device's Android version and the `androidXX` in the kernel version are not necessarily the same. For example, as of writing, a Google Pixel 8 is on `6.1.157-android14` while the system Android is 17.

## Supported Devices

> [!NOTE]
> These lists are maintained by the community — please update as needed!

See **[Supported Devices](supported-devices.md)**.

---

<details>
<summary><b> Install with Kernel Flasher — no PC, requires root</b></summary>

> [!NOTE]
> More convenient when upgrading KernelSU and can be done without a computer.

- Root access already granted to the flashing app (for first install from stock without root, use recovery/fastboot — see magiskboot section below)
- AnyKernel3 ZIP matching your kernel version from [Releases](https://github.com/WildKernels/GKI_KernelSU_SUSFS/releases)

**Steps:**

1. **Download the AnyKernel3 ZIP** from the latest [Releases](https://github.com/WildKernels/GKI_KernelSU_SUSFS/releases) page.
2. **Open the Kernel Flasher app**, grant root permissions when prompted.
3. **Select the AnyKernel3 ZIP** and flash. Do not interrupt.
4. **Reboot** when prompted and verify the manager shows the expected version.

**Supported flashing apps:**

| App | Notes |
|-----|-------|
| [Kernel Flasher](https://github.com/fatalcoder524/KernelFlasher) | Recommended, actively maintained |

</details>

<details>
<summary><b> Patch boot.img Manually (magiskboot) — Android / Linux</b></summary>

> [!TIP]
> Use the [official magiskboot build](https://github.com/topjohnwu/Magisk/releases) — works on Android and Linux.

**Preparation:**

1. Get your device's stock `boot.img`.
2. Download the AnyKernel3 ZIP for your kernel version from [Releases](https://github.com/WildKernels/GKI_KernelSU_SUSFS/releases).
3. Unpack the ZIP and get the `Image` file (the KernelSU kernel).

**Android** — via adb + `libmagiskboot.so` (in `/data/local/tmp/`):

```sh
# Push files
adb push Magisk-*/lib/arm64-v8a/libmagiskboot.so /data/local/tmp/magiskboot
adb push boot.img /data/local/tmp/
adb push Image /data/local/tmp/

# On device
adb shell
cd /data/local/tmp/
chmod +x magiskboot
./magiskboot unpack boot.img
mv -f Image kernel
./magiskboot repack boot.img
# Test then flash
fastboot boot new-boot.img
fastboot flash boot new-boot.img
```

**Linux** — official magiskboot:

```sh
chmod +x magiskboot
./magiskboot unpack boot.img
mv -f Image kernel
./magiskboot repack boot.img
fastboot boot new-boot.img
fastboot flash boot new-boot.img
```

</details>

<details>
<summary><b> Post-Install — Verify &amp; Finish Setup</b></summary>

Do these checks in order after flashing:

**1. Download matching manager — KernelSU / KernelSU-Next / ReSukiSU**

- [ ] Download the `manager-apk-*` from the same [Releases](https://github.com/WildKernels/GKI_KernelSU_SUSFS/releases) page you got the kernel from.
- [ ] Install / update it over any existing manager.
- [ ] Open the manager — it should show the kernel version you just flashed (e.g. `6.1.x-androidXX-Wild`) and report "Working".

**2. SUSFS**

- [ ] In the manager, install the [sidex15/susfs4ksu-module](https://github.com/sidex15/susfs4ksu-module).
- [ ] Reboot.

**3. Meta Module (if mounting modules)**

- [ ] [NoMount](https://github.com/maxsteeel/nomount) (Recommended) — `NoMount-metamodule-*commit*.zip` from [Releases](https://github.com/WildKernels/GKI_KernelSU_SUSFS/releases)
- [ ] [Mountify](https://github.com/backslashxx/mountify) — latest compatible module

> [!NOTE]
> Only one is required. Compatibility with SUSFS shifts with updates.

**4. DroidSpaces**

- [ ] Download the app: [ravindu644/Droidspaces-OSS](https://github.com/ravindu644/Droidspaces-OSS)

**5. Troubleshooting**

- **General issues** — try restarting your device.
- **Bootloop** — restore a stock boot.img via fastboot/recovery.
- **Manager and kernel version do not match (e.g. 31000 != 32000)** — install the latest kernel and manager from the release and reboot.
- **Root not working** — ensure the manager matches the flashed flavor (KernelSU / KernelSU-Next / ReSukiSU).

> [!CAUTION]
> **Nuclear option:** Uninstall all modules and reboot, then delete all files and folders in `/data/adb`. Reboot again. This wipes all KernelSU/Magisk module data — only use if nothing else works.

</details>

---

## Other methods

<details>
<summary>Alternative flashing tools</summary>

- [PixelFlasher](https://github.com/badabing2005/PixelFlasher)
- [Franco Kernel Manager](https://play.google.com/store/apps/details?id=com.franco.kernel&hl=en_CA&pli=1)

</details>

---

> [!NOTE]
> Portions of this documentation are adapted from the official [KernelSU documentation](https://kernelsu.org/).

See also: [Kernel Features Documentation](features.md)
