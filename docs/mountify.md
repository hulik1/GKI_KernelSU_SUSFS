# Mountify

Globally mounted modules via OverlayFS - metamodule enabling `CONFIG_OVERLAY_FS=y` is required.

## Source

- **Upstream:** [backslashxx/mountify](https://github.com/backslashxx/mountify)

## Description

Mountify is a metamodule that globally mounts modules via OverlayFS. It acts as a KernelSU metamodule and also works on APatch and Magisk.

- `CONFIG_OVERLAY_FS=y` is **required**
- `CONFIG_TMPFS_XATTR=y` is **highly encouraged** (in the source / available in kernel config)

It overlays `/mnt/vendor/fake_folder_name/system/bin` to `/system/bin` and other folders, mimicking an OEM mount.

## Build Integration

Mountify is documented as a meta module. Kernel config requirements are noted above - ensure `CONFIG_OVERLAY_FS=y` and `CONFIG_TMPFS_XATTR=y` are enabled in the kernel source.

## Related

- [nomount.md](nomount.md) - mount metamodule
- [index.md](index.md) - full feature index
