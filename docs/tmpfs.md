# TMPFS Features

The kernel includes extended attributes (xattr) and POSIX ACL support for tmpfs.

## TMPFS Extended Attributes (`TMPFS_XATTR`)

Enables extended attributes on tmpfs filesystems. This is required for Mountify support and other features that depend on extended attributes on tmpfs.

## TMPFS POSIX ACLs (`TMPFS_POSIX_ACL`)

Enables POSIX Access Control Lists on tmpfs filesystems, allowing more fine-grained permission control on tmpfs-mounted files.

## Build Integration

Both features are enabled via kernel configuration options (`CONFIG_TMPFS_XATTR` and `CONFIG_TMPFS_POSIX_ACL`) and are included in the builds by default when the corresponding feature flags are set.

## Related

- [index.md](../index.md) — full feature index
