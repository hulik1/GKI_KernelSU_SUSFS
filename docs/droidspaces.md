# DroidSpaces-OSS

DroidSpaces-OSS is a lightweight, LXC-inspired container runtime for Android and Linux, allowing full Linux distributions to run natively with zero performance penalty.

## Source

- **Upstream:** [ravindu644/Droidspaces-OSS](https://github.com/ravindu644/Droidspaces-OSS)

## Purpose

DroidSpaces provides container-like isolation for running Linux distributions on Android, using an LXC-inspired approach. It is designed to have minimal performance overhead.

## Build Integration

DroidSpaces-OSS patches are applied during the build workflow when `use_ds` is enabled. The source commit is resolved at the latest `main` branch tip at build time.

## Related

- [index.md](../index.md) — full feature index
