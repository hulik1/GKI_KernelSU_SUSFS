# NoMount

NoMount is a metamodule for the Android kernel that provides mount-related functionality used alongside root implementations.

This repository builds a flashable NoMount metamodule from the pinned NoMount source commit and uploads it as a separate artifact alongside the kernel build.

## Source

- **Repository:** [maxsteeel/nomount](https://github.com/maxsteeel/nomount)
- **Branch:** `dev`

## Build Integration

NoMount is resolved either at a pinned verified commit (when `commit_mode=verified`) or at the latest `dev` branch tip (when `commit_mode=latest` or `update`).

The build workflow:
1. Clones the NoMount source at the resolved commit.
2. Builds the metamodule archive from that commit.
3. Uploads the metamodule as `NoMount-Metamodule`.

The kernel and metamodule revisions must match exactly. The NoMount integration invokes the upstream `kernel/setup.sh` by its full immutable commit URL and passes that same SHA as the script argument.

## Related

- [kernelsu.md](kernelsu.md) — root implementation
- [index.md](../index.md) — full feature index
