# Kernel Features — Documentation Index

Per-feature documentation for the GKI2 kernels built from this repository.

## Root Implementations

| Feature | Doc | Source |
|---------|-----|--------|
| KernelSU-Next | [kernelsu.md](kernelsu.md) | [KernelSU-Next/KernelSU-Next](https://github.com/KernelSU-Next/KernelSU-Next) |
| KernelSU | [kernelsu.md](kernelsu.md) | [tiann/KernelSU](https://github.com/tiann/KernelSU) |
| ReSukiSU | [kernelsu.md](kernelsu.md) | [ReSukiSU/ReSukiSU](https://github.com/ReSukiSU/ReSukiSU) |
| NoMount | [nomount.md](nomount.md) | [maxsteeel/nomount](https://github.com/maxsteeel/nomount) |

## Root Hiding & Security

| Feature | Doc | Source |
|---------|-----|--------|
| SUSFS | [susfs.md](susfs.md) | [simonpunk/susfs4ksu](https://gitlab.com/simonpunk/susfs4ksu) |
| Baseband Guard | [bbg.md](bbg.md) | [vc-teahouse/Baseband-guard](https://github.com/vc-teahouse/Baseband-guard) |

## Kernel Modules & Compatibility

| Feature | Doc | Source |
|---------|-----|--------|
| NTSync | [ntsync.md](ntsync.md) | Internal (synthesized from kernel feature set) |

## Networking

| Feature | Doc | Source |
|---------|-----|--------|
| TCP Congestion Control (BBRv1, BBRv3, CUBIC, BIC, Westwood, HTCP) | [networking.md](networking.md) | Upstream kernel |
| WireGuard | [networking.md](networking.md) | [wireguard/wireguard-linux-compat](https://git.zx2c4.com/wireguard-linux-compat/) |
| IP Set / IPv6 NAT | [networking.md](networking.md) | Upstream kernel |
| Conntrack / connmark | [networking.md](networking.md) | Upstream kernel |
| CIFS (SMB/CIFS) | [networking.md](networking.md) | Upstream kernel |
| TTL Target | [networking.md](networking.md) | Upstream kernel |

## Filesystem & Storage

| Feature | Doc | Source |
|---------|-----|--------|
| TMPFS Extended Attributes | [tmpfs.md](tmpfs.md) | Upstream kernel |
| TMPFS POSIX ACLs | [tmpfs.md](tmpfs.md) | Upstream kernel |

## Debugging, Tracing & BPF

| Feature | Doc | Source |
|---------|-----|--------|
| BTF / eBPF / FUSE-BPF | [bpf.md](bpf.md) | Upstream kernel |
| Ptrace Leak Fix | [ptrace.md](ptrace.md) | Upstream kernel community |
| Unicode Fix | [unicode.md](unicode.md) | Internal |

## Performance

| Feature | Doc | Source |
|---------|-----|--------|
| Performance Tuning | [performance.md](performance.md) | Upstream kernel |

## Container Runtime

| Feature | Doc | Source |
|---------|-----|--------|
| DroidSpaces-OSS | [droidspaces.md](droidspaces.md) | [ravindu644/Droidspaces-OSS](https://github.com/ravindu644/Droidspaces-OSS) |

---

**Release Notes** — for build-specific version/commit info, see the [release workflow](https://github.com/WildKernels/GKI_KernelSU_SUSFS/actions/workflows/main.yml) or the releases page.
