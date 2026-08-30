# Unicode Fix

The Unicode Fix prevents path traversal and other detections using non-printable Unicode codepoints.

This fix is marked as experimental.

## Purpose

Certain path traversal attacks and detection-evasion techniques can use non-printable Unicode codepoints. The Unicode Fix patches the kernel to mitigate these vectors.

## Status

**Experimental** — use at your own risk.

## Build Integration

The Unicode Fix is applied as a patch during the build workflow when `use_unicode` is enabled. It is enabled by default.

## Related

- [index.md](../index.md) — full feature index
