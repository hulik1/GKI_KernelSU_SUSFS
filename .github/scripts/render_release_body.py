import json
import os
import sys
from pathlib import Path


PLACEHOLDERS = {
    "{{KSU_VERSION}}": lambda: os.environ.get("KSU_VERSION", "unknown"),
    "{{KSU_GIT_TAG}}": lambda: os.environ.get("KSU_GIT_TAG", "no-tag"),
    "{{KSUN_BRANCH}}": lambda: os.environ.get("KSUN_BRANCH", "dev"),
    "{{KSUN_COMMIT}}": lambda: os.environ.get("KSUN_COMMIT", "unknown"),
    "{{KSU_MANAGER}}": lambda: os.environ.get("KSU_MANAGER", "Placeholder"),
    "{{KSU_MANAGER_NOTE}}": lambda: os.environ.get("KSU_MANAGER_NOTE", ""),
    "{{SUSFS_BRANCHES}}": lambda: os.environ.get("SUSFS_COMMIT", "latest on auto-derived gki-{version} branch"),
    "{{SUSFS_BRANCHS}}": lambda: os.environ.get("SUSFS_COMMIT", "latest on auto-derived gki-{version} branch"),
}


def build_managers_markdown(text: str) -> str:
    raw = os.environ.get("MANAGER_LIST", "").strip()
    if not raw:
        return text
    try:
        managers = json.loads(raw)
    except Exception:
        return text
    if not isinstance(managers, list) or not managers:
        return text
    # Build markdown list for all selected managers
    flavor_labels = {"next": "KernelSU-Next", "kernelsu": "KernelSU", "resukisu": "ReSukiSU"}
    lines = []
    for m in managers:
        flavor = m.get("flavor", "")
        label = flavor_labels.get(flavor, flavor or "unknown")
        run_id = m.get("run_id")
        owner = m.get("owner", "")
        repo = m.get("repo", "")
        stock = m.get("stock", "")
        if run_id and owner and repo:
            url = f"https://github.com/{owner}/{repo}/actions/runs/{run_id}"
            note = f" — stock `{stock[:12]}`" if stock else ""
            lines.append(f"- **{label}:** [build-manager run]({url}){note}")
        else:
            lines.append(f"- **{label}** manager (no run ID)")
    replacement = "**Managers:**\n" + "\n".join(lines)
    # Replace the single-manager line in template
    # Template has: **Manager:** [build-manager run]({{KSU_MANAGER}}) — {{KSU_MANAGER_NOTE}}
    # Replace that whole line if present
    import re
    text = re.sub(r"\*\*Manager:\*\*.*\n", replacement + "\n", text, count=1)
    return text


def filter_sections(text: str) -> str:
    # Map heading substring -> required env flag
    # If flag is "false", that section is dropped.
    flag_map = {
        "SUSFS": os.environ.get("USE_SUSFS", "true") == "true",
        "Baseband Guard": os.environ.get("USE_BBG", "true") == "true",
        "BBG": os.environ.get("USE_BBG", "true") == "true",
        "DroidSpaces": os.environ.get("USE_DS", "true") == "true",
        "Networking": os.environ.get("USE_NET", "true") == "true",
        "NTSync": os.environ.get("USE_NTSYNC", "true") == "true",
        "Ptrace": os.environ.get("USE_PTRACE", "true") == "true",
        "Unicode": os.environ.get("USE_UNICODE", "true") == "true",
        "BPF": os.environ.get("USE_BPF", "true") == "true",
    }
    # Split keeping delimiters: first chunk is preamble before first ## 
    parts = text.split("\n## ")
    if len(parts) <= 1:
        return text
    kept = [parts[0]]
    for part in parts[1:]:
        heading_line = part.split("\n", 1)[0]
        keep = True
        for key, enabled in flag_map.items():
            if key.lower() in heading_line.lower() and not enabled:
                keep = False
                break
        # Also drop specific subsections inside Misc/Other Features if relevant
        # For now only top-level headings filtered; keep is per heading.
        if keep:
            kept.append("## " + part)
    return "\n".join(kept) if len(kept) > 1 else parts[0] + "\n## ".join(kept[1:])


def inject_feature_summary(text: str) -> str:
    feature_set = os.environ.get("FEATURE_SET", "").strip()
    root_flavor = os.environ.get("ROOT_FLAVOR", "").strip()
    if not feature_set and not root_flavor:
        return text
    summary_lines = []
    if root_flavor:
        summary_lines.append(f"**Root:** {root_flavor}")
    if feature_set:
        summary_lines.append(f"**Features:** {feature_set}")
    # Insert after the Features anchor list or after disclaimer
    summary = "> " + " | ".join(summary_lines) + "\n" if summary_lines else ""
    # Find the Features anchor list end (line with <!-- NOTE:)
    marker = "<!-- NOTE:"
    if marker in text and summary:
        text = text.replace(marker, summary + "\n" + marker, 1)
    return text


def render_markdown(template_path: Path):
    text = template_path.read_text()

    for placeholder, getter in PLACEHOLDERS.items():
        text = text.replace(placeholder, getter())

    text = build_managers_markdown(text)
    text = inject_feature_summary(text)
    text = filter_sections(text)

    print(text, end="")


config_path = Path(sys.argv[1])
if config_path.suffix.lower() == ".md":
    render_markdown(config_path)
    sys.exit(0)

# Backward-compatible JSON renderer for older release configs.

def emit(text=""):
    print(text)


def emit_list(items):
    if isinstance(items, list):
        for item in items:
            emit(f"- {item}")


def emit_description(value):
    if isinstance(value, list):
        for line in value:
            emit(line)
    elif value:
        emit(str(value))


data = json.loads(config_path.read_text())

emit("**IMPORTANT DISCLAIMER**")
for line in data["release"]["disclaimer"]:
    emit(line)

kernelsu = data.get("kernelsu", {})
emit()
emit(f"## {kernelsu.get('name', 'KernelSU-Next')}")
emit(f"- Version: {os.environ.get('KSU_VERSION', kernelsu.get('version', 'unknown'))}")
emit(f"- Tag: {os.environ.get('KSU_GIT_TAG', kernelsu.get('tag', 'no-tag'))}")
emit(f"- Branch: {os.environ.get('KSUN_BRANCH', kernelsu.get('branch', 'dev'))}")
emit(f"- Commit: {os.environ.get('KSUN_COMMIT', kernelsu.get('commit', 'unknown'))}")
if kernelsu.get("url"):
    emit(f"- URL: {kernelsu['url']}")
if kernelsu.get("manager"):
    emit(f"- Manager: {kernelsu['manager']}")

skip_keys = {"release", "kernelsu"}
for key in data.keys():
    if key in skip_keys:
        continue

    section = data[key]
    emit()
    emit(f"## {section.get('name', key)}")

    if section.get("description"):
        emit_description(section["description"])

    if section.get("version"):
        emit(f"- Version: {section['version']}")
    if section.get("tag"):
        emit(f"- Tag: {section['tag']}")
    if section.get("branch"):
        emit(f"- Branch: {section['branch']}")

    if key == "susfs":
        susfs_commit = os.environ.get("SUSFS_COMMIT", "")
        if susfs_commit:
            emit(f"- Commit: `{susfs_commit}`")
        else:
            emit("- Commit: latest on auto-derived gki-{version} branch")

    if section.get("items"):
        emit_list(section["items"])

    if section.get("url"):
        emit(f"- URL: {section['url']}")
