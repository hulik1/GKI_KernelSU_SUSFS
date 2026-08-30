# Patch boot.img Manually (magiskboot)

For some devices, the `boot.img` format isn't as common as `lz4`, `gz`, and uncompressed. A typical example is the Pixel, where the `boot.img` is compressed in the `lz4_legacy` format, while the ramdisk may be in `gz` or also compressed in `lz4_legacy`. Currently, if you directly flash the `boot.img` provided by KernelSU, the device may not be able to boot. In this case, you can manually patch the `boot.img`.

> [!TIP]
> It's always recommended to use `magiskboot` to patch images. There are two ways:
> - [magiskboot (official)](https://github.com/topjohnwu/Magisk/releases) - runs on Android devices (and Linux)
> - [magiskboot_build](https://github.com/capntrips/magiskboot_build) - cross-built binaries for Windows/macOS/Linux PCs
>
> The official build of `magiskboot` can only run on Android devices. If you want to run it on a PC, use the second option.

> [!WARNING]
> `Android-Image-Kitchen` isn't recommended for now because it doesn't handle the boot metadata (such as security patch level) correctly. Therefore, it may not work on some devices.

## Preparation

1. Get your device's stock `boot.img`. You can get it from your device manufacturer. You may need [payload-dumper-go](https://github.com/ssut/payload-dumper-go).
2. Download the AnyKernel3 ZIP file provided by KernelSU that matches the KMI version of your device.
3. Unpack the AnyKernel3 package and get the `Image` file, which is the kernel file of KernelSU.

## Using magiskboot on Android devices

1. Download latest Magisk from [GitHub Releases](https://github.com/topjohnwu/Magisk/releases).
2. Rename `Magisk-*(version).apk` to `Magisk-*.zip` and unzip it.
3. Push `libmagiskboot.so` to your device by ADB:
   ```sh
   adb push Magisk-*/lib/arm64-v8a/libmagiskboot.so /data/local/tmp/magiskboot
   ```
4. Push stock `boot.img` and `Image` from AnyKernel3 to your device:
   ```sh
   adb push boot.img /data/local/tmp/
   adb push Image /data/local/tmp/
   ```
5. Enter ADB shell and make it executable:
   ```sh
   adb shell
   cd /data/local/tmp/
   chmod +x magiskboot
   ```
6. Unpack `boot.img`:
   ```sh
   ./magiskboot unpack boot.img
   ```
   You will get a `kernel` file - this is your stock kernel.
7. Replace kernel with the KernelSU Image:
   ```sh
   mv -f Image kernel
   ```
8. Repack the boot image:
   ```sh
   ./magiskboot repack boot.img
   ```
   You will get a `new-boot.img` file. Flash this file to your device by fastboot:
   ```sh
   fastboot flash boot new-boot.img
   ```

## Using magiskboot on Windows / macOS / Linux PC

1. Download the corresponding `magiskboot` binary for your OS from [magiskboot_build](https://github.com/capntrips/magiskboot_build).
2. Prepare stock `boot.img` and `Image` in your PC.
3. Make it executable:
   ```sh
   chmod +x magiskboot
   ```
4. Unpack `boot.img`:
   ```sh
   ./magiskboot unpack boot.img
   ```
   You will get a `kernel` file - this is your stock kernel.
5. Replace kernel:
   ```sh
   mv -f Image kernel
   ```
6. Repack:
   ```sh
   ./magiskboot repack boot.img
   ```
   You will get a `new-boot.img` file. Flash it by fastboot:
   ```sh
   fastboot flash boot new-boot.img
   ```

> [!INFO]
> Official `magiskboot` can run in Linux environments normally. If you're a Linux user, you can use the official build.

---

Related: [Installation Overview](installation.md) · [Install with Kernel Flasher](kernelflasher.md) · [Releases](https://github.com/WildKernels/GKI_KernelSU_SUSFS/releases)
