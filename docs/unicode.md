# Unicode Fix

Prevents path traversal via non-printable Unicode (experimental). Internal to root hiding.

## Source

- **Source:** Internal to root hiding - [patch 6.1-](https://github.com/WildKernels/kernel_patches/blob/main/common/unicode_bypass_fix_6.1-.patch) (`kernel_patches/common/unicode_bypass_fix_6.1-.patch`) · [patch 6.1+](https://github.com/WildKernels/kernel_patches/blob/main/common/unicode_bypass_fix_6.1+.patch) (`kernel_patches/common/unicode_bypass_fix_6.1+.patch`)

## Purpose

Certain path traversal attacks and detection-evasion techniques can use non-printable Unicode codepoints. The Unicode Fix patches the kernel to mitigate these vectors.

It is documented as internal to root hiding (SUSFS/KernelSU) - not a standalone top-level feature.

## Status

**Experimental** - use at your own risk.

## Build Integration

The Unicode Fix is applied as a patch during the build workflow when `use_unicode` is enabled. It is enabled by default.

## Related

- [susfs4ksu.md](susfs4ksu.md) - root hiding
- [index.md](index.md) - full feature index
