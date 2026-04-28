import os
import glob
import json
import base64
import requests
import xml.etree.ElementTree as ET
from collections import defaultdict

CONFIG_DIR = ".github/kernel-config"
MANIFEST_URL_TEMPLATE = "https://android.googlesource.com/kernel/manifest/+/refs/heads/common-{branch}/default.xml?format=TEXT"

# Gather all kernel versions from config files
kernel_versions = set()
config_map = {}  # kernel_version -> config file
for config_path in glob.glob(os.path.join(CONFIG_DIR, "*.json")):
    with open(config_path) as f:
        data = json.load(f)
        for entry in data.get("include", []):
            ver = entry.get("kernel_version")
            if ver:
                kernel_versions.add(ver)
                config_map[ver] = os.path.basename(config_path)

# Map kernel_version to manifest branch name
def kernel_version_to_branch(ver):
    # e.g. 6.1.25-android14-2023-06 -> android14-6.1-2023-06
    m = None
    import re
    m = re.match(r"([\d.]+)-android(\d+)-(\d{4}-\d{2}|lts|exp)", ver)
    if m:
        kver, android, date = m.groups()
        return f"android{android}-{kver}-{date}"
    return None

manifest_projects = defaultdict(set)  # resource -> set of kernel_versions

for ver in sorted(kernel_versions):
    branch = kernel_version_to_branch(ver)
    if not branch:
        print(f"Could not parse branch for kernel version: {ver}")
        continue
    url = MANIFEST_URL_TEMPLATE.format(branch=branch)
    print(f"Fetching manifest for {ver} ({branch})")
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"Failed to fetch {url}")
        continue
    xml_content = base64.b64decode(resp.content).decode("utf-8")
    root = ET.fromstring(xml_content)
    for project in root.findall("project"):
        name = project.get("name")
        path = project.get("path", name)
        manifest_projects[(name, path)].add(ver)

with open("manifest_resource_summary.md", "w") as f:
    f.write("| Resource Name | Path | Appears In Kernel Versions |\n")
    f.write("|--------------|------|----------------------------|\n")
    for (name, path), vers in sorted(manifest_projects.items()):
        f.write(f"| `{name}` | `{path}` | {', '.join(sorted(vers))} |\n")

print("Summary written to manifest_resource_summary.md")
