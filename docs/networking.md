# Networking Features

This kernel includes a range of networking features and improvements, covering congestion control, VPN support, firewall capabilities, and traffic shaping.

## Congestion Control

| Algorithm | Description |
|-----------|-------------|
| **BBRv1** | Improved TCP congestion control. |
| **BBRv3** | Improved TCP congestion control. Available for Android 12 (5.10) through Android 15 (6.6); Android 16 (6.12) support coming soon. |
| **CUBIC** | Default TCP congestion control for many Linux systems. |
| **BIC** | Binary Increase Congestion control. |
| **Westwood** | TCP congestion control optimized for heterogeneous networks. |
| **HTCP** | H-TCP congestion control. |

## VPN Support

- **WireGuard** - Built-in VPN support via the WireGuard kernel module.

## Firewall & NAT

- **IP Set** - Advanced firewall capabilities via ip_set.
- **IPv6 NAT** - NAT support for IPv6.
- **TTL Target** - Network packet manipulation via TTL targeting.

## Traffic Shaping & Fair Queuing

- **CAKE** - Common Applications Kept Enhanced; a full-featured queue discipline.
- **fq** - Fair Queue packet scheduler.
- **fq_codel** - Fair Queuing with Controlled Delay.

## Connection Marking

- **connmark** - Connection marking for packet classification.

## Filesystem Support

- **CIFS** - Network filesystem support for SMB/CIFS sharing.

## Build Integration

Most networking features are upstream kernel configurations enabled in the kernel config for each Android/kernel variant. BBRv3 backports are applied as patches for specific Android/kernel versions.

## Related

- [index.md](../index.md) - full feature index
