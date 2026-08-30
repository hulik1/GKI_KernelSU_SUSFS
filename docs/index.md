# Kernel Features - Documentation Index

Per-feature documentation for the GKI2 kernels built from this repository.

## Root Implementations

| Root Flavor | Description | Source |
|-------------|-------------|----------|
| [KernelSU-Next](kernelsu-next.md) | Root solution for GKI devices, original KernelSU-Next implementation, always at latest dev-tip. SUSFS-enabled builds sourced from pershoot fork. | [KernelSU-Next/KernelSU-Next](https://github.com/KernelSU-Next/KernelSU-Next) · [pershoot/KernelSU-Next](https://github.com/pershoot/KernelSU-Next) |
| [KernelSU (Classic)](kernelsu-classic.md) | Original KernelSU by tiann, pinned to verified commit. SUSFS patches applied during build. | [tiann/KernelSU](https://github.com/tiann/KernelSU) |
| [ReSukiSU](resukisu.md) | ReSukiSU root fork, pinned to verified commit. Own SUSFS pins per flavor. | [ReSukiSU/ReSukiSU](https://github.com/ReSukiSU/ReSukiSU) |

## Root Hiding

| Feature | Description | Source |
|---------|-------------|--------|
| [SUSFS](susfs.md) | Root-hiding add-on for KernelSU using kernel patches and a userspace module. | [simonpunk/susfs4ksu](https://gitlab.com/simonpunk/susfs4ksu) |
| [Ptrace Leak Fix](ptrace.md) | Fixes ptrace info leak on kernels older than 5.16. Internal to root hiding. | [patch](https://github.com/WildKernels/kernel_patches/blob/main/gki_ptrace.patch) |
| [Unicode Fix](unicode.md) | Prevents path traversal via non-printable Unicode (experimental). Internal to root hiding. | Internal to root hiding · [patch 6.1-](https://github.com/WildKernels/kernel_patches/blob/main/common/unicode_bypass_fix_6.1-.patch) · [patch 6.1+](https://github.com/WildKernels/kernel_patches/blob/main/common/unicode_bypass_fix_6.1+.patch) |

## Meta Module

| Module | Description | Source |
|--------|-------------|--------|
| [NoMount](nomount.md) | Metamodule providing mount-related functionality alongside root implementations. | [maxsteeel/nomount](https://github.com/maxsteeel/nomount) |
| [Mountify](mountify.md) | Globally mounted modules via OverlayFS. | [backslashxx/mountify](https://github.com/backslashxx/mountify) |

## Security

| Feature | Description | Source |
|---------|-------------|--------|
| [Baseband Guard](bbg.md) | Lightweight LSM blocking unauthorized writes to critical partitions and device nodes. | [vc-teahouse/Baseband-guard](https://github.com/vc-teahouse/Baseband-guard) |

## Networking

| Feature | Description | Source |
|---------|-------------|--------|
| [TCP Congestion Control](networking.md) | BBRv1, BBRv3, CUBIC, BIC, Westwood, HTCP | Upstream kernel |
| [WireGuard](networking.md) | Built-in VPN support | [wireguard/wireguard-linux-compat](https://git.zx2c4.com/wireguard-linux-compat/) |
| [IP Set / IPv6 NAT](networking.md) | Advanced firewall capabilities | Upstream kernel |
| [Conntrack / connmark](networking.md) | Connection marking for packet classification | Upstream kernel |
| [CIFS](networking.md) | SMB/CIFS network filesystem | Upstream kernel |
| [TTL Target](networking.md) | Network packet manipulation | Upstream kernel |

## Filesystem & Storage

| Feature | Description | Source |
|---------|-------------|--------|
| [TMPFS Extended Attributes](tmpfs.md) | Extended attributes on tmpfs | Upstream kernel |
| [TMPFS POSIX ACLs](tmpfs.md) | POSIX ACL support on tmpfs | Upstream kernel |

## Debugging, Tracing & BPF

| Feature | Description | Source |
|---------|-------------|--------|
| [BTF / eBPF / FUSE-BPF](bpf.md) | BPF Type Format, extended BPF, FUSE-BPF interaction | Upstream kernel |

## Performance

| Feature | Description | Source |
|---------|-------------|--------|
| [NTSync](ntsync.md) | High-performance synchronization primitives compatible with Windows NT kernel API. | Internal |
| [Performance Tuning](performance.md) | Kernel configuration and tuning options | Upstream kernel |

## Container Runtime

| Feature | Description | Source |
|---------|-------------|--------|
| [DroidSpaces-OSS](droidspaces.md) | LXC-inspired container runtime for Android/Linux | [ravindu644/Droidspaces-OSS](https://github.com/ravindu644/Droidspaces-OSS) |

---

**Installation** - see [Installation Guide](installation.md) ([Kernel Flasher](kernelflasher.md) · [Patch boot.img with magiskboot](magiskboot.md)).

**Release Notes** - for build-specific version/commit info, see the [release workflow](https://github.com/WildKernels/GKI_KernelSU_SUSFS/actions/workflows/main.yml) or the releases page.
