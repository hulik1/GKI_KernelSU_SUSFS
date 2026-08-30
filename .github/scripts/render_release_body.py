#!/usr/bin/env python3
"""
Render release notes dynamically from workflow environment variables.

No static template file is read. The script assembles the markdown directly
from env vars set by the workflow.

Invoke without a template file argument:
    python3 .github/scripts/render_release_body.py > release_body.md
"""

import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("GITHUB_WORKSPACE", "."))

def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()

def parse_managers(raw: str):
    raw = raw.strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return data

def build_preamble() -> str:
    return (
        "# Wild Kernels for GKI2 Devices\n\n"
        "> [!CAUTION]\n"
        "> This software is provided for testing and educational purposes only. "
        "Use at your own risk. The developers are not responsible for any damage, "
        "data loss, or issues that may occur. Please ensure you have proper backups "
        "before installation.\n\n"
        "Join the Telegram group: <https://t.me/WildKernelsTG>\n\n"
        "---\n\n"
    )

def build_managers_section(managers) -> str:
    if not managers:
        return ""
    flavor_labels = {"next": "KernelSU-Next", "kernelsu": "KernelSU", "resukisu": "ReSukiSU"}
    lines = []
    for m in managers:
        flavor = m.get("flavor", "")
        label = flavor_labels.get(flavor, flavor or "unknown")
        run_id = m.get("run_id")
        stock = m.get("stock", "")
        if run_id:
            url = f"https://github.com/{m.get('owner', '')}/{m.get('repo', '')}/actions/runs/{run_id}"
            stock_note = f" (stock `{stock[:12]}`)" if stock else ""
            lines.append(f"- **{label}:** [{url}]({url}){stock_note}")
        else:
            lines.append(f"- **{label}:** release assets")
    return "**Managers:**\n" + "\n".join(lines) + "\n"

def build_ksu_section() -> str:
    version = env("KSU_VERSION", "unknown")
    tag = env("KSU_GIT_TAG", "no-tag")
    branch = env("KSUN_BRANCH", "dev")
    commit = env("KSUN_COMMIT", "unknown")
    manager_url = env("KSU_MANAGER", "")
    manager_note = env("KSU_MANAGER_NOTE", "")
    parts = ["## KernelSU", ""]
    parts.append(f"- **Version:** `{version}`")
    if tag and tag != "no-tag":
        parts.append(f"- **Tag:** `{tag}`")
    parts.append(f"- **Branch:** `{branch}`")
    parts.append(f"- **Commit:** `{commit}`")
    if manager_url:
        note = f" — {manager_note}" if manager_note else ""
        base = manager_url.split("/actions/")[0]
        parts.append(f"- **Manager:** [{base}]({manager_url}){note}")
    parts.append("")
    return "\n".join(parts)

def build_susfs_section() -> str:
    variant_envs = [
        ("android12-5.10", "susfs_commit_android12_5_10"),
        ("android13-5.10", "susfs_commit_android13_5_10"),
        ("android13-5.15", "susfs_commit_android13_5_15"),
        ("android14-5.15", "susfs_commit_android14_5_15"),
        ("android14-6.1", "susfs_commit_android14_6_1"),
        ("android15-6.6", "susfs_commit_android15_6_6"),
        ("android16-6.12", "susfs_commit_android16_6_12"),
    ]
    per_variant = []
    for variant, env_key in variant_envs:
        sha = env(env_key)
        if sha and len(sha) == 40:
            per_variant.append((variant, sha))
    if per_variant:
        parts = [
            "## SUSFS",
            "",
            "Pinned SUSFS commits per Android/kernel variant:",
            "",
        ]
        for variant, sha in per_variant:
            parts.append(f"- **{variant}:** `{sha}`")
        parts.append("")
        return "\n".join(parts)
    sha = env("SUSFS_COMMIT", "")
    if sha:
        return f"## SUSFS\n\n- **Commit:** `{sha}`\n"
    return ""

def build_root_section() -> str:
    root_flavor = env("ROOT_FLAVOR", "unknown")
    feature_set = env("FEATURE_SET", "")
    parts = ["## This Build", ""]
    parts.append(f"- **Root:** `{root_flavor}`")
    if feature_set:
        parts.append(f"- **Feature Set:** `{feature_set}`")
    parts.append("")
    return "\n".join(parts)

def build_features_section() -> str:
    enabled = []
    if env("USE_SUSFS", "true") == "true":
        enabled.append("SUSFS")
    if env("USE_BBG", "true") == "true":
        enabled.append("Baseband Guard")
    if env("USE_DS", "true") == "true":
        enabled.append("DroidSpaces-OSS")
    if env("USE_NET", "true") == "true":
        enabled.append("Networking")
    if env("USE_NTSYNC", "true") == "true":
        enabled.append("NTSync")
    if env("USE_PTRACE", "true") == "true":
        enabled.append("Ptrace Leak Fix")
    if env("USE_UNICODE", "true") == "true":
        enabled.append("Unicode Fix")
    if env("USE_BPF", "true") == "true":
        enabled.append("BTF / eBPF / FUSE-BPF")
    if env("USE_PERF", "true") == "true":
        enabled.append("Performance Tuning")

    if not enabled:
        return ""

    parts = [
        "## Features Included",
        "",
        "Each feature is documented separately in `docs/`:",
        "",
    ]
    feature_doc_map = [
        ("SUSFS", "susfs.md"),
        ("Baseband Guard", "bbg.md"),
        ("DroidSpaces-OSS", "droidspaces.md"),
        ("Networking", "networking.md"),
        ("NTSync", "ntsync.md"),
        ("Ptrace Leak Fix", "ptrace.md"),
        ("Unicode Fix", "unicode.md"),
        ("BTF / eBPF / FUSE-BPF", "bpf.md"),
        ("Performance Tuning", "performance.md"),
    ]
    for feature, doc in feature_doc_map:
        if feature in enabled:
            parts.append(f"- [{feature}](docs/{doc})")
    parts.append("")
    return "\n".join(parts)

def render() -> str:
    parts = []
    parts.append(build_preamble())
    parts.append(build_root_section())
    parts.append(build_ksu_section())
    parts.append(build_susfs_section())
    parts.append(build_managers_section(parse_managers(env("MANAGER_LIST", ""))))
    parts.append(build_features_section())
    return "\n".join(parts)

if __name__ == "__main__":
    output = render()
    print(output, end="")
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        Path(step_summary).write_text(output)
